FROM python:3.12-slim
WORKDIR /app
ENV PYTHONUNBUFFERED=1
COPY 00-modelagem-transacional/seed/requirements.txt seed.txt
COPY 04-elt-batch-com-python/pipeline/requirements.txt pipeline.txt
RUN pip install --no-cache-dir -r seed.txt -r pipeline.txt
COPY 00-modelagem-transacional/seed/seed.py .
COPY 03-warehouse-dedicado/warehouse/migrate.py .
COPY 04-elt-batch-com-python/pipeline/pipeline.py 04-elt-batch-com-python/pipeline/verify.py ./
COPY deploy/nas/jobs/ ./
ENTRYPOINT ["python", "batch.py"]
