{% set as_of = var('sla_as_of', run_started_at.isoformat()) %}

with referencia as (
    select cast('{{ as_of | replace("'", "''") }}' as timestamptz) as as_of
), conciliacao as (
    select
        e.*,
        r.as_of,
        case
            when p.pedido_id is null then 'pedido_orfao'
            when p.status = 'cancelado' then 'pedido_cancelado'
            when e.previsao_entrega is null then 'prazo_invalido'
            when e.status is null or e.status not in
                ('em_transito', 'entregue', 'devolvido', 'extraviado') then 'status_invalido'
            when e.event_ts is null or e.event_ts > r.as_of then 'evento_invalido'
            when e.status in ('devolvido', 'extraviado') then e.status
            when e.status = 'entregue' and e.event_ts > e.previsao_entrega then 'entregue_com_atraso'
            when e.status = 'em_transito' and r.as_of > e.previsao_entrega then 'atraso_aberto'
            else 'no_prazo'
        end as situacao_sla
    from {{ ref('stg_transportadora_entregas') }} e
    cross join referencia r
    left join {{ ref('stg_pedidos') }} p on e.pedido_id = p.pedido_id
)
select
    *,
    case
        when situacao_sla = 'atraso_aberto'
            then epoch(as_of - previsao_entrega)
        when situacao_sla = 'entregue_com_atraso'
            then epoch(event_ts - previsao_entrega)
    end as atraso_segundos
from conciliacao
