select
    pr.produto,
    pr.categoria,
    sum(i.quantidade * i.preco_unitario) as receita,
    sum(i.quantidade) as unidades
from {{ ref('stg_itens_pedido') }} i
join {{ ref('stg_pedidos') }} p on p.pedido_id = i.pedido_id
join {{ ref('stg_produtos') }} pr on pr.produto_id = i.produto_id
where p.status != 'cancelado'
group by 1, 2
order by receita desc, produto, categoria
limit 20
