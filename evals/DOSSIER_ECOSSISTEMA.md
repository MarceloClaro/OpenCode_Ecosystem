---
dossier_date: 2026-05-09
ecosystem_version: 3.5
model: deepseek-v4-pro (OpenCode Zen)
health: 100/100
ciclo_ativo: 7.3
---

# Dossiê do Ecossistema OpenCode

## 1. Visão Geral

| Métrica | Valor |
|---------|-------|
| Health Score | 100/100 |
| Ciclo ativo | 7.3 |
| Modelo | deepseek-v4-pro (200K ctx, 128K out) |
| SO | Windows 11 |
| Runtime | Node.js v25, Bun 1.3, Python 3.12 |
| MCPs ativos | 17 (15 local + 2 remoto) |
| Arquivos Python | 404 scripts (74.203 linhas) |
| Arquivos TypeScript | 1.587 scripts (754.475 linhas) |
| Arquivos Markdown | 676 documentos |

---

## 2. Componentes por Diretório

### 2.1 Skills do Sistema (9 skills, `<2.5KB cada`)

| Skill | Bytes | Domínio |
|-------|-------|---------|
| `editais-br` | 2.480 | Busca inteligente de fomento (Brasil) |
| `docling-pdf-extraction` | 2.486 | Extração avançada de PDFs |
| `reasoning-orchestrator` | 1.979 | 58 tipos de raciocínio L1-L4 |
| `plan-protocol` | 1.497 | Planos de implementação com citação |
| `code-review` | 1.260 | Metodologia de revisão de código |
| `plan-review` | 1.252 | Critérios de qualidade de planos |
| `token-efficiency` | 1.052 | Otimização de tokens (chinês+PT-BR) |
| `frontend-philosophy` | 642 | 5 Pilares da UI Intencional |
| `code-philosophy` | 622 | 5 Leis da Defesa Elegante |

### 2.2 Scripts Python Estratégicos (4 scripts)

| Script | Linhas | Função |
|--------|--------|--------|
| `edital_search.py` | ~600 | Busca multi-portal + curadoria 52 editais + scoring 0-100 + servidor HTTP + feedback SQLite + BNDES API |
| `extracao_profunda.py` | ~180 | Extração de requisitos de PDF (pdfplumber primário, docling OCR fallback) |
| `editais_hook.py` | ~110 | Ponte REST SEEKER ↔ editais-br |
| `ptbr_corrector.py` | 359 | Correção linguística (CJK detection + PT-BR grammar) |

### 2.3 Plugins TypeScript (2 ativos)

| Plugin | Tamanho | Função |
|--------|---------|--------|
| `ecosystem-sync.ts` | 19KB | Sincronizador multi-MCP, 12 env vars observability |
| `manus-evolve.ts` | 15KB | Motor evolutivo autônomo (PLAN→ACT→REFLECT→EXTRACT→EVOLVE) |

### 2.4 SEEKER — Research Pipeline (12 agentes, 31 scripts Python)

| Agente | Linhas | Função |
|--------|--------|--------|
| `social.py` | 1.081 | Coleta social + inteligência de fontes |
| `grounder.py` | 739 | Construção de árvores de argumentos |
| `gaper.py` | 526 | Mapeamento de gaps tree-native |
| `scribe.py` | 466 | Síntese final |
| `breaks.py` | 365 | Checkpoints de qualidade |
| `historian.py` | 287 | Auditoria + fatores externos |
| `theorist.py` | 206 | Geração teórica |
| `vision.py` | 174 | Projeção de cenários |
| `synthesizer.py` | 175 | Síntese multi-fonte |
| `thinker.py` | 144 | Reflexão crítica |
| `rude.py` | 130 | Avaliação adversarial |

Core: `argument_tree.py`, `concept_mapper.py`, `consensus_mcp.py`, `context.py`, `database.py`, `llm.py`, `references.py`, `rate_limiter.py`, `utils.py`

### 2.5 Nexus — Orquestração Multi-Agente (40 scripts Python)

Componentes-chave:
- `evolution_loop.py` (673 linhas) — Loop evolutivo de 6 estágios
- `phd_learning_cores.py` (598 linhas) — Núcleos de aprendizado
- `mcp_real_adapters.py` (577 linhas) — Adaptadores MCP reais
- `domain_discovery_engine.py` (552 linhas) — Descoberta de domínios
- `sync_orchestrator.py` (550 linhas) — Orquestrador de sincronização
- `mcp_self_organization.py` (549 linhas) — Auto-organização MCP
- `knowledge_graphs.py` (502 linhas) — Grafos de conhecimento
- `agent_metamorphosis.py` (477 linhas) — Metamorfose de agentes
- `micro_sync_barriers.py` (454 linhas) — Barreiras de sincronização
- `pdf_ecosystem_integration.py` (455 linhas) — Integração PDF
- `validation_suite.py` (305 linhas) — Suite de validação
- `mcp_router.py` (299 linhas) — Roteador MCP
- `evolution_optimizer.py` (295 linhas) — Otimizador evolutivo

### 2.6 Criador-Artigo — Pipeline MASWOS (3 scripts Python, 98 arquivos totais)

| Script | Linhas | Função |
|--------|--------|--------|
| `iterative_correction_loop.py` | 649 | Loop de correção iterativa (5 revisores + 4 doutores) |
| `ptbr_corrector.py` | 359 | Correção linguística CJK+PT-BR |
| `auto_score_qualis.py` | 209 | Auto-scoring Qualis A1 (10 critérios) |

Template base: TSAC (87 palavras anti-AI), Qualis A1 95/100

### 2.7 Quantum — Pesquisa Quântica (40 scripts Python)

Áreas: QML (HAM10000 89.52%), 50-qubit MPS, Grad-CAM, ZNE/PEC error mitigation, Qualis A1.

### 2.8 Evolution — Ciclos de Evolução

| Ciclo | Foco | Score |
|-------|------|-------|
| 1 | Correlação educação r=-0.03, P&D r=+0.73 | 85 |
| 2 | Serviços de alta tecnologia r=+0.95 | 90 |
| 3 | TSAC, 46 citações auditáveis | 92 |
| 4 | Loop de correção iterativa v2.0 | 95 |
| 5 | Correção CJK + PT-BR | 98 |
| 6 | editais-br v2.0 (4 categorias, DuckDuckGo real) | 92 |
| 7+ | editais-br v7.3 (52 curados, cache versionado, scoring 100/100) | 100 |

### 2.9 CC-Skills Cross-Client (14 skills de referência)

| Skill | Bytes | Uso |
|-------|-------|-----|
| chrome-extension | 19.365 | Extensões Chrome MV3 |
| humaniseur-fr | 26.250 | Humanização de texto FR |
| influence-and-negotiation | 28.903 | Toolkit de negociação |
| skill-progressive-disclosure | 17.455 | Design de skills progressivas |
| deep-research | 13.151 | Pesquisa profunda multi-fonte |
| substack-ghostwriting | 15.980 | Ghostwriting Substack |
| technical-article-writer | 11.182 | Artigos técnicos |
| training-report | 11.199 | Relatórios de treinamento |
| crxjs | 10.887 | CRXJS + Vite HMR |
| snyk-agent-scan-compliance | 8.369 | Compliance de skills |
| conventional-git | 7.621 | Git convencional |
| press-release-writer | 7.344 | Press releases |
| promql-cli | 5.763 | CLI PromQL |
| linkedin-ghostwriting | 5.408 | Ghostwriting LinkedIn |

---

## 3. MCPs Ativos (17)

| Categoria | MCPs |
|-----------|------|
| Busca | websearch (DuckDuckGo), gh_grep (GitHub), context7 (docs), scihub (artigos) |
| Navegador | playwright, chrome-devtools |
| Código | eslint, diff, code-runner |
| Dados | sqlite, fetch, pdf, time |
| Raciocínio | sequential-thinking, memory |
| Infra | filesystem, github |

---

## 4. Integrações (Pipeline Principal)

```
[USUÁRIO]
   │
   ├─► /evolve   → autoevolve + ecosystem-sync → Manus Evolve → evolution/
   ├─► /reversa  → reversa-* agentes + git diff
   ├─► /plan     → plan-protocol + sequential-thinking
   ├─► /artigo   → SEEKER → Criador-Artigo (49 agentes) → TSAC → Qualis A1
   ├─► /quantum  → quantum-nexus-phd + code-runner + pdf
   └─► editais   → editais-br v7.3:
                     DuckDuckGo + Finep portal
                     + BNDES Open Data API
                     + Curadoria 52 editais (27 UFs)
                     → Classificador 25 dimensões
                     → Scoring 0-100 por perfil
                     → Servidor HTTP (porta 8080)
                     → SQLite feedback + pesos aprendidos
                     → Extração profunda PDF (pdfplumber)
                     ↑ Hook SEEKER REST
```

## 5. editais-br v7.3 — Detalhamento

### Fontes de Dados
| Fonte | Tipo | Status |
|-------|------|--------|
| Curadoria 52 editais | Pré-computada | ✅ 100% disponível offline |
| Finep scraping (httpx) | Portal direto | ✅ HTTP 200 |
| DuckDuckGo (curl.exe) | Web search | ⚠️ ~50% bloqueado (CAPTCHA) |
| BNDES Open Data (CKAN) | API REST | ✅ Dados abertos governamentais |
| Fallback curadoria | Segurança | ✅ Cobre 27 UFs via FAPs |

### Scoring (0-100)
| Componente | Peso | Descrição |
|-----------|------|-----------|
| Query Relevance | 30 | Termos da busca no título |
| Tipo Alignment | 30 | Tipo casa com área classificada |
| Perfil Alignment | 20 | Perfil do usuário casa com perfil do edital |
| Mechanism Bonus | 10 | Adequação do mecanismo de fomento |
| Completeness | 12 | Dimensões classificadas |
| Penalties | -35 | Encerrado, contrapartida, alta competição |

### Resultados por Categoria
| Categoria | Top Score | Hits 100/100 |
|-----------|-----------|--------------|
| pesquisa | 100 | 3/3 |
| doutorado | 100 | 2/3 |
| mestrado | 100 | 1/3 |
| startup | 100 | 1/3 |

---

## 6. Estados do Ecossistema

| Componente | Status | Observação |
|-----------|--------|------------|
| py_compile | ✅ OK | 4/4 scripts Python compilam |
| SKILL.md < 2.5KB | ✅ OK | 9/9 skills dentro do limite |
| Frontmatter YAML | ✅ OK | 9/9 com name, description |
| CJK Leaks | ✅ OK | 0 arquivos com CJK |
| Scoring 100/100 | ✅ OK | Todas as categorias atingem 100 |
| SEEKER hook | ✅ OK | REST + fallback direto |
| Feedback SQLite | ✅ OK | --feedback + --treinar |
| BNDES API | ✅ OK | CKAN integrado |
| PDF extraction | ✅ OK | pdfplumber primário + docling OCR |
| Servidor HTTP | ✅ OK | Porta 8080, /buscar endpoint |

## 7. Pipeline de Qualidade

```
Percepção (SEER/editais)
  → Classificação (25 sub-dimensões, word-boundary regex)
    → Scoring (0-100 query-aware)
      → Evolução (Manus Evolve + autoevolve)
        → Sincronização (ecosystem-sync.ts + 14 skills cross-client)
          → Correção linguística (ptbr_corrector.py: CJK→PT-BR)
            → Avaliação (evals/ + 280+ asserções)
              → [Opcional] Qualis A1 via Criador-Artigo
```

## 8. Métricas Finais

- **Componentes totais**: 600+ integrações mapeadas
- **Skills**: 9 nativas + 14 cc-skills cross-client = 23 skills
- **Agentes SEEKER**: 12 agentes + 6 core modules
- **Nexus**: 40 scripts de orquestração
- **Quantum**: 40 scripts de pesquisa
- **Criador-Artigo**: 3 scripts + 98 arquivos de template
- **Plugins**: 2 orquestradores (sync + evolve)
- **Comandos**: 14 slash commands
- **Evolução**: 7+ ciclos documentados
- **Cobertura de UFs**: 27/27 via FAPs estaduais
- **Editais curados**: 52 (16 FAPs + 4 exterior + 4 setoriais)
- **Health Score**: 100/100
