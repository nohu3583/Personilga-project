import pandas as pd


def validate_prices(df: pd.DataFrame):

    # -----------------------
    # Column Validation
    # -----------------------

    required_columns = [
        "Price_SEK_per_kWh",
        "Price_EUR_per_kWh",
        "Price_Area",
        "Exchange_rate_EUR_SEK",
        "Time_beginning_period",
        "Time_end_period"
    ]

    missing = set(required_columns) - set(df.columns)

    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    # -----------------------
    # Validation rules
    # -----------------------

    #Min and Max values
    MIN_PRICE = -5
    MAX_PRICE = 20

    MIN_EXCHANGE_RATE = 8
    MAX_EXCHANGE_RATE = 12
    not_null = df[required_columns].notna().all(axis=1)

    valid_currency = df["Exchange_rate_EUR_SEK"].between(MIN_EXCHANGE_RATE, MAX_EXCHANGE_RATE)

    valid_price = df["Price_SEK_per_kWh"].between(MIN_PRICE, MAX_PRICE)
    duplicates_mask = df.duplicated(
        subset=["Time_beginning_period", "Price_Area"],
        keep="first"
    )
    valid_mask = (
        not_null
        & valid_currency
        & valid_price
        & ~duplicates_mask
    )


    valid_df = df[valid_mask].copy()
    invalid_df = df[~valid_mask].copy()

    # -----------------------
    # Report
    # -----------------------

    report = {
        "rows_total": len(df),
        "rows_valid": len(valid_df),
        "rows_invalid": len(invalid_df),
        "missing_values": (~not_null).sum(),
        "invalid_currency": (~valid_currency).sum(),
        "invalid_price": (~valid_price).sum(),
        "duplicate_time_area": duplicates_mask.sum(),
    }

    return valid_df, invalid_df, report