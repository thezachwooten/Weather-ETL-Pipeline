from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import asyncio
import sys
import os

# 1. Add the project root to the path so Airflow can find your 'scripts' and 'shared' folders
sys.path.append('/opt/airflow')

# 2. Import your ingestion logic
from scripts.ingest_weather import run_ingestion

# 3. Create a wrapper because Airflow's PythonOperator is synchronous
def trigger_ingestion():
    asyncio.run(run_ingestion())

# 4. Define the DAG
with DAG(
    'sc_weather_ingestion_v1',
    default_args={
        'owner': 'zwooten',
        'depends_on_past': False,
        'email_on_failure': False,
        'retries': 1,
        'retry_delay': timedelta(minutes=5),
    },
    description='Fetches raw weather data for SC locations and stores in Bronze layer',
    schedule='*/30 * * * *', # Runs every 30 minutes
    start_date=datetime(2026, 4, 27),
    catchup=False, # Don't try to run for all the 30-min slots in the past
    tags=['weather', 'ingestion'],
) as dag:

    ingest_task = PythonOperator(
        task_id='ingest_api_to_postgres_raw',
        python_callable=trigger_ingestion
    )