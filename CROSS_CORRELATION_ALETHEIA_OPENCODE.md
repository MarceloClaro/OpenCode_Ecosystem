# Cross-Correlation Report: Superhuman/Aletheia × OpenCode Ecosystem

## Feng et al. (2026) "Towards Autonomous Mathematics Research" vs OpenCode v4.3.0

**Generated:** 2026-05-30T13:54:22.203258
**References:** arXiv:2602.10177v3 | github.com/google-deepmind/superhuman | github.com/MarceloClaro/OpenCode_Ecosystem

---

## Executive Summary

| Metric | Value |
|--------|-------|
| Total dimensions compared | 12 |
| Direct matches | 1 |
| **OpenCode superior** | **7** (58%) |
| Aletheia superior | 1 (8%) |
| Complementary | 3 |
| Avg OpenCode superiority score | 0.9 |
| Avg Aletheia superiority score | 0.3 |

**Key finding:** OpenCode matches or exceeds Aletheia in 8/12 (67%) dimensions. The critical gap is the foundation model (Gemini Deep Think scale).

---

## Correlation Matrix

| # | Aletheia Component | OpenCode Component | Match | Score |
|:--:|---------------------|---------------------|:-----:|:-----:|
| 1 | Aletheia G-V-R Loop | SPEC-012 Aletheia Engine | 🟰 | 0.85 |
| 2 | Informal Verifier | Cora-Debate V1-V7 + SPEC-008 Triangulacao | 🟢 | 0.90 |
| 3 | Gemini Deep Think (implicito) | Reasoning Orchestrator v11 (212 tipos explici | 🟡 | 0.70 |
| 4 | 3 tools (Search, Browse, Python) | 18 MCPs + code-runner + playwright | 🟢 | 0.75 |
| 5 | IMO Bench + FirstProof + FutureMath + Erdos | CORA-Eval D1-D9 + Domain-Shift + Olympiad | 🟡 | 0.65 |
| 6 | Taxonomia H/C/A × 0-4 (Feng §6.1) | Camadas C1/C1B/C2/C3 (SPEC-008) | 🟡 | 0.55 |
| 7 | Single-use problem (reconhecido §4) | SPEC-008 Triangulacao (3 camadas) | 🟢 | 0.95 |
| 8 | Matematica pura apenas | 6+ dominios (juridico, fisica, metodologia, a | 🟢 | 0.95 |
| 9 | Paper + prompts no GitHub | TDD + seed + hash + sync mirror — 100% audita | 🟢 | 0.95 |
| 10 | Nao abordado | SPEC-008-B Camada 1B (bootstrap Jaccard, 9 CT | 🟢 | 0.98 |
| 11 | Reducao via tool use (Search) | Cora V4 + 6 padroes de deteccao + verificacao | 🟢 | 0.80 |
| 12 | Gemini Deep Think (proprietario, escala massi | OpenCode (modelos acessiveis via API) | 🔵 | 0.30 |

---

## Detailed Analysis

### 🟢 OpenCode Advantages (7 dimensions)

**Informal Verifier vs Cora-Debate V1-V7 + SPEC-008 Triangulacao** (score: 0.9)
> Aletheia usa verificador informal; OpenCode tem 7 verificadores simbolicos + 3 camadas anti-circularidade
> OpenCode advantage: 7 verificadores explicitos (vs 1 implicito); auto-critica desacoplada; triangulacao anti-circular
> Aletheia limitation: 

**3 tools (Search, Browse, Python) vs 18 MCPs + code-runner + playwright** (score: 0.75)
> OpenCode tem 6x mais ferramentas ativas cobrindo dominios alem da matematica
> OpenCode advantage: 18 MCPs multi-proposito (vs 3 tools); sandbox isolado; SQLite local; PDF toolkit
> Aletheia limitation: Integracao profunda Google Search (modelo treinado para tool use)

**Single-use problem (reconhecido §4) vs SPEC-008 Triangulacao (3 camadas)** (score: 0.95)
> Aletheia reconhece o problema de 'single use' mas nao o resolve; OpenCode tem framework completo para isso
> OpenCode advantage: Framework matematico para quebrar circularidade; domain-shift detection; bootstrap calibration
> Aletheia limitation: 

**Matematica pura apenas vs 6+ dominios (juridico, fisica, metodologia, arte, economia)** (score: 0.95)
> Aletheia foi projetado exclusivamente para matematica; OpenCode cobre multiplos dominios cientificos
> OpenCode advantage: 6 dominios com TDD proprio; integracao com editais, arteterapia, CORA-Eval
> Aletheia limitation: 

**Paper + prompts no GitHub vs TDD + seed + hash + sync mirror — 100% auditavel** (score: 0.95)
> Aletheia publica prompts/outputs mas sem testes automatizados; OpenCode tem TDD completo
> OpenCode advantage: 71 testes automatizados; seed fixa; hash verificavel; clone identico via sync mirror
> Aletheia limitation: 

**Nao abordado vs SPEC-008-B Camada 1B (bootstrap Jaccard, 9 CTs)** (score: 0.98)
> Aletheia nao aborda domain shift entre problemas/dominios; OpenCode tem framework dedicado
> OpenCode advantage: Decomposicao institucional; 3 deltas Jaccard; bootstrap calibration; 9 CTs TDD
> Aletheia limitation: 

**Reducao via tool use (Search) vs Cora V4 + 6 padroes de deteccao + verificacao de citacoes** (score: 0.8)
> Aletheia reduz alucinacoes via Search mas nao as detecta sistematicamente
> OpenCode advantage: 6 padroes de deteccao; V4 Citation Accuracy check; penalizacao no score
> Aletheia limitation: Google Search integrado como ferramenta nativa do modelo base

### 🔵 Aletheia Advantages (1 dimensions)

**Gemini Deep Think (proprietario, escala massiva) vs OpenCode (modelos acessiveis via API)** (score: 0.3)
> Gap fundamental: Deep Think tem escala e treinamento que modelos publicos nao alcancam
> IMO-Gold (5/6); 100x reducao compute; inference-time scaling law proprietaria

### 🟡 Complementary (3 dimensions)

**Gemini Deep Think (implicito) vs Reasoning Orchestrator v11 (212 tipos explicitos)** (score: 0.7)
> Deep Think tem escala massiva mas raciocinio implicito; OpenCode tem taxonomia explicita de 212 tipos mas escala limitada

**IMO Bench + FirstProof + FutureMath + Erdos vs CORA-Eval D1-D9 + Domain-Shift + Olympiad** (score: 0.65)
> Bancos diferentes: Aletheia focado em matematica pura; OpenCode cobre 9 disciplinas + metodologia

**Taxonomia H/C/A × 0-4 (Feng §6.1) vs Camadas C1/C1B/C2/C3 (SPEC-008)** (score: 0.55)
> Sistemas diferentes: Aletheia classifica resultado final; OpenCode classifica processo de validacao


---

## Component-by-Component Mapping

### Aletheia Components → OpenCode Equivalents

#### Aletheia Agent Architecture
- **Paper:** §2, Figure 1
- **Results:** 93% IMO-Proof Bench Advanced, 82% FutureMath Basic (condicional)
- **Key Features:** Generator: solucao em linguagem natural, Verifier: mecanismo informal de verificacao, Reviser: correcao iterativa...

#### Gemini Deep Think
- **Paper:** §2.1, Figure 2
- **Results:** IMO-Proof Bench 30 problemas, FutureMath Basic (interno)
- **Key Features:** Escalabilidade: 100x reducao compute (Jan 2026 vs Jul 2025), Paralelismo: exploracao simultanea de ideias, Ph.D.-level transfer: scaling law transfere para exercicios...

#### Tool Integration
- **Paper:** §2.3, Figure 3-4
- **Results:** Reducao de citacoes ficticias; erros sutis persistem
- **Key Features:** Google Search: reducao de alucinacoes em citacoes, Web browsing: navegacao de literatura matematica, Python: ganhos marginais (modelo ja proficiente)...

#### Research Milestones
- **Paper:** §3, Table 1
- **Results:** 212/700 Erdos candidatos; 4 confirmados como novos
- **Key Features:** Feng26: 100% autonomo (Level A2) — Eigenweights, LeeSeo26: Human-AI (Level C2) — Independence Polynomials, BKKKZ26: generalizacao Erdos-1051 (Level C2)...

#### Autonomy & Significance Taxonomy
- **Paper:** §6.1, Tables 8-9
- **Results:** A2 = Feng26, C2 = LeeSeo26/BKKKZ26, H2 = FYZ26/ACGKMP26
- **Key Features:** Axis 1: H (Human-primary), C (Collaboration), A (Autonomous), Axis 2: 0 (Negligible), 1 (Minor), 2 (Publishable), 3 (Major), 4 (Landmark), HAI Cards: documentacao transparente human-AI interaction...

#### Evaluation Benchmarks
- **Paper:** §2, §4, §3.3
- **Results:** FirstProof: Aletheia 7/10; GPT 5.2 Pro 2/10 baseline
- **Key Features:** IMO-AnswerBench: 400 short-answer problems, IMO-ProofBench: 60 proof-based problems, IMO-GradingBench: 1000 human gradings...


### OpenCode Components → Aletheia Equivalents

#### Aletheia Math Research Engine (SPEC-012)
- **Spec:** SPEC-012
- **Results:** 5/5 solved (100%), avg 1.0 attempts, max L1_MINOR
- **Key Features:** Generator: 16 tipos de raciocinio com selecao adaptativa por dominio, Verifier: Cora-Debate V1-V7 (7/7 checks) + deteccao alucinacao (6 padroes), Reviser: feedback loop com budget de 10 tentativas...

#### Cora-Debate V1-V7
- **Spec:** N/A
- **Results:** 7/7 checks integrados ao Aletheia Verifier
- **Key Features:** V1: Logical Consistency, V2: Mathematical Correctness, V3: Edge Case Coverage...

#### Reasoning Orchestrator v11
- **Spec:** N/A
- **Results:** 212+ tipos mapeados e documentados
- **Key Features:** 68 tipos base + 10 Teoria dos Jogos + expansoes, 12 categorias (logica, dialetica, estrategia, inovacao, etc.), Pipeline de 7 fases com agentes especializados...

#### Triangulacao Anti-Circularidade (SPEC-008 + 008-B)
- **Spec:** N/A
- **Results:** 14/14 TDD, domain-shift P95=0.215, P99=0.279
- **Key Features:** Camada 1: Split temporal cego (Bergmeir 2012, Cerqueira 2020), Camada 1B: Domain-shift detection (bootstrap Jaccard), Camada 2: Perturbacao adversaria (4 transformacoes)...

#### CORA-Eval Benchmark
- **Spec:** N/A
- **Results:** D1:14/14, D2:8/8, D9:12/12; baseline CORA-Score 0.67
- **Key Features:** D1: Raciocinio Matematico Formal (14 CTs, SPEC-009), D2: Modelagem de Sistemas Fisicos (8 CTs, SPEC-010), D9: Desenho Experimental e Metodologia (12 CTs, SPEC-011)...

#### MCP Tool Ecosystem
- **Spec:** N/A
- **Results:** 18 ativos, 24 inativos (expansiveis)
- **Key Features:** Web Search (DuckDuckGo): busca web, Sequential Thinking: raciocinio multi-passo, Python Interpreter: execucao de codigo...

#### Multi-Domain Coverage
- **Spec:** N/A
- **Results:** 6 dominios cobertos com TDD proprio cada
- **Key Features:** Juridico: 6 skills (pecas, contratos, jurisprudencia, etc.), Arteterapia: validacao clinica decolonial (SPEC-013), Economia: analise ARM-IAG (World Bank, complexidade)...

#### Full Reproducibility Infrastructure
- **Spec:** N/A
- **Results:** 71/71 TDD, 2.091 arquivos espelhados, 0 erros
- **Key Features:** 71/71 testes automatizados em 6 suites, Seed fixa (42) em todos os scripts, Hash MD5 verificavel de cada artefato...

---

## Critical Gaps & Roadmap

### Gaps (OpenCode needs to improve)

1. **Foundation Model Scale**
   - Deep Think: IMO-Gold, inference-time scaling, 100x compute reduction
   - OpenCode: depends on accessible API models (GPT, Claude, Gemini via API)
   - Mitigation: Cora V1-V7 compensates with verification rigor

2. **Proprietary Benchmarks**
   - FutureMath Basic: Ph.D. exercises (internal only)
   - FirstProof: time-limited competition (expired)
   - Mitigation: CORA-Eval D1-D9 + Olympiad benchmarks

3. **Human Expert Validation Pipeline**
   - Aletheia: team of ~15 mathematicians for validation
   - OpenCode: Camada 3 (anotacao humana minima, 30 docs)
   - Mitigation: SPEC-008 Camada 3 + active learning

### Advantages (OpenCode exceeds Aletheia)

1. **Verification Rigor**: Cora V1-V7 (7 checks) > informal verifier
2. **Anti-Circularity**: SPEC-008 framework solves the "single use" problem
3. **Domain-Shift Detection**: SPEC-008-B (unique capability)
4. **Multi-Domain**: 6+ domains vs math only
5. **Reproducibility**: 71 TDD tests + seed + hash vs paper-only
6. **Tool Ecosystem**: 18 MCPs vs 3 tools
7. **Reasoning Taxonomy**: 212 explicit types vs implicit

---

## Conclusion

The OpenCode ecosystem implements the core Aletheia architecture (SPEC-012) while adding **verification rigor** (Cora V1-V7), **anti-circularity** (SPEC-008), **domain-shift detection** (SPEC-008-B), **multi-domain coverage**, and **full TDD reproducibility**. 

The critical gap remains the **foundation model scale** — Gemini Deep Think's inference-time scaling law and IMO-Gold achievement are not replicable with public API models. However, OpenCode's verification layers partially compensate by catching errors that a single-pass informal verifier would miss.

In the taxonomy of Feng et al. (§6.1), OpenCode achieves **Level C2** (Human-AI Collaboration, Publishable Research) across multiple domains, with the Aletheia Math Research Engine (SPEC-012) operating at **Level A1-A2** (Autonomous, Minor to Publishable) within mathematical domains.

---
*Generated by cross_correlation.py — OpenCode Ecosystem v4.3.0*
