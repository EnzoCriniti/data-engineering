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
- **Integração implementada** 🟢: além do ambiente, já existe job/script/conecto