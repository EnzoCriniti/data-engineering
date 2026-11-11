"""Ingere uma janela da API e confirma as entregas junto com o checkpoint."""
import argparse
import json
import logging
import os
from datetime import UTC, datetime, timedelta
from pathlib import Path
from time import sleep
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import duckdb

LOG = logging.getLogger(__name__)
DDL = Path(__file__).with_name("staging.sql").read_text(encoding="utf-8")
SOURCE = "transportadora_x"


def instant(value):
    parsed = datetime.fromisoformat(value)
    if parsed.utcoffset() is None:
        raise ValueError("O timestamp deve incluir fuso horário.")
    return parsed.astimezone(UTC)


def fetch_page(url, key, params, attempts, timeout, wait=sleep):
    request = Request(f"{url.rstrip('/')}/entregas?{urlencode(params)}", headers={"X-API-Key": key})
    for attempt in range(attempts):
        delay = 2 ** attempt
        try:
            with urlopen(request, timeout=timeout) as response:
                return json.load(response)
        except HTTPError as error:
            if error.code != 429 and not 500 <= error.code < 600:
                raise
            if attempt + 1 == attempts:
                raise
            if error.code == 429:
                retry_after = error.headers.get("Retry-After", "")
                if retry_after.isdecimal():
                    delay = max(delay, int(retry_after))
                elif retry_after:
                    from email.utils import parsedate_to_datetime

                    delay = max(delay, (parsedate_to_datetime(retry_after) - datetime.now(UTC)).total_seconds())
            LOG.warning("HTTP %s. Nova tentativa em %.0f s.", error.code, delay)
        except (URLError, TimeoutError) as error:
            if attempt + 1 == attempts:
                raise
            LOG.warning("%s. Nova tentativa em %.0f s.", type(error).__name__, delay)
        wait(delay)
    raise ValueError("API_ATTEMPTS deve ser positivo.")


def deliveries(url, key, since, until, limit, attempts, timeout):
    params = {"limit": limit}
    if since is not None:
        params["updated_since"] = since.isoformat()
    if until is not None:
        params["updated_before"] = until.isoformat()
    cursors = set()
    while True:
        page = fetch_page(url, key, params, attempts, timeout)
        if not isinstance(page.get("data"), list):
            raise ValueError("Resposta sem lista data.")
        cursor = page.get("next_cursor")
        if type(page.get("has_more")) is not bool or page["has_more"] != bool(cursor):
            raise ValueError("Cursor e has_more inconsistentes.")
        yield from page["data"]
        if not cursor:
            return
        if not isinstance(cursor, str) or cursor in cursors:
            raise ValueError("Cursor inválido ou repetido.")
        cursors.add(cursor)
        params["cursor"] = cursor


def load(db, url, key, *, start=None, end=None, limit=100, overlap=timedelta(hours=24),
         attempts=3, timeout=10):
    if (start is None) != (end is None) or (start is not None and start >= end):
        raise ValueError("Informe uma janela completa [início, fim), com início anterior ao fim.")
    if not 1 <= limit <= 500 or overlap < timedelta(0) or attempts < 1 or timeout <= 0:
        raise ValueError("Configuração inválida de paginação, sobreposição ou retry.")

    db.execute("begin")
    try:
        db.execute(DDL)
        row = db.execute(
            "select updated_at from staging.transportadora_checkpoint where fonte = ?", [SOURCE]
        ).fetchone()
        checkpoint = row[0] if row else None
        since = start
        if since is None and checkpoint is not None:
            since = checkpoint - overlap
        high_water = checkpoint
        ingested = datetime.now(UTC)
        counts = {"lidos": 0, "gravados": 0, "ignorados": 0}
        for record in deliveries(url, key, since, end, limit, attempts, timeout):
            counts["lidos"] += 1
            delivery_id = record["entrega_id"]
            order_id = record["pedido_id"]
            updated = instant(record["updated_at"])
            if not isinstance(delivery_id, str) or not delivery_id.strip() or type(order_id) is not int:
                raise ValueError("entrega_id textual e pedido_id inteiro são obrigatórios.")
            if (since is not None and updated < since) or (end is not None and updated >= end):
                raise ValueError("API retornou atualização fora da janela solicitada.")
            payload = json.dumps(record, sort_keys=True, ensure_ascii=False, allow_nan=False)
            existing = db.execute(
                "select updated_at, payload from staging.transportadora_entregas where entrega_id = ?",
                [delivery_id],
            ).fetchone()
            if existing and existing[0] >= updated:
                if existing[0] == updated and json.loads(existing[1]) != record:
                    raise ValueError(f"Versões conflitantes da entrega {delivery_id} em {updated}.")
                counts["ignorados"] += 1
            else:
                db.execute(
                    """insert or replace into staging.transportadora_entregas
                       (entrega_id, pedido_id, updated_at, ingestion_ts, payload)
                       values (?, ?, ?, ?, ?)""",
                    [delivery_id, order_id, updated, ingested, payload],
                )
                counts["gravados"] += 1
            if high_water is None or updated > high_water:
                high_water = updated
        if start is None and high_water != checkpoint:
            db.execute(
                "insert or replace into staging.transportadora_checkpoint values (?, ?)",
                [SOURCE, high_water],
            )
        db.execute("commit")
    except BaseException:
        db.execute("rollback")
        raise

    LOG.info("Transportadora %s. Desde=%s até=%s checkpoint=%s.",
             counts, since, end, high_water if start is None else checkpoint)
    return counts


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start", type=instant)
    parser.add_argument("--end", type=instant)
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    with duckdb.connect(os.environ["DUCKDB_PATH"]) as db:
        load(
            db, os.environ["TRANSPORTADORA_URL"], os.environ["TRANSPORTADORA_API_KEY"],
            start=args.start, end=args.end, limit=int(os.getenv("API_PAGE_SIZE", "100")),
            overlap=timedelta(hours=float(os.getenv("API_OVERLAP_HOURS", "24"))),
            attempts=int(os.getenv("API_ATTEMPTS", "3")),
            timeout=float(os.getenv("API_TIMEOUT_SECONDS", "10")),
        )


if __name__ == "__main__":
    main()
