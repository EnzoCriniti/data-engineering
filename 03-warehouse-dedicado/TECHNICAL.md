# Complemento técnico - Separacao física entre OLTP e warehouse

## O que esta etapa aprofunda

Esta etapa mostra a diferenca entre separar tabelas em schemas e separar cargas em bancos diferentes. O objetivo não e trocar tecnologia, e isolar recursos.

## Por que surgiu essa necessidade

No inicio, colocar analytics no mesmo banco parece eficiente. Depois, as consultas crescem, os dashboards ficam frequentes e o banco transacional passa a sofrer.

Separar o warehouse resolve uma dor operacional:

- consultas analíticas não competem diretamente com o checkout;
- índices analíticos podem ser criados sem afetar tanto a origem;
- manutenção e backup podem ter politicas diferentes;
- o modelo dimensional deixa de depender do layout físico do OLTP.

## Por baixo dos panos

Mesmo quando os dois bancos usam PostgreSQL, eles tem processos, conexões, volumes e configuracoes separados. Isso muda o isolamento.

O OLTP contínua otimizado para transações pequenas e consistentes. O warehouse pode aceitar tabelas mais largas, dados desnormalizados e consultas longas.

O job `migrate` materializa dados da origem no warehouse. Ele faz uma carga simples: limpa as tabelas analíticas, cria dimensoes e popula a fato de vendas. Essa abordagem e propositalmente simples para mostrar a ponte entre os dois mundos.

## Alternativas

| Abordagem | Caracteristica |
| --- | --- |
| Read replica | Boa para reduzir impacto de leitura, mas ainda prende analytics ao formato da origem. |
| Warehouse dedicado em Postgres | Simples é barato para comecar. |
| DuckDB | Otimo para analytics local e arquivo único. |
| BigQuery / Snowflake / Redshift | Warehouses gerenciados para escala maior. |
| Lakehouse | Storage barato com tabelas transacionais sobre arquivos. |

## Como isso conecta a trilha

Esta etapa cria a base para falar de pipelines. Depois que existem origem e destino separados, surge a pergunta: como mover dados entre eles de forma confiável?
