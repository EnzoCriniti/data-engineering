"""Pontos de entrada dos jobs da NuvemStore no NAS."""

import argparse
import fcntl
import os
from contextlib import closing
from pathlib import Path

import psycopg2
from psycopg2.extensions import make_dsn


def configure_database(variable, host, database, password_key):
    if variable not in os.environ:
        os.environ[variable] = make_dsn(
            host=host, dbname=database, user=database,
            password=os.environ[password_key], connect_timeout=5,
        )


def seed_empty_database():
    os.environ["DATABASE_URL"] = os.environ["OLTP_URL"]
    os.environ["SEED_RESET"] = "false"
    import seed
    from pipeline import TABLES

    with closing(psycopg2.connect(os.environ["OLTP_URL"])) as conn, conn.cursor() as cur:
        populated = []
        for table in TABLES:
            cur.execute(f"SELECT EXISTS (SELECT 1 FROM {table})")
            if cur.fetchone()[0]:
                populated.append(table)

    if len(populated) == len(TABLES):
        print("OLTP já populado. Bootstrap ignorado.")
    elif populated:
        raise SystemExit("OLTP parcialmente populado. Confira os dados antes do bootstrap.")
    else:
        seed.main()


def refresh():
    import migrate
    import pipeline
    import verify

    migrate.main()
    pipeline.main()
    verify.main()


def main():
    os.umask(0o002)
    parser = argparse.ArgumentParser()
    parser.add_argument("job", choices=["seed", "simulate", "pipeline", "verify", "daily", "schedule"])
    job = parser.parse_args().job
    if job == "schedule":
        from scheduler import run

        run()
        return

    configure_database("OLTP_URL", "oltp", "nuvemstore", "OLTP_PASSWORD")
    if job in {"pipeline", "daily"}:
        configure_database("WAREHOUSE_URL", "warehouse", "warehouse", "WAREHOUSE_PASSWORD")

    # Todos os jobs do ambiente montam o mesmo volume local do DuckDB.
    lock_path = Path(os.environ["DUCKDB_PATH"]).with_name(".batch.lock")
    with lock_path.open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        if job == "seed":
            seed_empty_database()
        if job in {"simulate", "daily"}:
            from simulator import append_orders

            append_orders()
        if job in {"pipeline", "daily"}:
            refresh()
        if job == "verify":
            import verify

            verify.main()


if __name__ == "__main__":
    main()
