import re

import scrapy
from parsel import Selector
from scrapy.http import Response

from scripts.collectors.scraper.scraper import items as i
from scripts.collectors.scraper.scraper.items import ListingItem
from scripts.utils import EnvUtil as env
from scripts.utils.LoggerUtil import Logger

terminal = Logger("ListingSpider")


def _extract_raw_to_item(item: ListingItem, article: Selector, field: i.TYPE):
    item[field[i.NAME]] = article.xpath(field[i.SELECTOR]).get()


def _extract_text_to_item(item: ListingItem, article: Selector, field: i.TYPE):
    if not article:
        return []

    all_text_nodes = article.xpath(
        f"{field[i.SELECTOR]}//text()[not(ancestor::style) and not(ancestor::script)]"
    ).getall()

    item[field[i.NAME]] = [text.strip() for text in all_text_nodes if text.strip()]


class ListingSpider(scrapy.Spider):
    name = "listing"
    allowed_domains = ["otomoto.pl"]
    start_urls = ["https://www.otomoto.pl/osobowe?search%5Border%5D=created_at_first%3Adesc"]
    custom_settings = {
        "LOG_FILE": env.root + "/scripts/collectors/scraper/logs/listing_spider.log",
        "LOG_FILE_APPEND": False,
        "ITEM_PIPELINES": {
            "scraper.pipelines.ListingItemPipeline": 300,
        },
    }

    def __init__(self, max_pages=1, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.max_pages_to_crawl = int(max_pages)
        terminal.info(f"Spider initialized with max_pages_to_crawl: {self.max_pages_to_crawl}")

    def parse(self, response: Response):
        terminal.info(f"Crawling listing page: {response.url}")

        listings = response.xpath(ListingItem.CONTAINER_ARTICLE[i.SELECTOR])

        for listing_element in listings:
            item = ListingItem()

            item[ListingItem.PAGE_URL[i.NAME]] = response.url

            _extract_raw_to_item(item, listing_element, ListingItem.CONTAINER_ID)

            if not item[ListingItem.CONTAINER_ID[i.NAME]]:
                self.logger.warning(
                    f"Skipping listing as no data-id found for element: {listing_element.get()}"
                )
                continue

            _extract_text_to_item(item, listing_element, ListingItem.CONTAINER_SECTION_SUMMARY)
            _extract_text_to_item(item, listing_element, ListingItem.CONTAINER_SECTION_DETAILS)
            _extract_text_to_item(item, listing_element, ListingItem.CONTAINER_SECTION_PRICE)

            yield item

        current_page = 1
        match = re.search(r"page=(\d+)", response.url)
        if match:
            current_page = int(match.group(1))

        terminal.debug(
            f"Current page: {current_page}, Max pages to crawl: {self.max_pages_to_crawl}"
        )

        if current_page < self.max_pages_to_crawl:
            next_page = current_page + 1

            if "?" in response.url:
                next_page_url = re.sub(r"(page=)\d+", r"\g<1>" + str(next_page), response.url)
                if not re.search(
                    r"page=\d+", response.url
                ):  # If 'page=' not already in URL, add it
                    next_page_url = f"{response.url}&page={next_page}"
            else:
                next_page_url = f"{response.url}?page={next_page}"

            self.logger.info(f"Constructed next page URL: {next_page_url}")
            yield response.follow(next_page_url, callback=self.parse)
        else:
            terminal.debug(
                f"Reached maximum of {self.max_pages_to_crawl} pages. Stopping pagination."
            )
