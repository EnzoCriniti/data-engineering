"""Gera a URL interna preservando caracteres especiais da senha."""
import os
from urllib.parse import quote

password = quote(os.environ["AIRFLOW_DB_PASSWORD"], safe="")
print(f"postgresql+psycopg2://airflow:{password}@airflow-db:5432/airflow")
