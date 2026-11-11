# System Design - NuvemStore

Esta pasta descreve a arquitetura macro da NuvemStore, a empresa ficticia usada em todos os capítulos do repositorio.

Os capítulos 00 a 17 acompanham a evolução da plataforma de dados. Esta pasta apresenta o desenho da empresa, incluindo aplicação, domínios de negócio, redes, segurança e observabilidade.

## Como ler

- [company-architecture.md](./company-architecture.md): arquitetura macro da empresa.
- [data-platform.md](./data-platform.md): fontes, processamento, armazenamento e consumo de dados.
- [architecture-timeline.md](./architecture-timeline.md): como componentes entram, amadurecem e viram legado.
- [networking-and-security.md](./networking-and-security.md): isolamento, acessos e controles minimos.
- [reliability-and-observability.md](./reliability-and-observability.md): logs, alertas, qualidade, lineage e monitoramento.

## Ideia central

A arquitetura não nasce pronta. Ela evolui:

1. aplicação e OLTP;
2. analytics no mesmo banco;
3. warehouse dedicado;
4. pipelines batch;
5. múltiplas fontes;
6. orquestracao;
7. lake on-prem;
8. migracao para object storage;
9. lakehouse;
10. CDC e streaming;
11. dados para ML;
12. infraestrutura como código, qualidade e observabilidade;
13. consolidação da arquitetura e das evidências.

Alguns componentes deixam de ser o centro da arquitetura e viram legado controlado. O warehouse relacional, por exemplo, e essencial no inicio, mas perde protagonismo quando o lakehouse amadurece.
