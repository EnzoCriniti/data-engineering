# Capítulo 15 — Qualidade e contratos de dados 🟡

> **De onde viemos:** a plataforma tem ingestão de múltiplas fontes (OLTP, API externa, CDC, streaming) e infra reproduzível (cap 14). O `dbt test` (cap 05) já cobre `not_null` e `unique` nos modelos. Mas a borda de entrada — o dado *cru* que chega da API externa ou do OLTP — não é checada. Quando a transportadora muda o payload silenciosamente, ou um valor vem nulo onde não deveria, nada quebra de forma visível. O dado ruim só aparece num dashboard errado, dias depois.

## Cenário de negócio

A NuvemStore tomou uma decisão de produto com base num gráfico de receita que, descobriu-se depois, estava errado: a API da transportadora passou a mandar `valor_frete` em centavos em vez de reais, e ninguém percebeu por uma semana. O número inflou 100x num mart e ninguém tinha um alarme.

A lição: confiar que a fonte manda o dado certo não é estratégia. A plataforma precisa de **portões de qualidade** — validações que rodam *antes* do dado entrar nas camadas confiáveis, e que falham alto quando o contrato é violado.

## O que esta etapa mostra

A introdução de **contratos de dados** e **testes de qualidade** sobre as fontes: um conjunto de expectativas declaradas (tipos, faixas, não-nulidade, cardinalidade, unicidade) que rodam contra os dados crus e barram a entrada quando uma regra é violada — com um relatório legível de o que passou e o que falhou.

```text
fonte crua  ->  [PORTÃO DE QUALIDADE: expectativas]  ->  camada confiável
                       |
                       falha -> bloqueia + alerta + relatório
```

## Conceitos

**Contrato de dados.** Um acordo explícito entre quem produz e quem consome o dado: quais colunas existem, seus tipos, quais são obrigatórias, faixas válidas. Versionado e testável — não um "combinado" verbal.

**Expectativa (expectation).** Uma asserção sobre os dados: "`valor` é não-nulo e está entre 0 e 100000", "`pedido_id` é único", "`status` está no conjunto {pendente, pago, cancelado}". O conjunto de expectativas é a especificação executável do contrato.

**Validação na borda vs no modelo.** O `dbt test` valida o que já entrou e foi transformado. O portão de qualidade valida o dado *cru, na entrada* — pega o problema antes que ele contamine as camadas.

**Schema drift.** Quando a fonte muda a estrutura sem avisar (coluna some, tipo muda, unidade muda). O contrato detecta drift comparando o que chegou com o que foi acordado.

**Quarentena vs fail-fast.** Diante de dado ruim, há duas estratégias: bloquear o lote inteiro (fail-fast, bom para dados críticos) ou desviar as linhas ruins para quarentena e seguir com as boas. A escolha depende de quão tolerante o consumidor é.

**Data docs.** O relatório navegável de qual expectativa passou/falhou, com exemplos das linhas que violaram. Transforma "deu erro" em "estas 12 linhas têm `valor` negativo".

> Detalhamento técnico (Great Expectations vs dbt tests vs Soda, onde rodar no pipeline) em [`TECHNICAL.md`](./TECHNICAL.md).

## Status e como executar

**Status: 🟡 ambiente base / documentação.** O compose sobe um runner que valida o **gold do lakehouse** (cap 10/12) via **Trino** — o estado consolidado dos dados quando chegamos aqui. As suítes de expectativas e o checkpoint são o roteiro do [GUIDE.md](./GUIDE.md) (código no [SOLUTION.md](./SOLUTION.md)).

- **[RUNBOOK.md](./RUNBOOK.md)** — rodar a validação e gerar os data docs (com espaço para prints).

## A dor que sobra

Agora o dado que entra é validado, mas a operação ainda é cega: se um job do Airflow falhar às 3h da manhã, ou se uma tabela parar de ser atualizada, ninguém fica sabendo até alguém reclamar. O próximo capítulo trata disso: **observabilidade do pipeline** — métricas, freshness e alertas.
