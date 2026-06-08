# Cap. 02 — Dimensional no OLTP: analytics no mesmo banco

> **Aula deste capítulo.** Você aprende *por que* começar analytics no mesmo banco do OLTP é tentador — e por que dói. A orientação de cada arquivo está aqui; o DDL completo está no **[SOLUTION.md](./SOLUTION.md)**; os internals (autovacuum, MVCC, pool de conexões, work_mem) estão no **[TECHNICAL.md](./TECHNICAL.md)**.

## O problema que este capítulo resolve

O star schema foi desenhado no capítulo 01, mas ainda não existe como tabelas reais. A forma mais rápida de materializar é criar um schema `analytics` dentro do mesmo Postgres do OLTP — sem provisionar novo banco, sem pipeline, sem infra adicional.

Esta é uma decisão histórica real: a maioria das empresas começa analytics dentro do banco de produção porque é rápido e barato. O capítulo materializa essa decisão para que o engenheiro **sinta** o problema de contention que ela causa, justificando a separação do capítulo 03.

## Pré-requisitos

- **Capítulo anterior:** 01 concluído (star schema desenhado).
- **Docker:** versão 24+ com Docker Compose.

## Conceitos fundamentais

### Schemas do Postgres como isolamento lógico

O Postgres permite criar múltiplos schemas dentro do mesmo banco. `public` guarda as tabelas OLTP, `analytics` guarda as dimensionais. Isso organiza objetos, mas **não isola recursos**: CPU, memória, conexões, WAL e autovacuum são compartilhados.

### Por que a coexistência OLTP+OLAP é problemática

Queries analíticas fazem table scans e agregações pesadas. Transações OLTP precisam responder em milissegundos. Quando ambas rodam no mesmo processo:
- Autovacuum compete com queries analíticas por I/O
- Conexões analíticas ocupam slots que o checkout precisaria
- Locks de escrita podem bloquear reads longos (e vice-versa com MVCC mal configurado)
- Uma query `GROUP BY` de 5 minutos pode usar toda a memória disponível para sort

**Exemplo trabalhado — a Black Friday que derruba o relatório (e vice-versa).** São 20h de uma promoção. O checkout está fazendo milhares de `INSERT pedido` por minuto. Ao mesmo tempo, um gerente abre o dashboard "receita por categoria no mês", que dispara um `GROUP BY` varrendo a fato inteira. Como os dois rodam no **mesmo Postgres**: a query analítica segura `work_mem` e I/O por minutos → os INSERTs do checkout começam a enfileirar → o tempo de resposta do "Finalizar compra" sobe de 80ms para 4s → clientes abandonam o carrinho. O inverso também ocorre: o autovacuum disparado pela enxurrada de escritas compete por I/O e faz o relatório do gerente travar. **Nenhum dos dois é "a query lenta" — o problema é dividir o mesmo motor.** Sentir isso aqui é o que justifica a separação física do cap 03.

### Multi-init-script no Docker Postgres

O Postgres oficial monta scripts em `/docker-entrypoint-initdb.d/` e os executa em ordem alfabética. Montar `01-schema.sql` e `02-analytics.sql` garante que o OLTP existe antes do analytics.

---

## Etapa 1 — Criar o ambiente com docker-compose.yml

### Contexto
Este é o primeiro ambiente executável do portfolio. O compose sobe um único Postgres que inicializa com dois scripts: o schema OLTP do capítulo 00 e o schema analytics deste capítulo. O seeder do capítulo 00 é reutilizado para popular dados.

### Decisões de design
- *Um único Postgres*: proposital — o objetivo é demonstrar a coexistência e seus problemas.
- *Scripts montados em ordem*: `../00-modelagem-transacional/ddl/schema.sql` como `01-schema.sql` e `./ddl/analytics.sql` como `02-analytics.sql`. A numeração garante ordem.
- *Seeder reutilizado*: build do Dockerfile do capítulo 00, perfil `jobs` para não subir automaticamente.

### O que fazer
Criar `docker-compose.yml` com: serviço `postgres` (porta 5433, healthcheck com `pg_isready`, volumes montando os dois scripts), serviço `seeder` no perfil `jobs` (depends_on postgres healthy).

### ⚠️ Armadilhas
- Montar o volume sem numeração: scripts executam em ordem alfabética — `schema.sql` pode rodar depois de `analytics.sql` se o nome começar com 's'.
- Esquecer `depends_on: condition: service_healthy`: o seeder tenta conectar antes do Postgres aceitar conexões.

---

## Etapa 2 — Criar o schema analytics (`ddl/analytics.sql`)

### Contexto
O star schema do capítulo 01 vira DDL real. Quatro tabelas: `dim_tempo`, `dim_cliente` (com SCD2), `dim_produto`, `fct_vendas`.

### Decisões de design
- *`CREATE SCHEMA IF NOT EXISTS analytics`*: re-executável.
- *Todas as tabelas com `IF NOT EXISTS`*: o script inteiro pode rodar N vezes sem erro.
- *Surrogate keys com IDENTITY*: geradas no warehouse, não importadas da origem.
- *Índices nos FKs da fato*: `idx_fct_vendas_tempo`, `idx_fct_vendas_cliente`, `idx_fct_vendas_produto`. Queries analíticas filtram por dimensão — sem índice, cada query faz seq scan na fato.
- *Tabelas vazias por design*: o load job não é implementado neste capítulo (separação pedagógica — o capítulo 04 trata de carga).

### O que fazer
Escrever `ddl/analytics.sql` com `CREATE SCHEMA IF NOT EXISTS analytics` seguido das 4 tabelas com tipos corretos, FKs entre fato e dimensões, e índices. Manter as tabelas vazias