# Solução — Cap. 11: CDC com Debezium

> Gabarito de implementação. Siga o [GUIDE.md](./GUIDE.md) para o contexto.

## Estrutura de arquivos

```
11-cdc-com-debezium/
├── docker-compose.yml
├── connect/
│   └── register-postgres.json
├── consumer/
│   └── cdc_to_delta.py
└── simulators/
    └── oltp_traffic_sim.py
```

## `docker-compose.yml`

```yaml
services:
  # O OLTP precisa do wal_level=logical
  oltp:
    image: postgres:16
    container_name: p11-oltp
    ports:
      - "5435:5432"
    environment:
      POSTGRES_DB: nuvemstore
      POSTGRES_USER: nuvemstore
      POSTGRES_PASSWORD: nuvemstore
    command: ["postgres", "-c", "wal_level=logical"]
    # ... volumes e healthcheck padrão do OLTP ...

  redpanda:
    image: docker.redpanda.com/vectorized/redpanda:latest
    container_name: p11-redpanda
    command:
      - redpanda start
      - --smp 1
      - --overprovisioned
      - --kafka-addr PLAINTEXT://0.0.0.0:29092,OUTSIDE://0.0.0.0:9092
      - --advertise-kafka-addr PLAINTEXT://redpanda:29092,OUTSIDE://localhost:9092
    ports:
      - "9092:9092"
      - "29092:29092"

  redpanda-console:
    image: docker.redpanda.com/vectorized/console:latest
    container_name: p11-redpanda-console
    ports:
      - "8080:8080"
    environment:
      KAFKA_BROKERS: redpanda:29092
    depends_on:
      - redpanda

  kafka-connect:
    image: quay.io/debezium/connect:2.5
    container_name: p11-kafka-connect
    ports:
      - "8083:8083"
    environment:
      BOOTSTRAP_SERVERS: redpanda:29092
      GROUP_ID: 1
      CONFIG_STORAGE_TOPIC: my_connect_configs
      OFFSET_STORAGE_TOPIC: my_connect_offsets
      STATUS_STORAGE_TOPIC: my_connect_statuses
    depends_on:
      - redpanda
      - oltp
      
  # Simulador de Tráfego Contínuo (para testar o CDC na prática)
  oltp-simulator:
    build: ../00-modelagem-transacional/seed  # reaproveita imagem
    container_name: p11-oltp-sim
    volumes:
      - ./simulators/oltp_traffic_sim.py:/app/oltp_traffic_sim.py
    environment:
      DATABASE_URL: postgresql://nuvemstore:nuvemstore@oltp:5432/nuvemstore
    command: ["python", "-u", "oltp_traffic_sim.py"]
    depends_on:
      oltp: { condition: service_healthy }
    profiles: [simulators]
```

## `simulators/oltp_traffic_sim.py`

```python
"""Simulador de tráfego contínuo no OLTP para alimentar o CDC."""
import os, time, random
import psycopg2

DB_URL = os.getenv("DATABASE_URL")

def main():
    conn = psycopg2.connect(DB_URL)
    conn.autocommit = True
    cur = conn.cursor()
    
    print("Iniciando simulador de tráfego OLTP (Ctrl+C para parar)...")
    
    while True:
        # Escolhe aleatoriamente uma ação:
        # 1. Atualizar status de pagamento existente
        # 2. Inserir nova entrega
        acao = random.choice([1, 2])
        
        try:
            if acao == 1:
                cur.execute("SELECT pagamento_id FROM pagamento WHERE status = 'pendente' LIMIT 1")
                res = cur.fetchone()
                if res:
                    pid = res[0]
                    novo_status = random.choice(["pago", "recusado"])
                    cur.execute("UPDATE pagamento SET status = %s WHERE pagamento_id = %s", (novo_status, pid))
                    print(f"Pagamento {pid} atualizado para {novo_status}")
            
            elif acao == 2:
                cur.execute("SELECT pedido_id FROM pedido WHERE status = 'pago' ORDER BY RANDOM() LIMIT 1")
                res = cur.fetchone()
                if res:
                    pid = res[0]
                    cur.execute("SELECT 1 FROM entrega WHERE pedido_id = %s", (pid,))
                    if not cur.fetchone():
                        cur.execute(
                            "INSERT INTO entrega (pedido_id, entregador_id, status) VALUES (%s, %s, 'em_transito')",
                            (pid, random.randint(1, 30))
                        )
                        print(f"Nova entrega criada para pedido {pid}")
                        
        except Exception as e:
            print(f"Erro na simulação: {e}")
            
        time.sleep(random.uniform(2, 5))

if __name__ == "__main__":
    main()
```

## `connect/register-postgres.json`

```json
{
  "name": "nuvemstore-connector",
  "config": {
    "connector.class": "io.debezium.connector.postgresql.PostgresConnector",
    "tasks.max": "1",
    "database.hostname": "oltp",
    "database.port": "5432",
    "database.user": "nuvemstore",
    "database.password": "nuvemstore",
    "database.dbname": "nuvemstore",
    "topic.prefix": "pg",
    "schema.include.list": "public",
    "table.include.list": "public.pagamento,public.entrega",
    "plugin.name": "pgoutput",
    "slot.name": "debezium",
    "publication.autocreate.mode": "filtered"
  }
}
```

## Registrando o conector

```bash
curl -i -X POST -H "Accept:application/json" -H "Content-Type:application/json" localhost:8083/connectors/ -d @connect/register-postgres.json
```
