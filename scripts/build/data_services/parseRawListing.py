import argparse

from tqdm import tqdm

from scripts.parsers.DetailsParser import DetailsParser
from scripts.parsers.PriceParser import PriceParser
from scripts.parsers.SummaryParser import SummaryParser
from scripts.utils.LoggerUtil import Logger

PARSER_DETAILS = "details"
PARSER_SUMMARY = "summary"
PARSER_PRICE = "price"


def run_car_data_parser(batch_size: int, parser_type: str, only_missing: bool):
    """
    Initializes the parser, runs the data extraction and saving process,
    and displays progress with a TQDM bar.
    """
    logger = Logger(f"{parser_type.title()}DataParser")
    if parser_type == PARSER_SUMMARY:
        parser = SummaryParser()
    elif parser_type == PARSER_DETAILS:
        parser = DetailsParser()
    elif parser_type == PARSER_PRICE:
        parser = PriceParser()

    try:
        total = parser.get_total_records(only_missing)
        progress_bar = None

        logger.info(f"Starting car data parsing process with batch size: {batch_size}")

        for info in parser.run(batch_size, only_missing, total):
            if info == parser.STATUS_PROCESSING:
                if progress_bar is None:
                    progress_bar = tqdm(total=total, desc=f"Parsing {parser_type} data", leave=True)
                progress_bar.update(batch_size)

            elif info == parser.STATUS_FINISHED:
                if progress_bar:
                    progress_bar.close()
                logger.info("Parsing finished successfully.")
                break

            elif info == parser.STATUS_ERROR:
                if progress_bar:
                    progress_bar.close()
                logger.error("An error occurred during parsing.")
                break

    except Exception as e:
        if progress_bar:
            progress_bar.close()
        logger.critical(
            f"An unexpected error occurred during the parsing process: {e}", exc_info=True
        )


if __name__ == "__main__":
    arguments = argparse.ArgumentParser(description="Data Parser")
    arguments.add_argument(
        "--batch-size",
        type=int,
        default=1000,
        help="Number of records to process per batch (default: 1000)",
    )
    arguments.add_argument(
        "--parser-type",
        type=str,
        default="details",
        help="Data Parser to run (details/summary/price)",
    )
    arguments.add_argument(
        "--only-missing",
        action="store_true",
        help="Run only on missing entries."
    )
    args = arguments.parse_args()

    run_car_data_parser(args.batch_size, args.parser_type, args.only_missing)
