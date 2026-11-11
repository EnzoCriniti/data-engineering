select
    cast(p.produto_id as integer) as produto_id,
    p.nome as produto,
    c.nome as categoria
from {{ source('raw', 'raw_produto') }} p
join {{ source('raw', 'raw_categoria') }} c on p.categoria_id = c.categoria_id
