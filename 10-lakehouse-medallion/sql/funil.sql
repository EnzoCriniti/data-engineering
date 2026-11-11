WITH primeira_view AS (
    SELECT session_id, MIN(event_seq) AS seq
    FROM silver_eventos
    WHERE event_type = 'product_view'
    GROUP BY session_id
), coorte AS (
    SELECT v.session_id, v.seq, e.event_epoch_s AS inicio
    FROM primeira_view v
    JOIN silver_eventos e ON e.session_id = v.session_id AND e.event_seq = v.seq
    CROSS JOIN parametros p
    WHERE e.event_epoch_s >= p.inicio_s AND e.event_epoch_s < p.fim_s
), carrinho AS (
    SELECT s.session_id, s.inicio, MIN(e.event_seq) AS seq
    FROM coorte s LEFT JOIN silver_eventos e
        ON e.session_id = s.session_id AND e.event_seq > s.seq
        AND e.event_type = 'add_to_cart' AND e.event_epoch_s < s.inicio + 1800
    GROUP BY s.session_id, s.inicio
), checkout AS (
    SELECT s.session_id, s.inicio, MIN(e.event_seq) AS seq
    FROM carrinho s LEFT JOIN silver_eventos e
        ON e.session_id = s.session_id AND e.event_seq > s.seq
        AND e.event_type = 'checkout_started' AND e.event_epoch_s < s.inicio + 1800
    GROUP BY s.session_id, s.inicio
), compra AS (
    SELECT s.session_id, MIN(e.event_seq) AS seq
    FROM checkout s LEFT JOIN silver_eventos e
        ON e.session_id = s.session_id AND e.event_seq > s.seq
        AND e.event_type = 'purchase_completed' AND e.event_epoch_s < s.inicio + 1800
        AND e.pedido_confirmado_id IS NOT NULL
    GROUP BY s.session_id
)
SELECT v.session_id, v.inicio, v.seq AS visualizacao_seq, c.seq AS carrinho_seq,
       k.seq AS checkout_seq, b.seq AS compra_seq, e.pedido_confirmado_id AS pedido_id
FROM coorte v
JOIN carrinho c ON c.session_id = v.session_id
JOIN checkout k ON k.session_id = v.session_id
JOIN compra b ON b.session_id = v.session_id
LEFT JOIN silver_eventos e ON e.session_id = b.session_id AND e.event_seq = b.seq
