# Data Engineering Portfolio — uma jornada, não uma pilha de projetos

Este repositório conta a evolução natural de uma plataforma de dados para a NuvemStore, um e-commerce fictício com entregas próprias.

A regra da trilha: nenhuma ferramenta entra porque é "legal". Cada tecnologia aparece como resposta a uma dor concreta que a etapa anterior deixou clara.

Antes de seguir, leia o [COMPANY.md](./COMPANY.md). Ele descreve o domínio de negócio, as fontes de dados e as necessidades que guiam as decisões técnicas.

## Para recrutadores

A ideia deste repositório é simular a evolução do ambiente de dados de uma empresa, aumentando gradualmente o nível de maturidade.

Ele não é uma coleção de exemplos isolados. Cada projeto representa uma decisão comum em plataformas reais: primeiro entender a origem, depois separar analytics do transacional, depois lidar com múltiplas fontes, orquestração, lake, lakehouse, CDC, streaming, dados para ML e otimização física de storage.

O que este portfólio tenta demonstrar:

- entendimento de modelagem OLTP e OLAP;
- capacidade de criar pipelines batch reproduzíveis;
- noção de separação entre origem, staging, warehouse, lake e lakehouse;
- uso de Docker Compose para ambientes locais;
- entendimento de dbt, Airflow, Spark, Kafka/Redpanda, Debezium, Trino e metastore;
- preocupação com idempotência, migração entre camadas, validação e estado final de cada etapa;
- visão de plataforma, não apenas scripts soltos.

Os capítulos com status **Ambiente base** ainda não implementam toda a integração. Eles existem para deixar clara a arquitetura planejada e o caminho de evolução. Os capítulos com status **Integração implementada** já possuem scripts/jobs executáveis.

## Como ler este repo

Cada capítulo foi pensado para rodar isoladamente, um por vez, com o próprio `docker-compose.yml` quando houver ambiente implementado. Não há objetivo de subir vários capítulos ao mesmo tempo.

Cada capítulo tem três documentos com papéis distintos:

- **README.md** — a narrativa: o cenário de negócio, por que a etapa existe, os conceitos e a "dor que sobra" que leva ao capítulo seguinte. É a camada conceitual, sem comandos de execução.
- **RUNBOOK.md** — o guia rápido: como **subir e usar** o ambiente, com os comandos, a saída esperada e as validações.
- **TECHNICAL.md** — contexto histórico da tecnologia, funcionamento interno, alternativas e tradeoffs.

Para começar por um capítulo, leia o README (o porquê) e siga o RUNBOOK (o como subir).

O repositório separa dois níveis de entrega:

- **Ambiente base** 🟡: sobe os serviços principais no Docker para estudo e evolução futura.
- **Integração implementada** 🟢: além do ambiente, já existe job/script/conector executável que move ou transforma dados.

Cada capítulo recria o estado final do anterior como seu estado inicial, executa sua própria evolução e termina em um novo estado final que vira o ponto de partida do próximo.

Para entender a empresa como um sistema completo, veja também [system-design](./system-design). Essa pasta consolida a arquitetura macro da NuvemStore: aplicação, domínios, plataforma de dados, redes, segurança, observabilidade e evolução temporal.

## Status da jornada

| Etapa | Capítulo | Status | Papel na história |
| --- | --- | --- | --- |
| [00](./00-modelagem-transacional) | Modelagem transacional | 🟢 Integração implementada | Define a origem OLTP e o seeder compartilhado. |
| [01](./01-modelagem-dimensional) | Modelagem dimensional | 🟡 Ambiente base | Desenha o star schema e os conceitos OLAP. |
| [02](./02-dimensional-no-oltp) | Dimensional no mesmo OLTP | 🟡 Ambiente base | Mostra analytics em outro schema, mas ainda dividindo recursos com a aplicação. |
| [03](./03-warehouse-dedicado) | Warehouse dedicado | 🟢 Integração implementada | Separa OLTP e warehouse em bancos diferentes e migra dados. |
| [04](./04-elt-batch-com-python) | ELT batch com Python | 🟢 Integração implementada | Extrai do OLTP, carrega raw no DuckDB e cria marts. |
| [05](./05-transformacao-com-dbt) | Transformação com dbt | 🟡 Ambiente base | Reimplementa transformações manuais como modelos testáveis. |
| [06](./06-ingestao-api-externa) | Ingestão batch de API externa | 🟡 Ambiente base | Adiciona uma fonte externa batch: transportadora. |
| [07](./07-orquestracao-com-airflow) | Orquestração com Airflow | 🟡 Ambiente base | Coordena OLTP, API externa, dbt, retries e backfill. |
| [08](./08-data-lake-com-spark) | Data Lake on-prem com HDFS | 🟡 Ambiente base | Sobe HDFS, Spark e metastore/catálogo para histórico, JSON e dados semi-estruturados. |
| [09](./09-migracao-hdfs-para-s3) | Migração HDFS para S3 | 🟡 Ambiente base | Simula legado HDFS e migração gradual para MinIO/S3. |
| [10](./10-lakehouse-medallion) | Lakehouse + Medallion | 🟡 Ambiente base | Evolui object storage para Delta/Medallion com gold consultável e tabelas catalogadas. |
| [11](./11-cdc-com-debezium) | CDC com Debezium | 🟡 Ambiente base | Sobe Postgres com WAL lógico, Redpanda e Kafka Connect. |
| [12](./12-streaming-kappa) | Streaming Kappa | 🟡 Ambiente base | Sobe Redpanda para métricas em tempo real. |
| [13](./13-base-ml-fraude) | Base de ML para fraude | 🟡 Ambiente base | Prepara feature table para modelo simples de fraude de pagamentos. |

## A jornada em uma frase

1. Primeiro entendemos como o dado nasce no OLTP.
2. Depois desenhamos como ele deveria ser lido em analytics.
3. Em seguida mostramos a evolução real: analytics no mesmo banco, depois warehouse separado.
4. Depois implementamos ELT batch com Python.
5. Então organizamos transformações com dbt.
6. Adicionamos uma fonte externa batch para criar a dor de múltiplas origens.
7. A partir daí entram Airflow, lake HDFS, migração para S3, lakehouse, CDC, streaming e base de ML conforme as dores aparecem.

## Maturidade da plataforma

| Nível | Capítulos | O que demonstra |
| --- | --- | --- |
| Fundação | 00-03 | Domínio, OLTP, dimensional e separação física de warehouse. |
| Batch analytics | 04-06 | ELT batch, dbt e ingestão de API externa. |
| Operação | 07 | Orquestração, dependências, retries e backfill. |
| Lake e migração | 08-09 | HDFS on-prem, Spark, metastore e migração gradual para S3/MinIO. |
| Lakehouse | 10 | Delta, camadas bronze/silver/gold, catálogo e gold consultável. |
| Baixa latência | 11-12 | CDC, eventos, streaming e métricas em tempo real. |
| Dados para ML | 13 | Feature table para fraude de pagamentos. |

## Fontes de dados ao longo da trilha

No futuro, a plataforma terá várias naturezas de fonte:

- **OLTP interno**: clientes, produtos, pedidos, pagamentos, entregas.
- **API externa batch**: transportadora, status de entrega, SLA e ocorrências.
- **Arquivos/lake**: histórico bruto, JSON, logs e dados semi-estruturados.
- **CDC**: mudanças do OLTP capturadas pelo WAL.
- **Streaming**: eventos de GPS e métricas operacionais em tempo real.
- **Base de ML**: feature table para fraude de pagamentos, combinando histórico, CDC e sinais recentes.

Isso deixa a história mais próxima de uma plataforma de dados real: fontes diferentes, latências diferentes, contratos diferentes e motores diferentes.

## Migrações entre ambientes

Quando uma tecnologia nova entra, ela não deve parecer um ambiente mágico criado do zero. Ela entra como evolução de uma plataforma que já existe.

A narrativa ideal é:

1. subir o ambiente novo;
2. recriar o estado final do capítulo anterior;
3. migrar ou materializar os dados na nova camada;
4. validar contagens e métricas;
5. desligar ou reduzir a camada antiga.

Checklist de passagem entre capítulos:

- o estado final do capítulo anterior está descrito no início do README seguinte ("De onde viemos");
- o capítulo seguinte recria esse estado no próprio compose ou nos seus jobs;
- existe uma validação mínima de equivalência;
- o que fica legado ou fallback está explicitamente documentado;
- nada importante depende de um container antigo ainda rodando.

| Etapa nova | O que reaproveita | O que muda | Como valida |
| --- | --- | --- | --- |
| `05 dbt` | marts SQL do ELT manual | reimplementa transformações como modelos dbt | compara contagens e métricas dos marts antigos vs dbt |
| `06 API externa` | warehouse e marts internos | adiciona staging batch da transportadora | valida idempotência e reconciliação por `pedido_id` |
| `07 Airflow` | OLTP, API externa e dbt | troca execução manual por DAG orquestrado | compara runs manuais vs runs orquestradas |
| `08 Data Lake HDFS` | warehouse, OLTP e API externa | descarrega dados crus/históricos para HDFS, processa com Spark e registra no metastore | compara volume carregado e amostras contra origem/warehouse |
| `09 Migração HDFS -> S3` | lake HDFS legado | migra histórico para S3/MinIO mantendo acesso federado | valida queries federadas e contagens por partição |
| `10 Lakehouse` | dados migrados para object storage e metastore | converte para Delta e organiza bronze/silver/gold | compara gold vs marts anteriores e verifica histórico/catálogo |
| `11 CDC` | OLTP e lakehouse existentes | passa a atualizar por eventos do WAL | compara snapshot inicial e eventos aplicados no destino |
| `12 Streaming` | log/eventos e lakehouse existentes | calcula métricas com janelas em tempo real | compara agregados streaming vs recomputação batch |
| `13 Base ML fraude` | lakehouse, CDC e streaming | materializa feature table para modelo de fraude | valida point-in-time correctness e ausência de duplicidade |

## Estrutura de cada capitulo

Cada projeto tende a ter:

- `README.md`: problema, arquitetura, conceitos e dor que sobra.
- `RUNBOOK.md`: como subir e usar o ambiente, com comandos, saída esperada e validações.
- `TECHNICAL.md`: história da tecnologia, funcionamento interno, alternativas e tradeoffs.
- `docker-compose.yml`: ambiente local do capítulo, quando implementado.
- `diagrams/architecture.py`: diagrama como código.
- jobs/scripts quando a integração já estiver implementada.

## Controles minimos por maturidade

Para não encher o repositório de ferramentas antes da hora, observabilidade, segurança e qualidade entram de forma incremental:

| Momento | Controle principal | Por que entra aqui |
| --- | --- | --- |
| 04 ELT batch | idempotência e contagem origem/destino | garante que reprocessar não duplica dados. |
| 05 dbt | testes de dados e contratos de schema | SQL vira produto confiável. |
| 06 API externa | checkpoint, validação de payload e tratamento de erro | API falha, muda contrato e pode retornar dados duplicados. |
| 07 Airflow | logs por task, retries, backfill e SLA simples | pipeline vira operação. |
| 08 Lake HDFS | validação de arquivos, partições e registro no metastore | arquivos precisam ser descobertos e auditáveis. |
| 09 Migração HDFS -> S3 | reconciliação por partição e comparação de query | migração sem validação quebra consumidores. |
| 10 Lakehouse | schema enforcement, time travel e auditoria de versão | tabelas passam a ter contrato transacional. |
| 11 CDC | lag, offsets e idempotência do sink | eventos podem atrasar ou duplicar. |
| 12 Streaming | consumer lag, checkpoint e watermark | stream exige controle de atraso e estado. |
| 13 ML fraude | point-in-time correctness e drift básico | features erradas geram modelo enganoso. |

Segurança também entra progressivamente: variáveis em `.env`, separação de credenciais por serviço, usuários distintos por camada e cuidado para não commitar segredos reais. Como o projeto é local e didático, o foco é mostrar os controles essenciais sem transformar cada capítulo em uma stack de segurança completa.

## Stack ao longo da jornada

PostgreSQL, DuckDB, Python, dbt, API HTTP, Apache Airflow, HDFS, MinIO, Apache Spark, Hive Metastore, Delta Lake, Trino, Redpanda/Kafka, Debezium e Metabase.

Tudo foi pensado para rodar localmente com Docker e sem conta em cloud.

## CI/CD

O repositório tem GitHub Actions em [.github/workflows/ci.yml](./.github/workflows/ci.yml). Hoje o CI valida sintaxe de YAML, `docker compose config`, Python, JSON e parse de projetos dbt quando existirem.

O CI valida estrutura e sintaxe. Ele não substitui testes end-to-end dos pipelines; esses entram conforme cada integração for implementada.

## Roadmap de implementacao

Todos os capítulos já possuem documentação completa (README, RUNBOOK, TECHNICAL). A implementação de código segue esta ordem de prioridade:

- [x] `00` a `04` — trilha inicial executável (OLTP, dimensional, warehouse, ELT batch).
- [ ] `05` — implementar modelos dbt reais (staging + marts).
- [ ] `06` — implementar extractor batch da API externa.
- [ ] `07` — implementar DAG Airflow chamando OLTP, API externa e dbt.
- [ ] `08` — implementar jobs Spark para o data lake.
- [ ] `09` — implementar migração HDFS -> S3 com tiering.
- [ ] `10` — implementar lakehouse medallion com Delta Lake.
- [ ] `11` — implementar consumer CDC com Debezium.
- [ ] `12` — implementar streaming Kappa com Structured Streaming.
- [ ] `13` — implementar feature builder de fraude.

O objetivo não é ter a maior stack possível. O objetivo é mostrar julgamento: quando cada tecnologia entra, qual dor ela resolve e como a plataforma evolui sem perder rastreabilidade.

## Roadmap futuro

Pontos que ainda deixariam a plataforma mais próxima do dia a dia de um time pleno:

- qualidade de dados com testes de contrato e expectativas;
- observabilidade de pipelines e dados;
- monitoramento do ambiente Docker/serviços;
- alertas de falha e SLA;
- lineage operacional entre fontes, jobs e tabelas;
- catálogo de dados mais completo, com ownership e descrição de tabelas;
- custos e métricas de performance por camada.
