"""Diagrama de arquitetura - Capitulo 05: Transformacao com dbt.

    pip install -r requirements.txt
    python architecture.py
"""
from diagrams import Diagram, Cluster, Edge
from diagrams.onprem.database import PostgreSQL
from diagrams.onprem.compute import Server
from diagrams.programming.language import Python

with Diagram(
    "Cap 05 - Transformacao com dbt",
    filename="architecture",
    show=False,
    direction="LR",
):
    seeder = Python("seeder (Faker)")
    pg = PostgreSQL("PostgreSQL\n(OLTP)")

    with Cluster("ELT"):
        load = Python("extract + load")
        with Cluster("dbt (DAG de modelos)"):
            staging = Server("staging\n(limpeza)")
            marts = Server("marts\n(fatos/metricas)")
            staging >> Edge(label="ref()") >> marts

    seeder >> pg >> Edge(label="extract") >> load >> Edge(label="raw") >> staging
