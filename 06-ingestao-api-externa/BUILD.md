# Build — Capítulo 06: como construir a ingestão de API externa

> Guia **avançado e detalhado**. Status **ambiente base**: o roteiro abaixo é o plano de implementação. Para subir o ambiente atual, use o [RUNBOOK](./RUNBOOK.md).

## Objetivo

Implementar um extractor batch incremental que consome a API da transportadora, deduplica por chave natural e aterrissa o dado em `staging`, pronto para o dbt cruzar com o pedido interno.

## Pré-requisitos de conhecimento

- HTTP/JSON, paginação e contratos de API.
- Carga incremental e upsert no Postgres.
- Conceitos de retry/backoff (ver [TECHNICAL.md](./TECHNICAL.md)).

## Estado inicial

Estado final do [cap. 05](../05-transformacao-com-dbt): marts internos em dbt. Aqui adicionamos uma fonte externa — não se substitui o dbt.

## Passo 1 — Ambiente (`docker-compose.yml`)

- `api`: serve `api/entregas.json` como uma API HTTP fake.
- `warehouse`: Postgres com schema `staging` (DDL em `extractor/staging.sql`).
- `extractor`: job Python (profile `jobs`), a implementar.

## Passo 2 — Schema de staging (`extractor/staging.sql`)

Tabela `staging.transportadora_entregas` com `entrega_id` como chave natural (UNIQUE), campos de status/previsão/ocorrência e `atualizado_em`. Uma tabela de controle de checkpoint (`staging.ingestao_controle`) guarda o último `atualizado_em` processado.

## Passo 3 — Extractor incremental (`extractor/extractor.py`, a implementar)

- lê o checkpoint (último `atualizado_em`);
- chama a API filtrando por janela `> checkpoint`, paginando se necessário;
- valida o payload (campos obrigatórios, tipos);
- **upsert** em `staging.transportadora_entregas` por `entrega_id` (`ON CONFLICT DO UPDATE`);
- atualiza o checkpoint ao final, dentro da transação.

Tratar: `retry` com backoff para falhas transitórias, e rate limit.

## Passo 4 — Integração com dbt

No dbt, criar `stg_transportadora_entregas` e um modelo que cruza `pedido`/`entrega` interno com o status externo por `pedido_id`, medindo SLA e atraso.

## Validações (definição de pronto)

- [ ] `extractor` carrega a janela sem duplicar (`COUNT = COUNT(DISTINCT entrega_id)`).
- [ ] Reexecutar a mesma janela é idempotente.
- [ ] Checkpoint avança corretamente entre execuções.
- [ ] Payload inválido é rejeitado com erro claro.

## Estado final (gabarito para o próximo capítulo)

Plataforma com OLTP interno, dbt e fonte externa batch em staging. Coordenar tudo manualmente é frágil — gancho para o [Airflow no cap. 07](../07-orquestracao-com-airflow).
