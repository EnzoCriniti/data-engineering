select s.entrega_id
from {{ ref('mart_sla_entregas') }} s
left join {{ ref('stg_pedidos') }} p on s.pedido_id = p.pedido_id
where (
    s.situacao_sla in ('atraso_aberto', 'entregue_com_atraso', 'no_prazo')
    and (p.pedido_id is null or p.status = 'cancelado')
) or (
    s.situacao_sla in ('atraso_aberto', 'entregue_com_atraso')
    and coalesce(s.atraso_segundos, 0) <= 0
)
