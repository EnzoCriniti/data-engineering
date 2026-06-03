# Capítulo 02 — Dimensional dentro do mesmo banco OLTP 🟢

> **De onde viemos:** no [capítulo 01](../01-modelagem-dimensional) desenhamos o star schema. Historicamente, muitas empresas começaram materializando esse modelo numa outra área do próprio banco transacional — por exemplo, num schema `analytics`. É a primeira materialização do desenho, e é de propósito ingênua.

## Cenário de negócio

A NuvemStore ainda é pequena. Para ganhar velocidade, o time cria as tabelas analíticas dentro do mesmo PostgreSQL que atende o sistema transacional. Parece barato: não precisa de outro servidor, outro banco, outro backup nem outra operação. É um passo realista — muitas plataformas começam exatamente assim.

## O que esta etapa mostra

O mesmo Postgres passa a ter duas áreas (schemas) lado a lado:

```text
public      -> tabelas OLTP: cliente, pedido, item_pedido, pagamento, ...
analytics   -> tabelas OLAP: dim_tempo, dim_cliente, dim_produto, fct_vendas
```

Isso aproxima o analytics do dado de origem — estão no mesmo banco, sem rede no meio — mas também coloca, sob o mesmo motor, duas cargas de perfis opostos:

- **OLTP:** escritas pequenas, baixa latência, alta concorrência.
- **OLAP:** leituras grandes, com joins, agregações e scans de tabela inteira.

## Por que isso vira problema

O banco transacional passa a dividir CPU, memória, I/O, locks, conexões e janelas de manutenção com as consultas analíticas. Mesmo com o schema separado, os **recursos físicos continuam compartilhados**.

Uma query de "receita por categoria" pode competir com o checkout. Um `VACUUM`, uma carga pesada ou a construção de um índice podem afetar os dois mundos ao mesmo tempo. A lição central do capítulo: **separação lógica (schema) não é separação operacional (recursos)**.

## Conceitos

**Schema como namespace.** Um schema do Postgres agrupa tabelas sob um mesmo banco. Separar `public` de `analytics` organiza e dá clareza de propósito, mas não cria fronteira de CPU, memória ou I/O.

**Materialização.** Aqui o star schema deixa de ser desenho e vira tabela real (DDL em [`ddl/analytics.sql`](./ddl/analytics.sql)). As dimensões e a fato existem fisicamente; ainda não há um job de carga que as preencha — esse é o salto do [cap. 03](../03-warehouse-dedicado).

**Contenção de recursos.** O conceito que motiva o resto da trilha: quando OLTP e OLAP compartilham o mesmo motor, picos de um degradam o outro. É o argumento para o warehouse dedicado.

## Como executar e como foi construído

- **[RUNBOOK.md](./RUNBOOK.md)** — subir o ambiente (um Postgres com os dois schemas) e popular a origem com um comando pronto.
- **[BUILD.md](./BUILD.md)** — como o ambiente foi montado: o DDL do `analytics`, a reutilização do schema e do seeder do cap. 00 e o porquê de ainda não haver carga aqui.

> Aprofundamento técnico em [`TECHNICAL.md`](./TECHNICAL.md).

## A dor que sobra

Separar schemas ajudou a organizar, mas não isolou recursos. O próximo passo é separar **fisicamente** as bases: um Postgres para a origem transacional e outro para o warehouse. → [Capítulo 03: warehouse dedicado](../03-warehouse-dedicado).
