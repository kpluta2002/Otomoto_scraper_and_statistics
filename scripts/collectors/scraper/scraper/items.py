# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html
import scrapy

NAME = "name"
SELECTOR = "selector"
TYPE = dict[str, str]


class ListingItem(scrapy.Item):
    # Metadata
    PAGE_URL: TYPE = {NAME: "page_url", SELECTOR: ""}

    # Details
    CONTAINER_ARTICLE: TYPE = {NAME: "", SELECTOR: "//article[@data-id and not(@data-variant)]"}
    CONTAINER_ID: TYPE = {NAME: "id", SELECTOR: "./@data-id"}
    CONTAINER_SECTION_SUMMARY: TYPE = {NAME: "raw_summary", SELECTOR: "./section/div[2]"}
    CONTAINER_SECTION_DETAILS: TYPE = {NAME: "raw_details", SELECTOR: "./section/div[3]"}
    CONTAINER_SECTION_PRICE: TYPE = {NAME: "raw_price", SELECTOR: "./section/div[4]"}

    ITEMS = [
        PAGE_URL,
        CONTAINER_ID,
        CONTAINER_SECTION_SUMMARY,
        CONTAINER_SECTION_DETAILS,
        CONTAINER_SECTION_PRICE,
    ]

    for item in ITEMS:
        locals()[item[NAME]] = scrapy.Field()


class DetailsItem(scrapy.Item):
    # Metadata
    PAGE_URL: TYPE = {NAME: "page_url", SELECTOR: ""}

    ID: TYPE = {NAME: "id", SELECTOR: ""}

    # Details
    RAW_DESCRIPTION: TYPE = {NAME: "raw_description", SELECTOR: "//div[contains(@data-testid, 'content-description-section')]/div[2]/div"}
    RAW_BASIC_INFORMATION: TYPE = {NAME: "raw_basic_information", SELECTOR: "//div[contains(@data-testid, 'basic_information')]"}
    RAW_SPECIFICATION: TYPE = {NAME: "raw_specification", SELECTOR: "//div[contains(@data-testid, 'collapsible-groups-wrapper')]"}
    RAW_EQUIPMENT: TYPE = {NAME: "raw_equipment", SELECTOR: "//div[contains(@data-testid, 'content-equipments-section')]"}
    RAW_SELLER_INFO: TYPE = {
        NAME: "raw_seller_info", 
        SELECTOR: (
            "//div[contains(@data-testid, 'content-seller-area-section')]"
            "//text()[not("
                "ancestor::div[contains(@data-testid, 'google-map-container')]"
                " or ancestor::style"
                " or ancestor::script"
            ")]"
            )
        }

    ITEMS = [
        ID,
        PAGE_URL,
        RAW_DESCRIPTION,
        RAW_BASIC_INFORMATION,
        RAW_SPECIFICATION,
        RAW_EQUIPMENT,
        RAW_SELLER_INFO,
    ]

    for item in ITEMS:
        locals()[item[NAME]] = scrapy.Field()
