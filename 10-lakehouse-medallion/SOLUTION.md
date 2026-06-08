# Solução — Cap. 10: Lakehouse Medallion

> Gabarito de implementação. Os comentários no código apontam para os conceitos do **[GUIDE.md](./GUIDE.md)** (ex.: "ver Conceito 2 — Delta/`_delta_log`"). Para internals da stack, ver **[TECHNICAL.md](./TECHNICAL.md)**.

## Estrutura de arquivos

```
10-lakehouse-medallion/
├── docker-compose.yml
└── spark/
    ├── jobs/
    │   ├── bronze_ingest.py
    │   ├── silver_transform.py
    │   └── gold_marts.py
    └── Dockerfile
```

## `docker-compose.yml`

MinIO faz o papel de S3 (`s3a://datalake/...`), `minio-setup` cria o bucket, e `spark-submit` é o runner que executa cada job Delta sob demanda (perfil implícito — só roda via `docker compose run`).

```yaml
services:
  # Object storage S3-compatible — o "disco" do lakehouse
  minio:
    image: minio/minio
    container_name: p10-minio
    ports:
      - "9000:9000"
      - "9001:9001"
    environment:
      MINIO_ROOT_USER: ${MINIO_USER:-minioadmin}
      MINIO_ROOT_PASSWORD: ${MINIO_PASSWORD:-minioadmin}
    command: server /data --console-address ":9001"
    volumes:
      - minio-data:/data

  # Cria o bucket do datalake na subida
  minio-setup:
    image: minio/mc
    container_name: p10-minio-setup
    depends_on: [minio]
    entrypoint: >
      /bin/sh -c "
      sleep 5;
      mc alias set m http://minio:9000 ${MINIO_USER:-minioadmin} ${MINIO_PASSWORD:-minioadmin};
      mc mb -p m/datalake;
      exit 0;
      "

  # Runner Spark+Delta — executa os jobs bronze/silver/gold sob demanda:
  #   docker compose run spark-submit spark-submit /app/jobs/bronze_ingest.py
  spark-submit:
    build: ./spark
    container_name: p10-spark
    depends_on: [minio]
    volumes:
      - ./spark/jobs:/app/jobs
      - ./data:/app/data        # entregas.json de origem
    environment:
      AWS_ACCESS_KEY_ID: ${MINIO_USER:-minioadmin}
      AWS_SECRET_ACCESS_KEY: ${MINIO_PASSWORD:-minioadmin}
    profiles: [jobs]

volumes:
  minio-data:
```

## `spark/Dockerfile`

Imagem Spark 3.5 com os JARs de Delta e do conector S3A, e a config `s3a` apontando para o MinIO.

```dockerfile
FROM bitnami/spark:3.5

USER root
# Delta Lake + Hadoop AWS (S3A) + AWS SDK — versões compatíveis com Spark 3.5 / Hadoop 3.3
RUN install_packages curl && \
    cd /opt/bitnami/spark/jars && \
    curl -sLO https://repo1.maven.org/maven2/io/delta/delta-spark_2.12/3.2.0/delta-spark_2.12-3.2.0.jar && \
    curl -sLO https://repo1.maven.org/maven2/io/delta/delta-storage/3.2.0/delta-storage-3.2.0.jar && \
    curl -sLO https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-aws/3.3.4/hadoop-aws-3.3.4.jar && \
    curl -sLO https://repo1.maven.org/maven2/com/amazonaws/aws-java-sdk-bundle/1.12.262/aws-java-sdk-bundle-1.12.262.jar

# Aponta o S3A para o MinIO (endpoint interno do compose)
COPY spark-defaults.conf /opt/bitnami/spark/conf/spark-defaults.conf
```

## `spark/spark-defaults.conf`

```properties
spark.hadoop.fs.s3a.endpoint=http://minio:9000
spark.hadoop.fs.s3a.path.style.access=true
spark.hadoop.fs.s3a.impl=org.apache.hadoop.fs.s3a.S3AFileSystem
spark.hadoop.fs.s3a.connection.ssl.enabled=false
spark.sql.extensions=io.delta.sql.DeltaSparkSessionExtension
spark.sql.catalog.spark_catalog=org.apache.spark.sql.delta.catalog.DeltaCatalog
```

## `spark/jobs/bronze_ingest.py`

```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import current_timestamp, lit

def main():
    # Estas 2 configs registram o Delta como motor de tabela do Spark (ver GUIDE Etapa 1).
    # Sem elas, .format("delta") e MERGE não funcionam — o Spark só entenderia Parquet puro.
    spark = SparkSession.builder \
        .appName("Bronze Ingestion") \
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
        .getOrCreate()

    # Lendo arquivo local para simular a origem (em produção: OLTP export, API, Kafka...)
    print("Lendo dados brutos...")
    df = spark.read.json("file:///app/data/entregas.json")

    # Metadados de auditoria (GUIDE Etapa 2 — Decisões de design):
    # _ingested_at = QUANDO entrou no lake; _source = DE ONDE veio. Rastreabilidade.
    df_bronze = df \
        .withColumn("_ingested_at", current_timestamp()) \
        .withColumn("_source", lit("api_logistica"))

    # APPEND-ONLY: o bronze nunca sobrescreve (GUIDE Conceito 3).
    # É isso que preserva o histórico e permite reprocessar silver/gold sem reextrair a origem.
    # Trocar por mode("overwrite") 