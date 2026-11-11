"""Seeder determinístico e idempotente para o OLTP da NuvemStore."""
import os, random
from datetime import timedelta
from faker import Faker
import psycopg2

fake = Faker("pt_BR")
Faker.seed(42)
random.seed(42)

DB_URL = os.getenv("DATABASE_URL", "postgresql://nuvemstore:nuvemstore@oltp:5432/nuvemstore")
RESET = os.getenv("SEED_RESET", "true").lower() == "true"
# Volume parametrizável: os caps batch usam o default; o cap 13 (ML) sobe muito maior.
N_CLIENTES = int(os.getenv("SEED_CLIENTES", "250"))
N_PEDIDOS = int(os.getenv("SEED_PEDIDOS", "1200"))
# Injeção de comportamentos suspeitos (ligada só no cap 13). NÃO rotula fraude:
# gera o comportamento; a confirmação (chargeback) viria com atraso, em processo à parte.
FRAUDE = os.getenv("SEED_FRAUDE", "false").lower() == "true"

CATEGORIAS = ["Eletrônicos", "Roupas", "Alimentos", "Livros", "Casa e Jardim",
              "Esportes", "Brinquedos", "Saúde"]
VEICULOS = ["moto", "van", "bicicleta"]
METODOS = ["pix", "cartao_credito", "cartao_debito", "boleto"]

def main():
    conn = psycopg2.connect(DB_URL)
    conn.autocommit = False
    cur = conn.cursor()

    if RESET:
        cur.execute("""
            TRUNCATE entrega, pagamento, item_pedido, pedido,
                     produto, categoria, entregador, cliente
            RESTART IDENTITY CASCADE
        """)

    # Categorias
    categorias = []
    for cat in CATEGORIAS:
        cur.execute("INSERT INTO categoria (nome) VALUES (%s) ON CONFLICT DO NOTHING", (cat,))
        cur.execute("SELECT categoria_id FROM categoria WHERE nome = %s", (cat,))
        categorias.append(cur.fetchone()[0])

    # Produtos (~10 por categoria)
    produtos_cadastrados = []
    for cat_id in categorias:
        for _ in range(10):
            cur.execute(
                "INSERT INTO produto (nome, preco, categoria_id) VALUES (%s, %s, %s) RETURNING produto_id",
                (fake.word().capitalize() + " " + fake.word(), round(random.uniform(10, 500), 2), cat_id),
            )
            produtos_cadastrados.append(cur.fetchone()[0])

    # Clientes
    clientes = []
    for _ in range(N_CLIENTES):
        cur.execute(
            "INSERT INTO cliente (nome, cidade, email) VALUES (%s, %s, %s) RETURNING cliente_id",
            (fake.name(), fake.city(), fake.unique.email()),
        )
        clientes.append(cur.fetchone()[0])

    # Entregadores
    entregadores = []
    for _ in range(30):
        cur.execute(
            "INSERT INTO entregador (nome, veiculo) VALUES (%s, %s) RETURNING entregador_id",
            (fake.name(), random.choice(VEICULOS)),
        )
        entregadores.append(cur.fetchone()[0])

    # Pedidos + itens + pagamento + entrega
    for _ in range(N_PEDIDOS):
        status = random.choices(["pago", "cancelado", "pendente"], weights=[70, 15, 15])[0]
        cliente_id = random.choice(clientes)
        data_pedido = fake.date_time_between(start_date="-90d", end_date="now")

        # Comportamento suspeito (só com SEED_FRAUDE=true): ~2% dos pedidos.
        # Repare: marcamos só o COMPORTAMENTO; o status segue o fluxo normal.
        # Nenhuma coluna diz "fraude" — isso é proposital (sem label leakage).
        suspeito = FRAUDE and random.random() < 0.02

        cur.execute(
            "INSERT INTO pedido (cliente_id, data_pedido, status) VALUES (%s, %s, %s) RETURNING pedido_id",
            (cliente_id, data_pedido, status),
        )
        pedido_id = cur.fetchone()[0]

        # Itens (1-5 por pedido). Pedido suspeito tem ticket muito acima do normal.
        n_itens = random.randint(1, 5)
        produtos = random.sample(produtos_cadastrados, n_itens)
        preco_max = 5000 if suspeito else 500
        total = 0
        for prod_id in produtos:
            qtd = random.randint(1, 3)
            preco = round(random.uniform(10, preco_max), 2)
            cur.execute(
                "INSERT INTO item_pedido (pedido_id, produto_id, quantidade, preco_unitario) VALUES (%s,%s,%s,%s)",
                (pedido_id, prod_id, qtd, preco),
            )
            total += qtd * preco

        # Rajada: o pedido suspeito gera 2-3 pagamentos do mesmo cliente em minutos
        # (velocidade anormal). Eles entram como pagamentos extras logo abaixo.
        rajada = random.randint(2, 3) if suspeito else 1

        # Pagamento(s). Em pedido suspeito, várias tentativas em minutos (rajada).
        pag_status = "recusado" if status == "cancelado" else ("pago" if status == "pago" else "pendente")
        for i in range(rajada):
            cur.execute(
                "INSERT INTO pagamento (pedido_id, valor, metodo, status, data_pagamento) VALUES (%s,%s,%s,%s,%s)",
                (pedido_id, round(total, 2), random.choice(METODOS), pag_status,
                 data_pedido + timedelta(minutes=i)),
            )

        # Entrega (só para pagos)
        if status == "pago":
            ent_status = random.choices(["entregue", "em_transito"], weights=[80, 20])[0]
            cur.execute(
                "INSERT INTO entrega (pedido_id, entregador_id, status, data_saida, data_entrega) VALUES (%s,%s,%s,%s,%s)",
                (pedido_id, random.choice(entregadores), ent_status, data_pedido,
                 data_pedido if ent_status == "entregue" else None),
            )

    conn.commit()
    cur.execute("SELECT COUNT(*) FROM cliente")
    n_cli = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM pedido")
    n_ped = cur.fetchone()[0]
    print(f"Seed concluído: {n_cli} clientes, {n_ped} pedidos.")
    conn.close()

if __name__ == "__main__":
    main()
