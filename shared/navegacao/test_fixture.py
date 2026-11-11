"""Teste rápido do gerador e do SQL sem containers ou dependências extras."""

from datetime import datetime
import json
from pathlib import Path
import sqlite3
import unittest

from generate import fixture, PEDIDOS_DEMO


SQL = Path(__file__).resolve().parents[2] / "10-lakehouse-medallion/sql/funil.sql"


def execute_sql(lines):
    with sqlite3.connect(":memory:") as db:
        db.executescript("""
            CREATE TABLE silver_eventos (
                session_id TEXT, event_type TEXT, event_seq INTEGER,
                event_epoch_s INTEGER, pedido_confirmado_id INTEGER
            );
            CREATE TABLE parametros (inicio_s INTEGER, fim_s INTEGER);
            INSERT INTO parametros VALUES (1794279600, 1794366000);
        """)
        ids = {row[0] for row in PEDIDOS_DEMO}
        for line in sorted(set(lines)):
            event = json.loads(line)
            if "event_id" not in event:
                continue
            order_id = event.get("pedido_id")
            db.execute("INSERT INTO silver_eventos VALUES (?, ?, ?, ?, ?)", (
                event["session_id"], event["event_type"], event["event_seq"],
                int(datetime.fromisoformat(event["event_ts"]).timestamp()),
                order_id if order_id in ids else None,
            ))
        sessions = db.execute(SQL.read_text(encoding="utf-8")).fetchall()
    counts = tuple(sum(row[column] is not None for row in sessions) for column in range(2, 6))
    converted = sorted(row[6] for row in sessions if row[6] is not None)
    return counts, converted


class NavegacaoTest(unittest.TestCase):
    def test_base_reproduzivel(self):
        self.assertEqual(fixture(), fixture())
        self.assertEqual(len(fixture()), 16)
        self.assertEqual(execute_sql(fixture()), ((4, 3, 2, 1), [101]))

    def test_chegada_tardia(self):
        self.assertEqual(execute_sql(fixture() + fixture(lote="tardio")), ((4, 3, 2, 2), [101, 102]))


if __name__ == "__main__":
    unittest.main()
