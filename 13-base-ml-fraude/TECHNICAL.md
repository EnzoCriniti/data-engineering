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

Uma **feature store** é a infraestrutura completa ao redor: versionamento de fea