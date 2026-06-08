# Complemento técnico — Observabilidade de dados

## O que este capítulo aprofunda

Este capítulo mostra a diferença entre monitorar *software* (o serviço está de pé?) e observar *dados* (o dado está fresco, completo e no padrão?). O diferencial é entender os pilares próprios de dados — freshness, volume, schema, distribuição, lineage — e como definir SLOs que geram alerta acionável em vez de ruído.

## Pequena história

Monitoramento de infra é antigo (Nagios nos anos 1990, depois Prometheus em 2012, Grafana em 2014). Mas esses medem CPU, memória e latência — não pegam um pipeline que roda "com sucesso" e entrega dado errado.

A categoria **data observability** se formou por volta de 2019–2021, popularizada pela Monte Carlo, que cunhou os "cinco pilares" (freshness, volume, schema, distribuição, lineage). Surgiram alternativas open source como **Elementary** (observabilidade nativa do dbt) e **re_data**. A ideia central: tratar dado como produto que tem SLAs, e instrumentar o pipeline para detectar incidentes de *dados*, não só de *infra*.

## Por baixo dos panos

### Os cinco pilares

- **Freshness**: idade do dado mais recente (`now() - max(ts)`). Detecta jobs que pararam.
- **Volume**: contagem do último lote vs histórico. Detecta jobs meio-quebrados.
- **Schema**: mudança de estrutura (coberto pelos contratos do cap 15).
- **Distribuição**: os valores de uma coluna saíram do padrão (média, nulos, cardinalidade mudaram bruscamente).
- **Lineage**: o grafo de dependências, para diagnóstico de causa-raiz.

### Push vs pull

Há dois modelos de coleta. No **pull** (estilo Prometheus), um coletor central raspa métricas expostas por cada serviço periodicamente. No **push**, cada job empurra suas métricas para um gateway ao terminar. Para métricas de pipeline (que rodam em batch e não ficam de pé), o push costuma encaixar melhor — o job reporta "processei N linhas, freshness X" ao fim. O gabarito deste capítulo é essencialmente um coletor pull simplificado consultando o gold via Trino.

### Onde os SLOs disparam

Um SLO violado pode: (a) falhar a task de orquestração (a DAG para — o que o gabarito faz com `sys.exit(1)`); (b) abrir um incidente / paginar alguém; (c) só registrar para um painel. A escolha depende da gravidade. Freshness de um mart crítico → paginar; volume levemente abaixo → registrar e revisar.

### Calibração e alert fatigue

O fracasso clássico de observabilidade é alertar demais. A calibração usa o histórico: limiar de volume como fração da média móvel, freshness com folga sobre a cadência esperada, e janelas (não alertar por um pico isolado de 1 min). SLO bem calibrado = alerta raro = alerta levado a sério.

## Por que entra depois de qualidade

Qualidade (cap 15) valida o *dado*; observabilidade valida o *processo*. Faz sentido nesta ordem: primeiro você garante que o conteúdo que entra é válido, depois que o mecanismo que o produz está saudável e visível. Juntos, são os controles que transformam "roda no meu laptop" em "opera em produção".

## Tecnologias equivalentes

| Ferramenta | Quando usar |
| --- | --- |
| Prometheus + Grafana | Métricas de infra e de pipeline; padrão open source para dashboards. |
| Elementary | Observabilidade nativa do dbt, com relatórios e anomalias. |
| Monte Carlo / Bigeye | Plataformas gerenciadas com detecção automática de anomalias. |
| re_data | Observabilidade open source focada em dbt. |
| OpenLineage / Marquez | Padrão e backend de lineage entre jobs e datasets. |

## Quando usar

Use observabilidade de dados a partir do momento em que decisões de negócio dependem das tabelas — ou seja, assim que há um consumidor que se importa com freshness e completude. Para um pipeline experimental sem consumidor, é exagero.

Comece pelo barato e de alto valor: freshness e volume nas tabelas de saída. Distribuição e lineage automatizado vêm depois, conforme a plataforma cresce.

## Como isso aparece no projeto

Este capítulo instrumenta as tabelas gold da plataforma (via Trino) com freshness e volume vs SLOs, fechando o último controle essencial de produção. É o que teria pego o "gold de velocidade que parou de respirar" no instante em que o streaming parou.

## 📚 Referências

- [Google SRE Book — SLOs](https://sre.google/sre-book/service-level-objectives/) — como definir objetivos de nível de serviço.
- [The Five Pillars of Data Observability (Monte Carlo)](https://www.montecarlodata.com/blog-what-is-data-observability/) — origem do framework.
- [Elementary Docs](https://docs.elementary-data.com/) — observabilidade nativa do dbt.
- [OpenLineage](https://openlineage.io/) — padrão aberto de lineage.
