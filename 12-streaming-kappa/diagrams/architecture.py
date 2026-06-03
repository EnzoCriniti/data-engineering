"""Diagrama de arquitetura - Capitulo 12: Streaming (Kappa).

    pip install -r requirements.txt
    python architecture.py
"""
from diagrams import Diagram, Cluster, Edge
from diagrams.onprem.queue import Kafka
from diagrams.onprem.storage import Ceph as ObjectStore
from diagrams.programming.language import Python

with Diagram(
    "Cap 12 - Streaming em tempo real (Kappa)",
    filename="architecture",
    show=False,
    direction="LR",
):
    producer = Python("producer\n(eventos GPS)")
    topic_in = Kafka("topic: gps-events")

    with Cluster("Stream processor"):
        proc = Python("janelas de tempo\n+ estado")

    topic_out = Kafka("topic: live-metrics")
    lake = ObjectStore("lakehouse\n(historico, premissa)")

    producer >> topic_in >> proc
    proc >> Edge(label="metricas ao vivo") >> topic_out
    proc >> Edge(style="dashed", label="sink historico") >> lake
