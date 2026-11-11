select
    cast(pedido_id as integer) as pedido_id,
    cast(data_pedido as timestamp) as data_pedido,
    status
from {{ source('raw', 'raw_pedido') }}
