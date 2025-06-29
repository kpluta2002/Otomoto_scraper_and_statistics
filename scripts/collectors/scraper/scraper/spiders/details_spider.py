from typing import Literal, TypeAlias
from urllib.parse import urljoin

import scrapy
import scrapy.signals
from parsel import Selector
from scrapy.http import Request, Response
from sqlalchemy import and_, exists, not_, select, update
from sqlalchemy.orm import Session

from scripts.collectors.scraper.scraper import items as i
from scripts.collectors.scraper.scraper.items import DetailsItem
from scripts.shared.Models import RawDetails, RawListing
from scripts.utils import EnvUtil as env
from scripts.utils.DbUtil import DbConnector as db
from scripts.utils.LoggerUtil import Logger

terminal = Logger("DetailsSpider")
QUEUED = "Queued"
READY = "Ready"
CRAWLED = "Crawled"
STATUS_TYPE: TypeAlias = Literal["Queued", "Ready", "Crawled"]

BATCH_SIZE = 1000


def _extract_raw_to_item(item: DetailsItem, article: Selector, field: i.TYPE):
    item[field[i.NAME]] = article.xpath(field[i.SELECTOR]).get()


def _extract_all_raw_to_item(item: DetailsItem, response: Response, field: i.TYPE):
    all_text_nodes = response.xpath(field[i.SELECTOR]).getall()

    item[field[i.NAME]] = [text.strip() for text in all_text_nodes if text.strip()]


def _extract_text_to_item(item: DetailsItem, response: Response, field: i.TYPE):
    all_text_nodes = response.xpath(
        f"{field[i.SELECTOR]}//text()[not(ancestor::style) and not(ancestor::script)]"
    ).getall()

    item[field[i.NAME]] = [text.strip() for text in all_text_nodes if text.strip()]


def get_missing_and_ready_listing_ids_from_db(session: Session, limit: int) -> list[str]:
    """Fetches all IDs from RawListing that do not have a corresponding entry in RawDetails."""
    query = (
        select(RawListing.id)
        .where(
            and_(
                not_(exists(select(1).where(RawDetails.id == RawListing.id))),
                RawListing.status == READY,
            )
        )
        .limit(limit)
    )

    result = session.execute(query).scalars().all()
    return [str(id_) for id_ in result]


def set_listing_ids_status(session: Session, ids: list, status: STATUS_TYPE):
    query = update(RawListing).where(RawListing.id.in_(ids)).values(status=status)
    session.execute(query)
    session.commit()
    return True


def set_not_crawled_listing_ids_status(session: Session, ids: list, status: STATUS_TYPE):
    query = (
        update(RawListing)
        .where(and_(RawListing.id.in_(ids), not_(RawListing.status == CRAWLED)))
        .values(status=status)
    )
    session.execute(query)
    session.commit()
    return True


def yield_missing_details_ids_from_db(session: Session):
    """Yields IDs from RawListing that do not have a corresponding entry in RawDetails."""
    query = select(RawListing.id).where(
        not_(exists(select(1).where(RawDetails.id == RawListing.id)))
    )
    for id_ in session.execute(query).scalars():
        yield str(id_)


def _get_amount_of_missing_details_from_db(session: Session) -> int:
    query = select(RawListing.id).where(
        not_(exists(select(1).where(RawDetails.id == RawListing.id)))
    )

    result = session.execute(query).fetchall()

    return len(result)


class DetailsSpider(scrapy.Spider):
    name = "details"
    allowed_domains = ["otomoto.pl"]
    start_urls = []
    custom_settings = {
        "LOG_FILE": env.root + "/scripts/collectors/scraper/logs/details_spider.log",
        "LOG_FILE_APPEND": False,
        "ITEM_PIPELINES": {
            "scraper.pipelines.DetailsItemPipeline": 300,
        },
        "CONCURRENT_REQUESTS_PER_DOMAIN": 2,
        "CONCURRENT_REQUESTS": 6,
        "REDIRECT_ENABLED": True,
    }

    def __init__(self, max_pages=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        current_session = db().get_session()
        try:
            self.pages_to_crawl_count = _get_amount_of_missing_details_from_db(current_session)
        finally:
            current_session.close()
        self.base_url = "https://www.otomoto.pl/"
        self.missing_ids = []
        terminal.debug(f"Spider initialized with {self.pages_to_crawl_count} pages to crawl...")

    async def start(self):
        while True:
            with db().get_session() as current_session:
                self.missing_ids = get_missing_and_ready_listing_ids_from_db(
                    current_session, BATCH_SIZE
                )
                set_listing_ids_status(current_session, self.missing_ids, QUEUED)
                found_ids = False

                for car_id in self.missing_ids:
                    found_ids = True
                    details_url = urljoin(self.base_url, str(car_id))

                    if self.crawler.engine.needs_backout():
                        terminal.info(
                            "Scheduler needs backout. Waiting for scheduler to become empty..."
                        )
                        await self.crawler.signals.wait_for(scrapy.signals.scheduler_empty)
                        terminal.info("Scheduler is empty. Resuming yielding requests.")

                    yield Request(
                        url=details_url,
                        callback=self.parse,
                        meta={"details_id": car_id},
                        headers={"Referer": "https://www.otomoto.pl/osobowe/"},
                    )

                set_not_crawled_listing_ids_status(current_session, self.missing_ids, READY)

                if not found_ids:
                    terminal.info("No missing details found. Spider will finish.")

    def parse(self, response: Response):
        # Retrieve the details_id from the request's meta
        details_id = response.meta.get("details_id")

        if not details_id:
            self.logger.error(
                f"Request {response.url} did not have 'details_id' in meta. Skipping."
            )
            return

        terminal.debug(f"Crawling details page for ID: {details_id} at URL: {response.url}")

        item = DetailsItem()
        item[DetailsItem.ID[i.NAME]] = details_id
        item[DetailsItem.PAGE_URL[i.NAME]] = response.url

        _extract_text_to_item(item, response, DetailsItem.RAW_DESCRIPTION)
        _extract_text_to_item(item, response, DetailsItem.RAW_BASIC_INFORMATION)
        _extract_text_to_item(item, response, DetailsItem.RAW_SPECIFICATION)
        _extract_text_to_item(item, response, DetailsItem.RAW_EQUIPMENT)
        _extract_all_raw_to_item(item, response, DetailsItem.RAW_SELLER_INFO)

        yield item

        with db().get_session() as current_session:
            set_listing_ids_status(current_session, [details_id], CRAWLED)

        self.pages_to_crawl_count -= 1
        terminal.debug(f"Processed ID: {details_id}. Pages to crawl: {self.pages_to_crawl_count}")

    def closed(self, reason):
        terminal.info("Spider closing - updating QUEUED statuses to READY...")
        with db().get_session() as current_session:
            set_not_crawled_listing_ids_status(current_session, self.missing_ids, READY)
