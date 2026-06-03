"""Diagrama de arquitetura — Capítulo 01: ELT batch com Python.

Gera architecture.png. Requer Graphviz instalado no sistema.
    pip install -r requirements.txt
    python architecture.py
"""
from diagrams import Diagram, Cluster, Edge
from diagrams.onprem.database import PostgreSQL
from diagrams.onprem.compute import Server
from diagrams.programming.language import Python

with Diagram(
    "Cap 04 - ELT batch com Python (Python + SQL + cron)",
    filename="architecture",
    show=False,
    direction="LR",
):
    seeder = Python("seeder (Faker)")

    with Cluster("OLTP"):
        pg = PostgreSQL("PostgreSQL\n(pedidos)")

    with Cluster("Pipeline (cron)"):
        elt = Python("extract + load\n(psycopg2)")

    with Cluster("OLAP (warehouse)"):
        duck = Server("DuckDB\n(raw + SQL marts)")

    seeder >> Edge(label="popula") >> pg
    pg >> Edge(label="extract") >> elt >> Edge(label="load + SQL") >> duck
