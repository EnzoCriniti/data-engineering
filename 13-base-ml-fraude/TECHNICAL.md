# Complemento tecnico - Feature table e ML para fraude

## O que este capitulo aprofunda

Este capitulo mostra que dados para ML nao sao apenas "mais uma tabela". Eles exigem cuidado com tempo, qualidade, definicao de features e separacao entre treino e scoring.

## Conceitos importantes

Feature table e uma tabela com variaveis calculadas para um modelo. Ela deve ter chave, timestamp e features reproduziveis.

Point-in-time correctness significa que uma linha de treino so pode usar informacoes disponiveis naquele momento. Usar dado futuro gera label leakage e faz o modelo parecer melhor do que realmente e.

Batch features sao calculadas periodicamente, por exemplo historico de pagamentos dos ultimos 30 dias. Real-time features podem vir de streaming, como contagem de eventos recentes ou velocidade media em uma janela.

## Por que entra depois de streaming

Fraude pode usar sinais historicos e sinais recentes. Antes do streaming, a plataforma teria apenas historico batch. Depois do streaming, ela consegue combinar:

- perfil historico do cliente;
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

Este capitulo mostra que a plataforma de dados tambem pode servir produtos de ML, nao apenas dashboards. O modelo em si pode ser simples; o diferencial e a base correta, versionada e validavel.
