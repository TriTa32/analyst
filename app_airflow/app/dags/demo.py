from airflow import DAG
from airflow.providers.apache.druid.operators.druid import DruidOperator
from airflow.operators.python import PythonOperator
from airflow.hooks.base import BaseHook
from datetime import datetime, timedelta
import logging
import requests

logger = logging.getLogger(__name__)

def check_druid_connection(druid_conn_id: str = 'druid_default') -> None:
    conn = BaseHook.get_connection(druid_conn_id)
    url = f'http://{conn.host}:{conn.port or 8082}/status'
    
    response = requests.get(url, timeout=10)
    if response.status_code != 200:
        raise Exception(f"Druid health check failed: {response.status_code}")
    logger.info("Druid connection successful")

with DAG(
    'druid-ingest-monitored',
    default_args={
        'owner': 'airflow',
        'retries': 1,
        'retry_delay': timedelta(minutes=5),
    },
    schedule_interval=None,
    start_date=datetime(2025, 1, 1),
    catchup=False,
    tags=['druid'],
) as dag:

    check_connection = PythonOperator(
        task_id='check_connection',
        python_callable=check_druid_connection,
        op_kwargs={'druid_conn_id': 'druid_default'}
    )

    check_connection 