import sqlite3
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

import database
import transform


class TestTransformFunctions(unittest.TestCase):
    def test_get_average_daily_prices_uses_sqlite_compatible_filter(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "test_prices.db"
            conn = sqlite3.connect(db_path)
            conn.execute(
                """
                CREATE TABLE electricity_prices (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    Time_beginning_period TEXT NOT NULL,
                    Price_SEK_per_kWh REAL,
                    Price_Area TEXT
                )
                """
            )

            conn.executemany(
                """
                INSERT INTO electricity_prices (Time_beginning_period, Price_SEK_per_kWh, Price_Area)
                VALUES (?, ?, ?)
                """,
                [
                    ("2026-07-20 10:00:00", 10.0, "SE3"),
                    ("2026-07-21 10:00:00", 20.0, "SE3"),
                    ("2026-07-22 10:00:00", 30.0, "SE3"),
                    ("2026-07-20 10:00:00", 5.0, "SE1"),
                ],
            )
            conn.commit()
            conn.close()

            with patch.object(database, "DB_PATH", str(db_path)):
                df = transform.get_average_daily_prices("SE3", 7)

            self.assertEqual(len(df), 3)
            self.assertEqual(df.iloc[0]["day"], "2026-07-22")
            self.assertAlmostEqual(df.iloc[0]["avg_price_sek"], 30.0)

    def test_get_current_prices_returns_current_period_rows(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "test_prices.db"
            conn = sqlite3.connect(db_path)
            conn.execute(
                """
                CREATE TABLE electricity_prices (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    Time_beginning_period TEXT NOT NULL,
                    Time_end_period TEXT NOT NULL,
                    Price_SEK_per_kWh REAL,
                    Price_Area TEXT
                )
                """
            )

            now = "2026-07-25 11:30:00"
            rows = [
                (now, "2026-07-25 12:00:00", 10.0, "SE1"),
                ("2026-07-25 10:00:00", "2026-07-25 10:15:00", 99.0, "SE2"),
                ("2026-07-25 11:15:00", "2026-07-25 11:31:00", 20.0, "SE3"),
                ("2026-07-25 11:30:00", "2026-07-25 11:45:00", 30.0, "SE4"),
            ]

            conn.executemany(
                "INSERT INTO electricity_prices (Time_beginning_period, Time_end_period, Price_SEK_per_kWh, Price_Area) VALUES (?, ?, ?, ?)",
                rows,
            )
            conn.commit()
            conn.close()

            with patch.object(database, "DB_PATH", str(db_path)):
                with patch("transform.datetime") as mock_datetime:
                    mock_datetime.now.return_value = datetime.fromisoformat(now)
                    df = transform.get_current_prices()

            self.assertGreaterEqual(len(df), 1)
            self.assertTrue(
                all(
                    datetime.fromisoformat(row["Time_beginning_period"]) <= datetime.fromisoformat(now)
                    and datetime.fromisoformat(row["Time_end_period"]) > datetime.fromisoformat(now)
                    for _, row in df.iterrows()
                )
            )


if __name__ == "__main__":
    unittest.main()
