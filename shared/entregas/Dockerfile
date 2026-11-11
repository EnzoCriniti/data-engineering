FROM python:3.12-slim
WORKDIR /opt/nuvemstore
ENV PYTHONUNBUFFERED=1 DBT_SEND_ANONYMOUS_USAGE_STATS=false
COPY 05-transformacao-com-dbt/requirements.txt /tmp/dbt-requirements.txt
RUN pip install --no-cache-dir -r /tmp/dbt-requirements.txt
COPY 05-transformacao-com-dbt/ ./05-transformacao-com-dbt/
COPY 06-ingestao-api-externa/extractor/ ./06-ingestao-api-externa/extractor/
COPY shared/entregas/jobs.py ./shared/entregas/jobs.py
ENTRYPOINT ["python", "shared/entregas/jobs.py"]
