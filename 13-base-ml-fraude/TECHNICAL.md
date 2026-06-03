# Complemento técnico - Feature table e ML para fraude

## O que este capítulo aprofunda

Este capítulo mostra que dados para ML não são apenas "mais uma tabela". Eles exigem cuidado com tempo, qualidade, definição de features e separacao entre treino e scoring.

## Conceitos importantes

Feature table é uma tabela com variaveis calculadas para um modelo. Ela deve ter chave, timestamp e features reproduziveis.

Point-in-time correctness significa que uma linha de treino só pode usar informacoes disponíveis naquele momento. Usar dado futuro gera label leakage e faz o modelo parecer melhor do que realmente e.

Batch features são calculadas periodicamente, por exemplo histórico de pagamentos dos ultimos 30 dias. Real-time features podem vir de streaming, como contagem de eventos recentes ou velocidade média em uma janela.

## Por que entra depois de streaming

Fraude pode usar sinais históricos e sinais recentes. Antes do streaming, a plataforma teria apenas histórico batch. Depois do streaming, ela consegue combinar:

- perfil histórico do cliente;
- status recente de pagamento;
- comportamento operacional em tempo real;
- anomalias de entrega ou localizacao.

## Alternativas

| Abordagem | Quando usar |
| --- | --- |
| Tabela ML no warehouse/lakehouse | Simples e boa para portfolio. |
| Feast | Feature store open source. |
| Tecton | Feature platform gerenciada/comercial. |
| SageMaker Feature Store | Integrada ao ecossistema AWS. |
| Vertex AI Feature Store | Integrada ao ecossistema Google Cloud. |

## Como conecta a trilha

Este capítulo mostra que a plataforma de dados também pode servir produtos de ML, não apenas dashboards. O modelo em si pode ser simples; o diferencial e a base correta, versionada e validavel.
