# Solução — Snapshot no HDFS

- [Contrato v1](../shared/navegacao/evento-v1.schema.json) e [gerador](../shared/navegacao/generate.py) definem a fonte sintética.
- [Compose compartilhado](../10-lakehouse-medallion/docker-compose.yml) disponibiliza o perfil `hdfs`.
- [Comando `ingest`](../shared/navegacao/lake.py) e [envelopes de eventos](../shared/navegacao/events.py) preservam o JSON original. O snapshot candidato é promovido no HDFS após concluir a gravação de eventos e pedidos.

O particionamento deriva de UTC e separa registros inválidos para inspeção. O replay verifica o hash do multiconjunto em disco antes de aceitar o snapshot existente. [Reprodução](./RUNBOOK.md)
