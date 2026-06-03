# Build — Capítulo 03: como construir o warehouse dedicado

> Guia **avançado e detalhado** de construção. Passo a passo de implementação, com as decisões por trás de cada parte. Para apenas executar o que já está pronto, use o [RUNBOOK](./RUNBOOK.md).

## Objetivo

Separar fisicamente OLTP e analytics em dois bancos distintos e implementar um job de carga que materializa o modelo dimensional (cap 01) no warehouse, resolvendo chaves naturais em surrogate keys.

## Pré-requisitos de conhecimento

- Modelo dimensional: fato, dimensão, grão, surrogate keys (ver [cap 01](../01-modelagem-dimensional)).
- SQL de carga (INSERT ... SELECT, JOIN para lookup de chaves).
- Docker Compose com múltiplos serviços, healthchecks e profiles.

## Estado inicial

O estado final do [cap 02](../02-dimensional-no-oltp): origem OLTP modelada e populável, com analytics convivendo no mesmo banco. Aqui damos o próximo passo — isolamento físico.

## Passo 1 — Definir a topologia de dois bancos (`docker-compose.yml`)

Suba dois serviços Postgres independentes:

- `oltp`: monta o `schema.sql` do cap 00 via `docker-entrypoint-initdb.d`. Porta host `5435`.
- `warehouse`: monta `warehouse/schema.sql` (dimensional). Porta host `5436`.

Pontos de implementação:

- **Healthchecks** com `pg_isready` em ambos, para que os jobs só rodem quando os bancos estiverem prontos.
- **Profiles `jobs`** nos serviços `seeder` e `migrate`: eles não sobem com `up -d`; só rodam sob demanda com `run --rm`. Isso separa "ambiente" de "tarefa".
- **Reaproveitamento**: o `seeder` aponta para o contexto de build do cap 00 (`../00-modelagem-transacional/seed`). A origem do dado é sempre a mesma — não se duplica o seeder.
- **Configuração por `.env`**: portas, nomes de banco, usuários e senhas vêm de variáveis com defaults.

## Passo 2 — Escrever o schema dimensional (`warehouse/schema.sql`)

Crie o schema `analytics` com o star schema:

- `dim_cliente`, `dim_produto`, `dim_tempo`: cada uma com **surrogate key** própria (`sk_*` gerada por identidade) além da chave natural da origem (`cliente_id`, `produto_id`).
- `fct_vendas`: grão = um item de pedido. Guarda as métricas (`quantidade`, `valor_total`) e as FKs para as surrogate keys das dimensões, além das chaves naturais de rastreio (`pedido_id`, `item_pedido_id`).

A surrogate key desacopla o warehouse da origem e é o que viabilizaria o SCD Tipo 2 na `dim_cliente` mais adiante.

## Passo 3 — Implementar o job de migração (`warehouse/migrate.py`)

O job conecta às duas pontas (`OLTP_URL`, `WAREHOUSE_URL`) e carrega na ordem dimensões → fato. Decisões:

- **Idempotência**: começa com `TRUNCATE ... RESTART IDENTITY CASCADE` nas tabelas analíticas. Reexecutar produz o mesmo resultado, sem duplicar.
- **Ordem importa**: dimensões primeiro (geram as surrogate keys), fato por último (precisa resolver os lookups).
- **Resolução de chaves no banco**: a `fct_vendas` é populada com um `INSERT ... SELECT FROM (VALUES %s) JOIN dim_*`. Em vez de resolver as surrogate keys no Python, monta-se uma tabela de valores e deixa o Postgres fazer os JOINs com as dimensões já carregadas — mais simples e correto.
- **Filtro de negócio**: pedidos `cancelado` ficam fora do fato (não são receita realizada).
- **Carga em lote**: `execute_values` para inserir milhares de linhas eficientemente.
- **dim_tempo derivada**: dia, mês, trimestre e ano calculados a partir das datas distintas dos pedidos.

## Passo 4 — Empacotar o job (`warehouse/Dockerfile`)

Imagem `python:3.12-slim`, instala `psycopg2-binary` e roda `migrate.py`. Vira o serviço `migrate` (profile `jobs`) no compose.

## Validações (definição de pronto)

- [ ] `docker compose up -d oltp warehouse` sobe ambos com healthcheck saudável.
- [ ] `seeder` popula a origem; `migrate` carrega o warehouse sem erro.
- [ ] **Reconciliação**: receita total em `fct_vendas` = receita de itens não cancelados no OLTP (ver RUNBOOK, passo 4).
- [ ] Rodar `migrate` duas vezes seguidas não muda as contagens (idempotência).
- [ ] Contagem de `dim_cliente` = contagem de `cliente` na origem.

## Estado final (gabarito para o próximo capítulo)

Dois bancos separados, warehouse populado a partir do OLTP com modelo dimensional materializado e validado por reconciliação. A carga, porém, é um script monolítico sem testes nem lineage — o gancho para o ELT batch do [cap 04](../04-elt-batch-com-python) e a reescrita em dbt no [cap 05](../05-transformacao-com-dbt).
