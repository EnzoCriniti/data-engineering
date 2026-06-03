"""Diagrama de arquitetura - Capitulo 11: CDC com Debezium.

    pip install -r requirements.txt
    python architecture.py
"""
from diagrams import Diagram, Cluster, Edge
from diagrams.onprem.database import PostgreSQL
from diagrams.onprem.queue import Kafka
from diagrams.onprem.storage import Ceph as ObjectStore
from diagrams.programming.language import Python

with Diagram(
    "Cap 11 - CDC com Debezium",
    filename="architecture",
    show=False,
    direction="LR",
):
    gen = Python("load gen\n(insert/update)")
    pg = PostgreSQL("PostgreSQL\n(wal_level=logical)")

    with Cluster("Captura"):
        dbz = Python("Debezium\n(Kafka Connect)")

    kafka = Kafka("Kafka/Redpanda\n(topicos CDC)")
    sink = ObjectStore("sink -> Delta\n(MERGE idempotente)")

    gen >> pg >> Edge(label="WAL") >> dbz >> Edge(label="eventos") >> kafka >> sink
