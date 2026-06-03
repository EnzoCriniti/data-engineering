# Build — Capítulo 05: como construir o projeto dbt

> Guia **avançado e detalhado** de construção. Este capítulo está em status **ambiente base**: o roteiro abaixo é o plano de implementação que você seguirá. Para apenas subir o ambiente atual, use o [RUNBOOK](./RUNBOOK.md).

## Objetivo

Reescrever as transformações manuais do capítulo 04 como um projeto dbt versionado, com camadas, testes e lineage — sem perder equivalência com os marts anteriores.

## Pré-requisitos de conhecimento

- SQL analítico e os marts do [cap. 04](../04-elt-batch-com-python).
- Conceitos dbt: `ref()`, materializações, `schema.yml`, testes (ver [TECHNICAL.md](./TECHNICAL.md)).

## Estado inicial

O estado final do cap. 04: warehouse com camada raw e marts construídos por SQL solto em Python.

## Passo 1 — Inicializar o projeto

- `dbt_project.yml` com nome do projeto, paths de modelos e materializações default por camada (`staging` como view, `marts` como table).
- `profiles.yml` apontando para o warehouse (Postgres a partir deste capítulo, para conexão nativa do Metabase).
- `packages.yml` se for usar `dbt_utils`.

## Passo 2 — Camada staging

Um modelo `stg_*` por tabela de origem, relação 1:1 com o raw:

- renomeia e tipa colunas (o raw veio como VARCHAR no cap. 04);
- deduplica se necessário;
- materializa como `view` (barato, sempre fresco).

## Passo 3 — Camada marts

- `mart_receita_diaria` e `mart_top_produtos` recriados como modelos dbt, usando `ref()` para os staging.
- materializa como `table`.
- regras de negócio (excluir `cancelado`, etc.) vivem aqui, não no staging.

## Passo 4 — Testes (`schema.yml`)

- `unique` + `not_null` nas chaves;
- `relationships` entre fato e dimensões/staging;
- `accepted_values` em colunas de status.

`dbt build` deve falhar se qualquer teste falhar.

## Passo 5 — Migração e equivalência

Plano para não criar história nova do zero:

1. usar os marts do cap. 04 como referência;
2. recriar em dbt (`staging` → `marts`);
3. comparar contagens, receita diária e top produtos manual vs dbt;
4. reduzir o pipeline do cap. 04 a apenas extração/carga;
5. remover o SQL manual duplicado quando os testes dbt passarem.

## Validações (definição de pronto)

- [ ] `dbt build` roda modelos e testes sem falha.
- [ ] `dbt docs generate` produz lineage navegável.
- [ ] Marts dbt batem com os marts manuais do cap. 04.
- [ ] CI roda `dbt parse` sem erro.

## Estado final (gabarito para o próximo capítulo)

Transformações como produto: versionadas, testadas, com lineage. Falta orquestrar e lidar com múltiplas fontes — ganchos para o [cap. 06](../06-ingestao-api-externa) (API externa) e o [cap. 07](../07-orquestracao-com-airflow) (Airflow).
