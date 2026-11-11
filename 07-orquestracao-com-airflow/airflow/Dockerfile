FROM apache/airflow:2.11.0-python3.12
USER root
RUN install -d -o airflow -g 0 /opt/nuvemstore
USER airflow
WORKDIR /opt/nuvemstore
ENV DBT_SEND_ANONYMOUS_USAGE_STATS=false
COPY --chown=airflow:0 00-modelagem-transacional/seed/requirements.txt /tmp/seed-requirements.txt
COPY --chown=airflow:0 04-elt-batch-com-python/pipeline/requirements.txt /tmp/batch-requirements.txt
COPY --chown=airflow:0 05-transformacao-com-dbt/requirements.txt /tmp/dbt-requirements.txt
RUN python -m venv .venv && .venv/bin/pip install --no-cache-dir \
    -r /tmp/seed-requirements.txt -r /tmp/batch-requirements.txt -r /tmp/dbt-requirements.txt
COPY --chown=airflow:0 05-transformacao-com-dbt/ ./05-transformacao-com-dbt/
COPY --chown=airflow:0 06-ingestao-api-externa/extractor/ ./06-ingestao-api-externa/extractor/
COPY --chown=airflow:0 shared/entregas/jobs.py ./shared/entregas/jobs.py
COPY --chown=airflow:0 00-modelagem-transacional/seed/seed.py ./batch/
COPY --chown=airflow:0 03-warehouse-dedicado/warehouse/migrate.py ./batch/
COPY --chown=airflow:0 04-elt-batch-com-python/pipeline/pipeline.py 04-elt-batch-com-python/pipeline/verify.py ./batch/
COPY --chown=airflow:0 deploy/nas/jobs/ ./batch/
COPY --chown=airflow:0 07-orquestracao-com-airflow/airflow/dags/ /opt/airflow/dags/
COPY --chown=airflow:0 07-orquestracao-com-airflow/airflow/metadata_url.py ./metadata_url.py
