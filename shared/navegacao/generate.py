"""Fixture da coorte de 10/11/2026 (America/Sao_Paulo)."""

import argparse
from datetime import date, datetime, timedelta, timezone
import json
from uuid import UUID, uuid5


COORTE = date(2026, 11, 10)
INICIO = datetime(2026, 11, 10, 23, 50, tzinfo=timezone.utc)
NAMESPACE = UUID("23e901e2-17e9-4f6c-8cbb-e0dc7e5d217d")
PEDIDOS_DEMO = [(101, 10, "pago"), (102, 11, "pago")]


def fixture(pedidos=PEDIDOS_DEMO, lote="base"):
    pago, outro_pago = pedidos
    eventos = []

    def emitir(sessao, seq, tipo, segundos, **campos):
        session_id = uuid5(NAMESPACE, sessao)
        evento = {
            "schema_version": 1,
            "event_id": str(uuid5(session_id, str(seq))),
            "session_id": str(session_id),
            "event_seq": seq,
            "event_type": tipo,
            "event_ts": (INICIO + timedelta(seconds=segundos)).isoformat().replace("+00:00", "Z"),
            **campos,
        }
        eventos.append(json.dumps(evento, sort_keys=True, separators=(",", ":")))

    if lote == "tardio":
        emitir("checkout", 5, "purchase_completed", 240, pedido_id=outro_pago[0], cliente_id=outro_pago[1])
        return eventos
    if lote != "base":
        raise ValueError(f"lote desconhecido: {lote}")

    emitir("visualizacao", 1, "add_to_cart", 0, produto_id=1)
    emitir("visualizacao", 2, "product_view", 0, produto_id=1)
    emitir("carrinho", 1, "product_view", 10, produto_id=1)
    emitir("carrinho", 2, "add_to_cart", 10, produto_id=1)
    emitir("carrinho", 3, "purchase_completed", 11, pedido_id=pago[0])
    emitir("checkout", 1, "product_view", 20, produto_id=1)
    emitir("checkout", 2, "add_to_cart", 50, produto_id=1)
    emitir("checkout", 3, "checkout_started", 60)
    emitir("checkout", 4, "purchase_completed", 70, pedido_id=2_000_000_000)
    emitir("checkout", 6, "purchase_completed", 1820, pedido_id=outro_pago[0])
    emitir("compra", 1, "product_view", 599, produto_id=1)
    emitir("compra", 2, "add_to_cart", 601, produto_id=1)
    emitir("compra", 3, "checkout_started", 602)
    emitir("compra", 4, "purchase_completed", 603, pedido_id=pago[0], cliente_id=pago[1])
    return list(reversed(eventos)) + [eventos[-1], '{"schema_version":1,"event_type":"product_view"}']


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lote", choices=["base", "tardio"], default="base")
    args = parser.parse_args()
    print("\n".join(fixture(lote=args.lote)))
