# Diário da etapa 4 — Histórico de navegação

A fase 3 da história da NuvemStore reúne os capítulos 08–10. A entrega usa HDFS no laboratório de migração e MinIO com Spark sob demanda no ambiente cumulativo.

## Evidências da revisão

A fixture do dia 10/11/2026 usa quatro sessões. O teste rápido em SQLite confirmou `4 → 3 → 2 → 1` e `4 → 3 → 2 → 2` com chegada tardia. O job de integração usa dois pedidos pagos do PostgreSQL populado com o seeder reaproveitado na fase 2. Os horários de navegação pertencem à fixture. Os IDs e o status vêm do snapshot do OLTP.

A saída base esperada tem 16 linhas de bronze, um inválido, um retry e perda de 50% na passagem de checkout a compra. A gold guarda os IDs convertidos e a versão silver usada. [Reproduzir o teste integrado](../../10-lakehouse-medallion/RUNBOOK.md#validar) · [PR de revisão](https://github.com/EnzoCriniti/data-engineering/pull/4)

## Aceite no Agent Platform

1. Depois do aceite da fase 2 e da revisão da PR, atualizar a base para a `main` e seguir o [fluxo de publicação](../deploy-nas-agent-platform.md#fluxo-de-uma-etapa-até-o-nas).
2. Cadastrar `NAVEGACAO_MINIO_USER` e `NAVEGACAO_MINIO_PASSWORD` nos segredos do ambiente. O MinIO interno usa o volume nomeado `navegacao-data`. O volume `navegacao-lock` serializa as invocações do job.
3. Conferir os limites cumulativos no validador. O overlay acrescenta 512 MiB residentes para MinIO e 1.536 MiB durante Spark. Os limites propostos para produção são 768 MiB e 2.048 MiB, respectivamente. Medir o consumo e o pico com a fase 2 ativa.
4. Rodar o job `navegacao` na aba Etapas. Conferir `4 → 3 → 2 → 1`, a associação com um pedido pago do ambiente e os hashes dos lotes. Repetir e conferir as mesmas versões.
5. Parar e redeployar o staging preservando volumes. Rodar o job de novo e conferir os mesmos hashes, versão e resultado. Guardar SHA, logs, consumo medido e teste de persistência antes da tag e da aprovação de produção.

O resultado é consultado pelo Spark no próprio job. O catálogo e a consulta via Trino continuam como evolução do plano, condicionada à medição de recursos. Nenhuma publicação da fase 3 foi feita no NAS.

A imagem MinIO é construída a partir da release comunitária fixada em [minio.Dockerfile](../../10-lakehouse-medallion/minio.Dockerfile). O build do Agent Platform precisa acessar os registries e o proxy de módulos Go.
