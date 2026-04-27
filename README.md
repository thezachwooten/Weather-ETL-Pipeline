# Weather ETL Pipeline

A 3-stage asynchronous ETL pipeline that ingests live weather data across 40+ South Carolina zip codes, cleans and normalizes it, and aggregates it into a PostgreSQL database on an automated schedule.

## What it does

1. **Ingestion** — hits the WeatherAPI.com API every 30 minutes for each location and stores the raw JSON payload in PostgreSQL
2. **Processing** — picks up unprocessed raw rows, extracts and normalizes fields into a clean structured table, and marks raw rows as processed
3. **Aggregation** — runs once daily, calculates a 3-day rolling average temperature per location and stores it in an aggregation table

## Tech Stack

- **Python** — AsyncIO, HTTPX, APScheduler
- **FastAPI** — application entry point
- **SQLAlchemy** — async ORM with PostgreSQL
- **PostgreSQL** — raw, clean, and aggregated weather tables
- **Docker** — containerized Postgres instance via Docker Compose

## Project Structure

```
Weather-ETL-Pipeline/
├── pipelines/
│   ├── ingestion/        # fetches from WeatherAPI and stores raw payloads
│   ├── processing/       # cleans raw data into normalized rows
│   └── aggregation/      # calculates 3-day rolling averages
├── shared/
│   ├── db/
│   │   ├── models.py     # SQLAlchemy table definitions
│   │   ├── crud.py       # all database reads and writes
│   │   └── database.py   # async engine and session setup
│   ├── config.py         # environment variable loading
│   └── locations.py      # list of zip codes to track
├── main.py               # scheduler setup and app entry point
├── docker-compose.yml
├── .env.example
└── requirements.txt
```

## Getting Started

### 1. Clone the repo

```bash
git clone https://github.com/your-username/Weather-ETL-Pipeline.git
cd Weather-ETL-Pipeline
```

### 2. Set up environment variables

```bash
cp .env.example .env
```

Fill in your `.env`:

```
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5435/WeatherETL
WEATHER_API_KEY=your_weatherapi_key
```

Get a free API key at [weatherapi.com](https://www.weatherapi.com)

### 3. Start the database

```bash
docker-compose up -d
```

### 4. Install dependencies

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 5. Run the pipeline

```bash
python main.py
```

The scheduler will start, create the database tables on first run, and begin the ingestion cycle automatically.

## Database Schema

| Table | Description |
|-------|-------------|
| `raw_weather` | Raw JSON payloads from WeatherAPI, with `processed_at` timestamp for pipeline handoff |
| `clean_weather` | Normalized weather fields — temp, humidity, wind, condition, feel-like temps, etc. |
| `weather_3day_agg` | Daily 3-day rolling average temperature per location |

## Schedule

| Pipeline | Frequency |
|----------|-----------|
| Ingestion | Every 30 minutes |
| Processing | Every 35 minutes |
| Aggregation | Daily at midnight |

# Coming Soon
* Scalable Transformation: Migrating from standard Python to PySpark to enable distributed data processing, ensuring the pipeline can handle high-velocity environmental data beyond local memory limits. 
* Enterprise Orchestration: Transitioning from APScheduler to Apache Airflow (running via Docker) to manage task dependencies, improve error handling, and provide a centralized UI for pipeline monitoring.

# Soon-to-be file structure
Weather-ETL-Pipeline/
├── dags/
│   └── weather_etl_dag.py    # The Airflow schedule and task definitions
├── scripts/
│   ├── ingest.py             # existing HTTPX logic
│   ├── transform_spark.py    # NEW: PySpark cleaning logic
│   └── aggregate_spark.py    # NEW: PySpark rolling average logic
├── docker/
│   ├── airflow.Dockerfile    # Custom image to include PySpark/Dependencies
│   └── docker-compose.yaml   # Spins up Airflow, Postgres, and Spark Worker