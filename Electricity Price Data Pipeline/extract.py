import requests
import pandas as pd
from datetime import date


def fetch_prices_for_date(d: date):

    areas = ["SE1", "SE2", "SE3", "SE4"]
    all_data = []

    for area in areas:

        url = (
            f"https://www.elprisetjustnu.se/api/v1/prices/"
            f"{d.year}/{d.strftime('%m-%d')}_{area}.json"
        )

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            data = response.json()

            for row in data:
                row["area"] = area
                all_data.append(row)

        except requests.exceptions.Timeout:
            print(f"Timeout while fetching {area}")

        except requests.exceptions.HTTPError as e:
            print(f"HTTP error for {area}: {e}")

        except requests.exceptions.RequestException as e:
            print(f"Request failed for {area}: {e}")

        except ValueError:
            print(f"Invalid JSON returned for {area}")

    if not all_data:
        raise RuntimeError("No electricity price data was collected")

    df = pd.DataFrame(all_data)

    df = df.rename(columns={
        "time_start": "Time_beginning_period",
        "time_end": "Time_end_period",
        "EXR" : "Exchange_rate_EUR_SEK",
        "SEK_per_kWh": "Price_SEK_per_kWh",
        "EUR_per_kWh": "Price_EUR_per_kWh",
        "area": "Price_Area"
    })
    
    return df