# Cap. 06 — Ingestão de API externa: múltiplas fontes na plataforma

> **Aula deste capítulo.** Você aprende a ingerir uma fonte que você **não controla** — uma API REST com indisponibilidade, rate limiting, paginação e contrato instável. A orientação está aqui; o código do `extract.py` e do `staging.sql` está no **[SOLUTION.md](./SOLUTION.md)**; os internals (backoff exponencial, cursor vs offset, semântica do `ON CONFLICT`) estão no **[TECHNICAL.md](./TECHNICAL.md)**.

## O problema que este capítulo resolve

Até agora, a plataforma depende de uma única fonte — o OLTP interno. Mas a NuvemStore tem frota própria de entrega, e os dados logísticos vêm de um sistema externo via API REST. A plataforma precisa ingerir dados que ela não controla: com contratos HTTP, paginação, rate limiting e falhas de disponibilidade.

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

O extractor opera em janelas temporais (`updated_after >= last_success`). Se uma janela falha no meio, ela pode ser re-executada sem duplicar dados no destino. O padrão é DELETE+INSERT por janela ou UPSERT por chave natural.

**Exemplo trabalhado — por que UPSERT e não INSERT puro.** A janela das 14h carrega a entrega `E-50` com status `em_transito`. O job cai logo depois e você re-roda a mesma janela. Com `INSERT` puro, `E-50` entraria de novo → duplicata, e qualquer `COUNT` ou `SUM` mente. Com `INSERT ... ON CONFLICT (entrega_id) DO UPDATE`, a segunda execução *atualiza* a linha existente em vez de criar outra — e se o status mudou para `entregue` nesse meio-tempo, o UPSERT já reflete o valor novo. Re-rodar a janela é seguro por construção: é isso que "idempotência por janela" significa na prática.

---

## Etapa 1 — Criar o mock da API externa

### Contexto
Em um portfolio local, não dependemos de uma API real. Criamos um mock usando um JSON estático servido por um container. Isso simula o contrato da API logística.

### O que fazer
- `api/entregas.json`: JSON com dados de entregas (entrega_id, pedido_id, status, data_ocorrencia, latitude, longitude, velocidade).
- Servir com `python -m http.server` ou nginx em um container.
- docker-compose com serviço `api-mock` servindo o JSON.

### ⚠️ Armadilhas
- JSON com encoding diferente de UTF-8 causa erros silenciosos de parsing.
- Servir sem Content-Type `application/json` pode confundir clientes HTTP.

---

## Etapa 2 — Implementar o extractor batch

### Contexto
Script Python que consome a API, valida o payload e grava em staging no Postgres.

### Decisões de design
- *Retry com backoff*: `time.sleep(2 ** attempt)` para falhas transitórias (HTTP 429, 503).
- *Validação de schema*: verific