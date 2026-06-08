# Solução — Cap. 12: Streaming Kappa

> Gabarito de implementação. Siga o [GUIDE.md](./GUIDE.md) para o contexto.

## Estrutura de arquivos

```
12-streaming-kappa/
├── docker-compose.yml
├── simulators/
│   └── gps_producer.py
└── spark/
    └── jobs/
        └── streaming_gps.py
```

## `docker-compose.yml`

Reúne o **Redpanda** (broker Kafka do cap 11), o **MinIO** (lake do cap 09/10) e dois runners: `gps_producer` (perfil `simulators`) e `spark-submit` (job de streaming). O produtor publica em `gps_events`; o job consome de `redpanda:29092` e grava Delta em `s3a://datalake/gold/velocidade_regional`.

```yaml
services:
  redpanda:
    image: docker.redpanda.com/vectorized/redpanda:latest
    container_name: p12-redpanda
    command:
      - redpanda start
      - --smp 1
      - --overprovisioned
      - --kafka-addr PLAINTEXT://0.0.0.0:29092,OUTSIDE://0.0.0.0:9092
      - --advertise-kafka-addr PLAINTEXT://redpanda:29092,OUTSIDE://localhost:9092
    ports:
      - "${REDPANDA_BROKER_PORT:-9092}:9092"
      - "29092:29092"

  redpanda-console:
    image: docker.redpanda.com/vectorized/console:latest
    container_name: p12-redpanda-console
    ports:
      - "${REDPANDA_CONSOLE_PORT:-8080}:8080"
    environment:
      KAFKA_BROKERS: redpanda:29092
    depends_on: [redpanda]

  minio:
    image: minio/minio
    container_name: p12-minio
    ports: ["9000:9000", "9001:9001"]
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadmin
    command: server /data --console-address ":9001"
    volumes: [minio-data:/data]

  minio-setup:
    image: minio/mc
    container_name: p12-minio-setup
    depends_on: [minio]
    entrypoint: >
      /bin/sh -c "sleep 5; mc alias set m http://minio:9000 minioadmin minioadmin; mc mb -p m/datalake; exit 0;"

  # Produtor contínuo de telemetria GPS (perfil simulators)
  gps_producer:
    build: ../00-modelagem-transacional/seed   # reaproveita base python; instala kafka-python via requirements do simulators
    container_name: p12-gps-producer
    volumes:
      - ./simulators:/app/simulators
    working_dir: /app/simulators
    command: ["python", "-u", "gps_producer.py"]
    environment:
      KAFKA_BROKER: redpanda:29092
    depends_on: [redpanda]
    profiles: [simulators]

  # Runner Spark Structured Streaming (mesma imagem Delta+S3A do cap 10)
  spark-submit:
    build: ../10-lakehouse-medallion/spark
    container_name: p12-spark
    volumes:
      - ./spark/jobs:/app/jobs
    environment:
      AWS_ACCESS_KEY_ID: minioadmin
      AWS_SECRET_ACCESS_KEY: minioadmin
    depends_on: [redpanda, minio]
    profiles: [jobs]

volumes:
  minio-data:
```

> O produtor lê o broker de `KAFKA_BROKER` (use `redpanda:29092` dentro do compose; `localhost:9092` se rodar fora). No `gps_producer.py`, troque o `BROKER = "localhost:9092"` por `os.getenv("KAFKA_BROKER", "localhost:9092")` para funcionar nos dois modos.

## `simulators/gps_producer.py`

```python
"""Produtor contínuo de eventos GPS para o Redpanda (Kafka)."""
import os
import json
import time
import random
from datetime import datetime
from kafka import KafkaProducer

# redpanda:29092 dentro do compose; localhost:9092 se rodar fora
BROKER = os.getenv("KAFKA_BROKER", "localhost:9092")
TOPIC = "gps_events"

def main():
    producer = KafkaProducer(
        bootstrap_servers=BROKER,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    
    print(f"Enviando eventos para {TOPIC} (Ctrl+C para parar)...")
    
    while True:
        # Simulando um entregador enviando telemetria
        entregador_id = random.randint(1, 10)
        pedido_id = random.randint(100, 200)
        
        # Simulando uma região no centro de SP
        lat = random.uniform(-23.56, -23.54)
        lon = random.uniform(-46.64, -46.62)
        
        vel = random.uniform(0.0, 60.0)
        
        event = {
            "entregador_id": entregador_id,
            "pedido_id": pedido_id,
            "latitude": round(lat, 6),
            "longitude": round(lon, 6),
            "velocidade_kmh