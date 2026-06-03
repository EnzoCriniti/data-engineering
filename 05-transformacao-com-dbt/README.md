# Capítulo 05 — Transformação com dbt

> **De onde viemos:** no capítulo 04, o ELT batch com Python funcionou, mas o SQL ficou solto — sem testes, sem lineage, sem contratos de dados.

## Cenário de negócio

A NuvemStore cresceu e o time de analytics passou a depender dos relatórios. Um bug silencioso numa transformação pode gerar decisão errada de negócio. A dor agora não é mover dados; é **confiar** nas transformações.

## Por que dbt entra aqui

O capítulo 04 provou que SQL de transformação solto não escala em confiabilidade. O dbt transforma esse SQL num projeto de software versionado:

- modelos com dependências explícitas via `ref()` (lineage automático);
- testes de dados (`not_null`, `unique`, `relationships`, `accepted_values`);
- documentação e grafo de dependências gerados a partir do código;
- materializações (`view`, `table`, `incremental`) escolhidas por modelo;
- camadas claras: `staging` → `intermediate` → `marts`.

> O que fica **deliberadamente de fora**: orquestração (agenda, retries, backfill, dependências entre fontes). Isso é trabalho do Airflow, no cap. 07 — dbt transforma, não orquestra.

## Status desta etapa

**Ambiente/documentação.** O projeto dbt ainda não está implementado; o compose deixa a camada de BI pronta para quando os marts forem materializados. O roteiro completo de implementação está no [BUILD.md](./BUILD.md).

## Arquitetura

![Arquitetura](./diagrams/architecture.png)

> Código do diagrama: [`diagrams/architecture.py`](./diagrams/architecture.py).

## Conceitos

**dbt é T, não EL.** dbt assume que o dado já está no warehouse (carregado pelo ELT do cap. 04) e cuida só da **transformação**. Ele não extrai nem carrega da origem.

**Camadas staging → marts.** `staging` limpa e padroniza o raw (tipos, nomes, deduplicação) numa relação 1:1 com a origem. `marts` aplica regras de negócio e agrega para consumo. Separar as duas evita que regra de negócio se misture com limpeza técnica.

**Testes como contrato.** `not_null`, `unique` e `relationships` viram parte do build: se um teste falha, o `dbt build` falha — o dado ruim não chega ao BI silenciosamente.

**Lineage.** Como as dependências são declaradas via `ref()`, o dbt monta o grafo sozinho: dá para ver o que quebra se uma coluna da origem mudar.

> Aprofundamento técnico (materializações, snapshots/SCD, Jinja) em [`TECHNICAL.md`](./TECHNICAL.md).

## Como executar e como foi construído

- **[RUNBOOK.md](./RUNBOOK.md)** — subir o ambiente base (e, quando implementado, rodar `dbt build`).
- **[BUILD.md](./BUILD.md)** — o roteiro de implementação do projeto dbt e o plano de migração das transformações do cap. 04.

## A dor que sobra

dbt organiza transformações, mas não resolve agenda, retries, backfill e dependências entre múltiplas fontes. Antes disso, surge outra necessidade: a plataforma ainda só conhece o OLTP interno. Essa dor leva ao [capítulo 06](../06-ingestao-api-externa): ingestão batch de uma API externa.
