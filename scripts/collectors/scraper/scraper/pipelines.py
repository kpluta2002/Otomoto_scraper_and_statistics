from datetime import datetime

from itemadapter import ItemAdapter
from scrapy.spiders import Spider
from sqlalchemy.exc import IntegrityError

from scripts.collectors.scraper.scraper import items as i
from scripts.collectors.scraper.scraper.items import DetailsItem as di
from scripts.collectors.scraper.scraper.items import ListingItem as li
from scripts.shared.Models import RawDetails, RawListing
from scripts.utils.DbUtil import DbConnector as db
from scripts.utils.LoggerUtil import Logger

NAME = i.NAME


class ListingItemPipeline:
    def __init__(self):
        """
        Initializes database connection and sessionmaker.
        """
        self.session = db().get_session()
        self.logger = Logger(self.__class__.__name__)

    def process_item(self, item, spider: Spider):
        """
        Save the scraped raw listing data to the database.
        This method is called for every item pipeline component.
        """
        if not isinstance(item, i.ListingItem):
            return item

        adapter = ItemAdapter(item)

        # Basic validation for ID
        listing_id = adapter.get(li.CONTAINER_ID[NAME])
        if not listing_id:
            self.logger.warning(f"Item received without an 'id'. Skipping item: {item}")
            self.session.close()
            return item

        try:
            # Check if the listing already exists to avoid duplicates
            existing_listing = self.session.query(RawListing).filter_by(id=listing_id).first()

            if existing_listing:
                self.logger.info(f"Updating existing listing with ID: {listing_id}")
                existing_listing.page_url = adapter.get(li.PAGE_URL[NAME])
                existing_listing.raw_summary = ' '.join(adapter.get(li.CONTAINER_SECTION_SUMMARY[NAME], []))
                existing_listing.raw_details = ' '.join(adapter.get(li.CONTAINER_SECTION_DETAILS[NAME], []))
                existing_listing.raw_price = ' '.join(adapter.get(li.CONTAINER_SECTION_PRICE[NAME], []))
            else:
                # Create a new RawListing object and populate it with data from the item
                self.logger.info(f"Adding new listing with ID: {listing_id}")
                listing = RawListing(
                    id=listing_id,
                    page_url=adapter.get(li.PAGE_URL[NAME]),
                    raw_summary=' '.join(adapter.get(li.CONTAINER_SECTION_SUMMARY[NAME], [])),
                    raw_details=' '.join(adapter.get(li.CONTAINER_SECTION_DETAILS[NAME], [])),
                    raw_price=' '.join(adapter.get(li.CONTAINER_SECTION_PRICE[NAME], [])),
                )
                self.session.add(listing)

            self.session.commit()
        except IntegrityError:
            self.session.rollback()
            self.logger.error(f"IntegrityError: Duplicate item with ID {listing_id}. Rolling back.")
        except Exception as e:
            self.session.rollback()
            self.logger.error(f"Error saving item {listing_id} to DB: {e}")
        finally:
            self.session.close()

        return item


class DetailsItemPipeline:
    def __init__(self):
        """
        Initializes database connection and sessionmaker.
        """
        self.session = db().get_session()
        self.logger = Logger(self.__class__.__name__)

    def process_item(self, item, spider: Spider):
        """
        Save the scraped raw listing data to the database.
        This method is called for every item pipeline component.
        """
        if not isinstance(item, i.DetailsItem):
            return item

        adapter = ItemAdapter(item)

        # Basic validation for ID
        details_id = str(adapter.get(di.ID[NAME]))
        if not details_id:
            self.logger.warning(f"Item received without an 'id'. Skipping item: {item}")
            self.session.close()
            return item

        try:
            existing_details = self.session.query(RawDetails).filter_by(id=details_id).first()

            if existing_details:
                self.logger.info(f"Updating existing details with ID: {details_id}")
                existing_details.page_url = adapter.get(di.PAGE_URL[NAME])
                existing_details.raw_description = ' '.join(adapter.get(di.RAW_DESCRIPTION[NAME], []))
                existing_details.raw_basic_information = ' '.join(adapter.get(di.RAW_BASIC_INFORMATION[NAME], []))
                existing_details.raw_specification = ' '.join(adapter.get(di.RAW_SPECIFICATION[NAME], []))
                existing_details.raw_equipment = ' '.join(adapter.get(di.RAW_EQUIPMENT[NAME], []))
                existing_details.raw_seller_info = ' '.join(adapter.get(di.RAW_SELLER_INFO[NAME], []))
                existing_details.updated_at = datetime.now()
            else:
                self.logger.info(f"Adding new details with ID: {details_id}")
                listing = RawDetails(
                    id=details_id,
                    page_url = adapter.get(di.PAGE_URL[NAME]),
                    raw_description = ' '.join(adapter.get(di.RAW_DESCRIPTION[NAME], [])),
                    raw_basic_information = ' '.join(adapter.get(di.RAW_BASIC_INFORMATION[NAME], [])),
                    raw_specification = ' '.join(adapter.get(di.RAW_SPECIFICATION[NAME], [])),
                    raw_equipment = ' '.join(adapter.get(di.RAW_EQUIPMENT[NAME], [])),
                    raw_seller_info = ' '.join(adapter.get(di.RAW_SELLER_INFO[NAME], [])),
                )
                self.session.add(listing)

            self.session.commit()
        except IntegrityError:
            self.session.rollback()
            self.logger.error(f"IntegrityError: Duplicate item with ID {details_id}. Rolling back.")
        except Exception as e:
            self.session.rollback()
            self.logger.error(f"Error saving item {details_id} to DB: {e}")
        finally:
            self.session.close()

        return item