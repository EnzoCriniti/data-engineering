"""Confere o resultado da demonstração batch contra o PostgreSQL."""

from contextlib import closing

import duckdb
import psycopg2

from pipeline import DUCKDB_PATH, OLTP_URL, TABLES


def main():
    with (
        closing(psycopg2.connect(OLTP_URL)) as postgres,
        postgres.cursor() as source,
        duckdb.connect(DUCKDB_PATH, read_only=True) as warehouse,
    ):
        for table in TABLES:
            source.execute(f"SELECT COUNT(*) FROM {table}")
            (source_count,) = source.fetchone()
            (warehouse_count,) = warehouse.execute(
                f"SELECT COUNT(*) FROM raw_{table}"
            ).fetchone()
            if source_count == 0 or source_count != warehouse_count:
                raise SystemExit(
                    f"{table}: origem={source_count}, destino={warehouse_count}"
                )

        source.execute("""
            SELECT p.data_pedido::date AS dia,
                   COUNT(DISTINCT p.pedido_id),
                   SUM(i.quantidade * i.preco_unitario)
            FROM pedido p
            JOIN item_pedido i USING (pedido_id)
            WHERE p.status <> 'cancelado'
            GROUP BY dia
            ORDER BY dia
        """)
        expected = source.fetchall()
        actual = warehouse.execute("""
            SELECT dia, total_pedidos, CAST(receita AS DECIMAL(18, 2))
            FROM mart_receita_diaria
            ORDER BY dia
        """).fetchall()
        if not expected or expected != actual:
            raise SystemExit("O mart de receita diária diverge do PostgreSQL.")

        (products,) = warehouse.execute(
            "SELECT COUNT(*) FROM mart_top_produtos"
        ).fetchone()
        if products != 20:
            raise SystemExit(f"Esperava 20 produtos no ranking, recebi {products}.")

    orders = sum(row[1] for row in actual)
    revenue = sum(row[2] for row in actual)
    print(
        f"Reconciliação OK: {len(TABLES)} tabelas raw, {orders} pedidos, "
        f"receita {revenue:.2f}, {products} produtos no ranking."
    )


if __name__ == "__main__":
    main()
