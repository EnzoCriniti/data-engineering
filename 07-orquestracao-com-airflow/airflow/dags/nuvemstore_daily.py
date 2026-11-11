"""Agenda os mesmos jobs que podem ser executados manualmente."""
import os
import subprocess
from datetime import timedelta

import pendulum
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.types import DagRunType

PYTHON = "/opt/nuvemstore/.venv/bin/python"
BATCH = "/opt/nuvemstore/batch/batch.py"
DELIVERIES = "/opt/nuvemstore/shared/entregas/jobs.py"


def run_job(script, *args, **kwargs):
    subprocess.run([PYTHON, script, *args], check=True, **kwargs)


def execute(script, job):
    run_job(script, job)


def simulate(dag_run, **_):
    if dag_run.run_type != DagRunType.BACKFILL_JOB and not (dag_run.conf or {}).get("somente_reprocessar"):
        run_job(BATCH, "simulate", env={**os.environ, "SIM_AS_OF": dag_run.start_date.isoformat()})


def ingest(dag_run, data_interval_start, data_interval_end, **_):
    if dag_run.run_type == DagRunType.BACKFILL_JOB:
        run_job(DELIVERIES, "extract", "--start", data_interval_start.isoformat(),
                "--end", data_interval_end.isoformat())
    else:
        run_job(DELIVERIES, "extract")


def build(dag_run, **_):
    # O backfill repara o estado atual. A data histórica delimita a ingestão.
    run_job(DELIVERIES, "build", "--as-of", dag_run.start_date.isoformat())


with DAG(
    dag_id="nuvemstore_daily",
    description="Atualiza vendas e o SLA das entregas terceirizadas",
    schedule="0 6 * * *",
    start_date=pendulum.datetime(2026, 6, 1, 6, tz="UTC"),
    catchup=False,
    max_active_runs=1,
    default_args={
        "retries": 2,
        "retry_delay": timedelta(seconds=int(os.getenv("AIRFLOW_JOB_RETRY_SECONDS", "60"))),
    },
    tags=["nuvemstore"],
) as dag:
    simulate_orders = PythonOperator(task_id="simular_pedidos", python_callable=simulate)
    refresh_oltp = PythonOperator(task_id="carga_oltp", python_callable=execute,
                                  op_args=[BATCH, "pipeline"])
    ingest_carrier = PythonOperator(task_id="carga_api", python_callable=ingest)
    transform = PythonOperator(task_id="dbt_build", python_callable=build)
    verify = PythonOperator(task_id="verificar_sla", python_callable=execute,
                            op_args=[DELIVERIES, "report"])

    simulate_orders >> refresh_oltp >> ingest_carrier >> transform >> verify
