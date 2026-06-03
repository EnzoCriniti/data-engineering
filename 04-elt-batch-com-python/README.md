# Capítulo 04 — ELT batch com Python

> **De onde viemos:** no capítulo 03 separamos OLTP e warehouse e migramos os dados com um script. Funciona, mas é monolítico. Aqui formalizamos o movimento como um **ELT batch** explícito: extrair, carregar a área raw e transformar em marts.

## Cenário de negócio

O time de negócio da NuvemStore quer relatórios de receita diária e top produtos. Rodar essas consultas direto no OLTP degrada o checkout. A solução, deliberadamente simples, é um pipeline batch em Python: extrair do Postgres, carregar uma área `raw` no DuckDB e transformar com SQL escrito à mão.

A simplicidade é proposital — é ela que vai expor, no próximo capítulo, exatamente o que o dbt resolve.

## Por que esta stack

| Tecnologia | Por que entra | O que fica de fora (e por quê) |
| --- | --- | --- |
| PostgreSQL | Origem transacional, reaproveitada do cap. 00. | — |
| Python + psycopg2 | Extração explícita, sem framework escondendo o trabalho. | dbt ainda não — queremos sentir a dor do SQL solto. |
| DuckDB | Warehouse analítico local, leve, inspecionável, colunar. | Spark/lake — volume aqui não justifica. |
| SQL à mão | Transformação direta nos marts. | Testes/lineage — só no cap. 05. |
| Docker Compose | Sobe o ambiente em etapas visíveis. | Airflow — orquestração só no cap. 07. |

## Arquitetura

O diagrama da arquitetura é gerado por código em [`diagrams/architecture.py`](./diagrams/architecture.py). Rode-o (`pip install -r diagrams/requirements.txt && python diagrams/architecture.py`) para produzir o `architecture.png`.

O fluxo é `OLTP (Postgres) → extração Python → raw (DuckDB) → marts (SQL)`. O DuckDB é gravado em `data/warehouse/nuvemstore.duckdb`.

## Conceitos

**ELT vs ETL.** Aqui fazemos **ELT**: extrai e *carrega* o dado cru primeiro (tabelas `raw_*`), e só então *transforma* dentro do warehouse (marts via SQL). Carregar o raw antes de transformar preserva o dado original e torna o reprocessamento barato — não é preciso voltar à origem para recalcular um mart.

**Área raw como contrato.** As tabelas `raw_*` são um espelho fiel da origem, sem regras de negócio. Toda transformação parte daí. Isso isola "trazer o dado" de "dar sentido ao dado" — duas responsabilidades que, misturadas, viram o emaranhado que o dbt vem resolver.

**Idempotência.** O pipeline recria os marts com `CREATE OR REPLACE` e o seeder usa `RESET`. Reexecutar do começo ao fim leva sempre ao mesmo estado — pré-requisito de qualquer pipeline confiável.

**Marts.** `mart_receita_diaria` e `mart_top_produtos` são tabelas agregadas, prontas para o consumo de BI. O negócio não consulta o raw; consulta o mart.

> Aprofundamento técnico (DuckDB colunar, por que não Spark aqui, ELT vs ETL) em [`TECHNICAL.md`](./TECHNICAL.md).

## Camada de BI

O Metabase sobe separado do fluxo principal, para não esconder as etapas do pipeline. Neste capítulo o warehouse é DuckDB; a conexão ao BI usa o driver community de DuckDB. A partir do cap. 05 a saída analítica passa a ser materializada em Postgres, facilitando a conexão nativa do Metabase. Detalhes no [RUNBOOK](./RUNBOOK.md).

## Como executar e como foi construído

- **[RUNBOOK.md](./RUNBOOK.md)** — subir e usar o pipeline já pronto (comandos, saída esperada, validações).
- **[BUILD.md](./BUILD.md)** — o passo a passo de construção do extractor, dos marts e do empacotamento.

## A dor que sobra

O pipeline funciona, mas o SQL está solto: sem testes, sem lineage, sem contratos de dados. Um erro silencioso numa agregação vira decisão de negócio errada. Essa fragilidade é a motivação do [capítulo 05](../05-transformacao-com-dbt): transformação com dbt.
