import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "electricity_prices.db"


def initialize_database(db_path: str | Path = DB_PATH):
    conn = sqlite3.connect(db_path)

    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS electricity_prices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                Time_beginning_period TEXT NOT NULL,
                Time_end_period TEXT NOT NULL,
                Price_SEK_per_kWh REAL,
                Price_EUR_per_kWh REAL,
                Price_Area TEXT,
                Exchange_rate_EUR_SEK REAL,
                loaded_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

                UNIQUE(Time_beginning_period, Price_Area)
            )
            """
        )

        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_electricity_prices_area ON electricity_prices(Price_Area)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_electricity_prices_timestamp ON electricity_prices(Time_beginning_period)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_prices_area_time ON electricity_prices(Price_Area, Time_beginning_period);"
        )

        conn.commit()
    finally:
        conn.close()


if __name__ == "__main__":
    initialize_database()
    print(f"Database initialized at: {DB_PATH}")
