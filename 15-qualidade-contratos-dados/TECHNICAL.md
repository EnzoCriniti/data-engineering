# Complemento técnico — Qualidade de dados, contratos e onde validar

## O que este capítulo aprofunda

Este capítulo mostra que qualidade de dados não é um teste solto no fim do pipeline — é um portão explícito antes do consumo, com contratos versionados. Nesta altura da trilha o portão fica entre o **gold do lakehouse** (cap 10/12) e o BI/feature table: é a última fronteira antes de alguém decidir com o número. O diferencial é entender *onde* validar, *o que* validar (regras de negócio, não só tipos) e como tratar a falha (fail-fast vs quarentena).

## Pequena história

Por muito tempo, "qualidade de dados" significava um analista rodando um `SELECT count(*) WHERE coluna IS NULL` de vez em quando. A formalização veio em ondas: o **dbt** (2018) popularizou testes versionados junto dos modelos (`not_null`, `unique`, `relationships`). O **Great Expectations** (2018) trouxe a ideia de *expectativas* como especificação executável e os *data docs* navegáveis. O **Soda** e o **Monte Carlo** (2019–2020) levaram isso para o território de observabilidade e detecção automática de anomalias.

Em paralelo, o conceito de **data contract** ganhou força a partir de ~2022 (Chad Sanderson e outros): a ideia de que produtor e consumidor de dados devem ter um acordo versionado e testável, tratado com o mesmo rigor de um contrato de API.

## Por baixo dos panos

### Onde validar no pipeline

Há três pontos possíveis:
- **Na borda (ingestão)**: valida o dado cru assim que chega. Pega problema de fonte cedo. Faria sentido complementar, mas não é onde este capítulo atua.
- **Pós-transformação (modelo)**: o `dbt test` do cap 05. Valida o que foi derivado no auge da fase batch — pega bugs de transformação.
- **No consumo (saída)**: valida o produto final consolidado (o **gold** do lakehouse) antes de publicar para BI/ML. Última linha de defesa — e o foco deste capítulo.

Os três coexistem; este capítulo preenche a lacuna do consumo, validando o gold via Trino antes que o número vire decisão.

### Expectativas vs assertions de banco

Um `NOT NULL` no DDL é uma asserção do banco — rígida, e o banco rejeita a escrita. Uma expectativa é mais rica: faixas, domínios, cardinalidade, distribuições, e roda *fora* do caminho de escrita, sobre dados que já estão lá. Ela permite validar coisas que o banco não expressa ("95% dos pagamentos são via pix ou cartão") e produzir relatórios em vez de só barrar.

### Fail-fast vs quarentena

Tecnicamente, fail-fast é um checkpoint que retorna não-zero e interrompe a orquestração. Quarentena é um `INSERT ... WHERE NOT (regra)` para uma tabela de descarte, seguido do processamento do complemento. A decisão é de SLA: completude crítica favorece fail-fast; volume alto com falhas isoladas favorece quarentena.

### Schema drift e contratos

O contrato lista colunas e tipos esperados. Detectar drift é comparar o schema observado com o declarado a cada execução. Ferramentas maduras versionam o contrato e podem até *bloquear* um deploy do produtor que quebraria consumidores (shift-left).

## Por que entra depois de IaC

Com a infra reproduzível (cap 14), faz sentido endurecer o que roda sobre ela. Qualidade é o primeiro controle de produção que afeta diretamente a confiança no número final — por isso vem antes de observabilidade (cap 16), que monitora o *processo*, enquanto qualidade valida o *dado*.

## Tecnologias equivalentes

| Ferramenta | Quando usar |
| --- | --- |
| Great Expectations | Suítes ricas + data docs; bom para validação na borda e documentação. |
| dbt tests | Validação acoplada aos modelos; ótimo se você já vive no dbt. |
| Soda Core / SodaCL | Checks declarativos em YAML, foco em monitoramento contínuo. |
| Pandera | Validação de DataFrames Pandas/Polars em código Python. |
| Monte Carlo / Bigeye | Observabilidade de dados gerenciada, com detecção automática de anomalias. |

## Quando usar

Use validação no consumo (gold) sempre que o número for direto para uma decisão de negócio — é a defesa contra erros que sobreviveram a todas as transformações. Validação na borda (cru) complementa quando há fonte externa pouco confiável; o `dbt test` pós-transformação cobre bugs de modelo. Os três se somam.

Use contratos formais quando há mais de uma equipe na fronteira produtor/consumidor — é aí que o acordo explícito paga seu custo.

## Como isso aparece no projeto

Este capítulo coloca um portão entre o gold do lakehouse e o consumo, codificando regras de negócio (faixas de valor, domínios de status) que o banco sozinho não garante. É o que teria pego o "frete em centavos" no dia em que aconteceu.

## 📚 Referências

- [Great Expectations Docs](https://docs.greatexpectations.io/) — expectativas, checkpoints e data docs.
- [The Rise of Data Contracts (Chad Sanderson)](https://dataproducts.substack.com/p/the-rise-of-data-contracts) — o conceito de contrato de dados.
- [dbt tests](https://docs.getdbt.com/docs/build/data-tests) — testes acoplados a modelos.
- [Soda Core](https://docs.soda.io/) — checks de qualidade declarativos.
