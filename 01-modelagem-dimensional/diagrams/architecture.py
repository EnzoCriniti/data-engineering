"""ERD — Capítulo 01: Modelagem dimensional (star schema).

    pip install -r requirements.txt
    python architecture.py
"""
from diagrams import Diagram, Cluster, Edge
from diagrams.onprem.analytics import Dremio as Table  # icone neutro de tabela analitica

with Diagram(
    "Cap 01 - Star schema (OLAP dimensional)",
    filename="architecture",
    show=False,
    direction="TB",
):
    with Cluster("Star schema"):
        fato = Table("fct_vendas\n(fato - metricas)")
        dim_tempo = Table("dim_tempo")
        dim_cliente = Table("dim_cliente (SCD2)")
        dim_produto = Table("dim_produto")
        dim_loja = Table("dim_loja")

        dim_tempo >> Edge(label="sk") >> fato
        dim_cliente >> Edge(label="sk") >> fato
        dim_produto >> Edge(label="sk") >> fato
        dim_loja >> Edge(label="sk") >> fato
