# Especificação — API da Transportadora X (fonte externa)

> Contrato da API fake que simula a transportadora terceirizada. Ela é **proposital­mente imperfeita**: tem as dores reais de uma fonte que você não controla (paginação, rate limit, latência, schema instável). É essa imperfeição que dá sentido aos capítulos de ingestão resiliente (este), qualidade/contratos (15) e observabilidade (16). Uma API "perfeita" não ensinaria nada.

## Onde ela entra na arquitetura

A Transportadora X é uma **fonte upstream externa**: alimenta a plataforma, mas não pertence ao OLTP interno. O fluxo é

```text
API Transportadora ──(extractor batch)──> staging.transportadora_entregas ──(dbt)──> silver/gold
```

Diferente do OLTP (interno, schema estável que nós definimos via seeder), aqui o produtor é de terceiros e pode quebrar o contrato sem aviso. Por isso o dado aterrissa **cru** no staging antes de qualquer transformação — isola "trazer" de "dar sentido".

> Não confundir com uma **API de serving** (downstream), que serviria scores/features para consumo. Esta é entrada; aquela seria saída.

## Propriedades de propósito

Cada propriedade abaixo existe para forçar uma boa prática no extractor:

| Propriedade | Comportamento | O que força no consumidor |
| --- | --- | --- |
| **Paginação** | Resposta em páginas via cursor (`next_cursor`). | Iterar até `next_cursor` ser nulo, em vez de baixar tudo de uma vez. |
| **Rate limiting** | HTTP `429` ao exceder ~10 req/s, com header `Retry-After`. | Backoff exponencial respeitando `Retry-After`. |
| **Incremental** | Filtro `updated_since` (ISO 8601). | Puxar só o que mudou desde o último checkpoint, não full-load. |
| **Schema instável** | Em modo `SCHEMA_DRIFT=true`, muda a unidade de `valor_frete` (reais → centavos) ou renomeia um campo. | Gravar payload cru; validar contrato na camada seguinte (cap 15 pega o "frete em centavos"). |
| **Latência/falha** | Latência aleatória; `5xx` esporádico. | Retry idempotente + timeout. |
| **Autenticação** | Header `X-API-Key`. Chave inválida → `401`. | Segredo via env/IaC, nunca hardcoded. |
| **Event vs ingestion time** | Cada registro traz `event_ts` (quando ocorreu) distinto de quando foi lido. | Distinguir `event_ts` de `ingestion_ts` — base para PIT correctness (cap 13) e freshness (cap 16). |

## Endpoints

### `GET /entregas`

Lista ocorrências de entrega, paginadas e incrementais.

**Query params**

| Param | Obrig. | Descrição |
| --- | --- | --- |
| `updated_since` | não | ISO 8601. Só registros com `updated_at >= updated_since`. Omitido = desde o início. |
| `cursor` | não | Cursor da página seguinte (devolvido em `next_cursor`). |
| `limit` | não | Tamanho da página (default 100, máx 500). |

**Headers**

| Header | Descrição |
| --- | --- |
| `X-API-Key` | Chave de acesso. Ausente/ inválida → `401`. |

**Resposta `200`**

```json
{
  "data": [
    {
      "entrega_id": "TRX-000123",
      "pedido_id": 4821,
      "status": "entregue",
      "previsao_entrega": "2026-06-08T14:00:00Z",
      "ocorrencia": "entregue ao destinatario",
      "valor_frete": 15.00,
      "event_ts": "2026-06-08T13:52:11Z",
      "updated_at": "2026-06-08T13:52:40Z"
    }
  ],
  "next_cursor": "eyJvZmZzZXQiOjEwMH0=",
  "has_more": true
}
```

**Campos de `data[]`**

| Campo | Tipo | Notas |
| --- | --- | --- |
| `entrega_id` | string | Chave natural. Estável entre reentregas → base da idempotência (UPSERT). |
| `pedido_id` | int | FK lógica para o pedido interno (cruzado no dbt). |
| `status` | enum | `em_transito` \| `entregue` \| `devolvido` \| `extraviado`. |
| `previsao_entrega` | datetime | ISO 8601. |
| `ocorrencia` | string | Texto livre da ocorrência. |
| `valor_frete` | number | **Em reais.** Sob `SCHEMA_DRIFT` pode vir em centavos — o cap 15 detecta. |
| `event_ts` | datetime | Quando o evento ocorreu na transportadora. |
| `updated_at` | datetime | Quando o registro foi atualizado. Âncora do incremental. |

**Códigos de status**

| Código | Quando | Ação do extractor |
| --- | --- | --- |
| `200` | OK | Processar `data`, seguir `next_cursor` se `has_more`. |
| `401` | `X-API-Key` ausente/ inválida | Abortar — erro de config, não retry. |
| `429` | Rate limit | Aguardar `Retry-After` e repetir. |
| `5xx` | Falha transitória | Retry com backoff exponencial; após N tentativas, falhar a carga. |

### `GET /health`

Liveness simples. `200 {"status":"ok"}`. Usado pelo healthcheck do compose.

## Contrato de ingestão (resumo)

1. Ler checkpoint do último `updated_at` carregado com sucesso.
2. `GET /entregas?updated_since=<checkpoint>` e paginar via `cursor` até `has_more=false`.
3. Em `429`, respeitar `Retry-After`; em `5xx`, backoff exponencial.
4. **UPSERT por `entrega_id`** em `staging.transportadora_entregas` (idempotente — reprocessar a mesma janela não duplica).
5. Gravar o payload **cru** (validação de contrato fica para o cap 15).
6. Persistir o novo checkpoint só após sucesso da janela inteira.

> Implementação (extractor, retry/backoff, paginação) no [SOLUTION.md](./SOLUTION.md); internals em [TECHNICAL.md](./TECHNICAL.md).
