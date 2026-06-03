# Arquitetura macro da empresa

## Contexto

A NuvemStore e um e-commerce com entregas próprias e integracao com transportadora externa.

Fluxo simplificado:

```text
Cliente
  -> Frontend / Checkout
  -> Backend e-commerce
  -> OLTP
  -> Plataforma de dados
  -> BI / Operações / Fraude / ML
```

## Domínios principais

| Domínio | Responsabilidade | Dados principais |
| --- | --- | --- |
| Cliente | cadastro e perfil | cliente, cidade, histórico |
| Catálogo | produtos e categorias | produto, categoria, preco |
| Pedido | checkout e itens vendidos | pedido, item_pedido, status |
| Pagamento | autorizacao e risco | pagamento, metodo, valor, status |
| Entrega | despacho e status logistico | entrega, entregador, regiao |
| Transportadora externa | status e ocorrências | SLA, ocorrências, previsao |
| Analytics | métricas e consumo | marts, gold, dashboards |
| Fraude/ML | features e scoring | feature table, score, label |

## Sistemas macro

| Sistema | Papel |
| --- | --- |
| Frontend | interface do cliente e checkout. |
| Backend e-commerce | regras de negócio e escrita no OLTP. |
| PostgreSQL OLTP | fonte transacional principal. |
| API Transportadora | fonte externa batch. |
| Airflow | orquestracao de pipelines batch. |
| Spark | processamento distribuído. |
| HDFS | lake on-prem legado/inicial. |
| MinIO/S3 | object storage alvo moderno. |
| Hive Metastore | catálogo de datasets/tabelas do lake. |
| Delta Lake | tabelas transacionais no lakehouse. |
| Redpanda/Kafka | log de eventos e CDC. |
| Debezium | captura mudanças do OLTP. |
| Trino | query engine para BI e federação. |
| Metabase | dashboards e consumo analítico. |
| Feature Store local | tabela de features para fraude. |

## Consumidores

- Financeiro: receita diaria, ticket médio, status de pagamentos.
- Operações: entregas, atrasos, ocorrências, SLA.
- Produto: funil, top produtos, comportamento de navegação.
- Risco/fraude: pagamentos suspeitos e anomalias.
- Engenharia: saude dos pipelines, lag, falhas e qualidade.

## Limites da simulacao

Este repositorio simula arquitetura local com Docker. Em produção, haveria:

- VPC/sub-redes;
- IAM/segredos gerenciados;
- object storage cloud real;
- monitoramento centralizado;
- controle de acesso por grupos;
- ambientes separados: dev, staging e prod.
