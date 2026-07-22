import sqlite3
import pandas as pd

DB_PATH = "electricity_prices.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


def read_query(sql, params=None):
    with get_connection() as conn:
        return pd.read_sql_query(
            sql,
            conn,
            params=params
        )


def execute(sql, params=None):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(sql, params or ())
        conn.commit()


def is_database_empty():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM electricity_prices")
        count = cursor.fetchone()[0]
        return count == 0
    