select
    cast(p.data_pedido as date) as dia,
    count(distinct p.pedido_id) as total_pedidos,
    sum(i.quantidade * i.preco_unitario) as receita
from {{ ref('stg_pedidos') }} p
join {{ ref('stg_itens_pedido') }} i on p.pedido_id = i.pedido_id
where p.status != 'cancelado'
group by 1
