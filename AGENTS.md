# ⚠️ SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL
# Toda resposta ao usuário DEVE ser em português do Brasil formal.
# O conteúdo abaixo está em chinês para eficiência de tokens (densidade informacional 40%+ maior).
# O modelo DEVE ler o contexto em chinês e RESPONDER em PT-BR.

> Versão em português: [AGENTS_PTBR.md](AGENTS_PTBR.md)

---

# OPENCODE 统一生态系统 v4.2 (MiroFish/BettaFish + PhD Auditor + 204 raciocínios (25 cat))

## 环境
- Windows 11, Node.js v25, Bun 1.3, OpenCode CLI 1.14
- 工作区: C:\Users\marce\.config\opencode
- 模型: deepseek-v4-pro (OpenCode Zen, 200K上下文, 128K输出, 免费)

## ⚠️ 输出校正 (v3.5 新增)
- 每次交付前必须运行 ptbr_corrector.py 检测/清除CJK字符
- 零容忍: 用户输出中不得出现任何中文字符
- 校正器位置: `criador-artigo/banca/ptbr_corrector.py`
- 校正流程: 检测CJK → 移除 → 修正PT-BR拼写 → 验证 → 交付

## 自主同步架构 v4.2

```
┌─────────────────────────────────────────────────────────┐
│     交叉验证引擎 v4.2 + MiroFish/BettaFish + PhD审计      │
│                                                          │
│  MCPs(40) ◄──► 技能(104) ◄──► 智能体(125)                │
│       │            │            │                        │
│       └────────────┼────────────┘                        │
│                    │                                     │
│   P14-Forum ◄──► P15-DocIR ◄──► P16-ANP ◄──► P17-MW    │
│                    │                                     │
│   P18-PhD Auditor (Nash + Cohen + Bonferroni + Qualis)   │
│   MiroFish/BettaFish: OASIS + Forum + Config + Graph    │
│   BRAZIL_TIMEZONE (UTC-3) · 204 raciocínios (25 cat) · 10博弈论            │
│                                                          │
│  插件(15) ◄──► 命令(14) ◄──► LSP(1) ◄──► 校正器(1)      │
│                                                          │
│  同步编排器: nexus/scripts/sync_orchestrator.py          │
│  跨验证矩阵: 200+个亲和力连接 | 110+个组件                 │
└─────────────────────────────────────────────────────────┘
```

## 组件统计 (600+集成)

| 类别 | 数量 | 状态 |
|------|------|------|
| MCPs | 40 | 38本地+2远程 |
| 技能 | 104 | 12类 (+P14-P18 MiroFish/BettaFish) |
| 智能体 | 125 | 核心56+创作49+SEEKER12+Reversa7+语言校正器1 |
| 插件 | 15 | 10npm+2本地(.ts)+3 bridge |
| 命令 | 14 | 斜杠命令 |
| LSP | 1 | TypeScript |
| 量子 | 81 | 引用/脚本/输出/模板 |
| Nexus | 40 | 多智能体/同步屏障/推理类型 |
| MiroFish/BettaFish | 11 | OASIS+Forum+Config+Graph+Report+Nash+Stats+Qualis+Sensitivity+IMRAD+Debate |
| 推理类型 | 38 | 6分类 (逻辑5+辩证5+博弈论10+决策5+战略5+创新8) |
| 文章创建器 | 91 | MASWOS v4.6+桥接+自动评分 |
| SEEKER | 78 | 10智能体+论证树+10+学术来源 |
| 进化 | 9 | 6代ciclos + editais-br v7.1实战 + cache versionado + KeyError fix |
| 校正器 | 1 | ptbr_corrector.py (CJK检测+PT-BR语法) |

## MiroFish/BettaFish 集成 (v4.2 新增)
`skills/agent-forum/` — P14-P18完整管道: Agent Forum(多智能体辩论) → Debate Strategies(204 raciocínios (25 cat)+6策略+8配置) → PhD Auditor(NashSolver+StatisticalRigor+QualisA1Auditor+SensitivityAnalyzer+IMRADFormatter). 集成nexus-phd-strategist. BRAZIL_TIMEZONE(UTC-3)替换CHINA_TIMEZONE. 50指标真实数据仿真(World Bank/WHO/FAO/UNESCO).

## 量子Nexus v7.2
`quantum/` — 81文件: 21学术引用, 26 Python/Rust脚本, 7验证输出, QML医学HAM10000(89.52%), 50量子比特MPS, Grad-CAM, ZNE/PEC误差缓解, Qualis A1.

## Nexus多智能体 v6.2
`nexus/` — 40文件: 18架构引用, 20 Python脚本, 元粒度编排6层(L0-L6), 120+同步屏障, 500+验证约束, 204 raciocínios (25 cat)子类型, 120反馈点, Qualis A1审计.

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

## 快速命令

| 命令 | 协同MCP/插件 |
|------|-------------|
| `/evolve` | autoevolve+ecosystem-sync→发现并安装 |
| `/reversa` | reversa-*智能体+filesystem+diff+github |
| `/plan` | writing-plans技能+sequential-thinking MCP |
| `/auto` | openagent+所有MCPs |
| `/quantum` | quantum-nexus-phd+code-runner+pdf+sequential-thinking |
| `/artigo` | SEEKER+文章创建器+manus-evolve→Qualis A1 |

## MCP功能分类 (17活跃)

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

## 工程学科文档 (v4.7 新增 — Engenharia de Software com Agentes Inteligentes)

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
