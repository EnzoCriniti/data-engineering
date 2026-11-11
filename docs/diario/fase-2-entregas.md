# Diário — Entregas com múltiplas fontes

A NuvemStore terceirizou parte das entregas. Logística precisava localizar as remessas ainda em trânsito depois da previsão, sem misturar o volume com a frota própria ou esconder pedidos órfãos.

## Decisões

- O cap. 05 usa o DuckDB da fundação e materializa em `analytics_dbt`. O cap. 06 escreve o JSON cru e o checkpoint em `staging`.
- O grão do SLA é a entrega externa. O cruzamento usa `pedido_id` do OLTP. A igualdade com o prazo fica dentro do SLA. A consulta de exceções mantém órfãos, cancelados, devoluções, extravios e registros inválidos visíveis.
- A carga compara `updated_at` e grava o checkpoint junto com a janela. O backfill do Airflow repara a janela disponível da fonte e preserva a versão mais recente da entrega.

## Provas

| Ambiente | Resultado |
| --- | --- |
| Desktop via SSH, Python 3.11 e DuckDB 1.1.0 | 9 entregas em páginas de duas. `401`, `429` e falha na segunda página exercitados. Reexecução sem alteração, conflito de versões detectado e checkpoint preservado após falha e backfill. |
| dbt 1.9.4 | Dois builds com 8 modelos e 15 testes aprovados cada. Na primeira consulta, TRX-0 estava 7.200 s em atraso. Após a atualização para entregue, restaram zero atrasos abertos. |
| Agent Platform `47af4ba` | Manifesto e overlay aceitos sem avisos. O validador calculou limites de 3.168 MiB em staging e 3.840 MiB em produção, incluindo o maior job. O pico real será medido no NAS. |

## Aceite no NAS

1. Concluir o aceite da fundação. Promover os commits revisados pelo fluxo do Agent Platform, com staging antes de produção. As publicações de transformação e de fontes/orquestração têm marcos próprios no [plano](../plano-de-implementacao.md).
2. Cadastrar `TRANSPORTADORA_API_KEY`, `AIRFLOW_DB_PASSWORD` e `AIRFLOW_SECRET_KEY` no cofre de staging. Preservar os volumes `oltp-data`, `warehouse-data` e `duckdb-data`. Verificar que o agendador antigo foi interrompido pelo redeploy antes de ativar o DAG.
3. Conferir `airflow-init`, executar `seeder` para bootstrap de staging novo e rodar `pipeline` e `dbt` para conferir vendas. Rodar `airflow-ativar` e acompanhar a primeira execução. Use o job `sla` para coletar a consulta e os totais.
4. Conferir retry/backfill e persistência dos checkpoints e dos metadados após redeploy. Medir memória e tempo dos jobs, anexar logs à revisão e seguir a aprovação de produção.

## Evidência para o portfólio

Mostrar o pedido com atraso aberto, a atualização que o retira da lista e a recuperação da carga. A evidência de staging deve identificar o commit, o DAG run e o checkpoint. A publicação no NAS fica pendente até o aceite.
