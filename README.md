# Data Engineering Portfolio - uma jornada, nao uma pilha de projetos

Este repositorio conta a evolucao natural de uma plataforma de dados para a NuvemStore, um e-commerce ficticio com entregas proprias.

A regra da trilha: nenhuma ferramenta entra porque e "legal". Cada tecnologia aparece como resposta a uma dor concreta que a etapa anterior deixou clara.

Antes de seguir, leia o [COMPANY.md](./COMPANY.md). Ele descreve o dominio de negocio, as fontes de dados e as necessidades que guiam as decisoes tecnicas.

## Para recrutadores

A ideia deste repositorio e simular a evolucao do ambiente de dados de uma empresa, aumentando gradualmente o nivel de maturidade.

Ele nao e uma colecao de exemplos isolados. Cada projeto representa uma decisao comum em plataformas reais: primeiro entender a origem, depois separar analytics do transacional, depois lidar com multiplas fontes, orquestracao, lake, lakehouse, CDC, streaming, dados para ML e otimizacao fisica de storage.

O que este portfolio tenta demonstrar:

- entendimento de modelagem OLTP e OLAP;
- capacidade de criar pipelines batch reproduziveis;
- nocao de separacao entre origem, staging, warehouse, lake e lakehouse;
- uso de Docker Compose para ambientes locais;
- entendimento de dbt, Airflow, Spark, Kafka/Redpanda, Debezium, Trino e metastore;
- preocupacao com idempotencia, migracao entre camadas, validacao e estado final de cada etapa;
- visao de plataforma, nao apenas scripts soltos.

Os capitulos com status **Ambiente base** ainda nao implementam toda a integracao. Eles existem para deixar clara a arquitetura planejada e o caminho de evolucao. Os capitulos com status **Integracao implementada** ja possuem scripts/jobs executaveis.

## Como ler este repo

Cada capítulo foi pensado para rodar isoladamente, um por vez, com o próprio `docker-compose.yml` quando houver ambiente implementado. Não há objetivo de subir vários capítulos ao mesmo tempo.

Cada capítulo tem três arquivos com papéis distintos:

- **README.md** — a narrativa: o cenário de negócio, por que a etapa existe, os conceitos e a "dor que sobra" que leva ao capítulo seguinte. É a camada conceitual, sem comandos de execução.
- **RUNBOOK.md** — o guia rápido: como **subir e usar** o ambiente pronto, com os comandos, a saída esperada e as validações. É o que alguém segue para replicar o ambiente sem precisar construí-lo.
- **BUILD.md** — o guia avançado: o passo a passo de **construção**, as decisões de projeto e a "definição de pronto". É o roteiro de quem implementa o capítulo do zero.

O repositório separa dois níveis de entrega:

- **Ambiente base** 🟡: sobe os serviços principais no Docker para estudo e evolução futura; o BUILD descreve os jobs ainda a implementar.
- **Integração implementada** 🟢: além do ambiente, já existe job/script/conector executável que move ou transforma dados.

O capítulo atual recria o estado final do capítulo anterior como seu estado inicial (o "gabarito" em cada `STATE.md`), executa sua própria evolução e termina em um novo estado final que vira o gabarito do próximo.

Para entender a empresa como um sistema completo, veja também [system-design](./system-design). Essa pasta consolida a arquitetura macro da NuvemStore: aplicação, domínios, plataforma de dados, redes, segurança, observabilidade e evolução temporal.

## Status da jornada

| Etapa | Capitulo | Status | Papel na historia |
| --- | --- | --- | --- |
| [00](./00-modelagem-transacional) | Modelagem transacional | Integracao implementada | Define a origem OLTP e o seeder compartilhado. |
| [01](./01-modelagem-dimensional) | Modelagem dimensional | Modelo/documentacao | Desenha o star schema e os conceitos OLAP. |
| [02](./02-dimensional-no-oltp) | Dimensional no mesmo OLTP | Ambiente base | Mostra analytics em outro schema, mas ainda dividindo recursos com a aplicacao. |
| [03](./03-warehouse-dedicado) | Warehouse dedicado | Integracao implementada | Separa OLTP e warehouse em bancos diferentes e migra dados. |
| [04](./04-elt-batch-com-python) | ELT batch com Python | Integracao implementada | Extrai do OLTP, carrega raw no DuckDB e cria marts. |
| [05](./05-transformacao-com-dbt) | Transformacao com dbt | Ambiente/documentacao | Reimplementa transformacoes manuais como modelos testaveis. |
| [06](./06-ingestao-api-externa) | Ingestao batch de API externa | Ambiente/documentacao | Adiciona uma fonte externa batch: transportadora. |
| [07](./07-orquestracao-com-airflow) | Orquestracao com Airflow | Ambiente/documentacao | Coordena OLTP, API externa, dbt, retries e backfill. |
| [08](./08-data-lake-com-spark) | Data Lake on-prem com HDFS | Ambiente base | Sobe HDFS, Spark e metastore/catalogo para historico, JSON e dados semi-estruturados. |
| [09](./09-migracao-hdfs-para-s3) | Migracao HDFS para S3 | Ambiente base | Simula legado HDFS e migracao gradual para MinIO/S3. |
| [10](./10-lakehouse-medallion) | Lakehouse + Medallion | Ambiente base | Evolui object storage para Delta/Medallion com gold consultavel e tabelas catalogadas. |
| [11](./11-cdc-com-debezium) | CDC com Debezium | Ambiente base | Sobe Postgres com WAL logico, Redpanda e Kafka Connect. |
| [12](./12-streaming-kappa) | Streaming Kappa | Ambiente base | Sobe Redpanda para metricas em tempo real. |
| [13](./13-base-ml-fraude) | Base de ML para fraude | Ambiente base | Prepara feature table para modelo simples de fraude de pagamentos. |

## A jornada em uma frase

1. Primeiro entendemos como o dado nasce no OLTP.
2. Depois desenhamos como ele deveria ser lido em analytics.
3. Em seguida mostramos a evolucao real: analytics no mesmo banco, depois warehouse separado.
4. Depois implementamos ELT batch com Python.
5. Entao organizamos transformacoes com dbt.
6. Adicionamos uma fonte externa batch para criar a dor de multiplas origens.
7. A partir dai entram Airflow, lake HDFS, migracao para S3, lakehouse, CDC, streaming e base de ML conforme as dores aparecem.

## Maturidade da plataforma

| Nivel | Capitulos | O que demonstra |
| --- | --- | --- |
| Fundacao | 00-03 | Dominio, OLTP, dimensional e separacao fisica de warehouse. |
| Batch analytics | 04-06 | ELT batch, dbt e ingestao de API externa. |
| Operacao | 07 | Orquestracao, dependencias, retries e backfill. |
| Lake e migracao | 08-09 | HDFS on-prem, Spark, metastore e migracao gradual para S3/MinIO. |
| Lakehouse | 10 | Delta, camadas bronze/silver/gold, catalogo e gold consultavel. |
| Baixa latencia | 11-12 | CDC, eventos, streaming e metricas em tempo real. |
| Dados para ML | 13 | Feature table para fraude de pagamentos. |

## Fontes de dados ao longo da trilha

No futuro, a plataforma tera varias naturezas de fonte:

- **OLTP interno**: clientes, produtos, pedidos, pagamentos, entregas.
- **API externa batch**: transportadora, status de entrega, SLA e ocorrencias.
- **Arquivos/lake**: historico bruto, JSON, logs e dados semi-estruturados.
- **CDC**: mudancas do OLTP capturadas pelo WAL.
- **Streaming**: eventos de GPS e metricas operacionais em tempo real.
- **Base de ML**: feature table para fraude de pagamentos, combinando historico, CDC e sinais recentes.

Isso deixa a historia mais proxima de uma plataforma de dados real: fontes diferentes, latencias diferentes, contratos diferentes e motores diferentes.

## Migracoes entre ambientes

Quando uma tecnologia nova entra, ela nao deve parecer um ambiente magico criado do zero. Ela entra como evolucao de uma plataforma que ja existe.

A narrativa ideal e:

1. subir o ambiente novo;
2. recriar o estado final do capitulo anterior;
3. migrar ou materializar os dados na nova camada;
4. validar contagens e metricas;
5. desligar ou reduzir a camada antiga.

Checklist de passagem entre capitulos:

- o estado final do capitulo anterior esta descrito no `STATE.md`;
- o capitulo seguinte recria esse estado no proprio compose ou nos seus jobs;
- existe uma validacao minima de equivalencia;
- o que fica legado ou fallback esta explicitamente documentado;
- nada importante depende de um container antigo ainda rodando.

| Etapa nova | O que reaproveita | O que muda | Como valida |
| --- | --- | --- | --- |
| `05 dbt` | marts SQL do ELT manual | reimplementa transformacoes como modelos dbt | compara contagens e metricas dos marts antigos vs dbt |
| `06 API externa` | warehouse e marts internos | adiciona staging batch da transportadora | valida idempotencia e reconciliacao por `pedido_id` |
| `07 Airflow` | OLTP, API externa e dbt | troca execucao manual por DAG orquestrado | compara runs manuais vs runs orquestradas |
| `08 Data Lake HDFS` | warehouse, OLTP e API externa | descarrega dados crus/historicos para HDFS, processa com Spark e registra no metastore | compara volume carregado e amostras contra origem/warehouse |
| `09 Migracao HDFS -> S3` | lake HDFS legado | migra historico para S3/MinIO mantendo acesso federado | valida queries federadas e contagens por particao |
| `10 Lakehouse` | dados migrados para object storage e metastore | converte para Delta e organiza bronze/silver/gold | compara gold vs marts anteriores e verifica historico/catalogo |
| `11 CDC` | OLTP e lakehouse existentes | passa a atualizar por eventos do WAL | compara snapshot inicial e eventos aplicados no destino |
| `12 Streaming` | log/eventos e lakehouse existentes | calcula metricas com janelas em tempo real | compara agregados streaming vs recomputacao batch |
| `13 Base ML fraude` | lakehouse, CDC e streaming | materializa feature table para modelo de fraude | valida point-in-time correctness e ausencia de duplicidade |

## Estrutura de cada capitulo

Cada projeto tende a ter:

- `README.md`: problema, arquitetura, como subir o ambiente e dor que sobra.
- `STATE.md`: gabarito de implementacao com estado inicial, etapas, estado final, validacoes e passagem para o proximo capitulo.
- `TECHNICAL.md`: historia da tecnologia, funcionamento interno, alternativas e tradeoffs.
- `docker-compose.yml`: ambiente local do capitulo, quando implementado.
- `diagrams/architecture.py`: diagrama como codigo.
- jobs/scripts quando a integracao ja estiver implementada.

## Controles minimos por maturidade

Para nao encher o repositorio de ferramentas antes da hora, observabilidade, seguranca e qualidade entram de forma incremental:

| Momento | Controle principal | Por que entra aqui |
| --- | --- | --- |
| 04 ELT batch | idempotencia e contagem origem/destino | garante que reprocessar nao duplica dados. |
| 05 dbt | testes de dados e contratos de schema | SQL vira produto confiavel. |
| 06 API externa | checkpoint, validacao de payload e tratamento de erro | API falha, muda contrato e pode retornar dados duplicados. |
| 07 Airflow | logs por task, retries, backfill e SLA simples | pipeline vira operacao. |
| 08 Lake HDFS | validacao de arquivos, particoes e registro no metastore | arquivos precisam ser descobertos e auditaveis. |
| 09 Migracao HDFS -> S3 | reconciliacao por particao e comparacao de query | migracao sem validacao quebra consumidores. |
| 10 Lakehouse | schema enforcement, time travel e auditoria de versao | tabelas passam a ter contrato transacional. |
| 11 CDC | lag, offsets e idempotencia do sink | eventos podem atrasar ou duplicar. |
| 12 Streaming | consumer lag, checkpoint e watermark | stream exige controle de atraso e estado. |
| 13 ML fraude | point-in-time correctness e drift basico | features erradas geram modelo enganoso. |

Seguranca tambem entra progressivamente: variaveis em `.env`, separacao de credenciais por servico, usuarios distintos por camada e cuidado para nao commitar segredos reais. Como o projeto e local e didatico, o foco e mostrar os controles essenciais sem transformar cada capitulo em uma stack de seguranca completa.

## Stack ao longo da jornada

PostgreSQL, DuckDB, Python, dbt, API HTTP, Apache Airflow, HDFS, MinIO, Apache Spark, Hive Metastore, Delta Lake, Trino, Redpanda/Kafka, Debezium e Metabase.

Tudo foi pensado para rodar localmente com Docker e sem conta em cloud.

## CI/CD

O repositorio tem GitHub Actions em [.github/workflows/ci.yml](./.github/workflows/ci.yml). Hoje o CI valida sintaxe de YAML, `docker compose config`, Python, JSON e parse de projetos dbt quando existirem.

O CI valida estrutura e sintaxe. Ele nao substitui testes end-to-end dos pipelines; esses entram conforme cada integracao for implementada.

## Roadmap imediato

Prioridade para deixar o repositorio forte para curriculo:

1. Fechar `00` a `04` como trilha inicial executavel.
2. Implementar dbt real no `05`.
3. Implementar extractor batch da API externa no `06`.
4. Implementar Airflow real no `07` chamando OLTP, API externa e dbt.
5. Implementar jobs Spark no `08`.
6. Implementar migracao HDFS -> S3 no `09`.
7. Implementar lakehouse no `10`.
8. Implementar feature builder de fraude no `13`.

O objetivo nao e ter a maior stack possivel. O objetivo e mostrar julgamento: quando cada tecnologia entra, qual dor ela resolve e como a plataforma evolui sem perder rastreabilidade.

## Roadmap futuro

Pontos que ainda deixariam a plataforma mais proxima do dia a dia de um time pleno:

- qualidade de dados com testes de contrato e expectativas;
- observabilidade de pipelines e dados;
- monitoramento do ambiente Docker/servicos;
- alertas de falha e SLA;
- lineage operacional entre fontes, jobs e tabelas;
- catalogo de dados mais completo, com ownership e descricao de tabelas;
- custos e metricas de performance por camada.
