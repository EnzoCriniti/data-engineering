# Cap. 12 — Streaming Kappa: processamento contínuo de eventos

> **Aula deste capítulo.** Você aprende a arquitetura **Kappa** — processar tudo via streaming contínuo com **Spark Structured Streaming**: janelas, event-time, watermark, estado e checkpoint. A orientação está aqui; o código do produtor GPS e do `streaming_gps.py` está no **[SOLUTION.md](./SOLUTION.md)**; os internals (micro-batch vs continuous, gestão de estado, semântica de watermark) estão no **[TECHNICAL.md](./TECHNICAL.md)**.

## O problema que este capítulo resolve

O CDC do capítulo 11 captura mudanças no OLTP, mas o lakehouse ainda processa em batch/micro-batch. A NuvemStore tem entregadores com GPS gerando eventos a cada segundo — volume contínuo que precisa de métricas ao vivo: entregas ativas por região, velocidade média, alertas de desvio.

A arquitetura Kappa usa apenas o caminho de streaming para tudo: métricas em tempo real, reprocessamento histórico (replay do log), e alimentação de features para ML. Um único paradigma em vez de manter batch + streaming separados (Lambda).

## Pré-requisitos

- **Capítulo anterior:** 11 concluído (CDC operando).
- **Docker:** versão 24+ com Docker Compose.

## Conceitos fundamentais

### Kappa vs Lambda

**Lambda**: dois caminhos — batch (correto mas lento) e streaming (rápido mas aproximado). Mantém dois codebases sincronizados. Complexo operacionalmente.

**Kappa**: apenas streaming. Para reprocessar, basta reler o log desde o início ou desde um offset. Simplifica a arquitetura quando o log é retido por tempo suficiente e a engine de streaming é confiável.

**Exemplo trabalhado — o bug que você corrige uma vez, não duas.** Descobre-se que o cálculo de "velocidade média por região" estava errado (dividia pela contagem errada). Em **Lambda**, esse cálculo existe em *dois* lugares — o job batch e o job streaming — e você precisa corrigir, testar e fazer deploy dos dois, torcendo para que fiquem idênticos; se divergirem, o número ao vivo e o número histórico se contradizem. Em **Kappa**, existe só um job de streaming. Você corrige o código uma vez e faz **replay**: reposiciona o consumer para o offset inicial do log e deixa o mesmo job reprocessar todo o histórico com a lógica nova. Um codebase, uma verdade. Isso só funciona porque o log (Redpanda) retém os eventos tempo suficiente para reler.

### Janelas de tempo

Stream é infinito — para calcular métricas, recorta-se em janelas:
- **Tumbling**: janelas fixas sem sobreposição (ex: a cada 5 min).
- **Sliding**: janelas que se sobrepõem (ex: janela de 10 min a cada 1 min).
- **Session**: baseada em atividade — fecha quando há inatividade por N minutos.

### Event time vs processing time

- **Event time**: quando o evento aconteceu (timestamp do GPS).
- **Processing time**: quando o sistema recebeu.

Eventos atrasam. Um GPS enviado às 14:00 pode chegar às 14:03. Se a janela de 14:00-14:05 já fechou no processing time, o evento é perdido. **Watermark** define quanto atraso é tolerado antes de fechar a janela.

**Exemplo trabalhado — o GPS atrasado e o watermark de 2 minutos.** Um entregador entra num túnel às 14:04; o celular guarda os pontos e só envia quando sai, às 14:07. Esse evento tem **event time** 14:04 mas **processing time** 14:07. A métrica é "velocidade média na janela 14:00–14:05". Sem watermark, o Spark fecharia a janela assim que o relógio do *sistema* passasse de 14:05 e o ponto das 14:04 chegaria tarde demais — perdido. Com `withWatermark("event_time", "2 minutes")`, o Spark promete manter a janela 14:00–14:05 aberta até ter visto event-times até ~14:07, então o ponto atrasado *ainda entra* no cálculo certo. O tradeoff é direto: watermark maior tolera mais atraso mas adia o resultado; menor materializa rápido mas descarta retardatários. Você sintoniza pela cauda real de atraso dos seus eventos.

### Estado e checkpoint

Agregações de streaming mantêm **estado**: contagens parciais por chave e janela. O Spark salva checkpoints periodicamente. Se o processo cai, volta do último checkpoint sem reprocessar tudo.

### Backpressure

Quando produtores geram eventos mais rápido que consumidores processam, o lag cresce. Sistemas maduros precisam: auto-scaling de consumidores, monitoramento de lag, e alertas.

---

## Etapa 1 — Criar produtor de eventos GPS

### O que fazer
Script Python que simula entregadores enviando coordenadas GPS para tópico no Redpanda. Cada evento: `entregador_id`, `latitude`, `longitude`, `velocidade`, `timestamp`, `pedido_id`.

### Decisões de design
- *Produção contínua*: loop infinito com `time.sleep(1)` simulando GPS a cada segundo.
- *Múltiplos entregadores*: N entregadores simultâneos com rotas simuladas.
- *Serialização JSON*: simples e inspecionável. Avro seria mais eficiente mas adiciona complexidade com Schema Registry.

---

## Etapa 2 — Implementar consumer Spark Structured Streaming

### Contexto
Job Spark que lê o tópico GPS, calcula métricas por janela, e grava resultados.

### Decisões de design
- *Tumbling window de 5 minutos*: velocidade média por região.
- *Watermark de 2 minutos*: tolera atraso de até 2 min.
- *Output mode append*: grava apenas janelas finalizadas. Evita reescrita contínua.
- *Sink em Delta Lake*: métricas históricas preservadas com transações.

### O que fazer
`spark/jobs/streaming_gps.py`: SparkSession com Structured Streaming, lê do Redpanda, aplica watermark, calcula `avg(velocidade)` por `regiao` e window de 5 min, grava Delta em `s3a://lakehouse/gold/velocidade_regional/`.

### ⚠️ Armadilhas
- Watermark muito curto: perde eventos atrasados. Muito longo: atrasa materialização.
- Não configurar `spark.sql.streaming.checkpointLocation`: sem checkpoint, o job reprocessa tudo do zero ao reiniciar.
- Output mode `complete` reescreve toda a tabela a cada trigger — ineficiente para volumes grandes.

---

## Etapa 3 — Monitoramento e lag

### O que fazer
Monitorar consumer lag no Redpanda console. Se lag cresce consistentemente, o consumer não está acompanhando — precisa de mais recursos ou otimização.

---

## ✅ Checklist final

- [ ] Produtor GPS envia eventos continuamente para Redpanda
- [ ] Consumer Spark Structured Streaming processa sem erro
- [ ] Métricas de velocidade por região aparecem na tabela Delta gold
- [ ] Watermark funciona: eventos dentro da tolerância são incluídos
- [ ] Checkpoint funciona: reiniciar o job continua do ponto anterior
- [ ] Consumer lag é monitorável no console

Compreensão (você entendeu — responda sem olhar):

- [ ] Por que Kappa corrige um bug de métrica uma vez e Lambda duas? O que "replay" exige do log?
- [ ] Diferencie tumbling, sliding e session window com um exemplo de cada.
- [ ] Conte o cenário do GPS que sai do túnel: o que watermark resolve e qual é o tradeoff de ajustá-lo?
- [ ] O que o checkpoint guarda, e o que acontece sem ele quando o job reinicia?

## A dor que sobra

Agora a plataforma tem dados históricos (batch) e dados em tempo real (streaming). O próximo passo é combinar ambos para um caso de negócio concreto: detecção de fraude. O capítulo 13 constrói a feature table que alimenta um modelo de ML, com garantia de point-in-time correctness.
