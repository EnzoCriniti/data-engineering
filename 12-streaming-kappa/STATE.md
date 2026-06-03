# Gabarito de estado - Capítulo 12

## Objetivo do capítulo

Calcular métricas ao vivo com arquitetura Kappa, usando eventos continuos e processamento com estado.

## Estado inicial

O capítulo deve recriar o estado final do capítulo 11:

- log de eventos disponível;
- lakehouse como destino histórico;
- CDC ou eventos operacionais alimentando a plataforma;
- necessidade de métricas em segundos.

## Etapas do capítulo

1. Subir Redpanda.
2. Criar topicos de eventos operacionais.
3. Implementar producer de eventos de GPS/entrega.
4. Implementar processor com janelas.
5. Publicar métricas em topico de saída.
6. Persistir métricas no lakehouse.
7. Permitir reprocessamento relendo o log.

## Estado final esperado

Ao final, deve existir:

- topico de eventos de GPS;
- topico de métricas ao vivo;
- processor com estado;
- checkpoint ou mecanismo de recuperacao;
- métricas historizadas no lakehouse.

## Validações

- Eventos chegam ao topico de entrada.
- Métricas são atualizadas em janela.
- Eventos atrasados são tratados conforme regra de watermark.
- Reprocessar do inicio reproduz os agregados.
- Agregado streaming bate com recomputacao batch para a mesma janela.

## Como o proximo capítulo usa este estado

O capítulo 13 usa a plataforma histórica e os sinais recentes para preparar uma feature table de fraude de pagamentos.
