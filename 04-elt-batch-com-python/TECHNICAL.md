# Complemento tecnico - ELT batch com Python, Docker Compose e DuckDB

## O que este capitulo aprofunda

Este capitulo implementa o pipeline sem uma plataforma especializada. A intencao e deixar visivel o trabalho basico de engenharia de dados: extrair da origem, carregar uma area raw e transformar em tabelas de negocio.

## Pequena historia

Pipelines batch existem desde os primeiros sistemas corporativos: mover arquivos, copiar tabelas, executar SQL em horarios definidos. Antes de ferramentas modernas, muita coisa era feita com scripts, cron e SQL procedural.

Docker Compose surgiu a partir do projeto Fig, popularizado na metade da decada de 2010 e incorporado ao ecossistema Docker. Ele resolveu uma dor comum: descrever varios containers de uma aplicacao em um arquivo unico.

DuckDB surgiu no fim da decada de 2010 como um banco analitico embarcado. A proposta e ser para analytics o que SQLite e para aplicacoes locais: simples, local, sem servidor e rapido para consultas colunares.

## Por baixo dos panos

O pipeline deste capitulo faz ELT:

1. Extrai tabelas do Postgres com `psycopg2`.
2. Carrega copias raw no DuckDB.
3. Executa SQL no destino para criar marts.

Isso e diferente de ETL classico, em que a transformacao acontece antes da carga. Em ELT, o destino analitico faz o trabalho pesado.

O DuckDB e colunar e vetorizado. Ele processa blocos de valores por coluna, o que e eficiente para agregacoes, filtros e scans analiticos. Como roda embarcado, nao precisa de servidor, usuario ou rede. O arquivo `.duckdb` vira o warehouse local do capitulo.

Docker Compose separa as etapas:

- `oltp`: banco de origem.
- `seeder`: job one-shot que popula a origem.
- `pipeline`: job one-shot que cria o warehouse local.
- `metabase`: BI opcional.

## O que este capitulo ensina na pratica

O valor aqui nao e a ferramenta, e o entendimento. Ao escrever o ELT batch com Pythonmente, aparecem problemas que ferramentas modernas abstraem:

- idempotencia;
- ordem de execucao;
- controle de schema;
- repeticao de SQL;
- falta de testes de dados;
- dificuldade de lineage.

Essas dores justificam o dbt no capitulo 05 e Airflow no capitulo 07.

## Tecnologias equivalentes

| Tecnologia | Papel |
| --- | --- |
| SQLite | Banco local embarcado, mais transacional que analitico. |
| Pandas | Manipulacao local em memoria; otimo para volumes menores. |
| Polars | Dataframes colunares rapidos, com lazy execution. |
| Postgres como warehouse pequeno | Simples para BI, mas menos otimizado que motores colunares. |
| Apache Beam | Modelo portavel para batch/stream, mais complexo que o necessario aqui. |

## Quando usar

Use ELT batch com Python para aprendizado, prototipo pequeno ou tarefa muito simples. Ele e transparente e barato.

Evite quando a transformacao vira produto: sem testes, sem DAG, sem lineage e sem observabilidade, o custo operacional cresce rapido.

## Como isso aparece no projeto

O compose do capitulo sobe o ambiente em etapas para demonstrar a historia acontecendo: origem, seed, pipeline e depois BI. O DuckDB gerado em `data/warehouse` contem a area raw e os marts.
