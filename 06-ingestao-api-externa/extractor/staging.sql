create schema if not exists staging;

create table if not exists staging.transportadora_entregas (
    entrega_id varchar primary key,
    pedido_id integer not null,
    updated_at timestamptz not null,
    ingestion_ts timestamptz not null,
    payload json not null
);

create table if not exists staging.transportadora_checkpoint (
    fonte varchar primary key,
    updated_at timestamptz not null
);
