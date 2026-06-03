# Capitulo 02 - Dimensional dentro do mesmo banco OLTP

> De onde viemos: no capitulo 01 desenhamos o star schema. Historicamente, muitas empresas comecaram materializando esse modelo em outra area do proprio banco transacional, por exemplo em um schema `analytics`.

## Cenario de negocio

A NuvemStore ainda e pequena. Para ganhar velocidade, o time cria tabelas analiticas dentro do mesmo PostgreSQL que atende o sistema transacional. Parece barato: nao precisa de outro servidor, outro banco, outro backup nem outra operacao.

Esse e um passo realista. Muitas plataformas comecam assim.

## O que esta etapa mostra

O mesmo Postgres tem duas areas:

```text
public      -> tabelas OLTP: cliente, pedido, item_pedido, pagamento
analytics   -> tabelas OLAP: dim_cliente, dim_produto, dim_tempo, fct_vendas
```

Isso aproxima analytics do dado de origem, mas tambem mistura cargas com perfis opostos:

- OLTP: escritas pequenas, baixa latencia, alta concorrencia.
- OLAP: leituras grandes, joins, agregacoes e scans.

## Por que isso vira problema

O banco transacional passa a dividir CPU, memoria, I/O, locks, conexoes e manutencao com consultas analiticas. Mesmo quando o schema e separado, os recursos fisicos continuam compartilhados.

Uma query de receita por categoria pode competir com o checkout. Um `VACUUM`, uma carga ou um indice pesado pode afetar os dois mundos. A separacao logica nao e separacao operacional.

## Como rodar

```bash
cp .env.example .env
docker compose up -d db
docker compose run --rm seeder
```

O banco sobe com o schema OLTP do capitulo 00 e o schema `analytics` desta etapa.

Para refazer do zero:

```bash
docker compose down -v
docker compose up -d db
docker compose run --rm seeder
```

## A dor que sobra

Separar schemas ajudou a organizar, mas nao isolou recursos. O proximo passo e separar fisicamente as bases: um Postgres para a origem transacional e outro Postgres para o warehouse.
