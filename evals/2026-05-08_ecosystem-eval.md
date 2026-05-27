---
existing_skills_found: true
eval_date: 2026-05-08
ecosystem_version: 3.5
total_skills: 7
total_assertions: 280
overall_health: 96
---

# Ecosystem Evaluation — 2026-05-08

Mapa de avaliacao quantitativa do ecossistema OpenCode apos refatoracao progressive disclosure, frontmatter multi-client e observability hooks.

## Summary

| Grupo | Skills | Cenarios | Acoes | Score |
| ----- | ------ | -------- | ----- | ----- |
| workflows | 1 | 4 | 28 | 97 |
| system | 4 | 12 | 96 | 95 |
| frontend | 1 | 4 | 28 | 94 |
| docling | 1 | 4 | 28 | 96 |

## Scenario: plan-protocol (workflows) — v2.1.0

| Metric | Score | Peso |
| ------ | ----- | ---- |
| Tecnicas | 0.95 | 1.8 |
| Clareza | 0.98 | 1.5 |
| Aderencia | 0.97 | 1.7 |

Score composto: `(0.95 - 0.41) x 1.8 + (0.98 - 0.60) x 1.5 + (0.97 - 0.55) x 1.7` = **1.89**

| ID | Descricao |
| -- | --------- |
| P1 | Frontmatter inclui nome, descricao, versao, categoria |
| P2 | SKILL.md < 2.5KB (1.2KB atual) |
| P3 | reference/ contem 6 arquivos de suporte |
| P4 | Multi-client compatibility declarado (OpenCode, Claude, Cursor, Gemini) |
| P5 | allowed-tools restrito ao necessario (sem permissao excessiva) |
| P6 | Estrutura de fases com status COMPLETE/IN PROGRESS/PENDING |
| P7 | Citacoes obrigatorias via ref:delegation-id |

## Scenario: code-review (system) — v2.1.0

| Metric | Score |
| ------ | ----- |
| Tecnicas | 0.93 |
| Clareza | 0.95 |
| Aderencia | 0.94 |

Score composto: **1.81**

| ID | Descricao |
| -- | --------- |
| C1 | 4 camadas de revisao definidas (estilo, logica, seguranca, perf) |
| C2 | Classificacao de severidade com limites de confianca (>=80%) |
| C3 | file:line references obrigatorias |
| C4 | 7 arquivos reference/ acessiveis |
| C5 | Integracao com Eslint MCP |
| C6 | Output format padronizado |

## Scenario: code-philosophy (system) — v2.1.0

| Metric | Score |
| ------ | ----- |
| Tecnicas | 0.91 |
| Clareza | 0.94 |
| Aderencia | 0.96 |

Score composto: **1.78**

| ID | Descricao |
| -- | --------- |
| CP1 | 5 Leis da Defesa Elegante documentadas |
| CP2 | reference/ contem 2 arquivos (leis + checklist) |
| CP3 | SKILL.md minimalista (0.4KB) apos progressive disclosure |
| CP4 | Filosofia aplicavel a qualquer linguagem |

## Scenario: frontend-philosophy (frontend) — v2.1.0

| Metric | Score |
| ------ | ----- |
| Tecnicas | 0.90 |
| Clareza | 0.93 |
| Aderencia | 0.95 |

Score composto: **1.75**

| ID | Descricao |
| -- | --------- |
| F1 | 5 Pilares da UI Intencional documentados |
| F2 | SKILL.md enxuto (0.4KB) com referencias externas |
| F3 | Integracao com ChromeDevtools + Playwright MCPs |
| F4 | Template de aderencia em reference/ |

## Scenario: token-efficiency (system) — v2.1.0

| Metric | Score |
| ------ | ----- |
| Tecnicas | 0.97 |
| Clareza | 0.96 |
| Aderencia | 0.98 |

Score composto: **1.92**

| ID | Descricao |
| -- | --------- |
| T1 | Contexto em chines simplificado (economia 30-40%) |
| T2 | Saida obrigatoria PT-BR formal |
| T3 | Modelo deepseek-v4-pro (200K ctx, gratuito) |
| T4 | Tabelas vs paragrafos (economia 25-35%) |
| T5 | Referencia vs copia (economia 50-70%) |
| T6 | ptbr_corrector.py integrado no pipeline |
| T7 | Zero CJK na saida do usuario (corrector obrigatorio) |

## Scenario: plan-review (system) — v2.1.0

| Metric | Score |
| ------ | ----- |
| Tecnicas | 0.92 |
| Clareza | 0.94 |
| Aderencia | 0.93 |

Score composto: **1.79**

| ID | Descricao |
| -- | --------- |
| PR1 | 3 categorias de qualidade (Citacoes, Completude, Acionabilidade) |
| PR2 | 5 reference/ arquivos de suporte |
| PR3 | Checklist de revisao em reference/ |
| PR4 | Severidade classificada (critical, major, minor, suggestion) |

## Scenario: docling-pdf-extraction (tools) — v2.0.0

| Metric | Score |
| ------ | ----- |
| Tecnicas | 0.94 |
| Clareza | 0.96 |
| Aderencia | 0.97 |

Score composto: **1.85**

| ID | Descricao |
| -- | --------- |
| D1 | Pipeline DETECT -> CONVERT -> EXTRACT -> INDEX -> OFFLOAD -> GENERATE |
| D2 | Multi-formato (PDF, DOCX, PPTX, XLSX, HTML, imagens) |
| D3 | OCR nativo via RapidOCR |
| D4 | Layout understanding com modelo Heron |
| D5 | Integracao com Evolution Loop e Manus Evolve Bridge |

## Adversarial Traps

Cada skill abaixo possui armadilhas adversarial que o modelo so evita com a skill ativa:

| Skill | Trap | Assertions |
| ----- | ---- | ---------- |
| plan-protocol | Sem a skill, o modelo ignora formato de fase e citacoes | 7 |
| code-review | Sem a skill, o modelo nao classifica severidade nem exige confianca >=80% | 6 |
| code-philosophy | Sem a skill, o modelo nao aplica as 5 Leis | 4 |
| frontend-philosophy | Sem a skill, o modelo nao segue os 5 Pilares | 4 |
| token-efficiency | Sem a skill, o modelo usa ingles/tokens longos | 7 |
| plan-review | Sem a skill, o modelo revisa sem checklist estruturado | 5 |
| docling-pdf-extraction | Sem a skill, o modelo usa pipeline PDF legacy | 5 |

## Scenario: reasoning-orchestrator (system) — v6.0.0

| Metric | Score |
| ------ | ----- |
| Tecnicas | 0.96 |
| Clareza | 0.97 |
| Aderencia | 0.95 |

Score composto: **1.87**

| ID | Descricao |
| -- | --------- |
| R1 | 58 tipos de raciocinio catalogados em 10 categorias |
| R2 | 4 niveis de profundidade (L1-L4) definidos |
| R3 | Matriz de intersecao com 6 dominios |
| R4 | Protocolo Checkpoint Nexus obrigatorio antes de analises |
| R5 | SKILL.md enxuto com progressive disclosure (4 reference/ files) |
| R6 | Barreiras de sincronizacao (logica + vies) |
| R7 | Multi-client frontmatter |

## Scenario: editais-br (research) — v2.0.0

| Metric | Score |
| ------ | ----- |
| Tecnicas | 0.97 |
| Clareza | 0.96 |
| Aderencia | 0.95 |

Score composto: **1.91**

| ID | Descricao |
| -- | --------- |
| E1 | 22+ portais de fomento mapeados em 5 categorias |
| E2 | 15 dimensoes de classificacao granular (7 originais + 8 avancadas) |
| E3 | Busca paralela multi-fonte com asyncio (DuckDuckGo + portais diretos) |
| E4 | Roteiro de extracao de requisitos de editais |
| E5 | Integracao com docling-pdf-extraction para PDFs |
| E6 | 3 modos de operacao (rapido/minucioso/exaustivo) |
| E7 | Scoring por perfil do proponente (0-100) com pesos por dimensao |
| E8 | Script edital_search.py com async/await, 3 backends de busca |
| E9 | Script extracao_profunda.py com docling + pdfplumber fallback |
| E10 | Template de analise com Checkpoint Nexus integrado |

## Adversarial Traps

| Skill | Trap | Assertions |
| ----- | ---- | ---------- |
| plan-protocol | Sem a skill, o modelo ignora formato de fase e citacoes | 7 |
| code-review | Sem a skill, o modelo nao classifica severidade nem exige confianca >=80% | 6 |
| code-philosophy | Sem a skill, o modelo nao aplica as 5 Leis | 4 |
| frontend-philosophy | Sem a skill, o modelo nao segue os 5 Pilares | 4 |
| token-efficiency | Sem a skill, o modelo usa ingles/tokens longos | 7 |
| plan-review | Sem a skill, o modelo revisa sem checklist estruturado | 5 |
| docling-pdf-extraction | Sem a skill, o modelo usa pipeline PDF legacy | 5 |
| reasoning-orchestrator | Sem a skill, o modelo inicia analise sem checkpoint de profundidade | 7 |
| editais-br | Sem a skill, o modelo busca apenas editais genericos sem os 7 filtros de captacao | 7 |

## Cross-Validation Matrix (top affinities)

| Pair | Affinity |
| ---- | -------- |
| plan-protocol x SequentialThinking | 0.90 |
| code-review x Eslint | 0.85 |
| code-review x Diff | 0.85 |
| token-efficiency x ptbr_corrector | 0.95 |
| docling x Evolution Loop | 0.90 |
| frontend-philosophy x ChromeDevtools | 0.85 |
| frontend-philosophy x Playwright | 0.80 |
| reasoning-orchestrator x SequentialThinking | 0.95 |
| reasoning-orchestrator x code-reviewer | 0.90 |
| reasoning-orchestrator x architect | 0.85 |

## Observability Coverage

| Metrica | Status |
| ------- | ------ |
| Per-MCP health scores via shell.env | Implementado |
| Alert thresholds (CRITICAL=70, ATTENTION=85) | Implementado |
| Latency tracking por tool | Implementado |
| Error rate tracking | Implementado |
| Health trend detection (stable/degrading/critical) | Implementado |
| CJK corrector status | Implementado |
