import logging
import requests
import pandas as pd
from datetime import date

from logging_config import configure_logging

logger = configure_logging()


def fetch_prices_for_date(d: date):

    areas = ["SE1", "SE2", "SE3", "SE4"]
    all_data = []
    logger.info("Starting extraction for %s", d)

    for area in areas:

        url = (
            f"https://www.elprisetjustnu.se/api/v1/prices/"
            f"{d.year}/{d.strftime('%m-%d')}_{area}.json"
        )

        try:
            logger.debug("Fetching data for area %s from %s", area, url)
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            data = response.json()
            logger.info("Retrieved %d rows for %s", len(data), area)

            for row in data:
                row["area"] = area
                all_data.append(row)

        except requests.exceptions.Timeout:
            logger.warning("Timeout while fetching %s", area)

        except requests.exceptions.HTTPError as e:
            logger.error("HTTP error for %s: %s", area, e)

        except requests.exceptions.RequestException as e:
            logger.error("Request failed for %s: %s", area, e)

        except ValueError:
            logger.error("Invalid JSON returned for %s", area)

    if not all_data:
        logger.error("No electricity price data was collected for %s", d)
        raise RuntimeError("No electricity price data was collected")

    df = pd.DataFrame(all_data)
    logger.info("Built DataFrame with %d rows for %s", len(df), d)

    df = df.rename(columns={
        "time_start": "Time_beginning_period",
        "time_end": "Time_end_period",
        "EXR" : "Exchange_rate_EUR_SEK",
        "SEK_per_kWh": "Price_SEK_per_kWh",
        "EUR_per_kWh": "Price_EUR_per_kWh",
        "area": "Price_Area"
    })
    
    return df