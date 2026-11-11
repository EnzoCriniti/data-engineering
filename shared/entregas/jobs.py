"""Comandos usados no estudo, nos jobs manuais e no Airflow."""
import argparse
import json
import os
import subprocess
import sys
from contextlib import contextmanager
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parents[2]
DBT = ROOT / "05-transformacao-com-dbt"
EXTRACTOR = ROOT / "06-ingestao-api-externa" / "extractor" / "extract.py"


@contextmanager
def writer_lock():
    import fcntl

    path = Path(os.environ["DUCKDB_PATH"]).with_name(".batch.lock")
    with path.open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        yield


def build(as_of, sales_only=False):
    options = ["--select", "+mart_receita_diaria", "+mart_top_produtos"] if sales_only else []
    variables = ["--vars", json.dumps({"sla_as_of": as_of})] if as_of else []
    dbt = Path(sys.executable).with_name("dbt")
    with writer_lock():
        subprocess.run(
            [str(dbt), "build", "--project-dir", str(DBT), "--profiles-dir", str(DBT),
             *options, *variables],
            check=True,
        )


def extract(start=None, end=None):
    options = ["--start", start, "--end", end] if start else []
    with writer_lock():
        subprocess.run([sys.executable, str(EXTRACTOR), *options], check=True)


def report():
    with writer_lock(), duckdb.connect(os.environ["DUCKDB_PATH"], read_only=True) as db:
        for status, count in db.execute("""
            select situacao_sla, count(*) from analytics_dbt.mart_sla_entregas group by 1 order by 1
        """).fetchall():
            print(f"{status}: {count}")
        for row in db.execute("""
            select entrega_id, pedido_id, previsao_entrega, atraso_segundos
            from analytics_dbt.mart_sla_entregas
            where situacao_sla = 'atraso_aberto'
            order by atraso_segundos desc, entrega_id
        """).fetchall():
            print(*row, sep=" | ")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("job", choices=["sales", "extract", "build", "report"])
    parser.add_argument("--start")
    parser.add_argument("--end")
    parser.add_argument("--as-of")
    args = parser.parse_args()
    if bool(args.start) != bool(args.end):
        parser.error("--start e --end devem ser usados juntos")
    if args.job == "extract":
        extract(args.start, args.end)
    elif args.job == "report":
        report()
    else:
        build(args.as_of, sales_only=args.job == "sales")


if __name__ == "__main__":
    main()
