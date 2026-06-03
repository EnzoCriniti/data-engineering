import os

import psycopg2
from psycopg2.extras import execute_values


OLTP_URL = os.environ["OLTP_URL"]
WAREHOUSE_URL = os.environ["WAREHOUSE_URL"]


def fetch_all(cursor, sql):
    cursor.execute(sql)
    return cursor.fetchall()


def main():
    with psycopg2.connect(OLTP_URL) as source, psycopg2.connect(WAREHOUSE_URL) as target:
        with source.cursor() as src, target.cursor() as dst:
            dst.execute(
                """
                TRUNCATE TABLE
                    analytics.fct_vendas,
                    analytics.dim_tempo,
                    analytics.dim_cliente,
                    analytics.dim_produto
                RESTART IDENTITY CASCADE
                """
            )

            clientes = fetch_all(src, "SELECT id, nome, cidade, criado_em FROM cliente")
            execute_values(
                dst,
                """
                INSERT INTO analytics.dim_cliente (cliente_id, nome, cidade, criado_em)
                VALUES %s
                """,
                clientes,
            )

            produtos = fetch_all(
                src,
                """
                SELECT p.id, p.nome, c.nome
                FROM produto p
                JOIN categoria c ON c.id = p.categoria_id
                """,
            )
            execute_values(
                dst,
                """
                INSERT INTO analytics.dim_produto (produto_id, nome, categoria)
                VALUES %s
                """,
                produtos,
            )

            datas = fetch_all(
                src,
                """
                SELECT DISTINCT CAST(data_pedido AS DATE)
                FROM pedido
                WHERE status <> 'cancelado'
                ORDER BY 1
                """,
            )
            execute_values(
                dst,
                """
                INSERT INTO analytics.dim_tempo (data, dia, mes, trimestre, ano)
                VALUES %s
                """,
                [
                    (data, data.day, data.month, ((data.month - 1) // 3) + 1, data.year)
                    for (data,) in datas
                ],
            )

            vendas = fetch_all(
                src,
                """
                SELECT
                    p.id AS pedido_id,
                    i.id AS item_pedido_id,
                    CAST(p.data_pedido AS DATE) AS data,
                    p.cliente_id,
                    i.produto_id,
                    i.quantidade,
                    i.quantidade * i.preco_unitario AS valor_total
                FROM pedido p
                JOIN item_pedido i ON i.pedido_id = p.id
                WHERE p.status <> 'cancelado'
                """,
            )
            execute_values(
                dst,
                """
                INSERT INTO analytics.fct_vendas (
                    pedido_id,
                    item_pedido_id,
                    sk_tempo,
                    sk_cliente,
                    sk_produto,
                    quantidade,
                    valor_total
                )
                SELECT
                    data.pedido_id,
                    data.item_pedido_id,
                    dt.sk_tempo,
                    dc.sk_cliente,
                    dp.sk_produto,
                    data.quantidade,
                    data.valor_total
                FROM (VALUES %s) AS data (
                    pedido_id,
                    item_pedido_id,
                    data_pedido,
                    cliente_id,
                    produto_id,
                    quantidade,
                    valor_total
                )
                JOIN analytics.dim_tempo dt ON dt.data = data.data_pedido
                JOIN analytics.dim_cliente dc ON dc.cliente_id = data.cliente_id
                JOIN analytics.dim_produto dp ON dp.produto_id = data.produto_id
                """,
                vendas,
            )

    print(f"Migracao concluida: {len(clientes)} clientes, {len(produtos)} produtos, {len(vendas)} itens vendidos.")


if __name__ == "__main__":
    main()
