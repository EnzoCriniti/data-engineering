# Redes e seguranca

## Segmentacao lógica

Em produção, a NuvemStore separaria redes por responsabilidade:

| Zona | Exemplos | Exposicao |
| --- | --- | --- |
| Pública | frontend, gateway/API pública | internet |
| Aplicação | backend e-commerce | interna |
| Dados transacionais | OLTP | interna restrita |
| Plataforma de dados | Airflow, Spark, lake, lakehouse | interna |
| Consumo | Trino, Metabase | restrita a usuários internos |
| Observabilidade | logs, métricas, alertas | interna |

No Docker local, a segmentacao e simplificada. O principio contínua: expor portas apenas quando forem necessarias para operação ou estudo.

## Acessos

| Componente | Controle esperado |
| --- | --- |
| OLTP | usuário da aplicação separado de usuário de leitura/CDC. |
| Warehouse | usuário de carga e usuário BI read-only. |
| API externa | token ou chave por ambiente. |
| Airflow | conexões e segredos fora do código. |
| Metabase | acesso somente leitura aos dados analíticos. |
| CDC | usuário replicador com privilegios minimos. |
| Lake/Lakehouse | credenciais de object storage por serviço. |

## Segredos

Regras:

- `.env` local não deve conter segredo real;
- `.env.example` documenta variaveis, mas não credenciais reais;
- senhas e tokens reais ficariam em secret manager;
- logs não devem imprimir tokens, senhas ou payloads sensiveis.

## Dados sensiveis

Mesmo com dados Faker, a arquitetura considera boas praticas:

- minimizar PII em camadas de consumo;
- mascarar dados sensiveis em BI quando aplicavel;
- separar métricas agregadas de dados identificaveis;
- registrar ownership de tabelas;
- documentar retencao de dados.

## Riscos principais

| Risco | Mitigacao |
| --- | --- |
| BI acessando OLTP diretamente | usar warehouse/gold e usuário read-only. |
| CDC com privilegio excessivo | usuário replicador dedicado. |
| API externa instável | retries, timeout e checkpoint. |
| Dados sensiveis em logs | sanitizacao e padrão de logging. |
| Credenciais versionadas | `.gitignore`, `.env.example` e secret manager em produção. |
