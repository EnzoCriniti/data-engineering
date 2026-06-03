# Redes e seguranca

## Segmentacao logica

Em producao, a NuvemStore separaria redes por responsabilidade:

| Zona | Exemplos | Exposicao |
| --- | --- | --- |
| Publica | frontend, gateway/API publica | internet |
| Aplicacao | backend e-commerce | interna |
| Dados transacionais | OLTP | interna restrita |
| Plataforma de dados | Airflow, Spark, lake, lakehouse | interna |
| Consumo | Trino, Metabase | restrita a usuarios internos |
| Observabilidade | logs, metricas, alertas | interna |

No Docker local, a segmentacao e simplificada. O principio continua: expor portas apenas quando forem necessarias para operacao ou estudo.

## Acessos

| Componente | Controle esperado |
| --- | --- |
| OLTP | usuario da aplicacao separado de usuario de leitura/CDC. |
| Warehouse | usuario de carga e usuario BI read-only. |
| API externa | token ou chave por ambiente. |
| Airflow | conexoes e segredos fora do codigo. |
| Metabase | acesso somente leitura aos dados analiticos. |
| CDC | usuario replicador com privilegios minimos. |
| Lake/Lakehouse | credenciais de object storage por servico. |

## Segredos

Regras:

- `.env` local nao deve conter segredo real;
- `.env.example` documenta variaveis, mas nao credenciais reais;
- senhas e tokens reais ficariam em secret manager;
- logs nao devem imprimir tokens, senhas ou payloads sensiveis.

## Dados sensiveis

Mesmo com dados Faker, a arquitetura considera boas praticas:

- minimizar PII em camadas de consumo;
- mascarar dados sensiveis em BI quando aplicavel;
- separar metricas agregadas de dados identificaveis;
- registrar ownership de tabelas;
- documentar retencao de dados.

## Riscos principais

| Risco | Mitigacao |
| --- | --- |
| BI acessando OLTP diretamente | usar warehouse/gold e usuario read-only. |
| CDC com privilegio excessivo | usuario replicador dedicado. |
| API externa instavel | retries, timeout e checkpoint. |
| Dados sensiveis em logs | sanitizacao e padrao de logging. |
| Credenciais versionadas | `.gitignore`, `.env.example` e secret manager em producao. |
