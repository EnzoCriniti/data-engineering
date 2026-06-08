# Solução — Cap. 04: ELT batch com Python e DuckDB

> Gabarito de implementação. Siga o [GUIDE.md](./GUIDE.md) para o contexto.

## Estrutura de arquivos

```
04-elt-batch-com-python/
├── .env.example
├── docker-compose.yml
└── pipeline/
    ├── requirements.txt
    ├── Dockerfile
    └── pipeline.py
```

## `docker-compose.yml`

```yaml
services:
  oltp:
    image: postgres:16
    container_name: p04-oltp
    ports:
      - "${OLTP_PORT:-5435}:5432"
    environment:
      POSTGRES_DB: nuvemstore
      POSTGRES_USER: nuvemstore
      POSTGRES_PASSWORD: nuvemstore
    volumes:
      - oltp-data:/var/lib/postgresql/data
      - ../00-modelagem-transacional/ddl/schema.sql:/docker-entrypoint-initdb.d/01-schema.sql:ro
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U nuvemstore"]
      interval: 5s
      timeout: 5s
      retries: 10

  seeder:
    build: ../00-modelagem-transacional/seed
    container_name: p04-seeder
    environment:
      DATABASE_URL: postgresql://nuvemstore:nuvemstore@oltp:5432/nuvemstore
    depends_on:
      oltp: { condition: service_healthy }
    profiles: [jobs]

  pipeline:
    build: ./pipeline
    container_name: p04-pipeline
    environment:
      OLTP_URL: postgresql://nuvemstore:nuvemstore@oltp:5432/nuvemstore
      DUCKDB_PATH: /data/warehouse/nuvemstore.duckdb
    volumes:
      - ./data/warehouse:/data/warehouse
    depends_on:
      oltp: { condition: service_healthy }
    profiles: [jobs]

volumes:
  oltp-data:
```

## `pipeline/requirements.txt`

```
psycopg2-binary==2.9.9
duckdb==1.1.0
```

## `pipeline/Dockerfile`

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY pipeline.py .
CMD ["python", "pipeline.py"]
```

## `pipeline/pipeline.py`

```python
"""ELT batch: Postgres → DuckDB (raw VARCHAR) → marts."""
import os, logging
import psycopg2
import duckdb
from decimal import Decimal

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

OLTP_URL = os.getenv("OLTP_URL", "postgresql://nuvemstore:nuvemstore@localhost:5435/nuvemstore")
DUCKDB_PATH = os.getenv("DUCKDB_PATH", "data/warehouse/nuvemstore.duckdb")

TABLES = ["cliente", "categoria", "produto", "entregador",
          "pedido", "item_pedido", "pagamento", "entrega"]

def normalize(row):
    """Converte Decimal → float para compatibilidade com DuckDB."""
    return tuple(float(v) if isinstance(v, Decimal) else v for v in row)

def extract_and_load(pg_cur, duck):
    """Extract de cada tabela do Postgres e load como raw_* VARCHAR no DuckDB."""
    for table in TABLES:
        pg_cur.execute(f"SELECT * FROM {table}")
        cols = [desc[0] for desc in pg_cur.description]
        rows = [normalize(r) for r in pg_cur.fetchall()]

        duck.execute(f"DROP TABLE IF EXISTS raw_{table}")
        col_defs = ", ".join(f"{c} VARCHAR" for c in cols)
        duck.execute(f"CREATE TABLE raw_{table} ({col_defs})")

        if rows:
            placeholders = ", ".join(["?"] * len(cols))
            duck.executemany(f"INSERT INTO raw_{table} VALUES ({placeholders})", rows)

        log.info("raw_%s: %d linhas", table, len(rows))

def transform(duck):
    """Cria marts a partir das tabelas raw."""
    duck.execute("""
        CREATE OR REPLACE TABLE mart_receita_diaria AS
        SELECT
            CAST(p.data_pedido AS DATE) AS dia,
            COUNT(DISTINCT p.pedido_id) AS total_pedidos,
            SUM(CAST(ip.quantidade AS INT) * CAST(ip.preco_unitario AS DOUBLE)) AS receita
        FROM raw_pedido p
        JOIN raw_item_pedido ip ON ip.pedido_id = p.pedido_id
        WHERE p.status != 'cancelado'
        GROUP BY 1
        ORDER BY 1
    """)
    log.info("mart_receita_diaria criado.")

    duck.execute("""
        CREATE OR REPLACE TABLE mart_top_produtos AS
        SELECT
            pr.nome AS produto,
            cat.nome AS categoria,
            SUM(CAST(ip.quantidade AS INT) * CAST(ip.preco_unitario AS DOUBLE)) AS receita,
            SUM(CAST(ip.quantidade AS INT)) AS unidades
        FROM raw_item_pedido ip
        JOIN raw_produto pr ON pr.produto_id = ip.produto_id
        JOIN raw_categoria cat ON cat.categoria_id = pr.categoria_id
        JOIN raw_pedido p ON p.pedido_id = ip.pedido_id
        WHERE p.status != 'cancelado'
        GROUP BY 1, 2
        ORDER BY receita DESC
        LIMIT 20
    """)
    log.info("mart_top_produtos criado.")

def reconcile(pg_cur, duck):
    """Verifica contagens entre origem e destino."""
    for table in TABLES:
        pg_cur.execute(f"SELECT COUNT(*) FROM {table}")
        src = pg_cur.fetchone()[0]
        dst = duck.execute(f"SELECT COUNT(*) FROM raw_{table}").fetchone()[0]
        status = "✅" if src == dst else "❌"
        log.info("%s %s: origem=%d destino=%d", status, table, src, dst)

def main():
    pg = psycopg2.connect(OLTP_URL)
    duck = duckdb.connect(DUCKDB_PATH)

    with pg.cursor() as cur:
        extract_and_load(cur, duck)
        transform(duck)
        reconcile(cur, duck)

    pg.close()
    duck.close()
    log.info("Pipeline concluído.")

if __name__ == "__main__":
    main()
```

## `.env.example`

```env
OLTP_PORT=5435
OLTP_URL=postgresql://nuvemstore:nuvemstore@oltp:5432/nuvemstore
DUCKDB_PATH=/data/warehouse/nuvemstore.duckdb
```

## Validações

```bash
docker compose up -d oltp
docker compose --profile jobs run seeder
docker compose --profile jobs run pipeline
# ✅ todas as tabelas com count correto
docker compose --profile jobs run pipeline  # idempotente
```
