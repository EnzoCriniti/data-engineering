# Solução — Capítulo 05

[O projeto dbt](./dbt_project.yml) lê as tabelas `raw_*` em `main`. [Os modelos de staging](./models/staging/) convertem as colunas do lote antes de os [marts](./models/marts/) aplicarem as regras. O perfil publica em `analytics_dbt` e permite comparar o resultado com os marts da fundação. Valores monetários usam decimal e o ranking tem desempate estável.

No capítulo 06, o mesmo perfil cruza a fonte da transportadora com `stg_pedidos`. Os [testes](./tests/) conferem grão e elegibilidade para o SLA. Use o [runbook](./RUNBOOK.md) para rodar apenas os modelos de vendas antes de carregar a segunda fonte.
