from database_init import initialize_database
from extract import fetch_prices_for_date
from database import is_database_empty
from transform import get_last_date_recorded
from load import load_prices
from validate import validate_prices

from datetime import date, timedelta, datetime
from pathlib import Path

from logging_config import configure_logging

logger = configure_logging()

DB_PATH = Path(__file__).resolve().parent / "electricity_prices.db"

def process_date(processing_date):
    try:
        logger.info("Processing %s", processing_date)
        # Extract
        df = fetch_prices_for_date(processing_date)
        # Validate
        valid_df, invalid_df, report = validate_prices(df)

        # Load
        load_prices(valid_df)
        logger.info("Finished %s", processing_date)
        return True

    except Exception as e:
        logger.exception("Failed processing %s", processing_date)
        return False

def import_historic_data():

    start_date = date(2022, 11, 2)
    end_date = date.today()
    current = start_date

    logger.info("Importing historical data from %s to %s", start_date, end_date)
    while current <= end_date:
        process_date(current)
        current += timedelta(days=1)



def import_missing_data():

    last_date = get_last_date_recorded()
    logger.info("Latest recorded date before missing-data import: %s", last_date)
    next_date = last_date + timedelta(days=1)
    today = date.today()
    # Process any missing days up to today
    while next_date <= today:
        process_date(next_date)
        next_date += timedelta(days=1)

    # If it's after 13:00 local time, attempt to reprocess today (in case prices updated)
    # and try to import tomorrow's predictive prices if the API provides them.
    now = datetime.now()
    if now.hour >= 13:
        try:
            # Re-run today's processing to reconcile any changes
            process_date(today)
        except Exception as e:
            logger.exception("Reprocessing today failed")

        try:
            # Attempt to import tomorrow's data — API may return predictive prices after 13:00
            process_date(today + timedelta(days=1))
        except Exception as e:
            logger.exception("Attempting to import tomorrow failed (may not be available yet)")



def pipeline_start():

    initialize_database(DB_PATH)

    if is_database_empty():
        logger.info("Database empty. Importing historical data.")
        import_historic_data()

    else:
        logger.info("Database exists. Checking for new data.")
        import_missing_data()

if __name__ == "__main__":
    pipeline_start()