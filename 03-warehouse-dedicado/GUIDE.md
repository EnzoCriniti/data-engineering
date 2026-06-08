# Cap. 03 — Warehouse dedicado: separação física OLTP/OLAP

> **Aula deste capítulo.** Você aprende por que separar OLTP e OLAP em bancos distintos e como construir o **primeiro pipeline de carga** do portfólio. A orientação está aqui; o código do `migrate.py` e o DDL estão no **[SOLUTION.md](./SOLUTION.md)**; os internals (tuning de read replica, `work_mem`, plano de execução de JOIN) estão no **[TECHNICAL.md](./TECHNICAL.md)**.

## O problema que este capítulo resolve

No capítulo 02, OLTP e analytics dividem o mesmo Postgres. Isso funciona com pouco volume, mas qualquer query analítica pesada pode degradar o checkout. Este capítulo separa fisicamente: dois Postgres em containers distintos, com volumes, conexões e configurações independentes.

Além da separação, este capítulo implementa o **primeiro pipeline de carga** do portfolio: um job Python que lê da origem (OLTP), resolve surrogate keys, e popula o warehouse dimensional com idempotência total.

## Pré-requisitos

- **Capítulo anterior:** 02 concluído (star schema desenhado e entendido).
- **Docker:** versão 24+ com Docker Compose.

## Conceitos fundamentais

### Separação física vs lógica

Separação lógica (schemas) organiza objetos. Separação física (containers) isola recursos. Com dois Postgres:
- Cada um tem seu pool de conexões, CPU share, memória e volume de disco.
- Backup e VACUUM rodam independentemente.
- Um pode escalar sem afetar o outro.
- Analytics pode ter configuração otimizada para reads (mais `shared_buffers`, `work_mem` maior).

### Surrogate key resolution

O warehouse gera seus próprios surrogates via IDENTITY. O job de carga faz `INSERT INTO dim_cliente (...) SELECT ... FROM oltp.cliente` e depois usa `JOIN` para resolver FKs na fato: ao invés de inserir `cliente_id` na fato, insere o `sk_cliente` correspondente.

Isso pode ser feito em SQL puro: `INSERT INTO fct_vendas SELECT dc.sk_cliente, ... FROM oltp.item_pedido ip JOIN dim_cliente dc ON dc.cliente_id = ip.cliente_id WHERE dc.atual = true`.

**Exemplo trabalhado — o que "resolver surrogate" faz, linha a linha.** A origem tem o item:

```text
oltp.item_pedido:  pedido_id=500, cliente_id=C-7, produto_id=P-3, qtd=2, valor=140
```

A fato **não** pode guardar `C-7` e `P-3` (chaves da origem) — ela guarda os surrogates do warehouse. O `JOIN` faz a tradução: encontra em `dim_cliente` a linha *atual* de `C-7` (digamos `sk_cliente=102`) e em `dim_produto` a de `P-3` (`sk_produto=55`), e grava:

```text
fct_vendas:  sk_cliente=102, sk_produto=55, sk_tempo=..., quantidade=2, valor_total=140
```

Por que em SQL e não em Python? Resolver no Python seria um loop que, para cada item, busca o surrogate num dicionário — O(N) chamadas. O `INSERT...SELECT...JOIN` deixa o banco fazer tudo de uma vez, usando índice, num passe só. Para milhares de linhas a diferença é de minutos para segundos.

### Full reload vs incremental

Full reload trunca e recarrega tudo a cada execução. Incremental processa apenas dados novos (por watermark de data ou change flag).

Para o volume deste capítulo (~1200 pedidos), full reload é a escolha correta — simples, idempotente e rápido. Incremental adiciona complexidade (detectar mudanças, tratar deletes, manter watermark) que não se justifica ainda.

### Reconciliação

Após carregar, verificar que os dados batam: `COUNT(*)` de dim_cliente = COUNT de clientes na origem. `SUM(valor_total)` na fato = SUM na origem (excluindo cancelados). Se não bater, o pipeline tem bug.

### Docker Compose profiles

Profiles (`--profile jobs`) permitem que serviços como seeder e migrate não subam com `docker compose up -d` normal. Eles só rodam quando explicitamente chamados.

---

## Etapa 1 — Criar o docker-compose.yml com dois Postgres

### Contexto
Dois bancos separados: `oltp` (porta 5435) montando schema do cap 00, e `warehouse` (porta 5436) montando schema dimensional próprio. Ambos com healthcheck. Seeder e migrate no perfil `jobs`.

### Decisões de design
- *Portas diferentes*: evita conflito com Postgres local ou de outros capítulos.
- *Healthcheck com `pg_isready`*: `depends_on: condition: service_healthy` garante que o migrate só roda quando ambos os bancos estão prontos.
- *`.env.example`*: com `OLTP_URL` e `WAREHOUSE_URL` como defaults. O compose usa interpolação de variáveis.

### O que fazer
Escrever `docker-compose.yml` com: serviço `oltp` (monta schema.sql do cap 00), serviço `warehouse` (monta `warehouse/schema.sql`), serviço `seeder` (perfil jobs, depends_on oltp), serviço `migrate` (perfil jobs, depends_on oltp+warehouse).

### ⚠️ Armadilhas
- `depends_on` sem `condition: service_healthy` faz o migrate iniciar antes do Postgres aceitar conexões — o job falha com "connection refused".
- Usar a mesma porta para ambos os Postgres causa bind error.

---

## Etapa 2 — Criar o schema do warehouse (`warehouse/schema.sql`)

### Contexto
O schema analytics agora vive em seu próprio banco. As tabelas são as mesmas do capítulo 02 mas com ajustes: natural keys mantidas para rastreabilidade, chaves naturais para reconciliação.

### O que fazer
`CREATE SCHEMA IF NOT EXISTS analytics` com dim_tempo, dim_cliente (SCD2), dim_produto, fct_vendas. Mesma estrutura do cap 02, mas aqui o warehouse é dono soberano dessas tabelas.

---

## Etapa 3 — Implementar o job de migração (`warehouse/migrate.py`)

### Contexto
Este é o primeiro pipeline de dados real do portfolio. Conecta na origem, lê dimensões e fato, resolve surrogates, e carrega no warehouse.

### Decisões de design
- *Ordem de carga*: dimensões primeiro (dim_tempo → dim_cliente → dim_produto), fato por último (precisa dos surrogates).
- *TRUNCATE RESTART IDENTITY CASCADE*: idempotência — cada execução reconstrói tudo do zero.
- *Surrogate resolution em SQL*: `INSERT INTO fct_vendas SELECT dc.sk_cliente, dp.sk_produto, dt.sk_tempo ... FROM oltp JOIN dim_cliente dc ON ...`. Mais eficiente que resolver em Python.
- *Filtro de negócio*: pedidos cancelados excluídos da fato. Isso é uma regra de negócio do warehouse, não um bug.
- *Reconciliação*: após carga, compara counts e soma de receita entre origem e destino.
- *`execute_values`*: batch insert do psycopg2.extras para performance.

### O que fazer
Script Python que: conecta em ambos os bancos, trunca warehouse, insere dim_tempo (datas distintas dos pedidos), insere dim_cliente (versão SCD2 simples — snapshot atual), insere dim_produto (com categoria denormalizada), insere fct_vendas (com resolution de surrogates via JOIN), executa reconciliação.

### ⚠️ Armadilhas
- Esquecer `RESTART IDENTITY` no TRUNCATE: surrogate keys continuam crescendo entre execuções, dificultando testes de idempotência.
- Resolver surrogates em Python (loop com dict lookup) é O(N×M). Resolver em SQL (INSERT...SELECT...JOIN) é O(N log M) e muito mais rápido.
- Não fechar cursores/conexões pode esgotar o pool de conexões do Postgres em reexecuções rápidas.

### 📚 Para se aprofundar
- [psycopg2 execute_values](https://www.psycopg.org/docs/extras.html#psycopg2.extras.execute_values) — batch insert performático.
- [PostgreSQL TRUNCATE](https://www.postgresql.org/docs/current/sql-truncate.html) — semântica de RESTART IDENTITY e CASCADE.

---

## Etapa 4 — Dockerizar o migrate e criar .env.example

### O que fazer
- `warehouse/requirements.txt`: `psycopg2-binary==2.9.9`
- `warehouse/