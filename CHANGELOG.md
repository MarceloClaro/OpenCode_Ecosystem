# Changelog

All notable changes to this project will be documented in this file.

## [v5.0.0] - 2026-06-02
### Added
- Evo-12: MCP Expansion — 4 MCPs cientificos (latest-science, research-mcp, sura-papers, arxiv-mcp) = 10 fontes academicas unificadas
- Evo-12: 28 skills de datasets (gnomAD, GTEx, dbSNP, Ensembl, PDB, STRING, PubChem, OpenFDA, etc.) — total 38 science skills
- Evo-13: 4 Reasoning Engines — Z3 4.16 (prova formal), SymPy 1.14 (simbolico), miniKanren (logica relacional), Critical (15 falacias + vieses)
- Evo-11: 9 skills cientificas core (AlphaFold, PubMed, ChEMBL, UniProt, FoldSeek, ClinVar, PyMOL, OpenAlex)
- Evo-10: SandeClaw Integration — ProviderFactory (Multi-LLM fallback), Hot-Reload Skills, ReAct Agent Loop
- Evo-10: 5 MCPs criticos restaurados + SciHub reabilitado
- Evo-9: Qualis Target Navigator (7 fatores, 49 areas CAPES)

### Changed
- Skills: 46 → 150 (+104)
- MCPs: 41 → 46 (+5)
- Science skills: 2 → 38
- Reasoning engines: 0 → 4
- TDD suites: 226
- SDD specs: 162
- Science: 38
- Agency agents: 26
- MCP health: 58% → 50%
- README, AGENTS.md, AGENTS_PTBR.md atualizados para v5.0.0

## [v4.6.1] - 2026-05-27
### Added
- Taxonomia universal: 350 tipos de raciocinio em 35 categorias (I-XXXV), 335 referencias
- 11 novas categorias: Quantico-Informacionais, Cibernetico-Organizacionais, Geometrico-Topologicos, Linguistico-Semanticos, Psicometrico-Avaliativos, Climatico-Ambientais, Etico-Normativos Avancados, Esportivo-Performaticos, Musical-Acusticos, Culinario-Gastronomicos, Metafisico-Ontologicos
- 150 novos tipos de raciocinio (R201-R350)
- Integracao multimodal visao+texto (skill multimodal-vision): Vision Router com 3 providers (GPT-4o, Gemini 2.5 Pro, Claude Sonnet), 8 Visual Reasoning Types (VR01-VR08), pipeline 4 estagios
- Publicacao open-source: LICENSE (MIT), README.md, CONTRIBUTING.md, .gitignore, GitHub Actions CI (lint+test+LaTeX+artifacts)
- Validacao clinica em arteterapia decolonial (skill clinical-art-therapy): pipeline 8 estagios, framework 6 dimensoes, protocolo etico CEP/TCLE/LGPD, TCC integrado (Nadielle Darc)
- Cora-Debate V7: 7 sub-verificadores formais para codigo-fonte (V7a Syntax AST, V7b Logic Prover/Hoare, V7c Type Safety, V7d Resource Bounds/Big-O, V7e Security Patterns/OWASP, V7f Test Coverage, V7g Invariant Checker)
- Score composto V7 0-100 com pesos por sub-verificador
- TDD Academic v2.0 validado: 25/25 testes (100%), relatorios JSON+MD
- Anteprojeto PPGTE validado: PDF compilado (9 pgs, 161KB), apendice TDD inserido
- Dissertacao compilada: 30 pgs, 381KB, PDF via MiKTeX

### Changed
- Taxonomia: 212 -> 350 tipos (+65%), 27 -> 35 categorias (+30%)
- Cora-Debate: v1.0.0 -> v1.1.0, V1-V6 -> V1-V7 (7 verificadores, 21 sub-verificadores)
- SKILL.md Cora-Debate: 211 -> 306 linhas (+95 linhas)
- Documentacao: CHANGELOG.md, README.md, CONTRIBUTING.md para publicacao aberta
- CI/CD: GitHub Actions adicionado ao workflow de desenvolvimento

### Fixed
- LaTeX: Unicode █ (U+2588) em Gantt chart corrigido com comando \ganttbar
- LaTeX: \wedge fora de math mode corrigido para $F^{*}$
- LaTeX: \multirow pacote ausente adicionado
- KeyError score no editais-br v7.1: setdefault + CACHE_VERSION

## [v4.6.1] - 2026-05-27
### Added
- Artigo Qualis A1 completo (19 paginas, 26 referencias com DOIs auditaveis)
- Fundamentacao teorica rigorosa: UCB1, Platt Scaling, ECE, Cora-Debate
- Loop autonomo de micro-versionamento (DETECT->ANALYZE->APPLY->VERIFY->BUMP)
- 55 problemas IMO testados (2001-2020), PCI medio 98.3/100, 100% aprovacao
- Dataset IMO integrado: github.com/MarceloClaro/IMO_QUESTIONS_SOLUTIONS
- ASI-Evolve (GAIR-NLP) como submodule com Cognition Store (10 itens)
- 212 raciocinios em 27 categorias (8 autonômos: R201-R208)
- 4 correcoes automaticas: R23 (-56% desativacoes), R34 (-83%), func_eq (+8pp), Platt (ECE 0.25->0.12)
- Geometry fix: 5->11 reasoning types, PCI 96->98
- Afiliacao: GeoMaker+IA — Museu Escolar Itinerante (CNM 9.76.35.5698)

### Changed
- Taxonomia: 204->212 raciocinios (novas categorias XXVI Geometric, XXVII Perturbation)
- Classificador: keyword-based (38%) -> TF-IDF + cosine (70-95%)
- Calibracao: Platt Scaling integrado ao pipeline de producao
- Documentacao: 6 novos documentos tecnicos minuciosos
- README: badges atualizados (IMO, PCI, Cora, Artigo Qualis A1)

## [v4.6.1.0] - 2026-05-27
### Added
- Refined the ecosystem structure and improved repository organization.
- Expanded technical and conceptual documentation for the multi-agent platform.
- Strengthened the project foundation for future integrations, automations, and operational growth.

### Changed
- Improved the clarity of the ecosystem architecture presentation.
- Increased project maturity for release management and future versioning.

## [v4.0.0] - 2026-05-27
### Added
- Consolidated the multi-agent architecture vision of the OpenCode Ecosystem.
- Expanded the structured technical artifacts and project documentation.
- Prepared the repository for scalability across specialized agents and autonomous flows.

### Changed
- Improved overall repository structure and architectural clarity.
- Strengthened the conceptual and scientific narrative of the platform.

## [v1.0.0] - 2026-05-27
### Added
- Initial public release of the OpenCode Ecosystem.
- Introduced the foundational structure of the platform.
- Published the first documented vision for a coordinated multi-agent AI ecosystem.

### Changed
- Established the initial base for future evolution of the project.
