"""Diagrama de arquitetura - Capitulo 13: Base de ML para fraude."""

from diagrams import Diagram, Edge
from diagrams.onprem.analytics import Spark
from diagrams.onprem.database import PostgreSQL
from diagrams.onprem.queue import Kafka
from diagrams.programming.language import Python


with Diagram(
    "Cap 13 - Base de ML para fraude",
    filename="architecture",
    outformat="png",
    show=False,
):
    gold = Spark("lakehouse gold")
    stream = Kafka("metricas streaming")
    builder = Python("feature builder")
    features = PostgreSQL("ml.fraude_pagamento_features")

    [gold, stream] >> Edge(label="features") >> builder >> features
