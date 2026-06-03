CREATE SCHEMA IF NOT EXISTS ml;

CREATE TABLE IF NOT EXISTS ml.fraude_pagamento_features (
    pagamento_id integer PRIMARY KEY,
    pedido_id integer NOT NULL,
    cliente_id integer NOT NULL,
    valor numeric(12, 2) NOT NULL,
    metodo varchar(40) NOT NULL,
    status_pagamento varchar(40) NOT NULL,
    cidade_cliente varchar(100),
    categoria_mais_cara varchar(100),
    quantidade_itens integer NOT NULL,
    valor_medio_item numeric(12, 2) NOT NULL,
    pedidos_cliente_ultimos_30d integer,
    pagamentos_recusados_cliente_ultimos_30d integer,
    velocidade_entrega_media_5min numeric(12, 2),
    score_fraude numeric(6, 4),
    label_fraude boolean,
    feature_ts timestamp NOT NULL
);
