# Complemento técnico — Feature table, feature stores e ML para fraude

## O que este capítulo aprofunda

Este capítulo mostra que dados para ML não são apenas "mais uma tabela". Eles exigem cuidado com tempo, qualidade, definição de features e separação entre treino e scoring. O diferencial de um engenheiro de dados aqui não é o modelo — é garantir que a base de treino é correta, reproduzível e livre de vazamento de informação futura.

## Pequena história

Feature engineering sempre existiu em ML, mas por muito tempo era feito ad hoc em notebooks. O conceito de **feature store** como infraestrutura dedicada ganhou força a partir de 2017, quando o Uber publicou o paper sobre o Michelangelo — sua plataforma interna de ML que centralizava features para centenas de modelos.

Depois disso, surgiram soluções open source como Feast (2019), e os cloud providers lançaram seus próprios serviços: SageMaker Feature Store (AWS), Vertex AI Feature Store (Google) e Databricks Feature Store. O problema que todos resolvem é o mesmo: garantir que as features usadas no treino sejam exatamente as mesmas usadas na inferência (evitar **training-serving skew**).

O conceito de **point-in-time correctness** — garantir que o treino só use informação disponível até aquele momento — é central para qualquer modelo que opera sobre dados temporais, especialmente fraude.

## Por baixo dos panos

### Feature table vs feature store

Uma **feature table** é uma tabela com variáveis calculadas para um modelo. Ela tem chave (ex: `pagamento_id`), timestamp de referência (`feature_ts`) e features reproduzíveis. É o que este capítulo implementa.

Uma **feature store** é a infraestrutura completa ao redor: versionamento de features, serving online (baixa latência para inferência) e offline (batch para treino), point-in-time joins automáticos e catálogo de features compartilhado entre times. É o destino natural quando a empresa tem múltiplos modelos consumindo features sobrepostas.

### Point-in-time correctness

Significa que uma linha de treino só pode usar informações disponíveis naquele momento. Usar dado futuro gera **label leakage** e faz o modelo parecer melhor do que realmente é.

Na prática, isso se traduz em: toda query de feature histórica deve ter `WHERE data < feature_ts`. O `<` é estrito — incluir `<=` pode vazar o próprio evento que gerou a label.

### Batch features vs real-time features

- **Batch features** são calculadas periodicamente: histórico de pagamentos dos últimos 30 dias, ticket médio do cliente, quantidade de pedidos. Mudam lentamente e são baratas de calcular.
- **Real-time features** vêm de streaming: contagem de eventos nos últimos 5 minutos, velocidade média atual do entregador. Mudam constantemente e exigem infraestrutura de serving online.

A combinação de ambas é o que torna a detecção de fraude eficaz: o perfil histórico do cliente (batch) mais o comportamento recente (real-time).

### Training-serving skew

Acontece quando as features usadas no treino são calculadas de forma diferente das features usadas na inferência. Causas comuns:

- No treino, features são calculadas com SQL em batch. No serving, são calculadas com código Python em tempo real — lógica sutilmente diferente.
- No treino, features históricas usam dados completos. No serving, usam dados parciais (o mês ainda não terminou).
- No treino, features são arredondadas. No serving, não são.

A feature store resolve isso centralizando a definição da feature: uma única implementação alimenta tanto o treino quanto o serving.

## Por que entra depois de streaming

Fraude pode usar sinais históricos e sinais recentes. Antes do streaming, a plataforma teria apenas histórico batch. Depois do streaming, ela consegue combinar:

- perfil histórico do cliente;
- status recente de pagamento;
- comportamento operacional em tempo real;
- anomalias de entrega ou localização.

## Tecnologias equivalentes

| Abordagem | Quando usar |
| --- | --- |
| Tabela ML no warehouse/lakehouse | Simples e boa para portfolio ou times pequenos com poucos modelos. |
| Feast | Feature store open source. Suporta offline e online serving, point-in-time joins. |
| Tecton | Feature platform gerenciada/comercial. Forte em real-time features e orquestração. |
| SageMaker Feature Store | Integrada ao ecossistema AWS. Boa para quem já usa SageMaker. |
| Vertex AI Feature Store | Integrada ao ecossistema Google Cloud. |
| Databricks Feature Store | Integrada ao Databricks, com Unity Catalog. |
| Hopsworks | Feature store open source com foco em MLOps completo. |

## Quando usar

Use uma feature table dedicada quando o modelo precisa de features históricas com garantia temporal, quando treino e inferência consomem as mesmas variáveis, ou quando múltiplos modelos compartilham features.

Evite complexidade de feature store quando há um único modelo simples com poucas features estáticas. Nesse caso, uma query direta no warehouse é suficiente.

## Como isso aparece no projeto

Este capítulo mostra que a plataforma de dados também pode servir produtos de ML, não apenas dashboards. O modelo em si pode ser simples; o diferencial é a base correta, versionada e validável.

## 📚 Referências

- [Uber Michelangelo Paper](https://www.uber.com/blog/michelangelo-machine-learning-platform/) — paper que popularizou o conceito de feature store em produção.
- [Feast Documentation](https://docs.feast.dev/) — feature store open source com exemplos de point-in-time joins.
- [Rules of ML (Google)](https://developers.google.com/machine-learning/guides/rules-of-ml) — guia prático que inclui quando e como usar features corretamente.
- [Feature Store Summit Talks](https://www.featurestoresummit.com/) — conferência dedicada ao tema com palestras de empresas como Spotify, Uber e Netflix.
