# Trilha sem soluções (edição de exercícios)

## Para que serve

A `main` é o portfólio: código que roda, deploy no NAS, provas. Para dar aulas, mentorias ou estudar de novo do zero, é útil ter a **mesma trilha sem o gabarito**: o aluno recebe o cenário, a aula e o runbook, e constrói o código sozinho.

## Como funciona

A edição de exercícios vive na branch **`trilha-exercicios`**, **gerada automaticamente** a partir da `main`. Ninguém faz commit nela à mão. Ver [decisão 0004](./decisoes/0004-trilha-sem-solucoes-gerada.md).

```text
main (gabarito) ──[tools/gerar_trilha_exercicios.py]──> trilha-exercicios (exercício)
```

O script:

1. parte de uma cópia limpa da `main`;
2. para cada capítulo, lê `exercicio.yml`, que lista o que é solução (ex.: `seed/seed.py`, `pipeline/`);
3. remove esses arquivos e o `SOLUTION.md`;
4. no lugar de cada arquivo de código removido, deixa um esqueleto quando o `exercicio.yml` indicar (assinaturas de função com `TODO`, para o aluno não começar da página em branco);
5. mantém `README.md`, `GUIDE.md`, `RUNBOOK.md`, `TECHNICAL.md`, `.env.example`, `docker-compose.yml` e os dados de apoio;
6. remove `deploy/`, `.platform/` e `docs/diario/` (são do meu portfólio, não da aula);
7. troca o README raiz por uma versão "como fazer a trilha";
8. faz commit em `trilha-exercicios` com a referência do commit da `main` de origem.

Um workflow do GitHub Actions roda o script a cada push na `main`. Assim a trilha nunca fica desatualizada.

## Formato do `exercicio.yml`

```yaml
# 04-elt-batch-com-python/exercicio.yml
remover:
  - pipeline/pipeline.py
esqueletos:
  pipeline/pipeline.py: |
    """ELT batch: extrai do OLTP, carrega raw no DuckDB e cria os marts.

    Siga o GUIDE.md, etapas 1 a 4.
    """

    def extrair(): ...      # TODO etapa 1
    def carregar(): ...     # TODO etapa 2
    def criar_marts(): ...  # TODO etapa 3
manter:
  - pipeline/Dockerfile
  - pipeline/requirements.txt
```

Decisão por capítulo: o `docker-compose.yml` normalmente fica na trilha, porque o foco é o pipeline e não a infraestrutura. Nos capítulos em que montar o ambiente é o exercício (ex.: o 03), ele entra em `remover`.

## Como o aluno valida

O checklist do `GUIDE.md` e as validações do `RUNBOOK.md` servem para os dois lados. Quando o teste de ponta a ponta do CI existir para um capítulo, ele também vai para a trilha: o aluno sabe que terminou quando o teste passa.

## Estado

- [ ] `tools/gerar_trilha_exercicios.py`
- [ ] `exercicio.yml` nos capítulos 00, 02, 03 e 04
- [ ] workflow que atualiza a branch `trilha-exercicios`
- [ ] README da trilha
