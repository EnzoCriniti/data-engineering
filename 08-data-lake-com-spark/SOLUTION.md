# Solução — Cap. 08: Data lake com Spark

> Gabarito de implementação. Siga o [GUIDE.md](./GUIDE.md) para o contexto.

## Estrutura de arquivos

```
08-data-lake-com-spark/
├── docker-compose.yml
└── spark/
    ├── jobs/
    │   └── ingest_to_lake.py
    └── Dockerfile
```

## `docker-compose.yml`

```yaml
services:
  # Hadoop HDFS (Namenode + Datanode)
  namenode:
    image: bde2020/hadoop-namenode:2.0.0-hadoop3.2.1-java8
    container_name: p08-namenode
    environment:
      - CLUSTER_NAME=test
    env_file:
      - ./hadoop.env
    ports:
      - "9870:9870"
      - "9000:9000"

  datanode:
    image: bde2020/hadoop-datanode:2.0.0-hadoop3.2.1-java8
    container_name: p08-datanode
    env_file:
      - ./hadoop.env
    environment:
      SERVICE_PRECONDITION: "namenode:9870"
    ports:
      - "9864:9864"
    depends_on:
      - namenode

  # Apache Spark (Master + Worker)
  spark-master:
    image: bitnami/spark:3.5
    container_name: p08-spark-master
    environment:
      - SPARK_MODE=master
    ports:
      - "8081:8080" # UI
      - "7077:7077"

  spark-worker:
    image: bitnami/spark:3.5
    container_name: p08-spark-worker
    environment:
      - SPARK_MODE=worker
      - SPARK_MASTER_URL=spark://spark-master:7077
    depends_on:
      - spark-master

  # Hive Metastore Backend
  metastore-db:
    image: postgres:13
    container_name: p08-metastore-db
    environment:
      POSTGRES_DB: metastore
      POSTGRES_USER: hive
      POSTGRES_PASSWORD: hive
      
  # Metastore Service (mock simplificado para o Compose)
  # Em um setup real, usaríamos uma imagem oficial do Hive Metastore
```

## `spark/jobs/ingest_to_lake.py`

```python
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, IntegerType, StringType, DoubleType, TimestampType
from pyspark.sql.functions import col, to_date

def main():
    spark = SparkSession.builder \
        .appName("Ingest to Lake") \
        .master("local[*]") \
        .enableHiveSupport() \
        .getOrCreate()

    # Definir Schema explicitamente em vez de inferir do JSON
    schema = StructType([
        StructField("entrega_id", IntegerType(), True),
        StructField("pedido_id", IntegerType(), True),
        StructField("status", StringType(), True),
        StructField("data_ocorrencia", TimestampType(), True),
        StructField("latitude", DoubleType(), True),
        StructField("longitude", DoubleType(), True),
        StructField("velocidade_kmh", DoubleType(), True)
    ])

    # Simulando a leitura de um JSON gerado pelo OLTP/API
    # No ambiente real, apontar para hdfs://namenode:9000/landing/entregas.json
    print("Lendo dados JSON brutos...")
    df = spark.read.json("file:///app/data/entregas.json", schema=schema)
    
    # Criar coluna de partição
    df = df.withColumn("data_particao", to_date(col("data_ocorrencia")))

    # Escrever no Data Lake em Parquet, particionado por data
    print("Escrevendo Parquet no HDFS...")
    output_path = "hdfs://namenode:9000/lake/entregas"
    
    df.write \
      .mode("overwrite") \
      .partitionBy("data_particao") \
      .parquet(output_path)
      
    # Registrar no Hive Metastore
    print("Registrando tabela no Metastore...")
    df.write \
      .mode("overwrite") \
      .partitionBy("data_particao") \
      .saveAsTable("lake.entregas")
      
    print("Ingestão concluída com sucesso.")
    spark.stop()

if __name__ == "__main__":
    main()
```
