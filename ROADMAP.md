# Roadmap — OpenCode Ecosystem

> Visão de evolução do projeto: de onde viemos, onde estamos e para onde vamos.

---

## Histórico de Versões

| Versão | Marco Principal | Destaques |
|:------:|----------------|-----------|
| **v3.5** | Sincronização + CJK Zero-Tolerance | Sync orchestrator, `ptbr_corrector.py`, detecção e remoção de caracteres CJK, token efficiency (+40% densidade) |
| **v4.0** | MiroFish/BettaFish + PhD Auditor | Pipeline P14-P18 completo, Agent Forum com 38 raciocínios, NashSolver, StatisticalRigor, QualisA1Auditor, integração com nexus-phd-strategist |
| **v4.2** | P14-P18 + 38 Raciocínios | 10 estratégias de Teoria dos Jogos, BRAZIL_TIMEZONE (UTC-3), 50 indicadores reais (World Bank/WHO/FAO/UNESCO), SensitivityAnalyzer, IMRADFormatter |
| **v4.2.1** | 7 SVGs + DI Migration | 7 diagramas SVG interativos, Injeção de Dependência (Fases 1–7, 88/88 testes), Container com 11 serviços, bridge Python ⟷ TypeScript |
| **v4.2.2** | Antigravity Bridge + Skills Refinement | Plugin `antigravity-bridge.ts` registrado no Container (4 plugins TS), skill `antigravity-integration` indexada no registry (105 skills), MCP `antigravity-mcp` (41 total), 6 capacidades exclusivas Google DeepMind |
| **v4.2.3** | 🆕 PyPI Scout + DataOrchestrator + Multi-Domain Hooks | PyPI Scout (22+ bib. curadas, matriz de afinidade 5 pipelines, CLI 7 comandos), DataOrchestrator (NL → 8 domínios, 592 linhas), 10 Ecosystem Hooks v2.0 (R8:5 + R9:5), 30+ bibliotecas instaladas, 12 novas bibs (yfinance, ccxt, fredapi, biopython, etc.), 20+ fontes Qualis A1, artigo LaTeX ABNT 12 páginas, 3 fluxogramas SVG |

---

## Ciclos de Evolução Completados (AutoEvolve)

O plugin `manus-evolve.ts` executa o ciclo autônomo **PLAN → ACT → REFLECT → EXTRACT → EVOLVE**, gerando novas skills a cada iteração. A tabela abaixo documenta todos os ciclos completados:

| Ciclo | Skill Principal Gerada | Score | Insight Principal |
|:-----:|----------------------|:-----:|-------------------|
| evo-1 | Cross-validation quantitativa + World Bank API | 85/100 | Educação r=-0,03; P&D privado r=+0,73 |
| evo-2 | Pipeline de artigo acadêmico 35 páginas ABNT | 90/100 | Serviços de alta tecnologia r=+0,95 (preditor mais forte) |
| evo-3 | TSAC: 46 citações auditáveis + Sci-Hub pipeline | 92/100 | 46 anotações TSAC verificáveis por pares |
| evo-4 | Sci-Hub MCP + arXiv multi-source | 88/100 | Fontes múltiplas melhoram cobertura bibliográfica |
| evo-5 | Pearson Cross-Validation em 27 indicadores | 92/100 | Validação cruzada com 5 categorias de anomalias |
| evo-6 | Iterative Correction Loop v2.0 | 95/100 | Banca (5 revisores) + orientadores (4 doutores) + corretores: 86,5 → 92,7 |
| evo-7 | Sync v3.5 + detector CJK + token efficiency | 96/100 | Zero-tolerance CJK; contexto em chinês, output em PT-BR |
| evo-8 | Progressive disclosure + observabilidade | 98/100 | SKILL.md ≤ 2.500B; health score 96/100 |
| **evo-9** | **Antigravity Bridge v1.0 + SKILL indexada** | **98/100** | Pontão bidirecional OpenCode⇔Antigravity; skill `antigravity-integration` no registry; `references/antigravity-bridge-reference.md` com progressive disclosure; IESDS + Nash Generalizado N>2 adicionados à Teoria dos Jogos |
| **evo-10** | **PyPI Scout + Ecosystem Hooks v1.0 (Round 8)** | **95/100** | Catálogo curado 22+ bibliotecas, CLI 7 comandos, 5 hooks fundamentais, 7 bibliotecas instaladas |
| **evo-11** | **DataOrchestrator + Expansão Multi-Domínio (Round 9)** | **97/100** | 6 novos domínios, 5 novos hooks, DataOrchestrator NL, 5 bibliotecas, artigo ABNT |
| **evo-12** | **Auditoria Caixa Branca + Refinamento UX (Rounds 10-12)** | **95/100** | 9 componentes auditoria, ResearcherScore, BudgetAlert, AuditDashboard HTML, PipelineIntegration |
| **evo-13** | **Reasoning Orchestrator v9.0 + Teoria dos Jogos (Round 13)** | **96/100** | 68 tipos de raciocínio (58 base + 10 Game Theory), bridge AuditSystem, 11 categorias, integração Nash/Harsanyi/Shapley |

**Progressão geral:** 85 → 96 (+12,9%) · Média: 93/100

---

## Curto Prazo (Próximas Versões)

### Expansão de Plataformas
- **Linux e macOS:** suporte oficial completo (atualmente o Windows 11 é a plataforma principal)
- Adaptação de paths e scripts para ambientes Unix
- Testes de integração em múltiplos sistemas operacionais

### Cobertura de Testes > 95%
- Expandir suite de testes além dos 88/88 DI + 378/391 legado
- Adicionar testes de integração para pipelines completos (artigo, reversa, quantum)
- Cobertura de código com relatórios automatizados

### Mais Fontes para o SEEKER
- Integrar novas fontes acadêmicas (IEEE Xplore, SpringerLink, Google Scholar)
- Expandir `concept_map.json` com novos domínios de pesquisa
- Melhorar a cobertura de fontes para áreas específicas (engenharia, ciências sociais)

### Internacionalização (i18n)
- Suporte a múltiplos idiomas de saída (além de PT-BR)
- Tradução automática de documentação
- Corretor linguístico para outros idiomas

---

## Médio Prazo (6–12 Meses)

### Escala de Agentes e MCPs
- **150+ agentes** especializados (atualmente 125)
- **50+ servidores MCP** (atualmente 40)
- Novos agentes para domínios verticais: saúde, finanças, engenharia civil

### Backends Quânticos Adicionais
- Integração com IBM Qiskit Runtime
- Suporte a Amazon Braket
- Simuladores com ruído personalizado para validação experimental

### API REST
- Expor funcionalidades do ecossistema via API REST/GraphQL
- Endpoints para execução de pipelines (artigo, reversa, quantum)
- Dashboard web para monitoramento de saúde do ecossistema

### Melhorias no Pipeline Acadêmico
- Suporte a mais formatos de citação (APA, Vancouver, Chicago)
- Integração com sistemas de submissão de periódicos
- Templates para conferências específicas (ACM, IEEE, Springer)

---

## Longo Prazo (12+ Meses)

### Ecossistema Distribuído
- Execução de agentes em múltiplos nós
- Orquestração distribuída com Nexus NMA
- Balanceamento de carga entre servidores MCP

### Aprendizado Contínuo
- AutoEvolve com memória persistente entre sessões
- Transfer learning entre pipelines
- Benchmarks automatizados de qualidade

---

<div align="center">

**OpenCode Ecosystem v4.6** · Roadmap

*Última atualização: 2026-05-24*

</div>
