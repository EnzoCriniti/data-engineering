"""Acrescenta um lote de pedidos sintéticos por data UTC."""

import os
import random
from contextlib import closing
from datetime import UTC, datetime

import psycopg2


def append_orders():
    as_of = os.getenv("SIM_AS_OF")
    timestamp = datetime.fromisoformat(as_of) if as_of else datetime.now(UTC)
    if timestamp.utcoffset() is None:
        raise ValueError("SIM_AS_OF deve incluir fuso horário.")
    now = timestamp.astimezone(UTC).replace(tzinfo=None)
    day = now.date()
    rng = random.Random(day.toordinal())
    order_count = int(os.environ["SIM_PEDIDOS"])
    if order_count <= 0:
        raise ValueError("SIM_PEDIDOS precisa ser positivo.")

    with closing(psycopg2.connect(os.environ["OLTP_URL"])) as conn, conn, conn.cursor() as cur:
        cur.execute("CREATE TABLE IF NOT EXISTS simulacao_diaria (dia date PRIMARY KEY)")
        cur.execute(
            "INSERT INTO simulacao_diaria (dia) VALUES (%s) ON CONFLICT DO NOTHING",
            (day,),
        )
        if not cur.rowcount:
            print(f"{day}: pedidos diários já gerados.")
            return

        cur.execute("SELECT cliente_id FROM cliente ORDER BY cliente_id")
        customers = cur.fetchall()
        cur.execute("SELECT produto_id, preco FROM produto ORDER BY produto_id")
        products = cur.fetchall()
        cur.execute("SELECT entregador_id FROM entregador ORDER BY entregador_id")
        couriers = cur.fetchall()
        if not all((customers, products, couriers)):
            raise RuntimeError("Execute o seeder antes de simular pedidos.")

        terceirizar = os.getenv("SIM_TERCEIRIZAR") == "true"
        if terceirizar:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS simulacao_transportadora (
                    pedido_id integer PRIMARY KEY REFERENCES pedido(pedido_id) ON DELETE CASCADE
                )
            """)

        for index in range(order_count):
            (customer_id,) = rng.choice(customers)
            (courier_id,) = rng.choice(couriers)
            product_id, price = rng.choice(products)
            quantity = rng.randint(1, 3)
            cur.execute(
                "INSERT INTO pedido (cliente_id, data_pedido, status) VALUES (%s, %s, 'pago') RETURNING pedido_id",
                (customer_id, now),
            )
            (order_id,) = cur.fetchone()
            cur.execute(
                "INSERT INTO item_pedido (pedido_id, produto_id, quantidade, preco_unitario) VALUES (%s, %s, %s, %s)",
                (order_id, product_id, quantity, price),
            )
            cur.execute(
                "INSERT INTO pagamento (pedido_id, valor, metodo, status, data_pagamento) VALUES (%s, %s, 'pix', 'pago', %s)",
                (order_id, price * quantity, now),
            )
            if terceirizar and index % 2 == 0:
                cur.execute("INSERT INTO simulacao_transportadora VALUES (%s)", (order_id,))
            else:
                cur.execute(
                    "INSERT INTO entrega (pedido_id, entregador_id, status, data_saida) "
                    "VALUES (%s,%s,'em_transito',%s)",
                    (order_id, courier_id, now),
                )

    print(f"{day}: {order_count} pedidos acrescentados.")
