"""Diagrama de arquitetura - Capitulo 06: Ingestao batch de API externa."""

from diagrams import Diagram, Edge
from diagrams.onprem.client import Client
from diagrams.onprem.database import PostgreSQL
from diagrams.programming.language import Python


with Diagram(
    "Cap 06 - Ingestao batch de API externa",
    filename="architecture",
    outformat="png",
    show=False,
):
    api = Client("Transportadora X API")
    extractor = Python("extractor batch")
    staging = PostgreSQL("warehouse.staging")

    api >> Edge(label="HTTP batch") >> extractor >> Edge(label="upsert") >> staging
