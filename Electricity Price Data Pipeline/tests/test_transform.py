import sqlite3
import tempfile
import unittest
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


if __name__ == "__main__":
    unittest.main()
