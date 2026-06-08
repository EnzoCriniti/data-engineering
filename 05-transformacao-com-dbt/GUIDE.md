# Cap. 05 — Transformação com dbt: SQL como código testável

> **Aula deste capítulo.** Você aprende a tratar SQL como código versionado e testável com **dbt** — `ref()`, materializações, testes declarativos e lineage. A orientação está aqui; o código dos modelos e do `schema.yml` está no **[SOLUTION.md](./SOLUTION.md)**; os internals (como o dbt compila Jinja em SQL, ordena o DAG, e materializa view vs table vs incremental) estão no **[TECHNICAL.md](./TECHNICAL.md)**.

## O problema que este capítulo resolve

No capítulo 04, transformações são SQL solto dentro de strings Python. Não há como saber de onde veio cada coluna, não há testes automáticos, e uma mudança no schema upstream quebra tudo silenciosamente. Se o mart de receita está errado, ninguém descobre até um analista reclamar.

dbt resolve isso tratando SQL como código: modelos com dependências explícitas (`ref()`), testes declarativos, documentação gerada, e materialização configurável. A transformação sai do Python e vai para onde pertence — o destino analítico.

## Pré-requisitos

- **Capítulo anterior:** 04 concluído (raw layer em DuckDB).
- **Docker:** versão 24+ com Docker Compose.

## Conceitos fundamentais

### O que dbt faz (e o que não faz)

dbt **transforma** dados que já estão no destino. Ele NÃO extrai, NÃO carrega, NÃO orquestra. Ele espera que raw já exista (cap 04 faz isso) e transforma em staging e marts.

### ref() e o DAG de dependências

Em vez de escrever `FROM raw_cliente`, escreve-se `FROM {{ ref('stg_clientes') }}`. O dbt monta automaticamente o DAG: sabe que `mart_receita_diaria` depende de `stg_pedidos` que depende de `raw_pedido`. Se `stg_pedidos` falhar, os marts downstream não executam.

**Exemplo trabalhado — por que `ref()` e não o nome da tabela.** Suponha dois modelos: `mart_receita_diaria` lê de `stg_pedidos`. Se você escrever `FROM stg_pedidos` (string crua), o dbt não sabe que existe dependência — ele pode tentar construir o mart *antes* do staging, e a query falha porque a tabela ainda não existe. Pior: se `stg_pedidos` for renomeado, nada avisa que o mart quebrou. Com `FROM {{ ref('stg_pedidos') }}`, o dbt (1) descobre a ordem correta sozinho — staging primeiro, mart depois; (2) desenha o lineage `raw_pedido → stg_pedidos → mart_receita_diaria`; (3) se o staging falhar, *pula* o mart em vez de rodá-lo com dados velhos. O `ref()` é o que transforma SQL solto em um grafo gerenciado.

### Materializações

- **view**: recalcula a cada leitura. Bom para staging — não duplica dados, sempre reflete o estado atual do raw.
- **table**: persiste como tabela real. Bom para marts consumidos por BI — consulta rápida.
- **incremental**: processa apenas dados novos. Complexo mas necessário para volumes grandes.

### Testes declarativos

```yaml
- name: stg_clientes
  columns:
    - name: cliente_id
      tests: [not_null, unique]
```

O dbt gera uma query que verifica: se `cliente_id` tiver nulo ou duplicata, o teste falha. Isso substitui horas de validação manual.

**Exemplo trabalhado — o teste que pega o bug antes do analista.** O teste `unique` em `cliente_id` compila para algo como `SELECT cliente_id FROM stg_clientes GROUP BY cliente_id HAVING COUNT(*) > 1`. Se a origem duplicou um cliente (bug no seed, ou JOIN errado no staging), essa query retorna ≥1 linha e `dbt test` falha no CI — *antes* do dado chegar ao mart e inflar a contagem de "clientes ativos". Sem isso, o erro só aparece quando um analista estranha o número num dashboard, dias depois. O teste declarativo move a descoberta do bug de "produção, tarde" para "pipeline, na hora".

### Staging vs marts

- **Staging (`stg_*`)**: one-to-one com a origem. Renomeia colunas, aplica CAST de VARCHAR para tipos corretos, padroniza formatos. Materializa como view.
- **Marts (`mart_*`)**: modelos de negócio. Juntam múltiplos stagings, aplicam regras (excluir cancelados), calculam métricas. Materializa como table.

---

## Etapa 1 — Configurar o projeto dbt

### O que fazer
- `dbt_project.yml`: project name `nuvemstore`, model paths, default materializations (staging=view, marts=table).
- `profiles.yml`: apontando para DuckDB (adapter `dbt-duckdb`).

### ⚠️ Armadilhas
- dbt-duckdb precisa saber o path do arquivo `.duckdb`. Usar variável de ambiente para não hardcodar path absoluto.
- `profiles.yml` NÃO deve ir para o git em projetos reais (contém credenciais). Neste portfolio, vai para documentar o setup.

---

## Etapa 2 — Criar modelos de staging

### O que fazer
Um modelo por tabela da origem:
- `stg_clientes.sql`: SELECT de `raw_cliente`, CAST `cliente_id` para INT, `nome` para VARCHAR, `cidade` para VARCHAR, `email` para VARCHAR.
- `stg_produtos.sql`: JOIN com `raw_categoria` para desnormalizar.
- `stg_pedidos.sql`: CAST de datas, status.
- `stg_itens_pedido.sql`: CAST de quantidade e preço.
- `stg_pagamentos.sql`: CAST de valor e data.

### Decisões de design
- *Materialização como view*: staging não duplica dados. Sempre reflete raw atual.
- *Naming convention*: `stg_` prefix para distinguir de marts.
- *Typing aqui*: raw é tudo VARCHAR. Staging é onde o CAST acontece — se falhar, o erro é explícito e localizado.

### ⚠️ Armadilhas
- CAST de VARCHAR com valor inesperado 