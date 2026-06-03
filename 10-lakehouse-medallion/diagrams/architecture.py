"""Diagrama de arquitetura - Capitulo 10: Lakehouse + Medallion.

    pip install -r requirements.txt
    python architecture.py
"""
from diagrams import Diagram, Cluster, Edge
from diagrams.onprem.analytics import Spark
from diagrams.onprem.storage import Ceph as ObjectStore

with Diagram(
    "Cap 10 - Lakehouse (Delta) + Medallion",
    filename="architecture",
    show=False,
    direction="LR",
):
    with Cluster("Lakehouse (Delta sobre S3/MinIO)"):
        bronze = ObjectStore("bronze\n(cru, append-only)")
        silver = ObjectStore("silver\n(limpo, tipado)")
        gold = ObjectStore("gold\n(agregado p/ BI)")

    spark_b = Spark("Spark: ingest")
    spark_s = Spark("Spark: clean")
    spark_g = Spark("Spark: aggregate")

    spark_b >> bronze >> Edge(label="MERGE") >> spark_s >> silver >> spark_g >> gold
