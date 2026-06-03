CREATE SCHEMA IF NOT EXISTS staging;

CREATE TABLE IF NOT EXISTS staging.transportadora_entregas (
    entrega_id integer PRIMARY KEY,
    pedido_id integer NOT NULL,
    transportadora varchar(80) NOT NULL,
    status varchar(40) NOT NULL,
    cidade_destino varchar(100) NOT NULL,
    previsao_entrega date,
    entregue_em timestamp,
    ocorrencia text,
    atualizado_em timestamp NOT NULL,
    carregado_em timestamp NOT NULL DEFAULT now()
);
