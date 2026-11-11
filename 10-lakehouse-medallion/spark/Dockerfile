FROM apache/spark:3.5.5-scala2.12-java17-python3-ubuntu

USER root
WORKDIR /app
COPY shared/navegacao/requirements.txt /app/requirements.txt
RUN python3 -m pip install --no-cache-dir -r /app/requirements.txt
RUN python3 -m pip install --no-cache-dir --no-deps delta-spark==3.2.1
ARG MAVEN=https://repo.maven.apache.org/maven2
ADD ${MAVEN}/io/delta/delta-spark_2.12/3.2.1/delta-spark_2.12-3.2.1.jar /opt/spark/jars/
ADD ${MAVEN}/io/delta/delta-storage/3.2.1/delta-storage-3.2.1.jar /opt/spark/jars/
ADD ${MAVEN}/org/apache/hadoop/hadoop-aws/3.3.4/hadoop-aws-3.3.4.jar /opt/spark/jars/
ADD ${MAVEN}/com/amazonaws/aws-java-sdk-bundle/1.12.262/aws-java-sdk-bundle-1.12.262.jar /opt/spark/jars/
ADD ${MAVEN}/org/postgresql/postgresql/42.7.7/postgresql-42.7.7.jar /opt/spark/jars/
RUN chmod a+r /opt/spark/jars/*.jar && mkdir -p /lock && chown spark /lock
COPY shared/navegacao /app/
COPY 10-lakehouse-medallion/sql/funil.sql /app/funil.sql
ENV PYTHONPATH=/app PYSPARK_PYTHON=python3 SPARK_LOCAL_IP=127.0.0.1
USER spark
ENTRYPOINT ["/opt/spark/bin/spark-submit", "--master", "local[2]", "--driver-memory", "768m", "/app/lake.py"]
