select entrega_id from {{ ref('stg_transportadora_entregas') }}
except
select entrega_id from {{ ref('mart_sla_entregas') }}
