FROM python:3.12-slim
WORKDIR /api
ENV PYTHONUNBUFFERED=1
RUN pip install --no-cache-dir psycopg2-binary==2.9.9
COPY 06-ingestao-api-externa/api/app.py 06-ingestao-api-externa/api/entregas.json ./
CMD ["python", "app.py"]
