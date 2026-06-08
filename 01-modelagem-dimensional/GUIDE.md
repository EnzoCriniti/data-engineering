# Cap. 01 — Modelagem dimensional: projetando o star schema

> **Aula deste capítulo.** Aqui você aprende o *porquê* de cada decisão de design dimensional, com exemplos trabalhados. O DDL do star schema e o mapeamento OLTP→dimensional estão no **[SOLUTION.md](./SOLUTION.md)**; o aprofundamento (Kimball vs Inmon, cubos OLAP, fatos sem fato) está no **[TECHNICAL.md](./TECHNICAL.md)**. Este capítulo é **puramente de design** — não sobe ambiente nem roda código.

## O problema que este capítulo resolve

O OLTP do capítulo 00 é ótimo para registrar transações, mas péssimo para respondê-las. Uma pergunta simples como "qual a receita por categoria nos últimos 30 dias?" exige JOIN entre `item_pedido`, `produto`, `categoria` e `pedido`, com filtros de data e status. O query plan é complexo, a query é lenta, e executá-la em produção compete com o checkout.

Este capítulo é **puramente de design** — nenhum ambiente sobe, nenhum código executa. O objetivo é projetar o modelo dimensional que será materializado nos capítulos seguintes. Aqui se definem: o grão da tabela fato, quais dimensões existem, por que surrogate keys são necessárias, e como tratar mudanças em dimensões (SCD Type 2).

## Pré-requisitos

- **Capítulo anterior:** 00 concluído (entender o schema OLTP).
- **Nenhum ambiente** — este capítulo é de design e documentação.

## Conceitos fundamentais

### OLAP vs OLTP

OLTP otimiza para muitas escritas pequenas e concorrentes. OLAP otimiza para poucas leituras grandes e analíticas. São objetivos opostos — por isso precisam de modelos diferentes e, eventualmente, infraestrutura separada.

### Grão: a decisão mais importante

O grão define o que uma linha da tabela fato representa. Para `fct_vendas`, o grão é: **um item vendido em um pedido**. Cada linha = uma combinação de `pedido_id` + `produto_id`.

Misturar grãos na mesma fato (ex: linhas de item e linhas de pedido) é um anti-pattern clássico que corrompe métricas — `SUM(valor)` retorna valores diferentes dependendo do nível de agrupamento.

**Exemplo trabalhado — como o grão misto corrompe a soma.** O pedido `P-1` tem 2 itens (R$ 30 + R$ 70) e um `valor_total` de pedido de R$ 100. Se a fato misturar uma linha "de item" com uma linha "de pedido":

```text
grão      | pedido | valor
----------+--------+------
item      | P-1    |  30
item      | P-1    |  70
pedido    | P-1    | 100   ← intruso de outro grão
```

`SUM(valor)` agora dá **200**, quando a receita real do pedido é 100. O R$ 100 foi contado duas vezes (uma como pedido, outra como a soma dos itens). Por isso a regra é absoluta: **uma fato, um grão**. Se você precisa de métricas no nível de pedido, isso é uma *segunda* tabela fato (`fct_pedidos`), não linhas extras na mesma.

### Métricas: aditivas, semi-aditivas e não-aditivas

- **Aditivas**: podem ser somadas em qualquer dimensão. `quantidade`, `valor_total`.
- **Semi-aditivas**: somam em algumas dimensões mas não em todas. `saldo_conta` soma entre clientes mas não entre datas.
- **Não-aditivas**: nunca somam. `percentual`, `razão`. Precisam ser recalculadas a partir de componentes aditivos.

### Surrogate keys: por que não usar chaves naturais

O warehouse gera suas próprias chaves (`sk_cliente`, `sk_produto`, `sk_tempo`). A fato referencia surrogates, nunca chaves da origem. Motivos:
- Desacopla o warehouse da origem (se a origem trocar de banco, os surrogates não mudam).
- Permite SCD Type 2 (um mesmo `cliente_id` pode ter múltiplos surrogates, um por versão).
- Evita dependência de gaps ou reciclagem de IDs na origem.

### Slowly Changing Dimensions (SCD)

- **Tipo 1**: sobrescreve o valor antigo. Simples, mas perde histórico.
- **Tipo 2**: cria nova linha com `valido_de`, `valido_ate`, `atual`. Preserva histórico completo. Essencial quando uma venda antiga precisa ser associada à cidade do cliente _naquele momento_.
- **Tipo 3**: adiciona coluna `cidade_anterior`. Limitado a uma mudança.

Para `dim_cliente`, usamos **SCD Type 2** porque a cidade do cliente muda e analytics precisa do histórico.

**Exemplo trabalhado — por que SCD2 e não sobrescrever.** A cliente Ana comprou em janeiro morando em **Recife** e em junho mudou para **São Paulo**. Pergunta de negócio: "qual a receita por cidade?".

Com **SCD Tipo 1** (sobrescreve), o cadastro de Ana só guarda "São Paulo" — e a venda de janeiro, que aconteceu quando ela morava em Recife, passa a contar para São Paulo. O histórico mente.

Com **SCD Tipo 2**, `dim_cliente` tem duas linhas para Ana:

```text
sk_cliente | cliente_id | cidade    | valido_de  | valido_ate | atual
-----------+------------+-----------+------------+------------+------
101        | C-7        | Recife    | 2024-01-01 | 2024-05-31 | false
102        | C-7        | São Paulo | 2024-06-01 | NULL       | true
```

A venda de janeiro aponta para `sk_cliente=101` (Recife), a de junho para `102` (São Paulo). A receita por cidade fica **correta no tempo**. É por isso que a fato referencia o *surrogate* (`sk_cliente`), não o `cliente_id`: o surrogate captura a *versão* do cliente naquele momento.

### Denormalização intencional

No OLTP, `produto` e `categoria` são tabelas separadas (3NF). Na dimensional, `dim_produto` embute `categoria_nome` diretamente — uma denormalização proposital que reduz JOINs para o consumidor. Isso é o oposto do capítulo 00, e deve ser documentado como decisão consciente.

---

## Etapa 1 — Definir o grão da tabela fato

### Contexto
O grão é a primeira decisão. Tudo mais deriva dele: quais FKs existem, quais métricas são possíveis, como o cubo é navegável.

### O que fazer
Declarar explicitamente: "Cada linha de `fct_vendas` representa **um item vendido em um pedido**." O grão é `(pedido_id, produto_id)`. Documentar que pedidos cancelados são excluídos da fato (regra de negócio).

### ⚠️ Armadilhas
- Incluir pagamentos na mesma fato mistura grãos (um pedido pode ter N pagamentos mas M itens — a cardinalidade é diferente).
- Incluir pedidos cancelados infla receita incorretamente.

---

## Etapa 2 — Separar fatos de dimensões

### Contexto
Com o grão definido, separar o que é métrica (fica na fato) do que é contexto (vai para dimensões).

### O que fazer
- **`fct_vendas`**: `sk_venda` (IDENTITY), `sk_tempo`, `sk_cliente`, `sk_produto` (FKs para dimensões), `pedido_id`, `item_pedido_id` (chaves naturais para rastreabilidade), `quantidade` (INT), `valor_total` (NUMERIC).
- **`dim_tempo`**: `sk_tempo`, `data` (DATE UNIQUE), `dia`, `mes`, `trimestre`, `ano`. Derivada das datas distintas dos pedidos.
- **`dim_cliente`**: `sk_cliente`, `cliente_id` (natural key), `nome`, `cidade`, `email`, `valido_de`, `valido_ate`, `atual` (SCD2).
- **`dim_produto`**: `sk_produto`, `produto_id`, `nome`, `categoria` (denormalizado).

### ⚠️ Armadilhas
- Não incluir a chave natural na dimensão impede r