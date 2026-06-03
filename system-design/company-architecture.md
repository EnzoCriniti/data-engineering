# Arquitetura macro da empresa

## Contexto

A NuvemStore e um e-commerce com entregas proprias e integracao com transportadora externa.

Fluxo simplificado:

```text
Cliente
  -> Frontend / Checkout
  -> Backend e-commerce
  -> OLTP
  -> Plataforma de dados
  -> BI / Operacoes / Fraude / ML
```

## Dominios principais

| Dominio | Responsabilidade | Dados principais |
| --- | --- | --- |
| Cliente | cadastro e perfil | cliente, cidade, historico |
| Catalogo | produtos e categorias | produto, categoria, preco |
| Pedido | checkout e itens vendidos | pedido, item_pedido, status |
| Pagamento | autorizacao e risco | pagamento, metodo, valor, status |
| Entrega | despacho e status logistico | entrega, entregador, regiao |
| Transportadora externa | status e ocorrencias | SLA, ocorrencias, previsao |
| Analytics | metricas e consumo | marts, gold, dashboards |
| Fraude/ML | features e scoring | feature table, score, label |

## Sistemas macro

| Sistema | Papel |
| --- | --- |
| Frontend | interface do cliente e checkout. |
| Backend e-commerce | regras de negocio e escrita no OLTP. |
| PostgreSQL OLTP | fonte transacional principal. |
| API Transportadora | fonte externa batch. |
| Airflow | orquestracao de pipelines batch. |
| Spark | processamento distribuido. |
| HDFS | lake on-prem legado/inicial. |
| MinIO/S3 | object storage alvo moderno. |
| Hive Metastore | catalogo de datasets/tabelas do lake. |
| Delta Lake | tabelas transacionais no lakehouse. |
| Redpanda/Kafka | log de eventos e CDC. |
| Debezium | captura mudancas do OLTP. |
| Trino | query engine para BI e federacao. |
| Metabase | dashboards e consumo analitico. |
| Feature Store local | tabela de features para fraude. |

## Consumidores

- Financeiro: receita diaria, ticket medio, status de pagamentos.
- Operacoes: entregas, atrasos, ocorrencias, SLA.
- Produto: funil, top produtos, comportamento de navegacao.
- Risco/fraude: pagamentos suspeitos e anomalias.
- Engenharia: saude dos pipelines, lag, falhas e qualidade.

## Limites da simulacao

Este repositorio simula arquitetura local com Docker. Em producao, haveria:

- VPC/sub-redes;
- IAM/segredos gerenciados;
- object storage cloud real;
- monitoramento centralizado;
- controle de acesso por grupos;
- ambientes separados: dev, staging e prod.
