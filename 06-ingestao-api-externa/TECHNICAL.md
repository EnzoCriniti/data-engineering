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
- **Rate limiting**: a maioria das APIs limita requisições por 