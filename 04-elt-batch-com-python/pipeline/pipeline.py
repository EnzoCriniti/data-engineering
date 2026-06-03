import os
from decimal import Decimal

import duckdb
import psycopg2


DATABASE_URL = os.environ["DATABASE_URL"]
DUCKDB_PATH = os.getenv("DUCKDB_PATH", "/warehouse/nuvemstore.duckdb")

TABLES = [
    "cliente",
    "categoria",
    "produto",
    "pedido",
    "item_pedido",
    "pagamento",
    "entregador",
    "entrega",
]


def normalize(value):
    if isinstance(value, Decimal):
        return float(value)
    return value


def load_table(pg_cursor, duck_conn, table):
    pg_cursor.execute(f"SELECT * FROM {table}")
    rows = pg_cursor.fetchall()
    columns = [column.name for column in pg_cursor.description]

    duck_conn.execute(f"DROP TABLE IF EXISTS raw_{table}")
    column_sql = ", ".join(f"{column} VARCHAR" for column in columns)
    duck_conn.execute(f"CREATE TABLE raw_{table} ({column_sql})")

    if rows:
        placeholders = ", ".join(["?"] * len(columns))
        duck_conn.executemany(
            f"INSERT INTO raw_{table} VALUES ({placeholders})",
            [[normalize(value) for value in row] for row in rows],
        )

    print(f"raw_{table}: {len(rows)} linhas")


def build_marts(duck_conn):
    duck_conn.execute(
        """
        CREATE OR REPLACE TABLE mart_receita_diaria AS
        SELECT
            CAST(p.data_pedido AS DATE) AS data,
            COUNT(DISTINCT p.id) AS pedidos,
            SUM(CAST(i.quantidade AS INTEGER) * CAST(i.preco_unitario AS DOUBLE)) AS receita
        FROM raw_pedido p
        JOIN raw_item_pedido i ON i.pedido_id = p.id
        WHERE p.status <> 'cancelado'
        GROUP BY 1
        ORDER BY 1
        """
    )
    duck_conn.execute(
        """
        CREATE OR REPLACE TABLE mart_top_produtos AS
        SELECT
            pr.nome AS produto,
            c.nome AS categoria,
            SUM(CAST(i.quantidade AS INTEGER)) AS unidades,
            SUM(CAST(i.quantidade AS INTEGER) * CAST(i.preco_unitario AS DOUBLE)) AS receita
        FROM raw_item_pedido i
        JOIN raw_produto pr ON pr.id = i.produto_id
        JOIN raw_categoria c ON c.id = pr.categoria_id
        GROUP BY 1, 2
        ORDER BY receita DESC
        LIMIT 20
        """
    )
    print("marts: mart_receita_diaria, mart_top_produtos")


def main():
    with psycopg2.connect(DATABASE_URL) as pg_conn:
        with pg_conn.cursor() as pg_cursor:
            with duckdb.connect(DUCKDB_PATH) as duck_conn:
                for table in TABLES:
                    load_table(pg_cursor, duck_conn, table)
                build_marts(duck_conn)

    print(f"Pipeline concluido: {DUCKDB_PATH}")


if __name__ == "__main__":
    main()
