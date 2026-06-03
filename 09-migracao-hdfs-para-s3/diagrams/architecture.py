"""Diagrama de arquitetura - Capitulo 09: Migracao HDFS para S3.

    pip install -r requirements.txt
    python architecture.py
"""
from diagrams import Diagram, Cluster, Edge
from diagrams.onprem.analytics import Spark
from diagrams.onprem.storage import Ceph as ObjectStore
from diagrams.onprem.database import Hadoop

with Diagram(
    "Cap 09 - Migracao HDFS para S3",
    filename="architecture",
    show=False,
    direction="LR",
):
    with Cluster("Zona quente (baixa latencia)"):
        hdfs = Hadoop("HDFS\n(ultimos 7 dias)")

    with Cluster("Zona fria (barato)"):
        s3 = ObjectStore("S3/MinIO\n(historico)")

    spark = Spark("Spark\n(query federada)")
    tiering = Spark("job de tiering\n(quente -> frio)")

    hdfs >> Edge(label="hdfs://") >> spark
    s3 >> Edge(label="s3a://") >> spark
    hdfs >> Edge(style="dashed", label="> 7 dias") >> tiering >> s3
