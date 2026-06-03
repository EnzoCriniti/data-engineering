# Complemento tecnico - Modelagem dimensional e OLAP

## O que este capitulo aprofunda

Este capitulo mostra a virada de mentalidade: sair de um modelo feito para escrever rapido e chegar em um modelo feito para responder perguntas de negocio rapido.

## Pequena historia

Data warehouses ganharam forca nas decadas de 1980 e 1990, quando empresas passaram a separar sistemas operacionais dos sistemas analiticos. Duas escolas ficaram famosas:

- Inmon: warehouse corporativo centralizado, mais normalizado.
- Kimball: data marts dimensionais, orientados a processos de negocio.

O star schema ficou popular porque e simples de entender, performatico para BI e muito alinhado ao modo como analistas perguntam: uma metrica por varias dimensoes.

## Por baixo dos panos

Um modelo dimensional separa tabelas em fatos e dimensoes.

Fatos guardam eventos mensuraveis: uma venda, um pagamento, uma entrega. Normalmente tem chaves para dimensoes e metricas numericas.

Dimensoes guardam contexto: cliente, produto, tempo, loja, regiao. Sao usadas para filtrar, agrupar e explicar os fatos.

O ponto mais importante e o grao. Antes de modelar uma fato, e preciso dizer exatamente o que uma linha representa. Neste projeto, a fato de vendas pode representar um item vendido em um pedido. Se o grao fica confuso, as metricas ficam erradas.

## Star schema, snowflake e SCD

No star schema, dimensoes sao desnormalizadas de proposito. Produto e categoria podem ficar na mesma dimensao para evitar joins extras. Isso aumenta redundancia, mas melhora leitura.

No snowflake, dimensoes sao normalizadas em varias tabelas. Reduz redundancia, mas aumenta complexidade para o usuario e para o otimizador.

SCD, Slowly Changing Dimensions, trata mudancas em dimensoes. O Tipo 1 sobrescreve. O Tipo 2 cria uma nova versao da linha e preserva historico. Para analytics, SCD2 e essencial quando uma venda antiga precisa continuar associada ao contexto antigo do cliente.

## Tecnologias equivalentes e relacionadas

| Conceito | Alternativas |
| --- | --- |
| Modelagem Kimball | Data marts dimensionais por processo de negocio. |
| Modelagem Inmon | Warehouse corporativo normalizado. |
| Data Vault | Modelo historizado e auditavel, comum em ambientes enterprise. |
| One Big Table | Tabela larga para consulta rapida, mas com governanca mais dificil. |
| Cubos OLAP | Pre-agregacoes multidimensionais para consultas muito rapidas. |

## Quando usar

Use modelagem dimensional quando o objetivo e BI, dashboards, relatorios e exploracao analitica recorrente. Ela reduz atrito para quem consome dados.

Evite usar star schema como banco transacional. Ele duplica atributos, nao e ideal para escrita concorrente e nao protege o dominio com o mesmo rigor de um OLTP normalizado.

## Como isso aparece no projeto

Este capitulo desenha a camada analitica alvo. O capitulo 02 mostra a primeira materializacao no mesmo OLTP, o capitulo 03 separa o warehouse e o capitulo 05 melhora transformacoes com dbt.
