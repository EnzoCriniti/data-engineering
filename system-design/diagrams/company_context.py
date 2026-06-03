"""Diagrama macro da arquitetura da NuvemStore."""

from diagrams import Cluster, Diagram, Edge
from diagrams.onprem.analytics import Spark
from diagrams.onprem.client import Client
from diagrams.onprem.compute import Server
from diagrams.onprem.database import PostgreSQL
from diagrams.onprem.network import Nginx
from diagrams.onprem.queue import Kafka
from diagrams.onprem.storage import HDFS
from diagrams.programming.language import Python
from diagrams.saas.analytics import Snowflake


with Diagram(
    "NuvemStore - System Design Macro",
    filename="company_context",
    outformat="png",
    show=False,
):
    user = Client("Cliente")
    frontend = Nginx("frontend / checkout")
    backend = Server("backend e-commerce")
    oltp = PostgreSQL("OLTP")

    with Cluster("Fontes externas"):
        carrier = Server("API transportadora")
        gps = Kafka("eventos GPS")

    with Cluster("Plataforma de dados"):
        elt = Python("ELT batch")
        airflow = Python("Airflow")
        spark = Spark("Spark")
        hdfs = HDFS("HDFS legado")
        lakehouse = Snowflake("Lakehouse / Gold")
        stream = Kafka("Redpanda / CDC / Streaming")

    with Cluster("Consumo"):
        bi = Server("Metabase / BI")
        ml = Server("Features fraude")

    user >> frontend >> backend >> oltp
    oltp >> Edge(label="batch/CDC") >> elt
    carrier >> Edge(label="API batch") >> elt
    gps >> Edge(label="stream") >> stream
    airflow >> Edge(label="orquestra") >> elt
    elt >> spark >> hdfs >> lakehouse
    stream >> lakehouse
    lakehouse >> bi
    lakehouse >> ml
