"""Exercita a API HTTP, a carga incremental e os modelos com relógio fixo."""
import copy
import json
import os
import subprocess
import sys
import tempfile
import threading
import unittest
from contextlib import contextmanager
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import urlopen

import duckdb

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "06-ingestao-api-externa" / "api"))
sys.path.insert(0, str(ROOT / "06-ingestao-api-externa" / "extractor"))
from app import CarrierAPI
from extract import fetch_page, instant, load

DBT = ROOT / "05-transformacao-com-dbt"
AS_OF = "2026-06-08T16:00:00Z"


def seed_orders(path):
    if os.getenv("OLTP_URL"):
        from contextlib import closing

        import psycopg2

        # O CI usa um PostgreSQL descartável com o DDL do capítulo 00.
        with closing(psycopg2.connect(os.environ["OLTP_URL"])) as pg, pg, pg.cursor() as cur:
            cur.execute("insert into cliente (nome, cidade, email) values ('Logística', 'São Paulo', 'sla@local.test') returning cliente_id")
            (customer,) = cur.fetchone()
            ids = []
            for status in ["pago"] * 7 + ["cancelado"]:
                cur.execute(
                    "insert into pedido (cliente_id, data_pedido, status) values (%s, '2026-06-08', %s) returning pedido_id",
                    [customer, status],
                )
                ids.append(cur.fetchone()[0])
            cur.execute("insert into categoria (nome) values ('Teste') returning categoria_id")
            (category,) = cur.fetchone()
            cur.execute(
                "insert into produto (categoria_id, nome, preco) values (%s, 'Produto', 19.90) returning produto_id",
                [category],
            )
            (product,) = cur.fetchone()
            cur.executemany(
                "insert into item_pedido (pedido_id, produto_id, quantidade, preco_unitario) values (%s, %s, 2, 19.90)",
                [(order_id, product) for order_id in ids],
            )
        os.environ["DUCKDB_PATH"] = str(path)
        sys.path.insert(0, str(ROOT / "04-elt-batch-com-python" / "pipeline"))
        import pipeline

        pipeline.main()
        return ids

    ids = list(range(101, 109))
    with duckdb.connect(str(path)) as db:
        db.execute("""
            create table raw_pedido (pedido_id varchar, data_pedido varchar, status varchar);
            create table raw_categoria as select '1' as categoria_id, 'Teste' as nome;
            create table raw_produto as select '1' as produto_id, 'Produto' as nome, '1' as categoria_id;
            create table raw_item_pedido (
                item_pedido_id varchar, pedido_id varchar, produto_id varchar,
                quantidade varchar, preco_unitario varchar
            );
        """)
        for index, order_id in enumerate(ids):
            db.execute("insert into raw_pedido values (?, '2026-06-08', ?)",
                       [order_id, "cancelado" if index == 7 else "pago"])
            db.execute("insert into raw_item_pedido values (?, ?, '1', '2', '19.90')", [index, order_id])
    return ids


def fixture(ids):
    scenarios = [
        (ids[0], "em_transito", "14:00", "12:00"),
        (ids[0], "em_transito", "17:00", "12:00"),
        (ids[1], "entregue", "14:00", "14:00"),
        (ids[2], "entregue", "14:00", "15:00"),
        (ids[3], "devolvido", "14:00", "15:00"),
        (ids[4], "extraviado", "14:00", "15:00"),
        (-1, "em_transito", "14:00", "12:00"),
        (ids[7], "em_transito", "14:00", "12:00"),
        (ids[5], "em_transito", None, "12:00"),
    ]
    return [
        {
            "entrega_id": f"TRX-{index}", "pedido_id": order_id, "status": status,
            "previsao_entrega": f"2026-06-08T{promise}:00Z" if promise else None,
            "event_ts": f"2026-06-08T{event}:00Z", "updated_at": "2026-06-08T15:05:00Z",
            "ocorrencia": status, "valor_frete": 15,
        }
        for index, (order_id, status, promise, event) in enumerate(scenarios)
    ]


@contextmanager
def api_server(read, fault):
    with CarrierAPI(("127.0.0.1", 0), "local", read, fault=fault, rate_limit=1000) as server:
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            yield f"http://127.0.0.1:{server.server_port}"
        finally:
            server.shutdown()
            thread.join()


def dbt_build(path):
    dbt = Path(sys.executable).with_name("dbt.exe" if os.name == "nt" else "dbt")
    subprocess.run(
        [str(dbt), "build", "--project-dir", str(DBT), "--profiles-dir", str(DBT),
         "--vars", json.dumps({"sla_as_of": AS_OF})],
        env={**os.environ, "DUCKDB_PATH": str(path), "DBT_SEND_ANONYMOUS_USAGE_STATS": "false"},
        check=True,
    )


def state(db):
    return (
        db.execute("select * from staging.transportadora_entregas order by entrega_id").fetchall(),
        db.execute("select * from staging.transportadora_checkpoint").fetchall(),
    )


class PhaseTwoTest(unittest.TestCase):
    def test_incremental_and_sla(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "warehouse.duckdb"
            ids = seed_orders(path)
            original = fixture(ids)
            feed = copy.deepcopy(original)
            failure = None
            retry = False

            def fault(params):
                nonlocal retry
                if retry:
                    retry = False
                    return 429
                return failure if params.get("cursor") else None

            with api_server(lambda _: feed, fault) as url:
                with urlopen(url + "/health") as result:
                    self.assertEqual(result.status, 200)
                with self.assertRaises(HTTPError) as invalid:
                    fetch_page(url, "wrong", {}, 3, 2)
                self.assertEqual(invalid.exception.code, 401)
                delays = []
                retry = True
                self.assertEqual(len(fetch_page(url, "local", {"limit": 2}, 2, 2, delays.append)["data"]), 2)
                self.assertEqual(delays, [1])
                with duckdb.connect(str(path)) as db:
                    first = load(db, url, "local", limit=2)
                    self.assertEqual(first, {"lidos": 9, "gravados": 9, "ignorados": 0})
                    initial = state(db)
                    self.assertEqual(load(db, url, "local", limit=2)["gravados"], 0)
                    self.assertEqual(state(db), initial)

                    # A primeira página contém uma alteração válida antes da falha da segunda.
                    feed[0]["updated_at"] = "2026-06-08T15:04:00Z"
                    feed[0]["entrega_id"] = "TRX-NOVA"
                    failure = 503
                    with self.assertRaises(HTTPError):
                        load(db, url, "local", limit=2, attempts=1)
                    self.assertEqual(state(db), initial)

                    # Mesma versão com payload diferente deve falhar sem publicar.
                    feed[:] = copy.deepcopy(original)
                    failure = None
                    feed[0]["ocorrencia"] = "conflito"
                    with self.assertRaisesRegex(ValueError, "conflitantes"):
                        load(db, url, "local", limit=2)
                    self.assertEqual(state(db), initial)
                    feed[:] = copy.deepcopy(original)

                dbt_build(path)
                with duckdb.connect(str(path)) as db:
                    counts = dict(db.execute("""
                        select situacao_sla, count(*) from analytics_dbt.mart_sla_entregas group by 1
                    """).fetchall())
                    self.assertEqual(counts, {
                        "atraso_aberto": 1, "entregue_com_atraso": 1, "no_prazo": 2, "devolvido": 1,
                        "extraviado": 1, "pedido_orfao": 1, "pedido_cancelado": 1, "prazo_invalido": 1,
                    })
                    print("SLA inicial:", counts, flush=True)
                    self.assertEqual(db.execute("""
                        select entrega_id, pedido_id, atraso_segundos
                        from analytics_dbt.mart_sla_entregas where situacao_sla = 'atraso_aberto'
                    """).fetchall(), [("TRX-0", ids[0], 7200)])
                    self.assertEqual(db.execute("""
                        select total_pedidos, cast(receita as double) from analytics_dbt.mart_receita_diaria
                    """).fetchall(), [(7, 278.6)])
                    self.assertEqual(db.execute("""
                        select produto, unidades, cast(receita as double) from analytics_dbt.mart_top_produtos
                    """).fetchall(), [("Produto", 14, 278.6)])
                    if os.getenv("OLTP_URL"):
                        self.assertEqual(db.execute("""
                            select total_pedidos, round(receita, 2) from main.mart_receita_diaria
                        """).fetchall(), [(7, 278.6)])
                        self.assertEqual(db.execute("""
                            select produto, unidades, round(receita, 2) from main.mart_top_produtos
                        """).fetchall(), [("Produto", 14, 278.6)])

                    feed[0].update(status="entregue", event_ts="2026-06-08T15:30:00Z",
                                   updated_at="2026-06-08T15:35:00Z")
                    start, end = instant("2026-06-08T15:30:00Z"), instant("2026-06-08T16:00:00Z")
                    self.assertEqual(load(db, url, "local", start=start, end=end)["gravados"], 1)
                    repaired = state(db)
                    self.assertEqual(repaired[1], initial[1])
                    self.assertEqual(load(db, url, "local", start=start, end=end)["gravados"], 0)
                    self.assertEqual(state(db), repaired)
                    feed[:] = copy.deepcopy(original)
                    self.assertEqual(load(db, url, "local", start=instant("2026-06-08T15:00:00Z"),
                                          end=start)["gravados"], 0)
                    self.assertEqual(state(db), repaired)

                dbt_build(path)
                with duckdb.connect(str(path), read_only=True) as db:
                    self.assertEqual(db.execute("""
                        select count(*) from analytics_dbt.mart_sla_entregas
                        where situacao_sla = 'atraso_aberto'
                    """).fetchone()[0], 0)
                    print("Reprocessamento: 0 atrasos abertos, checkpoint preservado.", flush=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
