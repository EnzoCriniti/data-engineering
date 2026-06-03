# Build — Capítulo 01: como desenhar o modelo dimensional

> Guia **avançado e detalhado** de modelagem. Aqui não se sobe ambiente — desenha-se o star schema que os capítulos 02 e 03 materializam. Para ver o modelo em ação, use o [RUNBOOK](./RUNBOOK.md).

## Objetivo

Desenhar o modelo dimensional (star schema) da NuvemStore a partir da origem OLTP do cap. 00, tomando conscientemente as decisões de grão, surrogate keys e SCD que os pipelines seguintes vão implementar.

## Pré-requisitos de conhecimento

- O modelo OLTP do [cap. 00](../00-modelagem-transacional).
- Conceitos OLAP: fato, dimensão, grão, surrogate key, SCD, star vs snowflake (ver README e [TECHNICAL.md](./TECHNICAL.md)).

## Passo 1 — Definir o grão do fato

A decisão mais importante. Aqui: **um item vendido em uma venda** (`item_pedido`). Toda métrica e toda dimensão precisam ser compatíveis com esse grão. Misturar grãos (ex.: nível de pedido e nível de item na mesma fato) é a causa nº 1 de modelos quebrados.

## Passo 2 — Separar fatos de dimensões

- **Fato (`fct_vendas`)**: métricas aditivas (`quantidade`, `valor_total`) + FKs para as dimensões.
- **Dimensões**: atributos descritivos pelos quais se filtra/agrupa (`dim_tempo`, `dim_cliente`, `dim_produto`, `dim_loja`).

## Passo 3 — Surrogate keys

Cada dimensão tem uma chave artificial (`sk_*`) gerada no warehouse, além da chave natural da origem (`id_natural`/`*_id`). A fato referencia as surrogate, nunca as naturais. Isso desacopla o warehouse da origem e é pré-requisito do SCD2.

## Passo 4 — Desnormalizar de propósito

`dim_produto` traz a categoria embutida (sem tabela separada). É o oposto da 3FN do cap. 00 — e intencional: menos joins, leitura mais rápida. Documentar que é decisão consciente, não erro.

## Passo 5 — SCD Tipo 2 na dim_cliente

Atributos que mudam (cidade do cliente) exigem histórico. SCD2: ao mudar, fecha a linha atual (`valido_ate`, `atual=false`) e cria nova versão (`valido_de`, `atual=true`). Assim uma venda antiga continua atribuída à cidade que o cliente tinha **na época**. Esse é o desenho que o cap. 03 precisará implementar na carga.

## Passo 6 — A ponte OLTP → dimensional

Documentar o mapeamento de cada tabela OLTP para o destino dimensional: `pedido`+`item_pedido` → `fct_vendas`; `cliente` → `dim_cliente`; `produto`+`categoria` → `dim_produto`; datas de `pedido` → `dim_tempo`. Esse mapa é o contrato que o job `migrate` do cap. 03 executa.

## Validações (definição de pronto)

- [ ] Grão declarado explicitamente e único.
- [ ] Toda dimensão tem surrogate key e chave natural.
- [ ] `dim_cliente` modelada com colunas de SCD2.
- [ ] Mapeamento OLTP → dimensional documentado.
- [ ] `diagrams/architecture.py` compila e gera o ERD.

## Estado final (gabarito para o próximo capítulo)

O star schema desenhado e justificado, com a ponte da origem mapeada. O [cap. 02](../02-dimensional-no-oltp) faz a primeira materialização (no mesmo OLTP) e o [cap. 03](../03-warehouse-dedicado) separa o warehouse e implementa a carga.
