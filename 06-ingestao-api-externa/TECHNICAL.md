# Complemento técnico — Ingestão batch de API externa

## O que este capítulo aprofunda

Este capítulo adiciona uma fonte externa ao domínio. A plataforma deixa de depender apenas de tabelas internas e passa a lidar com contratos HTTP, janelas incrementais e falhas de integração.

## Pequena história

Integração batch com sistemas externos existe desde os primeiros mainframes: arquivos eram transferidos por FTP em janelas noturnas. Com a web, o padrão migrou para APIs HTTP — primeiro SOAP/XML nos anos 2000, depois REST/JSON a partir de meados da década de 2010.

O ecossistema moderno de ingestão batch nasceu da explosão de SaaS: Salesforce, Stripe, HubSpot, parceiros logísticos e dezenas de fornecedores passaram a expor dados via API. Ferramentas como Airbyte, Fivetran e Stitch surgiram para abstrair conectores, paginação e rate limiting. Mas entender o que essas ferramentas fazem por baixo — e quando elas falham — continua sendo trabalho de engenheiro.

## Por baixo dos panos

Uma extração batch de API normalmente segue este fluxo:

1. definir janela de busca, como `atualizado_em >= ultimo_sucesso`;
2. chamar endpoint paginado;
3. validar schema do payload;
4. gravar em staging;
5. registrar checkpoint da carga;
6. reprocessar sem duplicar.

O destino inicial deve ser staging. Transformar direto no consumo final mistura responsabilidades e dificulta replay.

APIs externas trazem dores específicas que bancos internos não têm:

- **Indisponibilidade**: a API pode sair do ar sem aviso. O extractor precisa de retry com backoff exponencial.
- **Rate limiting**: a maioria das APIs limita requisições por segundo ou por minuto. Ultrapassar o limite resulta em HTTP 429 e possível bloqueio temporário.
- **Paginação**: datasets grandes são retornados em páginas. O extractor precisa iterar até a última página, tratando cursores ou offsets.
- **Mudança de contrato**: o fornecedor pode adicionar, remover ou renomear campos sem aviso. O staging deve gravar o payload cru; transformações rígidas ficam na camada seguinte.
- **Dados atrasados ou fora de ordem**: janelas incrementais por `atualizado_em` podem perder registros que foram atualizados durante a janela anterior mas não apareceram a tempo.
- **Idempotência no destino**: rodar o extractor duas vezes para a mesma janela não deve duplicar dados. O padrão é UPSERT por chave natural ou DELETE+INSERT por janela.

## Tecnologias equivalentes

| Abordagem | Quando usar |
| --- | --- |
| API batch em Python | Simples, bom para volumes moderados e endpoints HTTP. Total controle sobre retry, paginação e parsing. |
| Airbyte | Muitos conectores prontos, bom para SaaS. Open source, mas requer infraestrutura própria. |
| Fivetran | Gerenciado, menos operação, maior custo. Ideal quando o time não quer manter conectores. |
| Meltano | EL (extract-load) baseado em Singer taps. Configurável via YAML, boa integração com dbt. |
| Kafka source connector | Quando a fonte publica eventos ou existe conector adequado no ecossistema Connect. |
| Webhook | Quando a fonte externa envia mudanças por push em vez de o consumidor puxar. |

## Quando usar

Use extração batch de API quando o fornecedor expõe dados via HTTP e a latência tolerada é de minutos a horas. É o padrão mais comum para integração com parceiros, logística, pagamentos e SaaS.

Evite quando a fonte tem volume muito alto e suporta streaming nativo (CDC, webhooks, filas). Nesse caso, o batch adiciona latência desnecessária e pode sobrecarregar a API com requests grandes.

## Como isso aparece no projeto

Esta etapa cria a dor que justifica Airflow. Com OLTP, dbt e API externa, já existem dependências e falhas suficientes para precisar de orquestração.

## 📚 Referências

- [RESTful API Design — Best Practices](https://restfulapi.net/) — convenções de design REST que afetam como o extractor consome a API.
- [HTTP Status Codes](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status) — referência MDN para entender 429, 503 e outros códigos relevantes.
- [Airbyte Documentation](https://docs.airbyte.com/) — plataforma open source de ingestão com centenas de conectores.
