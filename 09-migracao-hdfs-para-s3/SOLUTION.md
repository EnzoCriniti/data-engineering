# Solução — Reconciliação da migração

O [módulo de migração](../shared/navegacao/migration.py) calcula o SHA-256 do conteúdo canônico, escreve um prefixo candidato e compara o Parquet relido de HDFS e MinIO. O relatório guarda contagens, IDs distintos, repetições, limites de horário e o funil dos dois lados. A liberação exige igualdade de tipos e do multiconjunto completo, além da igualdade do funil por sessão e por coorte.

O [teste integrado](../shared/navegacao/integration.py) altera uma linha sem mudar contagens e exige que o candidato seja rejeitado. O [runbook](./RUNBOOK.md) mostra como produzir o relatório.
