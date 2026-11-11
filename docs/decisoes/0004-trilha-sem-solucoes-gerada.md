# 0004 — Trilha sem soluções em branch gerada por script

- **Status:** Aceita
- **Data:** 10/11/2026

## Contexto

Além do portfólio, a trilha tem valor para dar aulas e mentorias: o aluno recebe o cenário e a aula e constrói o código. Para isso precisa existir uma versão sem o gabarito. Ao mesmo tempo, a `main` precisa ter o código completo ([0001](./0001-codigo-real-na-main.md)).

## Decisão

A edição de exercícios vive na branch `trilha-exercicios`, gerada por `tools/gerar_trilha_exercicios.py` a partir da `main` a cada push, usando um `exercicio.yml` por capítulo que lista o que é solução. A branch nunca recebe commit à mão. Detalhes em [trilha-sem-solucoes.md](../trilha-sem-solucoes.md).

## Alternativas consideradas

- **Duas branches mantidas à mão:** toda correção precisaria ser feita duas vezes, e elas divergiriam.
- **Pasta `exercicios/` dentro da `main`:** duplica a estrutura inteira e confunde quem avalia o portfólio.
- **Repositório separado:** mais um lugar para manter e sincronizar; pode ser feito depois, a partir da branch, se as aulas acontecerem.

## Consequências

- Cada capítulo implementado ganha um `exercicio.yml`.
- O `SOLUTION.md` precisa apontar para os arquivos em vez de copiá-los, para que remover arquivos seja suficiente.
