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
    # Trocar por mode("overwrite") aqui é a armadilha que destrói o propósito do bronze.
    output_path = "s3a://datalake/bronze/entregas"
    print(f"Gravando Delta na camada Bronze: {output_path}")
    
    df_bronze.write \
        .format("delta") \
        .mode("append") \
        .save(output_path)
        
    print("Ingestão Bronze concluída.")
    spark.stop()

if __name__ == "__main__":
    main()
```

## `spark/jobs/silver_transform.py`

```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, sha2, when
from delta.tables import DeltaTable

def main():
    spark = SparkSession.builder \
        .appName("Silver Transformation") \
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
        .getOrCreate()

    bronze_path = "s3a://datalake/bronze/entregas"
    silver_path = "s3a://datalake/silver/entregas"

    print("Lendo da camada Bronze...")
    df_bronze = spark.read.format("delta").load(bronze_path)

    # LIMPEZA + PSEUDONIMIZAÇÃO DE PII (GUIDE Conceito 4):
    # - filter NOT NULL nas chaves = regra técnica; silver rejeita o que não passa.
    # - reduzir a precisão do GPS (decimal 5,2) generaliza a localização -> requisito LGPD.
    #   Em produção, o email também seria hasheado aqui: sha2(concat(salt, email), 256).
    df_clean = df_bronze \
        .filter(col("entrega_id").isNotNull() & col("pedido_id").isNotNull()) \
        .withColumn("latitude", when(col("latitude").isNotNull(), col("latitude").cast("decimal(5,2)")).otherwise(None)) \
        .withColumn("longitude", when(col("longitude").isNotNull(), col("longitude").cast("decimal(5,2)")).otherwise(None))
        
    print("Realizando MERGE na camada Silver (Deduplicação)...")
    
    # DEDUPLICAÇÃO VIA MERGE (GUIDE Conceito 2 + Etapa 3):
    # O bronze é append-only, então a MESMA entrega_id pode vir em várias ingestões
    # (ex.: status "em_rota" e depois "entregue"). Um append+distinct NÃO resolve,
    # porque as linhas são diferentes. O MERGE por chave mantém UMA linha por entrega_id,
    # com o estado mais recente. É o mesmo padrão de upsert que o CDC do cap 11 reusa.
    # Primeira execução: tabela não existe ainda -> grava direto. Depois: MERGE.
    if not DeltaTable.isDeltaTable(spark, silver_path):
        df_clean.write.format("delta").mode("overwrite").save(silver_path)
    else:
        silver_table = DeltaTable.forPath(spark, silver_path)
        
        silver_table.alias("target").merge(
            df_clean.alias("updates"),
            "target.entrega_id = updates.entrega_id"   # condição de chave: erre aqui e duplica/sobrescreve errado
        ).whenMatchedUpdateAll() \
         .whenNotMatchedInsertAll() \
         .execute()

    print("Transformação Silver concluída.")
    spark.stop()

if __name__ == "__main__":
    main()
```

## `spark/jobs/gold_marts.py`

```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, avg, count

def main():
    spark = SparkSession.builder \
        .appName("Gold Marts") \
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
        .getOrCreate()

    silver_path = "s3a://datalake/silver/entregas"
    gold_path = "s3a://datalake/gold/resumo_entregas"

    print("Lendo da camada Silver...")
    df_silver = spark.read.format("delta").load(silver_path)

    print("Calculando agregações...")
    # GOLD = métricas de negócio prontas para consumo (GUIDE Conceito 3).
    # Agrega a silver por status: total de entregas e velocidade média.
    df_gold = df_silver.groupBy("status").agg(
        count("entrega_id").alias("total_entregas"),
        avg("velocidade_kmh").alias("velocidade_media")
    )

    # OVERWRITE é seguro no gold (GUIDE Etapa 4): a tabela é DERIVADA da silver,
    # logo recalculável a qualquer momento -> sobrescrever é idempotente.
    # (Diferente do bronze, onde overwrite apagaria histórico irrecuperável.)
    print(f"Gravando Delta na camada Gold: {gold_path}")
    df_gold.write \
        .format("delta") \
        .mode("overwrite") \
        .save(gold_path)

    print("Marts Gold criados com sucesso.")
    spark.stop()

if __name__ == "__main__":
    main()
```

## Validações

Roda os três jobs em ordem e prova as garantias que o GUIDE ensinou:

```bash
# 1) Bronze append-only: rodar 2x faz o COUNT crescer
docker compose run spark-submit spark-submit /app/jobs/bronze_ingest.py
docker compose run spark-submit spark-submit /app/jobs/bronze_ingest.py

# 2) Silver deduplicada: COUNT == COUNT(DISTINCT entrega_id)
docker compose run spark-submit spark-submit /app/jobs/silver_transform.py

# 3) Gold consultável
docker compose run spark-submit spark-submit /app/jobs/gold_marts.py
```

Provas conceituais (rodar no `spark-sql` ou via Trino):

```sql
-- Time travel (GUIDE Conceito 2): comparar a versão atual com a versão 0
SELECT COUNT(*) FROM delta.`s3a://datalake/silver/entregas`;
SELECT COUNT(*) FROM delta.`s3a://datalake/silver/entregas` VERSION AS OF 0;

-- Histórico de commits registrado no _delta_log
DESCRIBE HISTORY delta.`s3a://datalake/silver/entregas`;

-- Silver realmente deduplicada: as duas contagens devem ser IGUAIS
SELECT COUNT(*) AS total,
       COUNT(DISTINCT entrega_id) AS distintos
FROM   delta.`s3a://datalake/silver/entregas`;
```

```python
# VACUUM: remove Parquets antigos não referenciados (limpeza de custo)
from delta.tables import DeltaTable
DeltaTable.forPath(spark, "s3a://datalake/silver/entregas").vacuum(168)  # retém 7 dias
```

Esperado: bronze cresce a cada run; `total == distintos` na silver (MERGE funcionou); `VERSION AS OF 0` mostra um estado anterior (time travel funciona); `DESCRIBE HISTORY` lista um commit por escrita.
