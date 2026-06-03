"""Diagrama de arquitetura - Capitulo 07: Orquestracao com Airflow.

    pip install -r requirements.txt
    python architecture.py
"""
from diagrams import Diagram, Cluster, Edge
from diagrams.onprem.database import PostgreSQL
from diagrams.onprem.workflow import Airflow
from diagrams.onprem.compute import Server
from diagrams.programming.language import Python

with Diagram(
    "Cap 07 - Orquestracao com Airflow",
    filename="architecture",
    show=False,
    direction="LR",
):
    with Cluster("Fontes"):
        pg = PostgreSQL("Postgres\n(pedidos)")
        csv = Python("CSV parceiro")
        api = Python("API marketing")

    with Cluster("Airflow DAG"):
        ing = Server("ingest tasks\n(retry/backfill)")
        dbt = Server("dbt run\n(apos ingestoes)")
        ing >> Edge(label="depende de") >> dbt

    air = Airflow("scheduler")

    [pg, csv, api] >> ing
    air >> Edge(style="dashed", label="orquestra") >> ing
