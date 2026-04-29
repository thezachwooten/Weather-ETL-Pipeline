from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from datetime import datetime, timedelta

def trigger_3_day_avg():
    import sys
    sys.path.append('/opt/airflow')
    from scripts.three_day_avg import run_3_day_avg
    run_3_day_avg()

with DAG(
    'sc_weather_3_day_avg',
    default_args={
        'owner': 'zwooten',
        'depends_on_past': False,
        'email_on_failure': False,
        'retries': 1,
        'retry_delay': timedelta(minutes=5),
    },
    description='Transforms clean weather into 3 day rolling avg using PySpark',
    schedule='0 0 * * *',  # runs at midnight
    start_date=datetime(2026, 4, 27),
    catchup=False,
    tags=['weather', 'aggregate', 'gold'],
) as dag:

    transform_task = PythonOperator(
        task_id='aggregate_3_day_avg',
        python_callable=trigger_3_day_avg
    )