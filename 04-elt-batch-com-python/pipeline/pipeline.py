"""ELT batch: Postgres → DuckDB (raw VARCHAR) → marts."""
import os, logging
import psycopg2
import duckdb
from contextlib import closing
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
    with closing(psycopg2.connect(OLTP_URL)) as pg, duckdb.connect(DUCKDB_PATH) as duck:
        pg.set_session(isolation_level="REPEATABLE READ", readonly=True)
        duck.execute("BEGIN TRANSACTION")
        with pg.cursor() as cur:
            extract_and_load(cur, duck)
            transform(duck)
            reconcile(cur, duck)
        duck.execute("COMMIT")
    log.info("Pipeline concluído.")

if __name__ == "__main__":
    main()
