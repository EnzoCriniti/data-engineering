# Cap. 17 — Capstone: como demonstrar a plataforma inteira

> **Aula deste capítulo.** Você aprende a consolidar uma trilha técnica numa narrativa única e a **provar** que ela funciona com evidências visuais — a habilidade de comunicar trabalho técnico, que vale tanto quanto construí-lo. Não há código novo; há uma galeria de provas a montar.

## O problema que este capítulo resolve

Um portfólio técnico tem dois leitores: quem mergulha (lê cada capítulo) e quem escaneia (recrutador, 30 segundos). A trilha 00–16 serve o primeiro. O capstone serve o segundo — e fecha a história para o primeiro. Sem ele, o repositório é uma sequência de exercícios; com ele, é uma plataforma.

A entrega aqui não é software, é **evidência organizada**: a arquitetura num lugar, as decisões resumidas, e prints que provam cada fase rodando.

## Por que prova visual importa

Documentação descreve; print demonstra. "Implementei um lakehouse Delta" é uma afirmação; um print do `DESCRIBE HISTORY` mostrando os commits, ao lado do gold consultável no Metabase, é prova. Recrutadores e entrevistadores confiam no que veem. Uma galeria curada de resultados é, muitas vezes, o que diferencia dois portfólios com o mesmo conteúdo técnico.

## A galeria de provas — o que capturar

Monte os prints conforme resolver cada capítulo e salve em `assets/`. A lista abaixo é o roteiro; cada item é uma prova de uma fase da plataforma.

### Fundação (00–03)
- Diagrama do star schema (cap 01) — `assets/01-star-schema.png`
- Warehouse dedicado com dados migrados, lado a lado com o OLTP — `assets/03-warehouse-vs-oltp.png`

### Batch analytics (04–06)
- `dbt docs` mostrando o DAG de lineage (cap 05) — `assets/05-dbt-lineage.png`
- `dbt test` passando — `assets/05-dbt-test.png`
- Mart de receita renderizado no Metabase — `assets/06-mart-receita.png`

### Operação (07)
- DAG do Airflow com as tasks verdes (sucesso) — `assets/07-airflow-dag.png`

### Lake e lakehouse (08–10)
- Console do MinIO com as camadas bronze/silver/gold — `assets/10-minio-camadas.png`
- `DESCRIBE HISTORY` da tabela Delta provando time-travel — `assets/10-delta-history.png`

### Baixa latência (11–12)
- Redpanda Console com os tópicos e mensagens fluindo — `assets/11-redpanda-console.png`
- Gold de velocidade regional atualizando em tempo real (cap 12) — `assets/12-streaming-gold.png`

### ML e produção (13–16)
- Feature table populada com `validate_pit.py` retornando 0 violações — `assets/13-pit-ok.png`
- `terraform apply` criando o bucket via LocalStack (cap 14) — `assets/14-terraform-apply.png`
- Portão de qualidade barrando dado ruim (cap 15) — `assets/15-portao-fechado.png`
- Coletor de observabilidade disparando alerta de SLO (cap 16) — `assets/16-alerta.png`

### Visão geral
- O diagrama de arquitetura consolidada deste capítulo — `assets/17-arquitetura.png`

## Como montar a narrativa de fechamento

1. **Abra pela dor, feche pela plataforma.** O README do capstone já faz isso — a tabela "jornada inteira em uma página" é o resumo executivo.
2. **Uma prova por fase.** Não precisa de cinquenta prints; precisa de um forte por fase, legível e legendado.
3. **Seja honesto sobre o roadmap.** A seção "dor que sobra" do README mostra maturidade — reconhecer limites vale mais que fingir completude.

## ✅ Checklist final

Operacional:

- [ ] Arquitetura consolidada documentada (README + diagrama)
- [ ] Galeria de prints com ao menos uma prova por fase
- [ ] Cada print legendado e referenciado no RUNBOOK
- [ ] Tabela "jornada em uma página" revisada e correta
- [ ] Seção de roadmap honesto presente

Compreensão (você entendeu — responda sem olhar):

- [ ] Por que o capstone não adiciona tecnologia nova, e ainda assim é valioso?
- [ ] Qual a diferença entre documentar e demonstrar? Dê um exemplo da galeria.
- [ ] Conte a jornada da plataforma em 4 frases, ligando cada fase à dor que a motivou.
- [ ] Por que reconhecer o roadmap pendente fortalece (em vez de enfraquecer) o portfólio?

## Fim da trilha

Aqui a jornada se completa: de um OLTP isolado a uma plataforma de dados de ponta a ponta, com cada decisão motivada por uma dor real e cada fase comprovada por um resultado visível. Volte ao [README raiz](../README.md) para a visão geral.
