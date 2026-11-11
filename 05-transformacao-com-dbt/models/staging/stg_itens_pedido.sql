select
    cast(item_pedido_id as integer) as item_pedido_id,
    cast(pedido_id as integer) as pedido_id,
    cast(produto_id as integer) as produto_id,
    cast(quantidade as integer) as quantidade,
    cast(preco_unitario as decimal(18, 2)) as preco_unitario
from {{ source('raw', 'raw_item_pedido') }}
