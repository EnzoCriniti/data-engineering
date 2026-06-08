# Cap. 16 — Observabilidade: ver a plataforma operar

> **Aula deste capítulo.** Você aprende a instrumentar a plataforma para responder "os dados estão frescos? o volume está normal? o job rodou?" e a disparar alerta antes do humano perceber. O conceito está aqui; o coletor e as regras estão no **[SOLUTION.md](./SOLUTION.md)**; os internals (Prometheus/Grafana, Elementary, push vs pull) estão no **[TECHNICAL.md](./TECHNICAL.md)**.

## O problema que este capítulo resolve

A validação de dados (cap 15) garante que o dado *que chega* está correto. Mas não diz nada sobre o *processo*: um job pode falhar, uma tabela pode parar de atualizar, um lote pode encolher — tudo sem um erro explícito. O dashboard serve dado velho ou incompleto, e a decisão é tomada errada. Observabilidade fecha essa lacuna: ela mede a saúde do pipeline e alerta quando algo sai do normal.

## Pré-requisitos

- **Capítulos anteriores:** 10/12 (gold do lakehouse, via Trino) e 15 (qualidade) — observamos as mesmas tabelas gold.
- **Docker:** versão 24+ com Docker Compose.

## Conceitos fundamentais

### Por que dados precisam de observabilidade própria

Monitoramento de software clássico (CPU, memória, latência) responde "o serviço está de pé?". Mas um pipeline pode estar *de pé* e mesmo assim entregar dado errado: o job rodou, não deu exceção, e mesmo assim a tabela está defasada ou pela metade. Observabilidade de dados mede o que importa para *dados*: frescor, volume, schema, distribuição.

### Freshness

A idade do dado mais recente. Calcula-se `now() - max(timestamp)` da tabela. Cada tabela tem um SLO de frescor implícito: o mart de receita "deveria" estar a no máximo X horas de atraso. Quando passa disso, é incidente — independente de cada linha ser válida.

**Exemplo trabalhado — o gold de velocidade que parou de respirar.** A gold `velocidade_regional` (cap 12) é alimentada pelo streaming a cada janela de poucos minutos; sua coluna `window` marca o fim da última janela processada. Numa madrugada o job de streaming morre (broker reiniciou, offset perdido) mas nada explode visivelmente — o gold simplesmente para de receber janelas novas. Cada linha que está lá é perfeitamente válida, então o cap 15 passa sem reclamar. O que pega isso é uma regra de **freshness**: `now() - max(window) > 1h ⇒ alerta`. O sinal não é sobre o conteúdo de uma linha; é sobre a *ausência* de janelas novas. Por isso freshness é um pilar separado de qualidade — ele detecta o que não aconteceu.

### Anomalia de volume

O tamanho do último lote comparado ao histórico. Um pipeline que processava ~50 mil linhas/dia e de repente processa 12 está meio-quebrado — talvez uma fonte parou, talvez um filtro ficou agressivo demais. Sem erro explícito, só o volume denuncia.

**Exemplo trabalhado — o filtro que comeu os dados.** Alguém edita uma query e troca um `WHERE status != 'cancelado'` por `WHERE status = 'cancelado'` (inverteu sem querer). O job roda, não dá erro, e grava as 200 linhas canceladas em vez das 49.800 boas. O dashboard não fica vazio — fica *quase* vazio, o que é pior, porque parece plausível. Uma regra de volume — "lote de hoje < 50% da média dos últimos 7 dias ⇒ alerta" — pega isso na hora. É o tipo de bug que passa por todo teste unitário e só a observação do volume em produção revela.

### SLA / SLO de dados

Um SLO é o alvo: "mart fresco em ≤ 2h, 99% dos dias". O alerta é a violação do SLO. Definir SLOs força a conversa certa: *quão fresco precisa estar?* — e evita alertar sobre atrasos que não importam.

### Alerta acionável vs ruído

O maior inimigo da observabilidade é o alerta que ninguém lê. Um bom alerta: dispara só quando há ação, diz o que/onde/quão grave, e aponta para a causa provável. Calibrar limiares (não alertar por 1 min de atraso num SLO de 2h) é o que mantém o sinal confiável.

### Lineage

O grafo de dependências fonte → job → tabela. Quando o mart está defasado, o lineage responde "por quê": o job de ingestão do OLTP, três passos atrás, falhou. Sem lineage, você debuga no escuro; com ele, vai direto à causa-raiz.

---

## Etapa 1 — Subir o coletor (`docker-compose.yml`)

### O que fazer
Um serviço em perfil `jobs` que conecta ao Trino do lakehouse (cap 10) e roda as checagens de freshness/volume sobre o gold. Opcionalmente, Prometheus + Grafana para visualizar (mencionados no TECHNICAL; o gabarito mantém o coletor enxuto).

### Decisões de design
- *Coletor como job*: pode rodar como uma task final da DAG do Airflow (cap 07) ou em cron. Não precisa ser serviço sempre ligado para o conceito.
- *Observar o gold via Trino*: medimos a saúde do produto final consolidado da plataforma, reusando o Trino que os caps 09/10 já sobem.

---

## Etapa 2 — Definir os SLOs por tabela (`observability/slos.json`)

### Contexto
Um arquivo declarativo: para cada tabela gold, qual coluna de timestamp usar (quando há), o limite de freshness, e a janela/limiar de volume.

### Decisões de design
- *SLO declarativo e versionado*: igual ao contrato do cap 15 — a regra mora no Git, não na cabeça de alguém.
- *Limites folgados e realistas*: freshness de ~1h para a gold de streaming; volume com piso de 50% da baseline.
- *Nem toda gold tem timestamp*: a gold batch agregada por status (`resumo_entregas`) não tem timestamp de linha — para ela monitoramos só volume; o freshness fica na gold de streaming (`velocidade_regional.window`).

### ⚠️ Armadilhas
- Limiar apertado demais → alert fatigue → o time ignora o painel.
- Medir freshness numa tabela agregada sem timestamp → ou você escolhe a coluna errada, ou mede o que não existe. Saiba qual gold carrega o sinal de frescor.

### 📚 Para se aprofundar
- [Google SRE Book — SLOs](https://sre.google/sre-book/service-level-objectives/)
- [Elementary — dbt-native observability](https://docs.elementary-data.com/)

---

## Etapa 3 — Rodar e alertar

### O que fazer
O coletor calcula cada métrica, compara com o SLO, e produz um relatório + um exit code (não-zero se algum SLO violado, para integrar com orquestração). Um alerta real (Slack/e-mail) é trivial de plugar depois.

### ⚠️ Armadilhas
- Tratar o coletor como auditoria pós-fato em vez de portão/alarme: o valor está em avisar cedo.

---

## ✅ Checklist final

Operacional:

- [ ] Coletor sobe e enxerga o gold do lakehouse via Trino (cap 10)
- [ ] SLOs definidos por tabela (freshness + volume)
- [ ] Coletor calcula freshness e volume corretamente
- [ ] Um SLO violado (ex.: simular tabela defasada) dispara alerta e exit não-zero
- [ ] Relatório lista cada métrica vs seu SLO de forma legível
- [ ] Limiares calibrados para não gerar ruído

Compreensão (você entendeu — responda sem olhar):

- [ ] Por que validar dados (cap 15) não substitui observar o processo (este cap)? Dê um caso que só freshness pega.
- [ ] Conte o caso do filtro que comeu os dados: por que só a métrica de volume o detecta?
- [ ] O que é alert fatigue e como calibrar limiares ajuda?
- [ ] Para que serve lineage no diagnóstico de um incidente?

## A dor que sobra

A plataforma agora tem infra reproduzível, dado validado e processo observado — os controles essenciais de produção. Falta amarrar tudo numa história única e demonstrável. O capítulo final é o **capstone**: arquitetura consolidada, a plataforma ponta-a-ponta e os resultados visíveis.
