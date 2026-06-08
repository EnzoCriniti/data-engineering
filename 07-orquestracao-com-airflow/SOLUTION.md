# Solução — Cap. 07: Orquestração com Airflow

> Gabarito de implementação. Siga o [GUIDE.md](./GUIDE.md) para o contexto.

## Estrutura de arquivos

```
07-orquestracao-com-airflow/
├── docker-compose.yml
└── airflow/
    ├── dags/
    │   └── nuvemstore_daily.py
    └── requirements.txt
```

## `docker-compose.yml`

```yaml
services:
  postgres-airflow:
    image: postgres:13
    container_name: p07-airflow-db
    environment:
      POSTGRES_USER: airflow
      POSTGRES_PASSWORD: airflow
      POSTGRES_DB: airflow
    volumes:
      - airflow-db-data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD", "pg_isready", "-U", "airflow"]
      interval: 5s
      retries: 5

  airflow-init:
    image: apache/airflow:2.8.1-python3.11
    container_name: p07-airflow-init
    environment:
      AIRFLOW__DATABASE__SQL_ALCHEMY_CONN: postgresql+psycopg2://airflow:airflow@postgres-airflow/airflow
      AIRFLOW__CORE__EXECUTOR: LocalExecutor
    command: version
    depends_on:
      postgres-airflow:
        condition: service_healthy

  airflow-webserver:
    image: apache/airflow:2.8.1-python3.11
    container_name: p07-airflow-webserver
    ports:
      - "8080:8080"
    environment:
      AIRFLOW__DATABASE__SQL_ALCHEMY_CONN: postgresql+psycopg2://airflow:airflow@postgres-airflow/airflow
      AIRFLOW__CORE__EXECUTOR: LocalExecutor
      AIRFLOW__CORE__LOAD_EXAMPLES: 'false'
    volumes:
      - ./airflow/dags:/opt/airflow/dags
      - ./airflow/requirements.txt:/requirements.txt
    command: >
      bash -c "pip install -r /requirements.txt && airflow db init && airflow users create --username admin --password admin --firstname Admin --lastname User --role Admin --email admin@example.com && airflow webserver"
    depends_on:
      airflow-init:
        condition: service_completed_successfully

  airflow-scheduler:
    image: apache/airflow:2.8.1-python3.11
    container_name: p07-airflow-scheduler
    environment:
      AIRFLOW__DATABASE__SQL_ALCHEMY_CONN: postgresql+psycopg2://airflow:airflow@postgres-airflow/airflow
      AIRFLOW__CORE__EXECUTOR: LocalExecutor
      AIRFLOW__CORE__LOAD_EXAMPLES: 'false'
    volumes:
      - ./airflow/dags:/opt/airflow/dags
      - ./airflow/requirements.txt:/requirements.txt
    command: >
      bash -c "pip install -r /requirements.txt && airflow scheduler"
    depends_on:
      airflow-init:
        condition: service_completed_successfully

volumes:
  airflow-db-data:
```

## `airflow/dags/nuvemstore_daily.py`

```python
"""DAG principal: Ingestão paralela (OLTP + API) -> Transformação (dbt)."""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator

default_args = {
    'owner': 'data_eng',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'nuvemstore_daily',
    default_args=default_args,
    description='Pipeline diário da NuvemStore',
    schedule_interval='@daily',
    start_date=datetime(2023, 1, 1), # Data fixa no passado para evitar recriação de runs fantasmas
    catchup=False,
    tags=['core'],
) as dag:

    # Task 1: Ingestão do OLTP usando o container pipeline do cap 04
    ingest_oltp = BashOperator(
        task_id='ingest_oltp',
        bash_command='docker start -a p04-pipeline', 
        # Em produção, chamaríamos a imagem ou script diretamente em vez de iniciar um container Docker in-docker.
        # Aqui, simulamos o disparo.
    )

    # Task 2: Ingestão da API usando o container extractor do cap 06
    ingest_api = BashOperator(
        task_id='ingest_api',
        bash_command='docker start -a p06-extractor',
    )

    # Task 3: Transformação com dbt (após as ingestões)
    run_dbt = BashOperator(
        task_id='run_dbt',
        bash_command='cd /opt/airflow/dags && echo "Simulando dbt run && dbt test"',
        # Em produção, teríamos o projeto dbt montado no Airflow ou usaríamos o Cosmos/DbtOperator.
    )

    # Dependências: As duas ingestões podem rodar em paralelo, dbt roda depois.
    [ingest_oltp, ingest_api] >> run_dbt
```
