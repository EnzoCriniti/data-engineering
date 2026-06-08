# Cap. 13 — Feature table para ML: base de detecção de fraude

> **Aula deste capítulo.** Você aprende a construir uma **feature table** para ML correta e reproduzível — o trabalho do engenheiro de dados não é o modelo, é garantir **point-in-time correctness** e ausência de **label leakage**. A orientação está aqui; o código do `feature_builder.py` e do `validate_pit.py` está no **[SOLUTION.md](./SOLUTION.md)**; os internals (PIT joins, training-serving skew, feature store) estão no **[TECHNICAL.md](./TECHNICAL.md)**.

## O problema que este capítulo resolve

A plataforma agora tem dados históricos (lakehouse), dados em tempo real (streaming), e múltiplas fontes (OLTP, API, GPS). O próximo passo é usar tudo isso para um caso de negócio concreto: **detecção de fraude em pagamentos**.

O diferencial de um engenheiro de dados aqui não é o modelo de ML — é garantir que a base de treino é **correta, reproduzível e livre de vazamento de informação futura** (label leakage). Este capítulo constrói a feature table com garantia de point-in-time correctness.

## Pré-requisitos

- **Capítulo anterior:** 12 concluído (streaming operando).
- **Docker:** versão 24+ com Docker Compose.

## Conceitos fundamentais

### Feature table vs feature store

Uma **feature table** é uma tabela com variáveis calculadas para um modelo: chave (`pagamento_id`), timestamp de referência (`feature_ts`), e features reproduzíveis. É o que este capítulo implementa.

Uma **feature store** é a infraestrutura completa: versionamento, serving online (baixa latência para inferência) e offline (batch para treino), point-in-time joins automáticos, e catálogo compartilhado. É o destino natural quando há múltiplos modelos.

### Point-in-time (PIT) correctness

Uma linha de treino só pode usar informações disponíveis **até aquele momento**. Toda query de feature histórica deve ter `WHERE data < feature_ts` (estrito). Usar `<=` pode vazar o próprio evento.

Exemplo: a feature "pagamentos recusados nos últimos 30 dias" para um pagamento feito em 15/jan deve contar apenas recusados entre 16/dez e 14/jan. Incluir 15/jan vaza a informação do próprio evento.

### Label leakage

Usar dado futuro no treino faz o modelo parecer melhor do que é. Causas comuns:
- Feature calculada com `NOW()` em vez de `feature_ts`.
- JOIN sem filtro temporal (inclui dados de qualquer época).
- Status final usado como feature (o modelo "aprende" que pagamento recusado = fraude, mas em produção o status ainda é "pendente").

**Exemplo trabalhado — o modelo de 99% que falha em produção.** Você treina um detector de fraude e ele acerta 99% no teste — comemoração. Acontece que uma das features foi `status_chargeback`, preenchido *semanas depois* do pagamento, quando o banco confirma a fraude. No treino histórico esse campo já existe, então o modelo basicamente "lê a resposta": chargeback ⇒ fraude. Em **produção**, no instante em que o pagamento acontece, `status_chargeback` ainda é NULL — a feature mais forte do modelo não existe, e a acurácia despenca para perto do acaso. O leak não foi um bug de código; foi usar um dado que, no `feature_ts` real, ainda não tinha nascido. É exatamente por isso que toda feature histórica leva `WHERE data < feature_ts`: ela força a base de treino a enxergar só o que existiria no momento da decisão.

### Batch features vs real-time features

- **Batch**: perfil histórico do cliente (pedidos nos últimos 30 dias, ticket médio). Muda lentamente.
- **Real-time**: velocidade atual do entregador, contagem de eventos recentes. Muda a cada segundo.

A combinação de ambas é o que torna a detecção de fraude eficaz.

### Training-serving skew

Quando features no treino são calculadas de forma diferente das features na inferência. Ex: treino usa SQL batch com dados completos, serving usa Python real-time com dados parciais. O resultado é diferente — o modelo performa pior em produção.

---

## Etapa 1 — Criar o schema da feature table (`features/schema.sql`)

### O que fazer
Tabela `ml.fraude_pagamento_features` com: PK `pagamento_id`, âncora temporal `feature_ts`, features transacionais (valor, método, itens), features históricas (pedidos/recusas 30d), features logísticas (ocorrências de entrega), features streaming (velocidade GPS), e label/score (preenchidos depois).

### Decisões de design
- *`feature_ts` como âncora*: todas as features históricas são calculadas relativas a esse timestamp.
- *Label separado*: `label_fraude` e `score_fraude` começam NULL. São preenchidos por processo diferente (labeling humano ou regra de negócio). Não fazem parte do cálculo de features.
- *Índice em `label_fraude WHERE NOT NULL`*: queries de treino filtram por label preenchido — índice parcial otimiza.

---

## Etapa 2 — Implementar o feature builder (`feature_builder/feature_builder.py`)

### Contexto
Script Python que lê as fontes que a plataforma já produz (OLTP para o transacional, gold do lakehouse para o histórico), calcula features por pagamento, e grava na feature table com UPSERT.

### Decisões de design
- *UPSERT por `pagamento_id`*: idempotente — rodar duas vezes não duplica.
- *Features históricas com filtro PIT*: `WHERE data_pedido >= feature_ts - INTERVAL '30 days' AND data_pedido < feature_ts`. O `<` é crucial.
- *Features de streaming com fallback*: se dados de GPS não existem, a feature é NULL (o modelo lida com missingness).
- *Batch processing*: processa em lotes de 500 para não estourar memória.

### O que fazer
Script com 4 estágios: (1) buscar pagamentos sem features calculadas, (2) calcular features transacionais via SQL, (3) calcular features históricas com PIT, (4) calcular features de streaming/logística, (5) UPSERT no destino.

### ⚠️ Armadilhas
- Usar `NOW()` em vez de `feature_ts`: vaza informação temporal — o modelo vê o futuro.
- Calcular features com `<=` em vez de `<`: inclui o próprio evento na contagem histórica.
- Não tratar `Decimal` do Postgres: psycopg2 devolve `Decimal`, que confunde libs de ML. Converter para float.

### 📚 Para se aprofundar
- [Feast Documentation](https://docs.feast.dev/) — feature store open source com point-in-time joins.
- [Uber Michelangelo](https://www.uber.com/blog/michelangelo-machine-learning-platform/) — paper que popularizou feature stores.

---

## Etapa 3 — Implementar validação de PIT (`feature_builder/validate_pit.py`)

### Contexto
Script que valida que nenhuma feature inclui dados posteriores ao `feature_ts`. Amostra N paga