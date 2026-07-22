from extract import fetch_prices_for_date
from datetime import date

df = fetch_prices_for_date(date(2022, 11, 2))

with open("output.txt", "w") as f:
    f.write(df.to_string() + "\n")
