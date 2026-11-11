"""Migração OLTP → Warehouse com resolução de surrogate keys."""
import os
import psycopg2
from psycopg2.extras import execute_values

OLTP_URL = os.getenv("OLTP_URL")
WAREHOUSE_URL = os.getenv("WAREHOUSE_URL")

def main():
    oltp = psycopg2.connect(OLTP_URL)
    wh = psycopg2.connect(WAREHOUSE_URL)

    with oltp.cursor() as src, wh.cursor() as dst:
        dst.execute("CREATE EXTENSION IF NOT EXISTS dblink")

        # --- Truncar destino ---
        dst.execute("""
            TRUNCATE analytics.fct_vendas, analytics.dim_tempo,
                     analytics.dim_cliente, analytics.dim_produto
            RESTART IDENTITY CASCADE
        """)

        # --- dim_tempo ---
        src.execute("SELECT DISTINCT data_pedido::date FROM pedido ORDER BY 1")
        tempos = []
        for (d,) in src.fetchall():
            tempos.append((d, d.day, d.month, (d.month - 1) // 3 + 1, d.year))
        execute_values(dst, """
            INSERT INTO analytics.dim_tempo (data, dia, mes, trimestre, ano) VALUES %s
        """, tempos)

        # --- dim_cliente ---
        src.execute("SELECT cliente_id, nome, cidade, email FROM cliente")
        clientes = [(r[0], r[1], r[2], r[3], True) for r in src.fetchall()]
        execute_values(dst, """
            INSERT INTO analytics.dim_cliente (cliente_id, nome, cidade, email, atual) VALUES %s
        """, clientes)

        # --- dim_produto ---
        src.execute("""
            SELECT p.produto_id, p.nome, c.nome
            FROM produto p JOIN categoria c ON c.categoria_id = p.categoria_id
        """)
        execute_values(dst, """
            INSERT INTO analytics.dim_produto (produto_id, nome, categoria) VALUES %s
        """, src.fetchall())

        # --- fct_vendas (surrogate resolution via subquery) ---
        dst.execute("""
            INSERT INTO analytics.fct_vendas
                (sk_tempo, sk_cliente, sk_produto, pedido_id, item_pedido_id, quantidade, valor_total)
            SELECT dt.sk_tempo, dc.sk_cliente, dp.sk_produto,
                   ip.pedido_id, ip.item_pedido_id, ip.quantidade,
                   ip.quantidade * ip.preco_unitario
            FROM dblink(%s,
                 'SELECT ip.pedido_id, ip.item_pedido_id, ip.produto_id, ip.quantidade,
                         ip.preco_unitario, p.data_pedido::date, p.cliente_id
                  FROM item_pedido ip JOIN pedido p ON p.pedido_id = ip.pedido_id
                  WHERE p.status != ''cancelado''')
            AS ip(pedido_id int, item_pedido_id int, produto_id int, quantidade int,
                  preco_unitario numeric, data_pedido date, cliente_id int)
            JOIN analytics.dim_tempo dt ON dt.data = ip.data_pedido
            JOIN analytics.dim_cliente dc ON dc.cliente_id = ip.cliente_id AND dc.atual = true
            JOIN analytics.dim_produto dp ON dp.produto_id = ip.produto_id
        """, (OLTP_URL,))

    wh.commit()

    # --- Reconciliação ---
    with oltp.cursor() as src, wh.cursor() as dst:
        src.execute("""
            SELECT COUNT(*), COALESCE(SUM(ip.quantidade * ip.preco_unitario), 0)
            FROM item_pedido ip JOIN pedido p ON p.pedido_id = ip.pedido_id
            WHERE p.status != 'cancelado'
        """)
        src_count, src_rev = src.fetchone()

        dst.execute("SELECT COUNT(*), COALESCE(SUM(valor_total), 0) FROM analytics.fct_vendas")
        dst_count, dst_rev = dst.fetchone()

        print(f"Origem:  {src_count} itens, receita={src_rev}")
        print(f"Destino: {dst_count} itens, receita={dst_rev}")

        if src_count == dst_count and abs(float(src_rev) - float(dst_rev)) < 0.01:
            print("✅ Reconciliação OK")
        else:
            print("❌ Reconciliação FALHOU")
            raise SystemExit(1)

    oltp.close()
    wh.close()

if __name__ == "__main__":
    main()
