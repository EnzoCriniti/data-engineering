# Solução — Funil no lakehouse

O [job Spark](../shared/navegacao/lake.py) publica e lê snapshots Delta por caminho. Bronze conserva os lotes Parquet aprovados pelo [manifesto](../shared/navegacao/migration.py). A [normalização](../shared/navegacao/events.py) valida, deduplica e enriquece a silver com os pedidos pagos do snapshot. [O SQL](./sql/funil.sql) calcula as etapas na ordem, dentro da sessão e antes de completar 30 minutos.

A gold registra sua versão, a versão silver, o hash do código e os hashes dos lotes. Uma reexecução da mesma entrada reaproveita as versões. A chegada tardia publica uma nova versão e permite consultar a anterior com `versionAsOf`.

[Siga o runbook](./RUNBOOK.md) para consultar a saída e gerar evidências.
