# Ecossistema Unificado OpenCode v4.2 (MiroFish/BettaFish + PhD Auditor + 38 Raciocínios)

> **Idioma de saída obrigatório:** Português Brasileiro Formal.  
> Este documento é a versão em PT-BR do [AGENTS.md](AGENTS.md).

---

## Ambiente

- **Sistema Operacional:** Windows 11
- **Node.js:** v25
- **Bun:** 1.3
- **OpenCode CLI:** 1.14
- **Espaço de trabalho:** `C:\Users\marce\.config\opencode`
- **Modelo:** deepseek-v4-pro (OpenCode Zen, 200K tokens de contexto, 128K tokens de saída, gratuito)

---

## Correção de Saída (v3.5)

- Antes de cada entrega, executar obrigatoriamente `ptbr_corrector.py` para detectar e remover caracteres CJK
- **Tolerância zero:** nenhum caractere chinês, japonês ou coreano pode aparecer na saída ao usuário
- **Localização do corretor:** `criador-artigo/banca/ptbr_corrector.py`
- **Fluxo de correção:** Detecção CJK → Remoção → Correção ortográfica PT-BR → Verificação → Entrega

---

## Arquitetura de Sincronização Autônoma v4.2

```
┌─────────────────────────────────────────────────────────┐
│  Motor de Validação Cruzada v4.2 + MiroFish/BettaFish   │
│              + PhD Auditor                               │
│                                                          │
│  MCPs(40) ◄──► Skills(104) ◄──► Agentes(125)            │
│       │            │              │                      │
│       └────────────┼──────────────┘                      │
│                    │                                     │
│   P14-Forum ◄──► P15-DocIR ◄──► P16-ANP ◄──► P17-MW    │
│                    │                                     │
│   P18-PhD Auditor (Nash + Cohen + Bonferroni + Qualis)   │
│   MiroFish/BettaFish: OASIS + Forum + Config + Graph    │
│   BRAZIL_TIMEZONE (UTC-3) · 38 raciocínios · 10 Teoria  │
│   dos Jogos                                              │
│                                                          │
│  Plugins(15) ◄──► Comandos(14) ◄──► LSP(1) ◄──►        │
│  Corretor(1)                                             │
│                                                          │
│  Orquestrador de Sincronização:                          │
│    nexus/scripts/sync_orchestrator.py                    │
│  Matriz de Validação Cruzada:                            │
│    200+ conexões de afinidade | 110+ componentes         │
└─────────────────────────────────────────────────────────┘
```

---

## Estatísticas de Componentes (600+ integrações)

| Categoria | Quantidade | Estado |
|-----------|:----------:|--------|
| MCPs | 40 | 38 locais + 2 remotos |
| Skills | 104 | 12 categorias (+P14-P18 MiroFish/BettaFish) |
| Agentes | 125 | Core 56 + Criação 49 + SEEKER 12 + Reversa 7 + Corretor linguístico 1 |
| Plugins | 15 | 10 npm + 2 locais (.ts) + 3 bridge |
| Comandos | 14 | Comandos slash |
| LSP | 1 | TypeScript |
| Quantum | 81 | Referências/scripts/outputs/templates |
| Nexus | 40 | Multiagente/barreiras de sincronização/tipos de raciocínio |
| MiroFish/BettaFish | 11 | OASIS + Forum + Config + Graph + Report + Nash + Stats + Qualis + Sensitivity + IMRAD + Debate |
| Tipos de Raciocínio | 38 | 6 categorias (Lógico 5 + Dialético 5 + Teoria dos Jogos 10 + Decisão 5 + Estratégico 5 + Inovação 8) |
| Criador de Artigos | 91 | MASWOS v4.6 + bridges + auto-score |
| SEEKER | 78 | 10 agentes + argument tree + 10+ fontes acadêmicas |
| Evolução | 9 | 6 ciclos geracionais + editais-br v7.1 em produção + cache versionado + correção KeyError |
| Corretor | 1 | ptbr_corrector.py (detecção CJK + gramática PT-BR) |

---

## Integração MiroFish/BettaFish (novidade v4.2)

`skills/agent-forum/` — Pipeline completo P14-P18: Agent Forum (debate multiagente) → Debate Strategies (38 raciocínios + 6 estratégias + 8 configurações) → PhD Auditor (NashSolver + StatisticalRigor + QualisA1Auditor + SensitivityAnalyzer + IMRADFormatter). Integrado ao nexus-phd-strategist. BRAZIL_TIMEZONE (UTC-3) substitui CHINA_TIMEZONE. Simulação de 50 indicadores com dados reais (World Bank/WHO/FAO/UNESCO).

---

## Quantum Nexus v7.2

`quantum/` — 81 arquivos: 21 referências acadêmicas, 26 scripts Python/Rust, 7 outputs de validação, QML médico HAM10000 (89,52% de acurácia), 50 qubits MPS, Grad-CAM, mitigação de erros ZNE/PEC, Qualis A1.

---

## Nexus Multiagente v6.2

`nexus/` — 40 arquivos: 18 referências de arquitetura, 20 scripts Python, orquestração meta-granular em 6 camadas (L0-L6), 120+ barreiras de sincronização, 500+ restrições de validação, 38 subtipos de raciocínio, 120 pontos de feedback, auditoria Qualis A1.

---

## Manus Evolve v1.0 (Motor Autônomo PlanAct)

`plugins/manus-evolve.ts` — Motor de evolução autônoma. Pipeline: PLAN → ACT → REFLECT → EXTRACT → EVOLVE. A cada ciclo, gera novas skills em `evolution/`. Aprende a partir de padrões de sucesso e aprova automaticamente ferramentas confiáveis.

---

## Criador de Artigos v2 (MASWOS)

`criador-artigo/` — 91 arquivos: 49 agentes especializados (A00-A44 + dispatcher), 14 referências (Qualis A1, ABNT, estatísticas), 24 templates. Orquestração multiagente, simulação de peer-review, exportação LaTeX/PDF.

---

## SEEKER v1 (Agentes de Pesquisa Básica)

`basis-research/` — 78 arquivos: 10 agentes Python, motor de argument tree, 10+ fontes acadêmicas (arXiv, OpenAlex, Semantic Scholar, PubMed, CORE). Pipeline de pesquisa profunda, cada afirmação rastreia evidência verificável.

---

## Pipeline de Produção Acadêmica v3.4

```
SEEKER (pesquisa) → Criador de Artigos (49 agentes, 8 estágios)
  → Escrita anti-IA (TSAC, 87 palavras banidas)
  → Validação cruzada (Pearson, 3 níveis)
  → Ciclo de correção iterativa:
      Banca de revisores (5 revisores) → Orientadores (4 doutores) →
      Corretores (6 motores)
      → Reavaliação automática de score → Repetir até score ≥ 95
  → AUTO_SCORE_QUALIS.py (10 critérios + pesos de revisores)
  → Corretor linguístico (detecção CJK + gramática PT-BR) ← novidade v3.4
  → MANUS EVOLVE (aprende com ciclos, gera novas skills)
  → Qualis A1 95/100
```

---

## Ciclos de Evolução

| Ciclo | Skill Gerada | Score | Insight Principal |
|:-----:|-------------|:-----:|-------------------|
| 1 | Validação cruzada quantitativa + análise World Bank | 85 | Educação r=-0,03; P&D privado r=+0,73 |
| 2 | Pipeline de artigo acadêmico | 90 | Serviços de alta tecnologia r=+0,95 (preditor mais forte) |
| 3 | Citações TSAC + pipeline Sci-Hub + validação cruzada | 92 | 46 anotações TSAC auditáveis |
| Auto | evo-1 a evo-5 | 85-95 | Manus Evolve gerou 5 skills autonomamente |
| 4 | Ciclo de correção iterativa v2.0 | 95 | Banca + orientadores + corretores: 86,5 → 92,7 |
| 5 | Corretor linguístico com detecção CJK | 98 | Contexto em chinês + saída PT-BR exige corretor obrigatório; tolerância zero para vazamento CJK |
| 6 | editais-br v2.0 validação em produção + 4 categorias | 92 | Busca paralela real (pesquisa/mestrado/doutorado/startup) com DuckDuckGo via curl.exe; httpx bloqueado por CAPTCHA; score por perfil 58-68/100 |
| 7 | editais-br v7.1 cache versionado + 50+ curados | 94 | KeyError score corrigido + CACHE_VERSION; 28 → 52 editais curados (16 FAPs estaduais, 4 exterior, 4 setoriais); fallback curadoria agora cobre todas as 27 UFs |

---

## Comandos Rápidos

| Comando | MCPs/Plugins Associados |
|---------|------------------------|
| `/evolve` | autoevolve + ecosystem-sync → descobrir e instalar |
| `/reversa` | agentes reversa-* + filesystem + diff + github |
| `/plan` | skill writing-plans + MCP sequential-thinking |
| `/auto` | openagent + todos os MCPs |
| `/quantum` | quantum-nexus-phd + code-runner + pdf + sequential-thinking |
| `/artigo` | SEEKER + criador de artigos + manus-evolve → Qualis A1 |

---

## Classificação Funcional dos MCPs (17 ativos)

| Função | MCPs |
|--------|------|
| Busca | websearch (DuckDuckGo), gh_grep (GitHub), context7 (documentação), scihub (papers) |
| Navegador | playwright, chrome-devtools |
| Código | eslint, diff, code-runner |
| Dados | sqlite, fetch, pdf, time |
| Raciocínio | sequential-thinking, memory |
| Infraestrutura | filesystem, github |

---

## Regras de Eficiência de Tokens

1. Contexto armazenado em chinês (densidade informacional +40%)
2. Toda saída deve ser em português brasileiro formal
3. Nomes de variáveis, paths e código mantêm o idioma original
4. Evitar repetição de informações — referenciar em vez de copiar
5. Utilizar tabelas em vez de parágrafos para dados estruturados
6. Compressão: diagnóstico → ação → resultado (padrão de três etapas)
7. **Correção de saída:** executar ptbr_corrector.py antes de cada entrega para detectar e remover caracteres CJK
8. **Tolerância zero:** nenhum caractere chinês pode aparecer na saída ao usuário

---

## Aprendizados da Sessão (Ciclo de Skills)

| Skill | Frequência de Uso | Efeito |
|-------|:-----------------:|--------|
| iterative_correction_loop | 5 vezes | 86,5 → 92,7 (+7,1%) |
| auto_score_qualis | 8 vezes | 74 → 95 (+28%) |
| Pesquisa SEEKER | 4 vezes | 12 → 55 DOIs |
| Substituição de vocabulário anti-IA | 11 vezes | 220 → 0 travessões |
| Validação cruzada Pearson | 3 vezes | 5 categorias de anomalias descobertas |
| Simulação de revisores (5 pessoas) | 6 vezes | 10 → 0 feedbacks pendentes |
| Corretor linguístico CJK | Cada entrega | 0 vazamentos de chinês para saída do usuário |
| editais-br curl/subprocess | 1 vez | httpx bloqueado → curl.exe + Firefox UA funciona |
| editais-br 4 categorias | 4 vezes | pesquisa/mestrado/doutorado/startup → 10 resultados reais cada |
| extracao_profunda | 1 vez | Sintaxe corrigida, extração funcional (contrapartida, prazos, docs) |
| editais-br v7.1 cache versionado | 1 vez | Bug KeyError score corrigido + CACHE_VERSION + setdefault score + invalidação de cache |

---

## Matriz de Validação Cruzada (Afinidade)

Maiores afinidades entre componentes:

| Componente A | Componente B | Afinidade |
|-------------|-------------|:---------:|
| scihub | Criador de Artigos | 0,95 |
| sequential-thinking | code-reviewer | 0,90 |
| academic_search | SEEKER-grounder | 0,85 |
| code-runner | Quantum Nexus | 0,90 |
| websearch | SEEKER-searcher | 0,85 |
| editais-br | websearch | 0,90 |
| editais-br | docling-pdf-extraction | 0,85 |

---

<div align="center">

**OpenCode Ecosystem v4.6** · Documentação de Agentes em Português Brasileiro

</div>
