# Complemento técnico — Modelagem dimensional e OLAP

## O que este capítulo aprofunda

Este capítulo mostra a virada de mentalidade: sair de um modelo feito para escrever rapido e chegar em um modelo feito para responder perguntas de negócio rapido.

## Pequena história

Data warehouses ganharam forca nas decadas de 1980 e 1990, quando empresas passaram a separar sistemas operacionais dos sistemas analíticos. Duas escolas ficaram famosas:

- Inmon: warehouse corporativo centralizado, mais normalizado.
- Kimball: data marts dimensionais, orientados a processos de negócio.

O star schema ficou popular porque e simples de entender, performatico para BI e muito alinhado ao modo como analistas perguntam: uma métrica por várias dimensoes.

## Por baixo dos panos

Um modelo dimensional separa tabelas em fatos e dimensoes.

Fatos guardam eventos mensuraveis: uma venda, um pagamento, uma entrega. Normalmente tem chaves para dimensoes e métricas numericas.

Dimensoes guardam contexto: cliente, produto, tempo, loja, regiao. São usadas para filtrar, agrupar e explicar os fatos.

O ponto mais importante e o grão. Antes de modelar uma fato, e preciso dizer exatamente o que uma linha representa. Neste projeto, a fato de vendas pode representar um item vendido em um pedido. Se o grão fica confuso, as métricas ficam erradas.

## Star schema, snowflake e SCD

No star schema, dimensoes são desnormalizadas de propósito. Produto e categoria podem ficar na mesma dimensao para evitar joins extras. Isso aumenta redundância, mas melhora leitura.

No snowflake, dimensoes são normalizadas em várias tabelas. Reduz redundância, mas aumenta complexidade para o usuário e para o otimizador.

SCD, Slowly Changing Dimensions, trata mudanças em dimensoes. O Tipo 1 sobrescreve. O Tipo 2 cria uma nova versão da linha e preserva histórico. Para analytics, SCD2 e essencial quando uma venda antiga precisa continuar associada ao contexto antigo do cliente.

## Tecnologias equivalentes e relacionadas

| Conceito | Alternativas |
| --- | --- |
| Modelagem Kimball | Data marts dimensionais por processo de negócio. |
| Modelagem Inmon | Warehouse corporativo normalizado. |
| Data Vault | Modelo historizado e auditável, comum em ambientes enterprise. |
| One Big Table | Tabela larga para consulta rapida, mas com governanca mais dificil. |
| Cubos OLAP | Pre-agregações multidimensionais para consultas muito rapidas. |

## Quando usar

Use modelagem dimensional quando o objetivo e BI, dashboards, relatorios e exploracao analítica recorrente. Ela reduz atrito para quem consome dados.

Evite usar star schema como banco transacional. Ele duplica atributos, não e ideal para escrita concorrente e não protege o domínio com o mesmo rigor de um OLTP normalizado.

## Como isso aparece no projeto

Este capítulo desenha a camada analítica alvo. O capítulo 02 mostra a primeira materializacao no mesmo OLTP, o capítulo 03 separa o warehouse e o capítulo 05 melhora transformacoes com dbt