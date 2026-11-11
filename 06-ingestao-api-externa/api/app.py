"""API de exemplo da Transportadora X."""
import base64
import binascii
import hashlib
import hmac
import json
import os
from collections import deque
from contextlib import closing
from datetime import UTC, datetime, timedelta
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Lock
from time import monotonic
from urllib.parse import parse_qs, urlsplit


def parse_instant(value):
    parsed = datetime.fromisoformat(value)
    if parsed.utcoffset() is None:
        raise ValueError("Informe o fuso horário.")
    return parsed.astimezone(UTC)


def fixture_records(path):
    def read(_as_of):
        return json.loads(path.read_text(encoding="utf-8"))
    return read


def simulated_records(as_of):
    """Adaptador do ambiente sintético. O contrato HTTP é o mesmo da fixture."""
    import psycopg2

    with closing(psycopg2.connect(
        host=os.environ["MOCK_OLTP_HOST"], dbname="nuvemstore", user="nuvemstore",
        password=os.environ["OLTP_PASSWORD"], connect_timeout=5,
    )) as conn, conn.cursor() as cur:
        conn.set_session(readonly=True)
        cur.execute("select to_regclass('public.simulacao_transportadora')")
        if cur.fetchone()[0] is None:
            return []
        cur.execute("""
            select p.pedido_id, p.data_pedido
            from pedido p join simulacao_transportadora s using (pedido_id)
            where p.data_pedido <= %s
        """, [as_of.replace(tzinfo=None)])
        rows = cur.fetchall()

    records = []
    for order_id, created in rows:
        sent = created.replace(tzinfo=UTC)
        promise = sent + timedelta(hours=18)
        event = sent
        status = "em_transito"
        if order_id % 3 != 0:
            completed = sent + timedelta(hours=12 if order_id % 3 == 1 else 30)
            if completed <= as_of:
                event = completed
                status = "entregue"
        records.append({
            "entrega_id": f"TRX-{order_id:06d}", "pedido_id": order_id, "status": status,
            "previsao_entrega": promise.isoformat(), "event_ts": event.isoformat(),
            "updated_at": event.isoformat(), "ocorrencia": status, "valor_frete": 15.0,
        })
    return records


class CarrierAPI(ThreadingHTTPServer):
    def __init__(self, address, key, read_records, *, rate_limit=10, fault=None):
        super().__init__(address, Handler)
        self.key = key
        self.read_records = read_records
        self.rate_limit = rate_limit
        self.fault = fault
        self.requests = deque()
        self.lock = Lock()

    def throttled(self):
        now = monotonic()
        with self.lock:
            while self.requests and now - self.requests[0] >= 1:
                self.requests.popleft()
            if len(self.requests) >= self.rate_limit:
                return True
            self.requests.append(now)
        return False

    def cursor(self, values):
        data = json.dumps(values).encode()
        signature = hmac.digest(self.key.encode(), data, hashlib.sha256)
        return base64.urlsafe_b64encode(signature + data).decode()

    def read_cursor(self, encoded):
        token = base64.urlsafe_b64decode(encoded)
        signature, data = token[:32], token[32:]
        if not hmac.compare_digest(signature, hmac.digest(self.key.encode(), data, hashlib.sha256)):
            raise ValueError("Cursor inválido.")
        return json.loads(data)

    def page(self, params):
        since_text = params.get("updated_since", [None])[0]
        until_text = params.get("updated_before", [None])[0]
        since = parse_instant(since_text) if since_text else None
        until = parse_instant(until_text) if until_text else None
        limit = int(params.get("limit", ["100"])[0])
        if not 1 <= limit <= 500 or (since and until and since >= until):
            raise ValueError("Janela ou limite inválido.")
        scope = [since_text, until_text, limit]
        snapshot = datetime.now(UTC)
        after = None
        cursor = params.get("cursor", [None])[0]
        if cursor:
            saved_scope, snapshot_text, updated, delivery_id = self.read_cursor(cursor)
            if saved_scope != scope:
                raise ValueError("Cursor pertence a outra consulta.")
            snapshot = parse_instant(snapshot_text)
            after = (parse_instant(updated), delivery_id)

        rows = []
        for record in self.read_records(snapshot):
            updated = parse_instant(record["updated_at"])
            key = (updated, record["entrega_id"])
            if updated > snapshot or (since and updated < since) or (until and updated >= until):
                continue
            if after is None or key > after:
                rows.append((key, record))
        rows.sort(key=lambda item: item[0])
        next_cursor = None
        if len(rows) > limit:
            updated, delivery_id = rows[limit - 1][0]
            next_cursor = self.cursor([scope, snapshot.isoformat(), updated.isoformat(), delivery_id])
        return {"data": [record for _, record in rows[:limit]],
                "next_cursor": next_cursor, "has_more": next_cursor is not None}


class Handler(BaseHTTPRequestHandler):
    def reply(self, status, data, headers=None):
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        for name, value in (headers or {}).items():
            self.send_header(name, value)
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        request = urlsplit(self.path)
        if request.path == "/health":
            self.reply(200, {"status": "ok"})
            return
        if request.path != "/entregas":
            self.reply(404, {"error": "rota inexistente"})
            return
        if not hmac.compare_digest(self.headers.get("X-API-Key", "").encode(), self.server.key.encode()):
            self.reply(401, {"error": "chave inválida"})
            return
        params = parse_qs(request.query)
        fault = self.server.fault(params) if self.server.fault else None
        if fault == 429 or self.server.throttled():
            self.reply(429, {"error": "limite de requisições"}, {"Retry-After": "1"})
            return
        if fault:
            self.reply(fault, {"error": "falha simulada"})
            return
        try:
            page = self.server.page(params)
        except (ValueError, binascii.Error) as error:
            self.reply(400, {"error": str(error)})
            return
        except Exception as error:
            self.log_error("Fonte sintética indisponível: %s", type(error).__name__)
            self.reply(503, {"error": "fonte indisponível"})
            return
        self.reply(200, page)

    def log_request(self, code="-", size="-"):
        self.log_message("%s %s %s", self.command, urlsplit(self.path).path, code)


def main():
    source = simulated_records if os.getenv("MOCK_OLTP_HOST") else fixture_records(
        Path(os.getenv("TRANSPORTADORA_FIXTURE", Path(__file__).with_name("entregas.json")))
    )
    with CarrierAPI(("0.0.0.0", int(os.getenv("PORT", "8000"))),
                    os.environ["TRANSPORTADORA_API_KEY"], source) as server:
        server.serve_forever()


if __name__ == "__main__":
    main()
