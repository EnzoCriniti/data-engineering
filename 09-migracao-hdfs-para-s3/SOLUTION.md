# Solução — Cap. 09: Migração HDFS para S3

> Gabarito de implementação. Siga o [GUIDE.md](./GUIDE.md) para o contexto.

## Estrutura de arquivos

```
09-migracao-hdfs-para-s3/
├── docker-compose.yml
├── spark/
│   └── jobs/
│       └── migrate_hdfs_to_s3.py
└── trino/
    └── catalog/
        └── hive.properties
```

## `docker-compose.yml`

```yaml
services:
  # MinIO (Object Storage S3-compatible)
  minio:
    image: minio/minio
    container_name: p09-minio
    ports:
      - "9000:9000"
      - "9001:9001"
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadminpassword
    command: server /data --console-address ":9001"
    
  # Setup inicial do MinIO (Cria o bucket)
  minio-setup:
    image: minio/mc
    container_name: p09-minio-setup
    depends_on:
      - minio
    entrypoint: >
      /bin/sh -c "
      sleep 5;
      mc alias set myminio http://minio:9000 minioadmin minioadminpassword;
      mc mb myminio/datalake;
      exit 0;
      "

  # Trino (Motor SQL Federado)
  trino:
    image: trinodb/trino:latest
    container_name: p09-trino
    ports:
      - "8082:8080"
    volumes:
      - ./trino/catalog:/etc/trino/catalog
```

## `trino/catalog/hive.properties`

```properties
connector.name=hive
hive.metastore.uri=thrift://hive-metastore:9083
hive.s3.aws-access-key=minioadmin
hive.s3.aws-secret-key=minioadminpassword
hive.s3.endpoint=http://minio:9000
hive.s3.path-style-access=true
```

## `spark/jobs/migrate_hdfs_to_s3.py`

```python
from pyspark.sql import SparkSession

def main():
    spark = SparkSession.builder \
        .appName("Migrate HDFS to S3") \
        .config("spark.hadoop.fs.s3a.access.key", "minioadmin") \
        .config("spark.hadoop.fs.s3a.secret.key", "minioadminpassword") \
        .config("spark.hadoop.fs.s3a.endpoint", "http://minio:9000") \
        .config("spark.hadoop.fs.s3a.path.style.access", "true") \
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
        .getOrCreate()

    hdfs_path = "hdfs://namenode:9000/lake/entregas"
    s3_path = "s3a://datalake/lake/entregas"

    print(f"Lendo dados do HDFS: {hdfs_path}")
    df_hdfs = spark.read.parquet(hdfs_path)
    
    hdfs_count = df_hdfs.count()
    print(f"Linhas encontradas no HDFS: {hdfs_count}")

    # Escrevendo no S3 (MinIO) mantendo as partições
    print(f"Escrevendo dados no S3: {s3_path}")
    df_hdfs.write \
        .mode("overwrite") \
        .partitionBy("data_particao") \
        .parquet(s3_path)

    # Validação
    print("Validando a migração...")
    df_s3 = spark.read.parquet(s3_path)
    s3_count = df_s3.count()
    
    print(f"Linhas lidas do S3: {s3_count}")
    
    if hdfs_count == s3_count:
        print("✅ Migração concluída e validada com sucesso!")
    else:
        print(f"❌ Falha na migração: HDFS={hdfs_count}, S3={s3_count}")

    spark.stop()

if __name__ == "__main__":
    main()
```
