# Complemento técnico - ELT batch com Python, Docker Compose e DuckDB

## O que este capítulo aprofunda

Este capítulo implementa o pipeline sem uma plataforma especializada. A intencao e deixar visivel o trabalho básico de engenharia de dados: extrair da origem, carregar uma área raw e transformar em tabelas de negócio.

## Pequena história

Pipelines batch existem desde os primeiros sistemas corporativos: mover arquivos, copiar tabelas, executar SQL em horarios definidos. Antes de ferramentas modernas, muita coisa era feita com scripts, cron e SQL procedural.

Docker Compose surgiu a partir do projeto Fig, popularizado na metade da década de 2010 e incorporado ao ecossistema Docker. Ele resolveu uma dor comum: descrever vários containers de uma aplicação em um arquivo único.

DuckDB surgiu no fim da década de 2010 como um banco analítico embarcado. A proposta e ser para analytics o que SQLite e para aplicações locais: simples, local, sem servidor e rapido para consultas colunares.

## Por baixo dos panos

O pipeline deste capítulo faz ELT:

1. Extrai tabelas do Postgres com `psycopg2`.
2. Carrega copias raw no DuckDB.
3. Executa SQL no destino para criar marts.

Isso e diferente de ETL classico, em que a transformacao acontece antes da carga. Em ELT, o destino analítico faz o trabalho pesado.

O DuckDB e colunar e vetorizado. Ele processa blocos de valores por coluna, o que e eficiente para agregações, filtros e scans analíticos. Como roda embarcado, não precisa de servidor, usuário ou rede. O arquivo `.duckdb` vira o warehouse local do capítulo.

Docker Compose separa as etapas:

- `oltp`: banco de origem.
- `seeder`: job one-shot que popula a origem.
- `pipeline`: job one-shot que cria o warehouse local.
- `metabase`: BI opcional.

## O que este capítulo ensina na pratica

O valor aqui não e a ferramenta, e o entendimento. Ao escrever o ELT batch com Pythonmente, aparecem problemas que ferramentas modernas abstraem:

- idempotência;
- ordem de execução;
- controle de schema;
- repeticao de SQL;
- falta de testes de dados;
- dificuldade de lineage.

Essas dores justificam o dbt no capítulo 05 e Airflow no capítulo 07.

## Tecnologias equivalentes

| Tecnologia | Papel |
| --- | --- |
| SQLite | Banco local embarcado, mais transacional que analítico. |
| Pandas | Manipulacao local em memória; otimo para volumes menores. |
| Polars | Dataframes colunares rapidos, com lazy execution. |
| Postgres como warehouse pequeno | Simples para BI, mas menos otimizado que motores colunares. |
| Apache Beam | Modelo portavel para batch/stream, mais complexo que o necessário aqui. |

## Quando usar

Use ELT batch com Python para aprendizado, prototipo pequeno ou tarefa muito simples. Ele e transparente é barato.

Evite quando a transformacao vira produto: sem testes, sem DAG, sem lineage e sem observabilidade, o custo operacional cresce rapido.

## Como isso aparece no projeto

O compose do capítulo sobe o ambiente em etapas para demonstrar a história acontecendo: origem, seed, pipeline e depois BI. O DuckDB gerado em `data/warehouse` contem a área raw e os marts.
