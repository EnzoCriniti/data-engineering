"""Diagrama de arquitetura - Capitulo 08: Data Lake com Spark.

    pip install -r requirements.txt
    python architecture.py
"""
from diagrams import Diagram, Cluster, Edge
from diagrams.onprem.analytics import Spark
from diagrams.onprem.storage import Ceph as ObjectStore  # icone generico de object storage
from diagrams.programming.language import Python

with Diagram(
    "Cap 08 - Data Lake com Spark (S3/MinIO)",
    filename="architecture",
    show=False,
    direction="LR",
):
    gen = Python("generator\n(eventos JSON)")

    with Cluster("Object Storage (S3-compatible)"):
        landing = ObjectStore("MinIO\nlanding (JSON cru)")
        curated = ObjectStore("MinIO\ncurated (Parquet)")

    with Cluster("Processamento distribuido"):
        spark = Spark("Spark\n(parse, joins, agregacao)")

    gen >> Edge(label="upload") >> landing
    landing >> Edge(label="read") >> spark >> Edge(label="write Parquet") >> curated
