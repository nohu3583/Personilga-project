# Swedish Electricity Price Pipeline

A small ETL pipeline that fetches day-ahead electricity prices for all four
Swedish price areas (SE1–SE4), validates and stores them in SQLite, and
visualizes the results with a Streamlit dashboard.

## What it does

- **Extract** — pulls daily price data per area from the elprisetjustnu.se API
- **Validate** — checks for missing columns, out-of-range prices and exchange
  rates, and duplicate records
- **Load** — inserts validated rows into SQLite in an idempotent way so the
  pipeline can be re-run safely
- **Dashboard** — shows historical trends, current prices per area, and daily
  statistics such as the highest and lowest hour and the average price

## Setup

Create and activate a Python environment, then install the dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage

Run the pipeline first to populate the database:

```bash
python3 pipeline.py
```

On the first run, the pipeline backfills historical data from 2022-11-02. On
later runs, it only fetches missing days and updates recent data where needed.

Then start the dashboard:

```bash
streamlit run dashboard.py
```

## Project structure

| File | Purpose |
|---|---|
| `extract.py` | Fetches raw price data from the API for each area |
| `validate.py` | Validates and filters rows before loading |
| `load.py` | Inserts validated rows into SQLite |
| `transform.py` | SQL/query helpers used by the dashboard |
| `database.py` | Database connection helpers |
| `database_init.py` | SQLite schema initialization |
| `pipeline.py` | Orchestrates extract → validate → load |
| `dashboard.py` | Streamlit dashboard UI |
| `tests/` | Unit tests for the transformation and query logic |

## Project architecture

The project follows a simple ETL flow:

1. **Extraction**: the pipeline requests price data for each price area from the
   external API.
2. **Validation**: rows are checked for structural issues and invalid values.
3. **Loading**: validated records are inserted into SQLite using an idempotent
   insert strategy.
4. **Presentation**: the dashboard reads from SQLite and presents the data to
   the user through Streamlit.

This keeps the data pipeline and the UI loosely coupled, while making it easy to
run, inspect, and extend the project.

## Tech Stack & Core Competencies

**Languages & Libraries:** Python, pandas, SQLite3

**Core competencies demonstrated:**
- **ETL pipeline design** — extract/validate/load separation, idempotent
  inserts (`UNIQUE` constraints + `INSERT OR IGNORE`/`REPLACE`), incremental
  loading based on latest-timestamp tracking rather than full reprocessing
- **Data quality & validation** — schema checks, range validation, duplicate
  detection with a structured quality report
- **SQL** — parameterized queries, index-aware query design (avoiding
  function-wrapped WHERE clauses), aggregation, window-style date grouping
- **Data visualization** — Streamlit dashboard with cached queries, live and
  historical views
- **Logging & observability** — structured logging across pipeline stages
- **Testing** — unit tests with temp databases and mocked API calls