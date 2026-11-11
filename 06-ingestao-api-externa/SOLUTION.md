# Solução — Capítulo 06

[A API de exemplo](./api/app.py) serve páginas ordenadas por `(updated_at, entrega_id)`. O cursor carrega o recorte da primeira página. O ambiente cumulativo gera entregas sintéticas a partir dos pedidos que o simulador marcou como terceirizados.

[O extractor](./extractor/extract.py) repete uma faixa inclusiva em torno do último `updated_at` confirmado. A chave da entrega impede duplicação. Versões antigas são ignoradas e conflitos na mesma versão interrompem a carga. O payload cru e o checkpoint entram na mesma transação DuckDB. Uma janela de reparo é delimitada por `--start` e `--end` e preserva o checkpoint regular.

[O mart de SLA](../05-transformacao-com-dbt/models/marts/mart_sla_entregas.sql) cruza entregas com pedidos. Órfãos, cancelados, devoluções, extravios e dados inválidos ficam disponíveis no [mart de exceções](../05-transformacao-com-dbt/models/marts/mart_excecoes_entregas.sql). O [runbook](./RUNBOOK.md) reproduz a carga e a correção.
