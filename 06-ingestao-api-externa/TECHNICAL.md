# Complemento tecnico - Ingestao batch de API externa

## O que este capitulo aprofunda

Este capitulo adiciona uma fonte externa ao dominio. A plataforma deixa de depender apenas de tabelas internas e passa a lidar com contratos HTTP, janelas incrementais e falhas de integracao.

## Por que isso importa

Empresas raramente vivem com uma unica origem. Alem do OLTP interno, surgem CRMs, ERPs, gateways de pagamento, parceiros logisticos, planilhas e APIs SaaS.

APIs externas trazem dores especificas:

- indisponibilidade;
- rate limit;
- paginacao;
- mudanca de contrato;
- dados atrasados;
- reprocessamento por janela;
- idempotencia no destino.

## Por baixo dos panos

Uma extracao batch de API normalmente segue este fluxo:

1. definir janela de busca, como `atualizado_em >= ultimo_sucesso`;
2. chamar endpoint paginado;
3. validar schema do payload;
4. gravar em staging;
5. registrar checkpoint da carga;
6. reprocessar sem duplicar.

O destino inicial deve ser staging. Transformar direto no consumo final mistura responsabilidades e dificulta replay.

## Alternativas

| Abordagem | Quando usar |
| --- | --- |
| API batch em Python | Simples, bom para volumes moderados e endpoints HTTP. |
| Airbyte | Muitos conectores prontos, bom para SaaS. |
| Fivetran | Gerenciado, menos operacao, maior custo. |
| Kafka source connector | Quando a fonte publica eventos ou existe conector adequado. |
| Webhook | Quando a fonte externa envia mudancas por push. |

## Como conecta a trilha

Esta etapa cria a dor que justifica Airflow. Com OLTP, dbt e API externa, ja existem dependencias e falhas suficientes para precisar de orquestracao.
