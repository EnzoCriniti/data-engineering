"""Diagrama de arquitetura consolidada - Capitulo 17: Capstone da plataforma."""

from diagrams import Diagram, Cluster, Edge
from diagrams.onprem.analytics import Spark, Metabase
from diagrams.onprem.database import PostgreSQL
from diagrams.onprem.queue import Kafka
from diagrams.onprem.workflow import Airflow
from diagrams.onprem.iac import Terraform
from diagrams.programming.language import Python


with Diagram(
    "Cap 17 - Plataforma consolidada NuvemStore",
    filename="architecture",
    outformat="png",
    show=False,
):
    with Cluster("Fontes"):
        oltp = PostgreSQL("OLTP")
        api = Python("API transportadora")
        gps = Kafka("GPS streaming")

    with Cluster("Plataforma"):
        ingest = Python("ELT / CDC / Kappa")
        lake = Spark("Lake / Lakehouse\n(Delta / Medallion)")

    with Cluster("Transversal"):
        orq = Airflow("Airflow")
        iac = Terraform("Terraform / LocalStack")

    with Cluster("Consumo"):
        bi = Metabase("BI")
        ml = PostgreSQL("Feature table (ML)")

    [oltp, api, gps] >> Edge(label="ingestao") >> ingest >> lake
    lake >> Edge(label="gold") >> [bi, ml]
    orq >> Edge(style="dashed", label="orquestra") >> ingest
    iac >> Edge(style="dashed", label="provisiona") >> lake
