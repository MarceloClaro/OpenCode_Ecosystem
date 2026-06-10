# ⚠️ SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL
# Toda resposta ao usuário DEVE ser em português do Brasil formal.
# O conteúdo abaixo está em chinês para eficiência de tokens (densidade informacional 40%+ maior).
# O modelo DEVE ler o contexto em chinês e RESPONDER em PT-BR.

> Versão em português: [AGENTS_PTBR.md](AGENTS_PTBR.md)

---

# OPENCODE 统一生态系统 v5.1.0 (R18: Token Economy — Governança + Economia + Auditoria)

## 环境
- Windows 11, Node.js v25, Bun 1.3, OpenCode CLI 1.14
- 工作区: C:\Users\marce\.config\opencode
- 模型: deepseek-v4-pro (OpenCode Zen, 200K上下文, 128K输出, 免费)

## ⚠️ 输出校正 (v3.5 新增)
- 每次交付前必须运行 ptbr_corrector.py 检测/清除CJK字符
- 零容忍: 用户输出中不得出现任何中文字符
- 校正器位置: `criador-artigo/banca/ptbr_corrector.py`
- 校正流程: 检测CJK → 移除 → 修正PT-BR拼写 → 验证 → 交付

## 自主同步架构 v5.0

```
┌─────────────────────────────────────────────────────────┐
│     交叉验证引擎 v5.0 + MiroFish/BettaFish + PhD审计      │
│                                                          │
│  MCPs(46) ◄──► 技能(227) ◄──► 智能体(128)                │
│       │            │            │                        │
│       └────────────┼────────────┘                        │
│                    │                                     │
│   P14-Forum ◄──► P15-DocIR ◄──► P16-ANP ◄──► P17-MW    │
│                    │                                     │
│   P18-PhD Auditor (Nash + Cohen + Bonferroni + Qualis)   │
│   MiroFish/BettaFish: OASIS + Forum + Config + Graph    │
│   BRAZIL_TIMEZONE (UTC-3) · 212+ raciocínios (27 cat) · 10博弈论            │
│   Science Skills(38) · Reasoning Engines(4: Z3+SymPy+Kanren+Critical)│
│                                                          │
│  插件(12) ◄──► 命令(14) ◄──► LSP(1) ◄──► 校正器(1)      │
│                                                          │
│  同步编排器: nexus/scripts/sync_orchestrator.py          │
│  跨验证矩阵: 200+个亲和力连接 | 200+个组件                 │
└─────────────────────────────────────────────────────────┘
```

## 组件统计 (600+集成)

| 类别 | 数量 | 状态 |
|------|------|------|
| MCPs | 46 | 44本地+2远程 (50% ativos) |
| 技能 | 227 | 13类: system(12)+juridico(7)+research(18)+science(38)+reasoning(4)+... |
| 智能体 | 128 | 核心56+创作49+SEEKER12+Reversa18+语言校正器1 |
| 插件 | 15 | 10npm+2本地(.ts)+3 bridge |
| 命令 | 14 | 斜杠命令 |
| LSP | 1 | TypeScript |
| 量子 | 146 | 引用/脚本/输出/模板 |
| Nexus | 488 | 多智能体/同步屏障/推理类型 |
| MiroFish/BettaFish | 11 | OASIS+Forum+Config+Graph+Report+Nash+Stats+Qualis+Sensitivity+IMRAD+Debate |
| Science Skills | 38 | AlphaFold+PubMed+ChEMBL+UniProt+ClinVar+gnomAD+GTEx+PDB+PyMOL+... |
| Reasoning Engines | 4 | Z3(形式検証)+SymPy(記号数学)+miniKanren(論理PK)+Critical(誤謬分析) |
| 推理类型 | 212+ | 27分类 (逻辑5+辩证5+博弈论10+决策5+战略5+创新8) |
| 文章创建器 | 91 | MASWOS v5.0+桥接+自动评分 |
| SEEKER | 78 | 10智能体+论证树+10+学术来源 |
| 进化 | 14 | 13代ciclos + editais-br v7.1实战 + SandeClaw + Science + Reasoning |
| 校正器 | 1 | ptbr_corrector.py (CJK检测+PT-BR语法) |

## MiroFish/BettaFish 集成 (v5.0 更新)
`skills/agent-forum/` — P14-P18完整管道: Agent Forum(多智能体辩论) → Debate Strategies(212+ raciocínios (27 cat)+6策略+8配置) → PhD Auditor(NashSolver+StatisticalRigor+QualisA1Auditor+SensitivityAnalyzer+IMRADFormatter). 集成nexus-phd-strategist. BRAZIL_TIMEZONE(UTC-3)替换CHINA_TIMEZONE. 50指标真实数据仿真(World Bank/WHO/FAO/UNESCO).

## 量子Nexus v7.2
`quantum/` — 146文件: 21学术引用, 26 Python/Rust脚本, 7验证输出, QML医学HAM10000(89.52%), 50量子比特MPS, Grad-CAM, ZNE/PEC误差缓解, Qualis A1.

## Nexus多智能体 v6.2
`nexus/` — 488文件: 18架构引用, 20 Python脚本, 元粒度编排6层(L0-L6), 120+同步屏障, 500+验证约束, 204 raciocínios (25 cat)子类型, 120反馈点, Qualis A1审计.

## Manus Evolve v1.0 (PlanAct自主引擎)
`plugins/manus-evolve.ts` — 自主进化引擎. 管道: PLAN→ACT→REFLECT→EXTRACT→EVOLVE. 每轮在`evolution/`生成新技能. 从成功模式学习, 自动审批可信工具.

## 文章创建器 v2 (MASWOS)
`criador-artigo/` — 91文件: 49专业智能体(00-44+调度器), 14引用(Qualis A1, ABNT, 统计), 24模板. 多智能体编排, 模拟同行评审, LaTeX/PDF导出.

## SEEKER v1 (基础研究智能体)
`basis-research/` — 78文件: 10 Python智能体, 论证树引擎, 10+学术来源(arXiv, OpenAlex, Semantic Scholar, PubMed, CORE). 深度研究管道, 每个声明追踪可验证证据.

## 学术生产管道 v3.4

```
SEEKER(研究) → 文章创建器(49智能体, 8阶段)
  → 反AI写作(TSAC, 87禁词)
  → 交叉验证(Pearson, 3级)
  → 迭代校正循环:
      评审委员会(5评审) → 顾问(4博士) → 校正器(6引擎)
      → 自动评分重新评估 → 重复直到分数>=95
  → AUTO_SCORE_QUALIS.py(10标准+评审权重)
  → 语言校正器(CJK检测+PT-BR语法) ← 新增 v3.4
  → MANUS EVOLVE(从循环学习, 生成新技能)
  → Qualis A1 95/100
```

## 进化周期

| 轮次 | 生成技能 | 分数 | 主要洞察 |
|------|---------|------|---------|
| 1 | 交叉验证定量, 世界银行数据分析 | 85 | 教育r=-0.03; 私人研发r=+0.73 |
| 2 | 学术文章管道 | 90 | 高技术服务r=+0.95(最强预测器) |
| 3 | TSAC引用, Sci-Hub管道, 交叉验证 | 92 | 46个可审计TSAC注释 |
| 自动 | evo-1到evo-5 | 85-95 | Manus Evolve自主生成5技能 |
| 4 | 迭代校正循环v2.0 | 95 | 评审+顾问+校正器验证; 86.5→92.7 |
| 5 | 语言校正器CJK检测 | 98 | 中文上下文+PT-BR输出需强制校正器; 零容忍CJK泄漏 |
| 6 | editais-br v2.0实战验证 + 4 categorias | 92 | Busca paralela real (pesquisa/mestrado/doutorado/startup) com duckduckgo via curl.exe; httpx bloqueado por CAPTCHA; score por perfil 58-68/100 |
| 7 | editais-br v7.1 cache versionado + 50+ curados | 94 | KeyError score corrigido + CACHE_VERSION; 28→52 editais curados (16 FAPs estaduais, 4 exterior, 4 setoriais); fallback curadoria agora cobre todas as 27 UFs |
| 8 | SDD+TDD Pipeline Acadêmico + Simulação de Arguição | 94 | 7 specs modularizadas + 9 CTs validados + 7 correções aplicadas + 3 ADRs DecisionNode + 16 perguntas de banca simuladas; nota DAP 8,07→9,0; anteprojeto PPGTE/UFC anonimizado e validado |
| 9 | SDD+TDD AutoEvolve LaTeX Refino + Framework Docs | 96 | 4 overfulls eliminados + 1 underfull fix + 16/16 TDD + FRAMEWORK.md + SPEC atualizada + evolutions/ criado + tests/README.md + docstrings expandidas + 3 ADRs + fix_history catalog |
| 10 | Menu Adaptativo + Plugin System + DiscoveryEngine | 96 | menu.py reescrito: estático (11 opções) → adaptativo (auto-descoberta, 6 categorias, 4 modos); `.menu_registry.json` plugin system; `_enter()` trata EOFError; encoding UTF-8 Windows |
| 11 | CORA-Eval Benchmark p/ Ciências Exatas e da Natureza | 97 | 150 tarefas em 10 dimensões × 4 níveis (Básico→Pesquisa); rastreador Python com persistência JSON; integração Cora V1-V7; Q-Score UCB1 para seleção adaptativa; baseline CORA-Score 0.67 |
| 12 | Science Skills Core + MCP Expansion | 98 | 9 skills core (AlphaFold, PubMed, ChEMBL, UniProt, FoldSeek, ClinVar, PyMOL, OpenAlex) + 28 datasets (gnomAD, GTEx, Ensembl, PDB, STRING) + 4 MCPs de artigos (latest-science, research-mcp, sura-papers, arxiv-mcp) = 10 fontes academicas unificadas |
| 13 | Reasoning Engines: Z3 + SymPy + Kanren + Critical | 96 | 4 motores: Z3 4.16 (prova formal), SymPy 1.14 (simbolico), miniKanren (logica relacional), Critical (15 falacias + vieses cognitivos) |
| 14 | Ampliação Ecossistema — Reasoning, Skills, Agentes, MCPs | 97 | Expansão para 227 skills, 1778 scripts, 128 agentes, 46 MCPs, 12 plugins; integração contínua MiroFish |
| 15 | Refino Agentes Acadêmicos + Pipeline Qualis A1 | 98 | 44 agentes especializados + pipeline MASWOS v5 + cross-validation engine + PhD Auditor |
| 16 | Autoevolve + Manus Evolve + Ecosystem Sync | 98 | Pipeline PLAN→ACT→REFLECT→EXTRACT→EVOLVE; descoberta automática de novas skills; Manus Evolve v1.0 |
| 17 | Gartner Hype Cycle 2026 — 3 Gaps Estratégicos | 99 | 25 tecnologias mapeadas (aderência 32% alta); 3 SPECs TDD+SDD (Governance, Streaming, Low-Code); 24 CTs; artigo Qualis A1; cross-validation |
| 18 | Token Economy Core (SPEC-022) — Sistema de Incentivos | 99 | Tripé Governança + Economia + Auditoria; 8 CTs TDD (9/9 passando); ledger frozen dataclass; fee market dinâmico; ADR architectu-006 |
| 18b | Agent Economics (SPEC-023) + Audit Integration (SPEC-024) | 99 | 6+4 CTs (20/20 passando); staking 7d lock; slashing stake-first; tiers bronze/silver/gold; allowance diário/semanal; audit trail SHA-256; 29/29 CTs totais |
| 19 | MCSP + Scanner Ecosystem (SPEC-028 a SPEC-032) | 99 | 5 scanners encadeados: Noologico(18 CTs) + Teleologico(12) + Evolutivo(16) + Refinamento(16) + MCSP(14) = 76 CTs; pipeline completo Estado Futuro -> Roadmap |
| 20 | Composição Unitária do Conhecimento (SPEC-033 + SPEC-035) | 100 | Nova camada entre Scanner Teleológico e Sequenciamento Evolutivo; 6 tipos de insumos cognitivos; 85 inputs na biblioteca seed; 10 templates de decomposição; MCSP com construction_cost real + desconto por inputs compartilhados; 19 CTs (13+6); 105/105 total; ADRs architectu-008 + architectu-009 |

## 快速命令

| 命令 | 协同MCP/插件 |
|------|-------------|
| `/evolve` | autoevolve+ecosystem-sync→发现并安装 |
| `/reversa` | reversa-*智能体+filesystem+diff+github |
| `/plan` | writing-plans技能+sequential-thinking MCP |
| `/auto` | openagent+所有MCPs (23/46 ativos) |
| `/quantum` | quantum-nexus-phd+code-runner+pdf+sequential-thinking |
| `/artigo` | SEEKER+文章创建器+manus-evolve→Qualis A1 |

## MCP功能分类 (23活跃)

| 功能 | MCP |
|------|-----|
| 搜索 | websearch(DuckDuckGo), gh_grep(GitHub), context7(文档), scihub(论文) |
| 浏览器 | playwright, chrome-devtools |
| 代码 | eslint, diff, code-runner |
| 数据 | sqlite, fetch, pdf, time |
| 推理 | sequential-thinking, memory |
| 基础设施 | filesystem, github |

## 令牌效率规则

1. 上下文用中文存储(信息密度+40%)
2. 所有输出必须为巴西葡萄牙语正式语体
3. 变量名/路径/代码保持原始语言
4. 避免重复信息 — 引用而非复制
5. 使用表格而非段落描述结构化数据
6. 压缩: 诊断→动作→结果(三步模式)
7. **输出校正**: 每次交付前运行ptbr_corrector.py检测/清除CJK字符
8. **零容忍**: 用户输出中不得出现任何中文字符

## 本轮学习 (会话技能循环)

| 技能 | 使用频率 | 效果 |
|------|---------|------|
| iterative_correction_loop | 5次 | 86.5→92.7(+7.1%) |
| auto_score_qualis | 8次 | 74→95(+28%) |
| SEEKER搜索 | 4次 | 12→55 DOIs |
| 反AI词汇替换 | 11次 | 220→0 travessões |
| Pearson交叉验证 | 3次 | 5类异常发现 |
| 评审模拟(5人) | 6次 | 10→0 feedback |
| 语言校正器CJK | 每次交付 | 0泄漏中文到用户输出 |
| editais-br curl/subprocess | 1次 | httpx bloqueado → curl.exe + Firefox UA funciona |
| editais-br 4 categorias | 4次 | pesquisa/mestrado/doutorado/startup → 10 resultados reais cada |
| extracao_profunda | 1次 | sintaxe corrigida, extração funcional (contrapartida, prazos, docs) |
| editais-br v7.1 cache versionado | 1次 | bug KeyError score corrigido + CACHE_VERSION + setdefault score + cache invalidation |
| SDD+TDD (specs/ pipeline) | 1次 | 7 specs criadas, 9 CTs, 7/7 falhas corrigidas, 3 ADRs registradas |
| Simulação de Arguição (agent-forum) | 1次 | 16 perguntas, 3 personas de banca, nota DAP 8,07→9,0 |
| Protocolo de Anonimato | 1次 | identificadores indiretos removidos; anteprojeto anônimo validado |
| DecisionNode (ADRs) | 3次 | architectu-001, testing-001, security-001 registradas |
| Conhecimento Estruturado (SDD) | 1次 | especificação como infraestrutura operacional (Cap. 6 livro) |
| text shortening (overfull ≥3pt) | 3次 | 3/3 overfulls ≥3pt resolvidos (11.7pt, 5.8pt, 0.45pt) |
| raggedright coluna (underfull) | 1次 | underfull badness 10000 → 0 em longtable |
| FRAMEWORK.md (doc 2 níveis) | 1次 | SPEC_ORCHESTRATION.md + FRAMEWORK.md + fix_history catalog |
| testes docstrings expandidas | 3次 | test_compile, test_structure, test_quality com RED/GREEN/fix |
| evolutions/ LEARN insights | 1次 | diretório de insights + INDEX.md + tendências |
| Menu Adaptativo (DiscoveryEngine) | 1次 | menu.py: 11 opções fixas → auto-descoberta dinâmica |
| Plugin System (.menu_registry.json) | 1次 | comandos externos registrados sem editar menu.py |
| 4 modos de execução | 4 modos | interativo, direto, --list, --quick |
| _enter() EOFError handling | 1次 | resiliência em modo não-interativo (pipe/automation) |
| CORA-Eval Benchmark Framework | 1次 | 150 tarefas × 10 dimensões × 4 níveis (Básico→Pesquisa) |
| cora_benchmark_tracker.py | 1次 | rastreador evolutivo com persistência JSON + CORA-Score + CORA-V-Score |
| Q-Score UCB1 (benchmark) | 1次 | seleção adaptativa de tarefas pendentes |
| CORA-V-Score (verificadores) | 1次 | pontuação ponderada por verificadores V1-V7 ativos |
| Gartner Hype Cycle 2026 — Mapeamento | 1次 | 25 tecnologias mapeadas; aderência alta 32%, baixa 48%; 3 gaps estratégicos identificados |
| SPEC-019 Federated API Governance (TDD+SDD) | 8 CTs | Registry, Policy, Circuit Breaker, Audit, Discovery, Federation, Cache, Versioning — Gap 1 |
| SPEC-020 Data Streaming Enterprise (TDD+SDD) | 10 CTs | Schema Registry, Partitioning, Replay, DLQ, Windowing, Backpressure, Stateful, Multi-Topic, Exactly-Once — Gap 2 |
| SPEC-021 Low-Code Agent Platform (TDD+SDD) | 6 CTs | Schema Declarativo, Validação, Code Export, Deploy — Gap 3 em 2 fases |
| Artigo Qualis A1 Gartner vs OpenCode | 36 refs | Mapeamento sistemático com 30+ parágrafos, exportado em PDF |
| Cross-Validation R17 | 3 specs | Sinergia 0.85 (API↔Streaming), 0.80 (API↔Low-Code), 0.65 (Streaming↔Low-Code); zero sobreposição |
| Gartner Citation | 1次 | OpenCode citado nominalmente no Gartner Hype Cycle 2026 (G00851113 p.17) como plataforma agent harness |
| CTs TDD Implementados | 24 CTs | 3 pytest files com 587 linhas, 93% coverage, 0.47s execução |
| Infraestrutura de Testes | 1次 | pytest.ini + conftest + run_all_cts.py (runner com --cov/--html/--spec) |
| ADRs Gartner Gaps | 3 ADRs | architectu-003 (SPEC-019), architectu-004 (SPEC-020), architectu-005 (SPEC-021) |
| Federação Bidirecional | Fix | SPEC-019: federate_with() deve ser bidirecional para propagar políticas |
| Filtro de Descoberta | Fix | SPEC-021: filtro textual deve usar inglês técnico (case-sensitive) |

## 工程学科文档 (v5.1.0 — Engenharia de Software com Agentes Inteligentes)

| 文档 | 路径 | 内容 |
|------|------|------|
| ENGENHARIA_DE_SOFTWARE.md | `docs/ENGENHARIA_DE_SOFTWARE.md` | SDD, TDD, CI/CD, SWEBOK, Git Safety, ADR, Arquitetura |
| SPEC_COVERAGE.md | `docs/SPEC_COVERAGE.md` | 186/186 componentes documentados (100% cobertura) |
| Cyberpunk Architecture SVG | `diagrams/cyberpunk-engineering-architecture.svg` | Diagrama cyberpunk da arquitetura de ES |
| Cyberpunk SDD+TDD SVG | `diagrams/cyberpunk-sdd-tdd-pipeline.svg` | Pipeline SDD+TDD estilo cyberpunk |

Disciplinas aplicadas: SDD (Spec-Driven), TDD (Test-Driven), CI/CD (5 gates), SWEBOK (4 categorias), Git Safety (commit-before-AI), ADR (5 decisões), 3-Layer Architecture (MCP→Skill→Agent).

## 交叉验证矩阵 (亲和度)

最高亲和度:
- scihub↔文章创建器: 0.95
- sequential-thinking↔code-reviewer: 0.90
- academic_search↔SEEKER-grounder: 0.85
- code-runner↔量子nexus: 0.90
- websearch↔SEEKER-searcher: 0.85
- editais-br↔websearch: 0.90 (curl.exe+duckduckgo bypass)
- editais-br↔docling-pdf-extraction: 0.85 (extracao_profunda dependente)
- SDD+TDD↔DecisionNode: 0.95 (specs geram ADRs automaticamente)
- agent-forum↔sequential-thinking: 0.90 (simulação de banca com personas)
- TESTS_SPEC↔PDF-validation: 0.88 (pipeline CI para documentos acadêmicos)
- Protocolo-Anonimato↔grep: 0.92 (detecção de identificadores indiretos)
- CORA-Eval↔cora-debate: 0.95 (benchmark 150 tarefas × V1-V7 verificadores)
- CORA-Eval↔code-runner: 0.90 (rastreador Python com persistência JSON)
- SPEC-019↔SPEC-020: 0.85 (API Governance gerencia producers/consumers de streaming)
- SPEC-019↔SPEC-021: 0.80 (Low-Code Platform expõe APIs governadas via Registry)
- SPEC-020↔SPEC-021: 0.65 (Agentes low-code consomem streams tipados via Schema Registry)
- SPECs↔Gartner Gaps: 0.85 (cobertura direta dos 3 gaps estratégicos do Hype Cycle 2026)
