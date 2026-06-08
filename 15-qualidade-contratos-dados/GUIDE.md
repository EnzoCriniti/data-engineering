# Cap. 15 — Qualidade de dados: contratos e portões de validação

> **Aula deste capítulo.** Você aprende a transformar "confio que a fonte manda o dado certo" em um contrato executável que falha alto quando violado. O conceito está aqui; as suítes de expectativas e o código estão no **[SOLUTION.md](./SOLUTION.md)**; os internals (GE vs Soda vs dbt tests, onde validar no pipeline) estão no **[TECHNICAL.md](./TECHNICAL.md)**.

## O problema que este capítulo resolve

A plataforma ingere dados de várias fontes, e cada fonte é um ponto de falha silencioso: a API externa muda o payload, o OLTP manda um nulo inesperado, uma unidade muda de reais para centavos. Sem validação na borda, esse erro vira número errado num dashboard — e a decisão de negócio é tomada com base nele. Este capítulo coloca um portão de qualidade entre a fonte e as camadas confiáveis.

## Pré-requisitos

- **Capítulos anteriores:** 10/12 (gold do lakehouse, via Trino) e 05 (dbt tests) — é sobre o gold consolidado que validamos.
- **Docker:** versão 24+ com Docker Compose.

## Conceitos fundamentais

### Contrato de dados

É um acordo explícito e versionado sobre a forma do dado: colunas, tipos, obrigatoriedade, faixas, domínios. A diferença para um "combinado" informal é que o contrato é **executável** — você roda ele contra os dados e ele passa ou falha. Quem produz o dado sabe que quebrar o contrato quebra um teste; quem consome confia que o que passou está dentro do acordado.

### Expectativa

A unidade do contrato. Cada expectativa é uma asserção verificável:
- `expect_column_values_to_not_be_null(pedido_id)`
- `expect_column_values_to_be_between(valor, 0, 100000)`
- `expect_column_values_to_be_in_set(status, ["pendente","pago","cancelado"])`
- `expect_column_values_to_be_unique(pagamento_id)`

Uma **suíte** é o conjunto de expectativas de uma tabela — a especificação do contrato dela.

### Onde colocar o portão na trilha

A plataforma desta altura já não tem mais DuckDB nem marts soltos: o estado consolidado dos dados é o **gold do lakehouse** (Delta, cap 10/12), consultado por Trino. O portão de qualidade vai exatamente aí — entre o gold e o consumo (BI/feature table). É a última fronteira antes de alguém tomar decisão com o número.

Isso é complementar ao `dbt test` do cap 05 (que valida modelos no auge da fase batch) e à validação que faria sentido na ingestão. Aqui validamos o produto final consolidado: se o gold passou, o dashboard pode confiar.

**Exemplo trabalhado — o frete em centavos.** A transportadora muda a unidade de `valor_frete` de reais para centavos: um frete de R$ 15,00 entra como `1500`. Sem contrato, esse valor flui pela pipeline até o gold de receita, infla o total em 100x, e o gráfico mente por uma semana. Com uma expectativa de faixa no gold (`valor` entre 0 e um máximo plausível), o portão falha na primeira execução pós-mudança: o relatório aponta as linhas que violam o teto. O erro vira um alarme imediato e específico, não uma decisão errada descoberta tarde. A expectativa não precisou prever *qual* mudança aconteceria — só precisou codificar o que era um valor plausível.

### Schema drift

A mudança estrutural não-anunciada: uma coluna some, um tipo muda, uma nova coluna aparece. O contrato detecta drift porque ele lista as colunas esperadas e seus tipos — se a fonte parar de mandar `valor_frete`, a expectativa `expect_column_to_exist` falha.

### Quarentena vs fail-fast

Diante de dado ruim, duas posturas:
- **Fail-fast**: bloqueia o lote inteiro. Bom quando o dado é crítico e processar parcialmente é pior que não processar.
- **Quarentena**: desvia as linhas ruins para uma tabela à parte e segue com as boas. Bom quando perder o lote todo por causa de 12 linhas é caro demais.

A escolha é de design, e depende de quão tolerante o consumidor é.

**Exemplo trabalhado — quando quarentenar é melhor que falhar.** Um lote diário de 50.000 pedidos chega com 12 linhas de `cidade` nula. Fail-fast bloquearia os 50.000 por causa de 12 — e o dashboard do dia fica vazio. Quarentena desvia as 12 para `quarentena_pedidos`, processa as 49.988 boas, e registra o problema para alguém investigar. O dashboard fica certo (sem as 12) e nada se perde de vista. A regra prática: quanto maior o lote e mais isoladas as falhas, mais a quarentena ganha; quanto mais crítica a completude, mais o fail-fast ganha.

---

## Etapa 1 — Subir o runner de qualidade (`docker-compose.yml`)

### O que fazer
Um serviço em perfil `jobs` com um client Trino instalado, conectando ao Trino do lakehouse (cap 10) e montando a pasta de contratos (`quality/`) do projeto.

### Decisões de design
- *Perfil `jobs`*: validação é um job sob demanda, não um serviço sempre ligado.
- *Consultar o gold via Trino*: validamos o estado consolidado real da plataforma (gold Delta, cap 10/12), reaproveitando o Trino que os caps 09/10 já sobem — não subimos um motor de query próprio.

---

## Etapa 2 — Definir as suítes de expectativas (`quality/expectations/`)

### Contexto
Uma suíte por tabela gold crítica (ex.: `resumo_entregas`, `velocidade_regional`). Cada suíte é o contrato executável daquela tabela.

### Decisões de design
- *Expectativas de domínio, não só técnicas*: além de `not_null`/`unique`, codifique regras de negócio (`valor` numa faixa plausível, `status` num conjunto fechado). É aí que mora o valor.
- *Faixas folgadas mas reais*: `valor entre 0 e 100000` pega o frete-em-centavos sem disparar falso-positivo no dia a dia.

### ⚠️ Armadilhas
- Só validar tipos e nulos: isso o banco já garante. O ganho está nas regras de negócio (faixas, domínios, cardinalidade).
- Faixas apertadas demais: geram alarme falso e treinam o time a ignorar o portão.

### 📚 Para se aprofundar
- [Great Expectations — Core concepts](https://docs.greatexpectations.io/docs/core/introduction/)
- [Data Contracts (Chad Sanderson)](https://dataproducts.substack.com/p/the-rise-of-data-contracts)

---

## Etapa 3 — Criar o checkpoint e rodar a validação

### O que fazer
Um checkpoint amarra suíte + fonte de dados e executa a validação, gerando um resultado pass/fail e os data docs (relatório HTML navegável).

### Decisões de design
- *Checkpoint no pipeline*: em produção, ele roda como uma task do Airflow (cap 07) antes da carga. Falhou → a DAG para.
- *Data docs versionáveis*: o relatório pode ser publicado para o time ver o histórico de qualidade.

### ⚠️ Armadilhas
- Rodar a validação *depois* da carga: aí ela vira auditoria, não portão. O ponto é barrar antes.

---

## ✅ Checklist final

Operacional:

- [ ] Runner sobe e enxerga o gold do lakehouse via Trino (cap 10)
- [ ] Suíte de expectativas definida para ao menos `resumo_entregas` e `velocidade_regional`
- [ ] Checkpoint roda e gera resultado pass/fail
- [ ] Data docs são gerados e abrem no navegador
- [ ] Uma expectativa que falha (ex.: injetar um valor fora da faixa) realmente bloqueia/reporta
- [ ] Expectativas incluem regras de negócio, não só tipos/nulos

Compreensão (você entendeu — responda sem olhar):

- [ ] Qual a diferença entre validar o produto final consolidado (gold, este cap) e validar o modelo no batch (`dbt test`, cap 05)?
- [ ] Conte o caso do frete em centavos: por que uma expectativa de faixa pegaria isso e onde?
- [ ] Quando você escolhe quarentena em vez de fail-fast? Dê o critério.
- [ ] O que é schema drift e qual expectativa o detecta?

## A dor que sobra

O dado que entra agora é validado, mas a operação é cega a falhas: um job que quebra de madrugada ou uma tabela que parou de atualizar passam despercebidos. O próximo capítulo ataca isso: **obser