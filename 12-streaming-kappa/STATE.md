# Gabarito de estado - Capitulo 12

## Objetivo do capitulo

Calcular metricas ao vivo com arquitetura Kappa, usando eventos continuos e processamento com estado.

## Estado inicial

O capitulo deve recriar o estado final do capitulo 11:

- log de eventos disponivel;
- lakehouse como destino historico;
- CDC ou eventos operacionais alimentando a plataforma;
- necessidade de metricas em segundos.

## Etapas do capitulo

1. Subir Redpanda.
2. Criar topicos de eventos operacionais.
3. Implementar producer de eventos de GPS/entrega.
4. Implementar processor com janelas.
5. Publicar metricas em topico de saida.
6. Persistir metricas no lakehouse.
7. Permitir reprocessamento relendo o log.

## Estado final esperado

Ao final, deve existir:

- topico de eventos de GPS;
- topico de metricas ao vivo;
- processor com estado;
- checkpoint ou mecanismo de recuperacao;
- metricas historizadas no lakehouse.

## Validacoes

- Eventos chegam ao topico de entrada.
- Metricas sao atualizadas em janela.
- Eventos atrasados sao tratados conforme regra de watermark.
- Reprocessar do inicio reproduz os agregados.
- Agregado streaming bate com recomputacao batch para a mesma janela.

## Como o proximo capitulo usa este estado

O capitulo 13 usa a plataforma historica e os sinais recentes para preparar uma feature table de fraude de pagamentos.
