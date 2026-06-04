# Capítulo 03 — Warehouse dedicado

> **De onde viemos:** no capítulo 02, o modelo dimensional ficou em outro schema, mas ainda dentro do mesmo Postgres da aplicação. A separação era lógica, não operacional — analytics e checkout continuavam disputando o mesmo banco.

## Cenário de negócio

As consultas analíticas da NuvemStore cresceram. Relatórios de receita, produto e cliente passaram a competir com o checkout e com as escritas transacionais: uma consulta pesada de BI segurava o banco no horário de pico de vendas. A resposta é separar **fisicamente** as bases.

```text
oltp       ->  Postgres da aplicação (escrita transacional)
warehouse  ->  Postgres dedicado a analytics (leitura pesada)
```

Mesmo usando Postgres dos dois lados, a arquitetura muda de natureza: analytics deixa de competir com o banco de produção, e a carga entre os dois vira um processo explícito e auditável.

## Arquitetura

Dois bancos independentes e um job de carga que materializa o modelo dimensional do capítulo 01 no warehouse:

- `oltp` — origem transacional, com o schema do capítulo 00.
- `warehouse` — base analítica dedicada, com o star schema (`analytics.dim_*` e `analytics.fct_vendas`).
- `seeder` — job que popula a origem (reaproveitado do capítulo 00).
- `migrate` — job que lê do OLTP e carrega dimensões e fato no warehouse, resolvendo chaves naturais em surrogate keys.

## Conceitos

**Por que separar fisicamente, e não só por schema.** Isolamento lógico (schemas) divide a organização do dado, mas não os recursos: CPU, memória, cache e I/O continuam compartilhados. Sob carga analítica pesada, o banco transacional sofre. Separar em instâncias distintas dá **isolamento de recursos** — o pior relatório do mundo não derruba o checkout.

**Carga como processo explícito.** Mover dado do OLTP para o warehouse deixa de ser um `SELECT` ad hoc e vira um job versionado, idempotente e validável. Isso é o embrião de um pipeline.

**Surrogate keys na prática.** A `fct_vendas` não referencia `produto_id` da origem diretamente; referencia `sk_produto`, gerada no warehouse. A carga resolve cada chave natural na surrogate correspondente via JOIN com as dimensões já carregadas. Esse desacoplamento é o que, mais adiante, viabiliza SCD Tipo 2 e protege o warehouse de mudanças na origem.

**Reconciliação.** Toda migração precisa de uma prova de equivalência. Aqui, a receita total em `fct_vendas` deve bater com a receita de itens não cancelados no OLTP. Sem essa checagem, uma migração silenciosamente errada vira decisão de negócio errada.

## Como executar

Este README descreve o *porquê*. Para subir e usar o ambiente — comandos, saída esperada e validações — veja o **[RUNBOOK.md](./RUNBOOK.md)**.

## A dor que sobra

Agora existe isolamento físico, mas a carga e a transformação ainda são simples demais: um único script, sem testes, sem lineage, sem modularidade. Conforme as regras de negócio se acumulam no SQL, isso vira um emaranhado frágil. Essa dor leva ao [capítulo 04](../04-elt-batch-com-python) (ELT batch com Python) e, em seguida, ao [dbt no capítulo 05](../05-transformacao-com-dbt).
