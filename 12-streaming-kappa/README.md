# Capitulo 12 - Streaming em tempo real (Kappa)

> De onde viemos: CDC captura mudancas quase em tempo real, mas o negocio tambem precisa calcular metricas ao vivo.

## Cenario de negocio

A NuvemStore recebe eventos de GPS dos entregadores. Operacoes quer acompanhar entregas ativas por regiao, velocidade media e anomalias em janelas de tempo.

Essa necessidade pede processamento continuo com estado.

## Status desta etapa

Status atual: **ambiente base**.

O compose sobe:

- Redpanda;
- Redpanda Console.

Producer, processor, topicos e sinks serao implementados depois.

## Como esta etapa migra a anterior

Streaming entra depois do CDC porque transportar eventos nao basta; agora a plataforma precisa calcular metricas continuas com estado.

Plano de migracao:

1. reutilizar o log de eventos como fonte principal;
2. criar producer para eventos operacionais, como GPS de entregadores;
3. processar janelas de tempo para metricas ao vivo;
4. persistir metricas no lakehouse para historico;
5. comparar agregados streaming com uma recomputacao batch da mesma janela;
6. manter batch como auditoria/reprocessamento, nao como fonte principal de baixa latencia.

## Como subir

```bash
cp .env.example .env
docker compose up -d
```

Redpanda Console:

```text
http://localhost:8080
```

## Conceitos principais

- Lambda vs Kappa.
- Event time vs processing time.
- Tumbling, sliding e session windows.
- Watermark para eventos atrasados.
- Estado, checkpointing e backpressure.

Veja o detalhamento em [TECHNICAL.md](./TECHNICAL.md).

## A dor que sobra

Depois de batch, lakehouse, CDC e streaming, a plataforma tem sinais historicos e recentes. A proxima etapa e preparar esses dados para um caso de ML: fraude de pagamentos. Essa dor leva ao capitulo 13.
