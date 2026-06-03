# Capitulo 05 - Transformacao com dbt

> De onde viemos: no capitulo 04, o ELT batch com Python funcionou, mas o SQL ficou solto, sem testes, sem lineage e sem contratos de dados.

## Cenario de negocio

A NuvemStore cresceu e o time de analytics passou a depender dos relatorios. Um bug silencioso em uma transformacao pode gerar decisao errada de negocio. A dor agora nao e apenas mover dados; e confiar nas transformacoes.

## Por que dbt entra aqui

dbt transforma SQL em um projeto versionado:

- modelos com dependencias explicitas via `ref()`;
- testes de dados como `not_null`, `unique` e `relationships`;
- documentacao e lineage;
- materializacoes como `view`, `table` e `incremental`;
- separacao entre staging, intermediate e marts.

## Status desta etapa

Status atual: **ambiente/documentacao**.

Este capitulo ainda nao tem o projeto dbt implementado. O README tecnico explica o papel da tecnologia e o compose atual deixa a camada de BI pronta para quando os marts forem materializados.

Quando a integracao for implementada, esta etapa deve receber:

- `dbt_project.yml`;
- modelos `staging` e `marts`;
- `schema.yml` com testes;
- profiles para conectar no warehouse;
- comandos `dbt run`, `dbt test` e `dbt docs generate` validados.

## Como esta etapa migra a anterior

dbt nao deve criar uma historia nova do zero. Ele deve substituir, com mais controle, as transformacoes manuais do capitulo 04.

Plano de migracao:

1. usar as tabelas raw/marts geradas pelo ELT batch com Python como referencia;
2. recriar os marts em modelos dbt (`staging` -> `marts`);
3. comparar contagens, receita diaria e top produtos entre a versao manual e a versao dbt;
4. manter o ELT batch com Python apenas como extracao/carga, reduzindo a responsabilidade dele sobre transformacao;
5. remover SQL manual duplicado quando os testes dbt estiverem passando.

## Arquitetura

![Arquitetura](./diagrams/architecture.png)

Codigo do diagrama: [`diagrams/architecture.py`](./diagrams/architecture.py).

## Como subir o ambiente base

```bash
cp .env.example .env
docker compose up -d
```

UI do Metabase:

```text
http://localhost:3002
```

## A dor que sobra

dbt organiza transformacoes, mas nao resolve agenda, retries, backfill e dependencias entre fontes. Essa dor leva ao capitulo 06: API externa batch.
