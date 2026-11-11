# Solução — Capítulo 07

[O DAG](./airflow/dags/nuvemstore_daily.py) chama o lote da fundação e [os jobs manuais de entregas](../shared/entregas/jobs.py). LocalExecutor usa o mesmo volume DuckDB. O agendador limita as execuções simultâneas e os comandos manuais compartilham o lock do lote.

A tarefa da API retenta de forma independente. Um backfill passa o intervalo lógico para o extractor e preserva o checkpoint regular. O mart é recalculado para o instante da execução de reparo. A API publica o último estado disponível, de modo que reconstruir uma foto histórica exigiria versões ou snapshots preservados.

[O runbook](./RUNBOOK.md) mostra como iniciar, conferir e recuperar o DAG.
