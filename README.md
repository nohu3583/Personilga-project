# Swedish Electricity Price Pipeline

A small ETL pipeline that fetches day-ahead electricity prices for all four
Swedish price areas (SE1–SE4), validates and stores them in SQLite, and
displays them in a Streamlit dashboard.

## What it does

- **Extract** — pulls daily price data per area from the elprisetjustnu.se API
- **Validate** — checks for missing columns, out-of-range prices/exchange
  rates, and duplicate records
- **Load** — inserts validated rows into SQLite (idempotent — safe to re-run)
- **Dashboard** — Streamlit app showing historical trends, current prices per
  area, and daily statistics (highest/lowest hour, today's average)

## Setup

```bash
pip install -r requirements.txt
```

## Usage

Run the pipeline first to populate the database:

```bash
python pipeline.py
```

On first run this backfills historical data from 2022-11-02; on later runs
it only fetches missing days.

Then launch the dashboard:

```bash
streamlit run dashboard.py
```

## Project structure

| File | Purpose |
|---|---|
| `extract.py` | Fetches raw price data from the API |
| `validate.py` | Validates and filters rows before loading |
| `load.py` | Inserts validated rows into SQLite |
| `transform.py` | Query functions used by the dashboard |
| `database.py` / `database_init.py` | DB connection and schema setup |
| `pipeline.py` | Orchestrates extract → validate → load |
| `dashboard.py` | Streamlit dashboard |
| `tests/` | Unit tests | Right now pretty short but will add more test

## Project archictecture
To be added