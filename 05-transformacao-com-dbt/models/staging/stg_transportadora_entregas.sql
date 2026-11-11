select
    entrega_id,
    pedido_id,
    payload ->> 'status' as status,
    case when regexp_matches(payload ->> 'previsao_entrega', '(Z|[+-][0-9]{2}:[0-9]{2})$')
        then try_cast(payload ->> 'previsao_entrega' as timestamptz)
    end as previsao_entrega,
    case when regexp_matches(payload ->> 'event_ts', '(Z|[+-][0-9]{2}:[0-9]{2})$')
        then try_cast(payload ->> 'event_ts' as timestamptz)
    end as event_ts,
    updated_at,
    ingestion_ts
from {{ source('transportadora', 'transportadora_entregas') }}
