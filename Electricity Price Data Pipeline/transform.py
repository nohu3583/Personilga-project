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


def _build_where_clause(area=None, start_date=None, end_date=None, extra_conditions=None):
    """Build a WHERE clause + params list from common filter arguments.

    Time filters compare Time_beginning_period directly (no function wrapping
    the column), so SQLite can still use the index on it. start_date/end_date
    can be plain 'YYYY-MM-DD' strings or full ISO timestamps - string
    comparison against the stored ISO timestamps works correctly either way.

    extra_conditions: optional list of raw SQL condition strings (no params)
    to AND in alongside the standard filters, e.g. a fixed date-range clause.
    """
    conditions = []
    params = []

    if area is not None:
        conditions.append("Price_Area = ?")
        params.append(area)

    if start_date is not None:
        conditions.append("Time_beginning_period >= ?")
        params.append(start_date)

    if end_date is not None:
        conditions.append("Time_beginning_period <= ?")
        params.append(end_date)

    if extra_conditions:
        conditions.extend(extra_conditions)

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
    """Gets the latest available price record for today, per area."""
    sql = """
    SELECT Price_SEK_per_kWh, Time_beginning_period, Price_Area
    FROM electricity_prices
    WHERE Time_beginning_period >= DATE('now')
      AND Time_beginning_period < DATE('now', '+1 day')
    ORDER BY Time_beginning_period DESC
    LIMIT 4
    """
    return read_query(sql)


def get_average_daily_prices(area=None, days=None):
    cutoff_date = None
    if days is not None:
        cutoff_date = (datetime.now().date() - timedelta(days=days)).isoformat()

    where_sql, params = _build_where_clause(area=area, start_date=cutoff_date)

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

    today_range = [
        "Time_beginning_period >= DATE('now')",
        "Time_beginning_period < DATE('now', '+1 day')",
    ]
    where_sql, params = _build_where_clause(area=area, extra_conditions=today_range)

    sql = f"""
    SELECT *
    FROM electricity_prices{where_sql}
    ORDER BY Price_SEK_per_kWh {order}
    LIMIT ?
    """
    params.append(limit)

    return read_query(sql, params)


def get_todays_average_price(area=None):
    today_range = [
        "Time_beginning_period >= DATE('now')",
        "Time_beginning_period < DATE('now', '+1 day')",
    ]
    where_sql, params = _build_where_clause(area=area, extra_conditions=today_range)

    sql = f"SELECT AVG(Price_SEK_per_kWh) AS avg_price FROM electricity_prices{where_sql}"
    return read_query(sql, params)


def get_tommorows_prices(area):
    sql = """
    SELECT Time_beginning_period, Price_SEK_per_kWh
    FROM electricity_prices
    WHERE Time_beginning_period >= DATE('now', '+1 day')
      AND Time_beginning_period < DATE('now', '+2 day')
      AND Price_Area = ?
    ORDER BY Time_beginning_period
    """
    return read_query(sql, [area])