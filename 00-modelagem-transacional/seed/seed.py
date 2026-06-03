import os
import random
from datetime import datetime, timedelta
from decimal import Decimal

import psycopg2
from faker import Faker


DATABASE_URL = os.environ["DATABASE_URL"]
SEED_CUSTOMERS = int(os.getenv("SEED_CUSTOMERS", "250"))
SEED_ORDERS = int(os.getenv("SEED_ORDERS", "1200"))
SEED_RESET = os.getenv("SEED_RESET", "true").lower() in {"1", "true", "yes", "sim"}

fake = Faker("pt_BR")
Faker.seed(42)
random.seed(42)


def execute_many(cursor, statement, rows):
    cursor.executemany(statement, rows)


def reset_database(cursor):
    cursor.execute(
        """
        TRUNCATE TABLE
            entrega,
            entregador,
            pagamento,
            item_pedido,
            pedido,
            produto,
            categoria,
            cliente
        RESTART IDENTITY CASCADE
        """
    )


def main():
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor() as cursor:
            if SEED_RESET:
                reset_database(cursor)

            categorias = [
                "Eletronicos",
                "Casa",
                "Moda",
                "Beleza",
                "Esporte",
                "Livros",
                "Mercado",
            ]
            execute_many(cursor, "INSERT INTO categoria (nome) VALUES (%s)", [(c,) for c in categorias])

            produtos = []
            for categoria_id, categoria in enumerate(categorias, start=1):
                for indice in range(1, 9):
                    nome = f"{categoria} Produto {indice}"
                    preco = Decimal(str(round(random.uniform(19.9, 799.9), 2)))
                    produtos.append((categoria_id, nome, preco))
            execute_many(
                cursor,
                "INSERT INTO produto (categoria_id, nome, preco) VALUES (%s, %s, %s)",
                produtos,
            )

            clientes = []
            for _ in range(SEED_CUSTOMERS):
                clientes.append(
                    (
                        fake.name(),
                        fake.unique.email(),
                        fake.city(),
                        fake.date_between(start_date="-2y", end_date="-30d"),
                    )
                )
            execute_many(
                cursor,
                "INSERT INTO cliente (nome, email, cidade, criado_em) VALUES (%s, %s, %s, %s)",
                clientes,
            )

            entregadores = [(fake.name(), random.choice(["Norte", "Sul", "Leste", "Oeste", "Centro"])) for _ in range(30)]
            execute_many(cursor, "INSERT INTO entregador (nome, regiao) VALUES (%s, %s)", entregadores)

            cursor.execute("SELECT id, preco FROM produto")
            produtos_ref = cursor.fetchall()

            pedidos = []
            for _ in range(SEED_ORDERS):
                data_pedido = datetime.now() - timedelta(days=random.randint(0, 120), hours=random.randint(0, 23))
                pedidos.append(
                    (
                        random.randint(1, SEED_CUSTOMERS),
                        data_pedido,
                        random.choices(
                            ["criado", "pago", "enviado", "entregue", "cancelado"],
                            weights=[4, 18, 16, 55, 7],
                        )[0],
                    )
                )
            execute_many(cursor, "INSERT INTO pedido (cliente_id, data_pedido, status) VALUES (%s, %s, %s)", pedidos)

            itens = []
            pagamentos = []
            entregas = []
            for pedido_id, (_, data_pedido, status) in enumerate(pedidos, start=1):
                total = Decimal("0")
                for produto_id, preco in random.sample(produtos_ref, random.randint(1, 4)):
                    quantidade = random.randint(1, 3)
                    total += preco * quantidade
                    itens.append((pedido_id, produto_id, quantidade, preco))

                pagamento_status = "aprovado" if status in {"pago", "enviado", "entregue"} else random.choice(["pendente", "recusado"])
                pagamentos.append((pedido_id, random.choice(["cartao_credito", "pix", "boleto"]), pagamento_status, total, data_pedido + timedelta(minutes=5)))

                if status in {"enviado", "entregue"}:
                    entrega_status = "entregue" if status == "entregue" else "em_rota"
                    entregas.append((pedido_id, random.randint(1, 30), entrega_status, data_pedido + timedelta(hours=8)))

            execute_many(
                cursor,
                "INSERT INTO item_pedido (pedido_id, produto_id, quantidade, preco_unitario) VALUES (%s, %s, %s, %s)",
                itens,
            )
            execute_many(
                cursor,
                "INSERT INTO pagamento (pedido_id, metodo, status, valor, atualizado_em) VALUES (%s, %s, %s, %s, %s)",
                pagamentos,
            )
            execute_many(
                cursor,
                "INSERT INTO entrega (pedido_id, entregador_id, status, despachado_em) VALUES (%s, %s, %s, %s)",
                entregas,
            )

    print(f"Seed concluido: {SEED_CUSTOMERS} clientes, {SEED_ORDERS} pedidos.")


if __name__ == "__main__":
    main()
