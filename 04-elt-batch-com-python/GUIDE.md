# Cap. 04 — ELT batch com Python: extrair, carregar raw e transformar em DuckDB

> **Aula deste capítulo.** Você aprende o padrão **ELT** (extrair, carregar raw, transformar no destino) e por que ele substitui o migrate monolítico do cap 03. A orientação está aqui; o código do `pipeline.py` está no **[SOLUTION.md](./SOLUTION.md)**; os internals (armazenamento colunar do DuckDB, vetorização, por que VARCHAR-everything no raw) estão no **[TECHNICAL.md](./TECHNICAL.md)**.

## O problema que este capítulo resolve

O migrate do capítulo 03 mistura extract, transform e load em um único script. Não há separação entre dados brutos e dados transformados — se uma regra de negócio no mart está errada, é preciso re-extrair tudo da origem. Além disso, o warehouse é Postgres, que funciona mas não é otimizado para queries analíticas colunares.

Este capítulo implementa o padrão ELT correto: extrair da origem e carregar como raw (fielmente, sem transformação), depois transformar no destino. O destino passa a ser DuckDB — um motor analítico colunar embarcado que não precisa de servidor.

## Pré-requisitos

- **Capítulo anterior:** 03 concluído.
- **Docker:** versão 24+ com Docker Compose.

## Conceitos fundamentais

### ELT vs ETL

ETL transforma antes de carregar. ELT carrega raw e transforma no destino. ELT é preferível em plataformas modernas porque:
- Raw é preservado: se a regra de negócio muda, basta reprocessar — não é preciso re-extrair.
- O destino analítico (DuckDB, Spark, BigQuery) geralmente transforma mais rápido que scripts Python intermediários.
- Separação de responsabilidades: ingestão e transformação são jobs distintos com donos diferentes.

**Exemplo trabalhado — a regra de negócio que muda.** No cap 03, "receita" excluía pedidos cancelados. Suponha que o negócio agora também queira excluir pedidos de teste (`status='teste'`). Com **ETL** (transforma antes de carregar), o dado já entrou no warehouse filtrado pela regra antiga — para aplicar a nova você precisa **re-extrair tudo da origem**, que pode estar lenta, indisponível, ou já ter mudado. Com **ELT**, o `raw_pedido` guarda *todos* os pedidos como vieram; corrigir a regra é reescrever um `WHERE` no mart e rodar só a fase de transform — segundos, sem tocar a origem. O raw é a sua rede de segurança.

### Raw layer: VARCHAR-everything

Ao carregar raw, declare tudo como VARCHAR. Não faça cast no extract. Motivos:
- Dados da origem podem ter valores inesperados que quebram CAST (ex: string "N/A" em coluna numérica).
- O raw deve ser fiel à origem — é a "fotografia" do dado como veio.
- O CAST pertence à camada de transformação (mart), onde regras de limpeza são explícitas.

**Exemplo trabalhado — o CAST que mata o pipeline.** A origem tem a coluna `peso_kg` e um registro veio com `"N/A"` (um vendedor não preencheu). Se o extract fizer `CAST(peso_kg AS DOUBLE)` na entrada, a linha `"N/A"` derruba o job inteiro — e você perde *todas* as outras linhas boas junto. Carregando como VARCHAR, `"N/A"` entra intacto no `raw_produto`. No mart, você decide conscientemente o que fazer: `TRY_CAST(peso_kg AS DOUBLE)` vira `NULL` para o lixo e preserva o resto. A diferença é onde a falha acontece: no raw, nunca; no mart, de forma controlada e visível.

### DuckDB: quando usar

DuckDB é para analytics o que SQLite é para aplicações: embarcado, sem servidor, arquivo único. Ideal para:
- Volumes até centenas de GB (cabe em uma máquina).
- Desenvolvimento local e prototipação de marts.
- Queries colunares que seriam lentas em Postgres row-oriented.

Não é ideal para: acesso concorrente pesado, workloads transacionais, ou substituir um warehouse distribuído em produção.

### Idempotência: DROP+CREATE vs CREATE OR REPLACE

Para tabelas raw, `DROP TABLE IF EXISTS raw_X; CREATE TABLE raw_X AS ...` garante que cada execução reconstrói do zero. Para marts, `CREATE OR REPLACE TABLE` faz o mesmo em uma operação atômica no DuckDB.

---

## Etapa 1 — Criar o docker-compose.yml

### O que fazer
Serviços: `oltp` (Postgres com schema do cap 00), `seeder` (perfil jobs), `pipeline` (perfil jobs, monta volume local para persistir `.duckdb`). Metabase opcional em perfil `bi`.

### ⚠️ Armadilhas
- Não montar volume para o DuckDB: o arquivo é criado dentro do container e perdido ao remover.

---

## Etapa 2 — Implementar o pipeline (`pipeline/pipeline.py`)

### Contexto
O pipeline faz três coisas em sequência: Extract (Postgres → Python), Load (Python → DuckDB raw), Transform (SQL no DuckDB → marts).

### Decisões de design
- *Extract com `cursor.description`*: lê nomes de colunas dinamicamente. Não hardcoda colunas — se a origem adicionar uma coluna, o extract captura automaticamente.
- *Raw com VARCHAR*: `CREATE TABLE raw_cliente (cliente_id VARCHAR, nome VARCHAR, ...)`. Typing fica nos marts.
- *Normalização de Decimal*: `psycopg2` retorna `decimal.Decimal` para NUMERIC. DuckDB não aceita Decimal em `executemany`. Converter para `float` antes de inserir.
- *DROP+CREATE por tabela raw*: idempotente por definição.
- *Marts com CREATE OR REPLACE*:
  - `mart_receita_diaria`: receita e contagem de pedidos por dia, excluindo cancelados, com CAST de VARCHAR para tipos corretos.
  - `mart_top_produtos`: top 20 produtos por receita, com JOIN raw_item_pedido → raw_produto → raw_categoria.

### O que fazer
Script Python com três fases separadas por logs claros. Extract: itera tabelas da origem com `SELECT *`, captura column names via `cursor.description`. Load: para cada tabela, `DROP TABLE IF EXISTS raw_X`, `CREATE TABLE raw_X` com todas colunas VARCHAR, `executemany` para inserir. Transform: executa SQL de cada mart.

### ⚠️ Armadilhas
- `executemany` do DuckDB espera listas de tuplas, não listas de listas. `cursor.fetchall()` retorna tuplas — ok.
- Esquecer de converter Decimal: `duckdb.InvalidInputException: Could not convert`.
- Não fechar conexão do DuckDB: arquivo pode ficar locked para queries subsequentes.

### 📚 Para se aprofundar
- [DuckDB Python API](https://duckdb.org/docs/api/python/overview) — como usar DuckDB em Python.
- [cursor.description (PEP 249)](https://peps.python.org/pep-0249/#description) — metadados de colunas em DB-API.

---

## Etapa 3 — Containerizar o pipeline

### O que fazer
- `pipeline/requirements.txt`: `psycopg2-binary==2.9.9`, `duckdb==1.1.0`
- `pipeline/Dockerfile`: `python:3.12-slim`, copy requirements first, install, copy code, CMD.

---

## ✅ Checklist final

- [ ] Pipeline roda do zero e gera `.duckdb`
- [ ] Todos os `raw_*` têm count = count da origem
- [ ] `mart_receita_diaria` exclui pedidos cancelados
- [ ] Receita total do mart = receita de não-cancelados na origem
- [ ] Rodar pipeline duas vezes produz mesmo resultado (idempotência)
- [ ] `python -m py_compile pipeline/pipeline.py` passa

Compreensão (você entendeu — responda sem olhar):

- [ ] Conte o cenário da regra de negócio que muda: o que ETL obriga a refazer e o que ELT poupa?
- [ ] Por que carregar tudo como VARCHAR no raw? Dê um exemplo de valor da origem que quebraria um CAST no extract.
- [ ] Em que situações DuckDB é a escolha certa — e em quais ele **não** é?
- [ ] Por que `psycopg2` exige converter `Decimal` para `float` antes de inserir no DuckDB?

## A dor que sobra

Transformações são SQL solto em strings Python. Não há lineage (de onde veio cada coluna?), não há testes (o mart está correto?), não há documentação automática. Qualquer mudança no schema upstream quebra silenciosamente. O capítulo 05 resolve isso com dbt.
