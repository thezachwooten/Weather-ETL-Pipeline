from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from datetime import datetime, timedelta

def trigger_transform():
    import sys
    sys.path.append('/opt/airflow')
    from scripts.transform_weather import run_transform
    run_transform()

with DAG(
    'sc_weather_transform',
    default_args={
        'owner': 'zwooten',
        'depends_on_past': False,
        'email_on_failure': False,
        'retries': 1,
        'retry_delay': timedelta(minutes=5),
    },
    description='Transforms raw weather data from Bronze to Silver layer using PySpark',
    schedule='*/35 * * * *',  # runs 5 minutes after the ingestion DAG
    start_date=datetime(2026, 4, 27),
    catchup=False,
    tags=['weather', 'transform', 'silver'],
) as dag:

    transform_task = PythonOperator(
        task_id='transform_raw_to_clean',
        python_callable=trigger_transform
    )