# 0001 — Código real na `main`

- **Status:** Aceita
- **Data:** 10/11/2026

## Contexto

Em junho de 2026 o repositório tinha código nos capítulos 00 a 04. Na reorganização como trilha de estudo (commit `85d04b1`), o código saiu dos arquivos e passou a existir só dentro dos `SOLUTION.md`. A `main` ficou com 18 capítulos documentados e nenhum arquivo executável, e o README ainda marcava capítulos como implementados.

Quem avalia um portfólio abre a branch padrão e procura código. Encontrar só Markdown passa a impressão de um projeto que nunca rodou.

## Decisão

- A `main` tem o código como arquivos reais, que rodam e são testados no CI.
- O código é a fonte da verdade. O `SOLUTION.md` deixa de copiar o código e passa a explicar as decisões, apontando para os arquivos.
- Os selos de status do README só mudam quando o capítulo roda e passa no teste de ponta a ponta.

## Alternativas consideradas

- **Manter só a trilha em Markdown:** bom para aulas, ruim como portfólio (não há o que rodar nem o que mostrar no ar).
- **Duas branches mantidas à mão (exercício e gabarito):** cada correção precisaria ser feita duas vezes, e as branches divergiriam. Substituída pela branch gerada ([0004](./0004-trilha-sem-solucoes-gerada.md)).
- **Código na `main` e também copiado no `SOLUTION.md`:** dobra a manutenção e os dois divergem (já tinha acontecido: os `.env.example` e os RUNBOOKs não batiam com os composes das soluções).

## Consequências

- Os capítulos são convertidos ao novo `SOLUTION.md` aos poucos, na etapa em que forem implementados.
- A edição sem soluções passa a depender de um script ([0004](./0004-trilha-sem-solucoes-gerada.md)).
