"""ERD — Capítulo 00: Modelagem transacional (OLTP, normalizado).

    pip install -r requirements.txt
    python architecture.py
"""
from diagrams import Diagram, Cluster, Edge
from diagrams.onprem.database import PostgreSQL

with Diagram(
    "Cap 00 - Modelo transacional (OLTP normalizado)",
    filename="architecture",
    show=False,
    direction="LR",
):
    with Cluster("PostgreSQL (OLTP - 3FN)"):
        categoria = PostgreSQL("categoria")
        produto = PostgreSQL("produto")
        cliente = PostgreSQL("cliente")
        pedido = PostgreSQL("pedido")
        item = PostgreSQL("item_pedido")
        pagamento = PostgreSQL("pagamento")
        entrega = PostgreSQL("entrega")
        entregador = PostgreSQL("entregador")

        categoria >> Edge(label="1:N") >> produto
        cliente >> Edge(label="1:N") >> pedido
        pedido >> Edge(label="1:N") >> item
        produto >> Edge(label="1:N") >> item
        pedido >> Edge(label="1:1") >> pagamento
        pedido >> Edge(label="1:1") >> entrega
        entregador >> Edge(label="1:N") >> entrega
