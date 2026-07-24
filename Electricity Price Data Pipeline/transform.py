from database import read_query
from datetime import datetime, timedelta

VALID_COLUMNS = {
    "id",
    "Time_beginning_period",
    "Price_SEK_per_kWh",
    "Price_Area",
    "loaded_at",
}

def _validate_columns(columns):
    """Normalize and validate a column selection into a SQL-ready string."""
    if columns is None:
        return "*"

    if isinstance(columns, str):
        columns = [columns]

    for col in columns:
        if col not in VALID_COLUMNS:
            raise ValueError(f"Invalid column requested: {col}")

    return ", ".join(columns)

def _validate_order_by(order_by):
    order_by = order_by or "Time_beginning_period"
    if order_by not in VALID_COLUMNS:
        raise ValueError("Not a valid column")
    return order_by

def _validate_order(order):
    order = order or "ASC"
    if order not in ("ASC", "DESC"):
        raise ValueError("Invalid order")
    return order


def _build_where_clause(area=None, start_date=None, end_date=None, date_column="Time_beginning_period"):
    """Build a WHERE clause + params list from common filter arguments."""
    conditions = []
    params = []

    if area is not None:
        conditions.append("Price_Area = ?")
        params.append(area)

    if start_date is not None:
        conditions.append(f"{date_column} >= ?")
        params.append(start_date)

    if end_date is not None:
        conditions.append(f"{date_column} <= ?")
        params.append(end_date)

    where_sql = f" WHERE {' AND '.join(conditions)}" if conditions else ""
    return where_sql, params


def get_prices(area=None, start_date=None, end_date=None, order=None, limit=None, order_by=None, columns=None):
    column_sql = _validate_columns(columns)
    order_by = _validate_order_by(order_by)
    order = _validate_order(order)

    where_sql, params = _build_where_clause(area, start_date, end_date)

    sql = f"SELECT {column_sql} FROM electricity_prices{where_sql} ORDER BY {order_by} {order}"

    if limit is not None:
        sql += " LIMIT ?"
        params.append(limit)

    return read_query(sql, params)


def get_current_prices():
    """Gets the latest available price record."""
    sql = """
    SELECT Price_SEK_per_kWh, Time_beginning_period, Price_Area
    FROM electricity_prices
    WHERE DATE(Time_beginning_period) = DATE('now')
    ORDER BY Time_beginning_period DESC
    LIMIT 4
    """
    return read_query(sql)


def get_average_daily_prices(area=None, days=None):
    cutoff_date = None
    if days is not None:
        cutoff_date = (datetime.now().date() - timedelta(days=days)).isoformat()

    where_sql, params = _build_where_clause(
        area=area,
        start_date=cutoff_date,
        date_column="DATE(Time_beginning_period)",
    )

    sql = f"""
    SELECT
        DATE(Time_beginning_period) AS day,
        AVG(Price_SEK_per_kWh) AS avg_price_sek
    FROM electricity_prices{where_sql}
    GROUP BY DATE(Time_beginning_period)
    ORDER BY day DESC
    """

    return read_query(sql, params)


def get_last_date_recorded():
    sql = """
    SELECT Time_beginning_period
    FROM electricity_prices
    ORDER BY Time_beginning_period DESC
    LIMIT 1
    """

    df = read_query(sql)

    if df.empty:
        return None

    last_timestamp = df.iloc[0]["Time_beginning_period"]
    return datetime.fromisoformat(last_timestamp).date()


def get_extreme_prices(area=None, order=None, limit=1):
    order = _validate_order(order)

    where_sql, params = _build_where_clause(area=area, date_column="DATE(Time_beginning_period)")
    # today-only filter, appended manually since it's not a user-supplied date
    today_clause = "DATE(Time_beginning_period) = DATE('now')"
    where_sql = f" WHERE {today_clause} AND {where_sql[7:]}" if where_sql else f" WHERE {today_clause}"

    sql = f"""
    SELECT *
    FROM electricity_prices{where_sql}
    ORDER BY Price_SEK_per_kWh {order}
    LIMIT ?
    """
    params.append(limit)

    return read_query(sql, params)

def get_todays_average_price(area=None):
    where_sql, params = _build_where_clause(area=area, date_column="DATE(Time_beginning_period)")
    today_clause = "DATE(Time_beginning_period) = DATE('now')"
    where_sql = f" WHERE {today_clause} AND {where_sql[7:]}" if where_sql else f" WHERE {today_clause}"

    sql = f"SELECT AVG(Price_SEK_per_kWh) AS avg_price FROM electricity_prices{where_sql}"
    return read_query(sql, params)

def get_tommorows_prices(area):
    sql = """
    SELECT Time_beginning_period, Price_SEK_per_kWh
    FROM electricity_prices
    WHERE DATE(Time_beginning_period) = DATE('now', '+1 day')
    AND Price_Area = ?
    ORDER BY Time_beginning_period
    """
    return read_query(sql, [area])

