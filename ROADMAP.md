# Roadmap — OpenCode Ecosystem

Este documento apresenta o histórico de versões, os ciclos de evolução completados e as metas futuras do **OpenCode Ecosystem**.

---

## Histórico de Versões Principais

| Versão | Marco principal | Destaques |
|:------:|----------------|-----------|
| **v3.5** | Sincronização v3.5 | Detector CJK + `ptbr_corrector.py` + token efficiency (+40% densidade) |
| **v4.0** | Integração MiroFish/BettaFish | Pipeline P14-P18 + PhD Auditor + nexus-phd-strategist |
| **v4.2** | P14-P18 completo | 38 tipos de raciocínio + Teoria dos Jogos (10 estratégias) + Agent Forum |
| **v4.2.1** | Documentação e estabilização | 7 SVGs de arquitetura + DI Migration Fases 1-7 (88/88 testes) + 125 agentes |

---

## Ciclos de Evolução Completados

O plugin **manus-evolve.ts** executa o ciclo autônomo **PLAN → ACT → REFLECT → EXTRACT → EVOLVE**, gerando novas skills em `evolution/` a partir de padrões de sucesso. Abaixo, os 8 ciclos completados:

| Ciclo | Skill principal gerada | Score | Principais conquistas |
|:-----:|----------------------|:-----:|----------------------|
| **evo-1** | Cross-validation + World Bank API | 85/100 | Educação r=-0.03; P&D privado r=+0.73 |
| **evo-2** | Pipeline de artigo 35 páginas ABNT | 90/100 | Serviços de alta tecnologia r=+0.95 (preditor mais forte) |
| **evo-3** | TSAC: 46 citações auditáveis | 95/100 | 46 anotações TSAC anti-IA auditáveis |
| **evo-4** | Sci-Hub MCP + arXiv multi-source | 88/100 | Integração multi-fonte para pesquisa acadêmica |
| **evo-5** | Pearson CV em 27 indicadores | 92/100 | Cross-validation com 27 indicadores socioeconômicos |
| **evo-6** | Iterative Correction Loop v2.0 | 95/100 | Banca + orientadores + corretores: 86,5 → 92,7 (+7,1%) |
| **evo-7** | Sync v3.5 + detector CJK | 96/100 | Zero tolerância CJK; contexto chinês → saída PT-BR |
| **evo-8** | Progressive disclosure + observabilidade | 98/100 | Skills ≤ 2.500B + health monitoring contínuo |

**Progressão geral:** 85 → 98 (+15,3%) · Média: 91,1/100

---

## Estado Atual (v4.2.1)

| Indicador | Valor |
|-----------|:-----:|
| Agentes especializados | 125 |
| MCP Servers | 40 (38 local + 2 remoto) |
| Skills | 104 em 12 categorias |
| Tipos de raciocínio | 38 em 6 categorias |
| Estratégias de Teoria dos Jogos | 10 |
| Estratégias RAG | 9 (auto-select via Adaptive RAG) |
| Container DI — serviços registrados | 11 (8 core + 3 plugins TS) |
| Testes DI passando | 88/88 |
| Health score Nexus | 96/100 |
| Confiança Reversa Framework | 100/100 |
| Linhas de código Python | ~114.000 |

---

## Metas de Curto Prazo

| Meta | Descrição | Prioridade |
|------|-----------|:----------:|
| Suporte multiplataforma | Expandir oficialmente para Linux e macOS, além do Windows 11 | Alta |
| Cobertura de testes > 95% | Aumentar a cobertura dos testes legado (atualmente 378/391) e adicionar testes para módulos não cobertos | Alta |
| Mais fontes SEEKER | Adicionar fontes acadêmicas adicionais ao pipeline de pesquisa (Google Scholar, IEEE, Scopus) | Média |
| Internacionalização (EN, ES) | Suporte a inglês e espanhol na saída dos agentes, além do PT-BR | Média |
| Documentação expandida | Criar TUTORIALS.md, GLOSSARY.md e AGENTS_PTBR.md | Alta |

---

## Metas de Médio Prazo

| Meta | Descrição | Prioridade |
|------|-----------|:----------:|
| 150+ agentes | Expandir o catálogo de agentes especializados para cobrir novos domínios | Média |
| 50+ MCPs | Adicionar novos servidores MCP para integração com mais ferramentas e APIs | Média |
| Mais backends quânticos | Integrar com IBM Quantum, Amazon Braket e simuladores adicionais além do MPS | Média |
| API REST | Expor uma API REST para acesso externo ao ecossistema, permitindo integração com aplicações terceiras | Alta |
| Dashboard de monitoramento | Interface visual para acompanhar saúde do ecossistema, ciclos de evolução e métricas em tempo real | Média |

---

## Metas de Longo Prazo

| Meta | Descrição | Prioridade |
|------|-----------|:----------:|
| Cloud deployment | Possibilitar a execução do ecossistema em ambientes cloud (AWS, GCP, Azure) com orquestração distribuída | Alta |
| Marketplace de skills | Plataforma para compartilhamento e distribuição de skills entre usuários e organizações | Média |
| Colaboração multiusuário | Suporte a múltiplos usuários trabalhando simultaneamente no mesmo ecossistema em tempo real | Média |
| Certificação acadêmica | Integração com plataformas de publicação para submissão automática de artigos Qualis A1 | Baixa |
| Agentes autônomos de longa duração | Agentes que operam continuamente em background, monitorando e evoluindo o ecossistema sem intervenção | Média |

---

## Como Contribuir para o Roadmap

Sugestões e contribuições são bem-vindas. Para propor uma nova meta ou funcionalidade:

1. Abra uma [issue](https://github.com/MarceloClaro/OpenCode_Ecosystem/issues) descrevendo a proposta
2. Consulte o [CONTRIBUTING.md](CONTRIBUTING.md) para o processo de contribuição
3. Submeta um PR com a implementação, se aplicável

---

<div align="center">

**OpenCode Ecosystem v4.2.1** — Roadmap

*Atualizado em 2026-05-21 · BRAZIL_TIMEZONE UTC-3*

</div>
