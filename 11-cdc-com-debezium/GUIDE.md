# Cap. 11 — CDC com Debezium: capturando mudanças em tempo real

> **Aula deste capítulo.** Você aprende **CDC** (Change Data Capture) — escutar o WAL do Postgres via **Debezium** para receber INSERT/UPDATE/DELETE em near-real-time, sem polling. A orientação está aqui; o JSON do conector e o consumer estão no **[SOLUTION.md](./SOLUTION.md)**; os internals (logical replication, slots, envelope Debezium, semântica at-least-once) estão no **[TECHNICAL.md](./TECHNICAL.md)**.

## O problema que este capítulo resolve

O lakehouse do capítulo 10 processa em batch — dados só ficam atualizados após a execução do job. Se um pagamento é atualizado no OLTP agora, o lakehouse só reflete a mudança horas depois. Para casos como fraude e monitoramento, isso é lento demais.

CDC (Change Data Capture) resolve: em vez de fazer polling na origem, o pipeline **escuta o WAL do Postgres** e recebe eventos de INSERT, UPDATE e DELETE em tempo real. Debezium faz isso via Kafka Connect.

## Pré-requisitos

- **Capítulo anterior:** 10 concluído (lakehouse Medallion).
- **Docker:** versão 24+ com Docker Compose.

## Conceitos fundamentais

### O que é CDC

CDC captura mudanças no banco de dados lendo o log de transações (WAL no Postgres). Diferente de polling (`SELECT * WHERE updated_at > last_run`), CDC:
- Não sobrecarrega a origem com queries repetidas.
- Captura DELETEs (que polling não detecta).
- Opera em near-real-time (segundos, não horas).
- Preserva a ordem cronológica das mudanças.

**Exemplo trabalhado — o DELETE que o polling nunca vê.** Suponha o pipeline antigo: `SELECT * FROM pagamento WHERE updated_at > last_run` a cada 5 min. Um pagamento fraudulento é inserido às 10h00 e *removido* pelo antifraude às 10h02. Quando o polling roda às 10h05, a linha já não existe — o pipeline nunca soube que ela existiu nem que sumiu. Pior: se a coluna `updated_at` não for atualizada num UPDATE, o polling também perde a mudança. CDC lê o **WAL**, que registra *toda* operação física na ordem em que aconteceu: ele vê o INSERT às 10h00 *e* o DELETE às 10h02 como dois eventos. Para fraude e auditoria, capturar o que foi apagado é justamente o ponto.

### WAL e logical replication

O Postgres registra toda mudança no WAL (Write-Ahead Log) antes de aplicá-la. Com `wal_level=logical`, o Postgres expõe mudanças em formato consumível. Debezium atua como uma réplica lógica: lê o WAL, controla offset, e transforma mudanças em eventos.

### Debezium: snapshot + streaming

O fluxo tem duas fases:
1. **Snapshot inicial**: copia o estado atual completo de cada tabela.
2. **Streaming**: a partir daí, publica apenas mudanças novas (INSERT, UPDATE, DELETE).

Cada evento carrega: chave, estado anterior (`before`), estado novo (`after`), operação (`c`=create, `u`=update, `d`=delete), e metadados (LSN, timestamp, transação).

### Kafka Connect

Framework que gerencia conectores. Debezium é o connector de **source** (publica eventos em tópicos). Um **sink** posterior pode gravar em Delta Lake, Postgres, Elasticsearch, ou S3. O Connect gerencia configuração, offsets, tarefas e tolerância a falhas.

### Redpanda como alternativa ao Kafka

Redpanda implementa o protocolo Kafka em C++. Mais simples de operar (sem ZooKeeper, sem JVM), com mesma API. Para um portfolio local, é mais leve que Kafka.

### At-least-once e idempotência

Pipelines de eventos geralmente entregam at-least-once — uma mensagem pode ser entregue mais de uma vez (retry após timeout). O destino precisa ser idempotente: `MERGE` por PK e versão do evento garante que duplicatas não viram linhas duplicadas.

**Exemplo trabalhado — a mesma mudança entregue duas vezes.** O consumer lê o evento "pedido P-9 mudou para `pago`" (LSN 5000), aplica no Delta, mas cai antes de confirmar o offset. No restart, o Kafka re-entrega o *mesmo* evento — isso é at-least-once. Com um `INSERT` ingênuo, P-9 viraria duas linhas. Com `MERGE` por PK + `WHEN MATCHED AND source.lsn > target.lsn`: na segunda vez, `target.lsn` já é 5000 e `source.lsn` (5000) não é *maior*, então o MERGE não faz nada — a duplicata é absorvida. O mesmo predicado protege contra eventos fora de ordem: um evento velho (LSN 4000) chegando depois nunca sobrescreve o estado novo. A versão (LSN) é o que torna o destino seguro contra replays e reordenações.

---

## Etapa 1 — Configurar o ambiente CDC

### O que fazer
Compose com: OLTP (Postgres com `wal_level=logical`), Redpanda (ou Kafka), Kafka Connect com plugin Debezium, console para visualizar tópicos.

### ⚠️ Armadilhas
- Postgres precisa de `wal_level=logical` e `max_replication_slots >= 2`. Sem isso, Debezium falha silenciosamente.
- Debezium precisa de um slot de replicação dedicado. Se o slot não for limpo após remoção do conector, o WAL cresce indefinidamente e pode encher o disco.

---

## Etapa 2 — Registrar o conector Debezium

### O que fazer
POST para a API do Kafka Connect com configuração JSON: database hostname, port, user, password, tabelas a capturar, serialização (JSON ou Avro), slot name.

### ⚠️ Armadilhas
- Não definir `slot.name` explícito: Debezium cria nome automático que é difícil de rastrear.
- Não definir `publication.autocreate.mode`: pode capturar tabelas que não deveria.

---

## Etapa 3 — Implementar consumer que grava no lakehouse

### Contexto
Um consumer Spark Structured Streaming (ou script Python) que lê tópicos do Redpanda e faz MERGE nas tabelas Delta da camada bronze/silver.

### Decisões de design
- *MERGE por PK + versão*: `WHEN MATCHED AND source.lsn > target.lsn THEN UPDATE`. Garante que eventos fora de ordem não sobrescrevem dados mais recentes.
- *Tratamento de deletes*: marcar como `_deleted=true` em vez de DELETE físico. Permite audit trail.

### O que fazer
`consumer/cdc_to_delta.py`: Spark Structured Streaming lendo de Redpanda, parseando envelope Debezium, aplicando MERGE na tabela Delta.

---

## ✅ Checklist final

- [ ] OLTP configurado com `wal_level=logical`
- [ ] Conector Debezium registrado e em estado RUNNING
- [ ] Tópicos criados no Redpanda para cada tabela capturada
- [ ] INSERT/UPDATE/DELETE no OLTP geram eventos nos tópicos
- [ ] Consumer aplica MERGE no lakehouse sem duplicatas
- [ ] Re-processar mensagens (replay) não corrompe dados (idempotência)

Compreensão (você entendeu — responda sem olhar):

- [ ] Conte o cenário do pagamento inserido e removido entre dois pollings: por que CDC vê e o polling não?
- [ ] O que `wal_level=logical` habilita, e o que acontece com o disco se um slot de replicação não for limpo?
- [ ] Quais as duas fases do Debezium (snapshot e streaming) e o que cada evento carrega (`before`/`after`/op/LSN)?
- [ ] Por que `MERGE` por PK + LSN protege contra **replays** *e* contra eventos **fora de ordem**?

## A dor que sobra

CDC captura mudanças, mas o lakehouse ainda processa em micro-batches. Para métricas em tempo real (entregas ativas, velocidade de entregadores), é preciso processar o stream continuamente. O capítulo 12 introduz a arquitetura Kappa com Spark Structured Streaming.
