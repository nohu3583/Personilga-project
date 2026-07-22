from database import get_connection

def load_prices(df):

    expected_columns = [
        "Time_beginning_period",
        "Time_end_period",
        "Price_SEK_per_kWh",
        "Price_EUR_per_kWh",
        "Price_Area",
        "Exchange_rate_EUR_SEK",
    ]

    missing_columns = [col for col in expected_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")

    df_to_load = df[expected_columns].copy()

    rows = df_to_load.to_dict(orient="records")

    with get_connection() as conn:
        conn.executemany(
            """
            INSERT OR IGNORE INTO electricity_prices (
                Time_beginning_period,
                Time_end_period,
                Price_SEK_per_kWh,
                Price_EUR_per_kWh,
                Price_Area,
                Exchange_rate_EUR_SEK
            )
            VALUES (
                :Time_beginning_period,
                :Time_end_period,
                :Price_SEK_per_kWh,
                :Price_EUR_per_kWh,
                :Price_Area,
                :Exchange_rate_EUR_SEK
            )
            """,
            rows
        )
        conn.commit()
