# Cap. 06 — Ingestão de API externa: múltiplas fontes na plataforma

> **Aula deste capítulo.** Você aprende a ingerir uma fonte que você **não controla** — uma API REST com indisponibilidade, rate limiting, paginação e contrato instável. A orientação está aqui; os links para o código estão no **[SOLUTION.md](./SOLUTION.md)**; os internals (backoff exponencial, cursor vs offset, semântica do `ON CONFLICT`) estão no **[TECHNICAL.md](./TECHNICAL.md)**.

## O problema que este capítulo resolve

Até agora, a plataforma depende de uma única fonte — o OLTP interno. A NuvemStore terceirizou parte das entregas e recebe ocorrências da Transportadora X por API REST. A plataforma precisa ingerir dados que ela não controla: com contratos HTTP, paginação, rate limiting e falhas de disponibilidade.

Este capítulo adiciona a segunda fonte de dados ao pipeline e cria a dor que justifica orquestração no capítulo 07.

## Pré-requisitos

- **Capítulo anterior:** 05 concluído (dbt configurado).
- **Docker:** versão 24+ com Docker Compose.

## Conceitos fundamentais

### Por que APIs externas são diferentes de bancos internos

Bancos internos são confiáveis: estão sempre disponíveis, respondem rápido, têm schema estável. APIs externas são o oposto:
- **Indisponibilidade**: podem sair do ar sem aviso. O extractor precisa de retry com backoff exponencial.
- **Rate limiting**: HTTP 429 quando ultrapassa o limite. O extractor precisa respeitar headers `Retry-After`.
- **Paginação**: datasets grandes vêm em páginas. Cursor-based é preferível a offset-based (mais estável com inserções concorrentes).
- **Mudança de contrato**: o fornecedor pode adicionar, remover ou renomear campos sem aviso prévio.

**Exemplo trabalhado — o retry que salva a janela.** O extractor pede a página 3 de entregas e recebe `HTTP 429 Too Many Requests` com header `Retry-After: 2`. Sem tratamento, o job morre e a janela inteira fica sem carregar. Com backoff: a tentativa 1 falha → dorme `2^1=2s` → tentativa 2 ainda 429 → dorme `2^2=4s` → tentativa 3 retorna `200` e a página entra. O backoff *exponencial* (e não fixo) existe porque, se a API está sobrecarregada, martelar de 2 em 2 segundos só piora; espaçar progressivamente dá tempo de ela se recuperar. Combine com idempotência por janela e uma falha transitória vira um soluço de segundos, não um pipeline quebrado.

### Staging como destino inicial

O extractor deve gravar em staging, não no modelo final. Staging preserva o payload original — se a regra de negócio mudar, basta reprocessar staging sem re-extrair da API.

### Idempotência por janela

O extractor opera em janelas temporais (`updated_since` inclusivo com sobreposição em torno do checkpoint). Se uma janela falha no meio, ela pode ser re-executada sem duplicar dados no destino. O padrão é DELETE+INSERT por janela ou UPSERT por chave natural.

**Exemplo trabalhado — por que UPSERT e não INSERT puro.** A janela das 14h carrega a entrega `E-50` com status `em_transito`. O job cai logo depois e você re-roda a mesma janela. Com `INSERT` puro, `E-50` entraria de novo → duplicata, e qualquer `COUNT` ou `SUM` mente. Com `INSERT ... ON CONFLICT (entrega_id) DO UPDATE`, a segunda execução *atualiza* a linha existente em vez de criar outra — e se o status mudou para `entregue` nesse meio-tempo, o UPSERT já reflete o valor novo. Re-rodar a janela é seguro por construção: é isso que "idempotência por janela" significa na prática.

---

## Etapa 1 — Criar o mock da API externa

### Contexto
Em um portfolio local, não dependemos de uma API real. O mock expõe o contrato HTTP da transportadora e usa uma fixture JSON no modo de estudo.

### O que fazer
- `api/entregas.json` contém IDs de entrega e pedido, status, prazo e timestamps.
- `api/app.py` serve `/entregas` com chave, cursor e limites por data.
- O serviço `transportadora` também publica `/health`.

### ⚠️ Armadilhas
- JSON com encoding diferente de UTF-8 causa erros silenciosos de parsing.
- Servir sem Content-Type `application/json` pode confundir clientes HTTP.

---

## Etapa 2 — Implementar o extractor batch

### Contexto
Script Python que consome a API, valida o payload e grava em staging no DuckDB.

### Decisões de design
- *Retry com backoff*: `time.sleep(2 ** attempt)` para falhas transitórias (HTTP 429, 503).
- *Validação de schema*: verificar que campos esperados existem antes de inserir. Preservar campos extras no payload JSON.
- *Staging SQL*: `CREATE TABLE IF NOT EXISTS staging.transportadora_entregas (...)` com dados tipados a partir do JSON.
- *UPSERT por `entrega_id`*: `INSERT ... ON CONFLICT (entrega_id) DO UPDATE` garante idempotência.

### O que fazer
`extractor/extract.py`: faz GET na API, parseia JSON, valida campos obrigatórios, faz upsert de versões mais novas e confirma o checkpoint junto com a janela. Registra contagens de linhas gravadas e ignoradas.

### ⚠️ Armadilhas
- Não tratar HTTP 429: o extractor pode ser bloqueado pela API.
- Carregar todo o JSON em memória: para APIs reais com milhões de registros, usar streaming (response.iter_lines ou paginação).
- Não logar o status code de cada request: debugging impossível em produção.

---

## Etapa 3 — Criar o schema de staging (`extractor/staging.sql`)

### O que fazer
DDL da tabela `staging.transportadora_entregas` com colunas mapeadas do JSON, chave primária em `entrega_id`, `CREATE TABLE IF NOT EXISTS`.

---

## ✅ Checklist final

- [ ] Mock da API serve JSON corretamente
- [ ] Extractor roda e popula staging.transportadora_entregas sem erro
- [ ] Rodar extractor duas vezes não duplica registros (UPSERT)
- [ ] COUNT de staging.transportadora_entregas = COUNT de entregas no JSON
- [ ] Script compila: `python -m py_compile extractor/extract.py`

Compreensão (você entendeu — responda sem olhar):

- [ ] Liste quatro formas em que uma API externa é menos confiável que um banco interno, e o que o extractor faz para cada uma.
- [ ] Por que backoff **exponencial** e não um sleep fixo? O que acontece com a API se você martelar de 2 em 2 segundos?
- [ ] Conte o cenário do re-run da janela: por que `INSERT` puro duplica e `ON CONFLICT DO UPDATE` não?
- [ ] Por que gravar em **staging** e não direto no modelo final?

## A dor que sobra

Agora existem três jobs independentes: extração OLTP, extração API externa, e transformação dbt. Quem coordena a ordem? Quem retenta se a API cai? Quem avisa se o dbt falhou? O capítulo 07 introduz Airflow para orquestrar.
