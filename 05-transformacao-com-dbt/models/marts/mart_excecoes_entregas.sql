select *
from {{ ref('mart_sla_entregas') }}
where situacao_sla in (
    'pedido_orfao', 'pedido_cancelado', 'prazo_invalido', 'status_invalido',
    'evento_invalido', 'devolvido', 'extraviado'
)
