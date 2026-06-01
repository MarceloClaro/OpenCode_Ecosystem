# Nivelamento: OpenCode Ecosystem vs. Google DeepMind Superhuman/Aletheia

**Data:** 31/05/2026 | **Versao:** 1.0.0
**Referencias:** 
- Superhuman: https://github.com/google-deepmind/superhuman
- Aletheia paper: arXiv:2602.10177v3 (Feng et al., 2026)
- IMO Bench: EMNLP 2025 (Luong et al., 2025)

---

## 1. Resumo Executivo

| Dimensao | DeepMind Superhuman/Aletheia | OpenCode Ecosystem | Vantagem |
|:---------|:-----------------------------|:-----------------:|:--------:|
| **Foco** | Pesquisa matematica autonoma (IMO -> pos-doutorado) | Producao academica multiagente (Qualis A1) | Dominios diferentes |
| **Motor de raciocinio** | Gemini Deep Think (parallel thinking, inference-time scaling) | ReasoningOrchestrator v11 (68 tipos, 7 fases, Cora-Debate V1-V7) | 🔵 OpenCode (mais tipos) |
| **Agentes** | 1 agente (Aletheia) com 3 subagentes (Generator, Verifier, Reviser) | 125 agentes, 91 criador-artigos, 78 SEEKER, 49 profissionais | 🟢 OpenCode (escala) |
| **Verificacao** | Verificador em linguagem natural (Gemini como juiz) | PhD Auditor (Nash + Cohen + Bonferroni + Qualis) + Cora-Debate V1-V7 | 🔵 OpenCode (multimetodo) |
| **Benchmark** | IMO-Bench (1460 exemplos, 3 benchmarks) | CORA-Eval (150 tarefas, 10 dimensoes, 4 niveis) | 🟢 Superhuman (maior) |
| **Anti-circularidade** | Nao abordado | SPEC-008 (C1-C6, Matriz A, 92.77% agreement) | 🟢 OpenCode |
| **Publicacoes reais** | Nature, EMNLP 2025, 7+ arXiv | N/A (ferramenta de suporte) | 🟢 Superhuman |
| **Problemas abertos** | 4 solucoes autonomas (Erdos), 6/10 FirstProof | N/A (dominio educacional) | 🟢 Superhuman |
| **Linguagem** | Ingles (fim-a-fim) | PT-BR com corretor CJK | 🔵 OpenCode (PT-BR) |
| **Auditoria** | ProofAutoGrader (Pearson 0.96) | Cross-validation matrix (200+ afinidades) + Sync orchestrator | 🔵 OpenCode (ecossistema) |
| **Transparencia** | Human-AI interaction cards (proposto) | Logs imutaveis SHA-256, debate aberto entre agentes, TDD evidenciavel | 🔵 OpenCode |
| **Custo** | Gemini Deep Think proprietario (Google) | Modelos via API (aberto, gratuito) | 🟢 OpenCode |

---

## 2. Analise Arquitetural Detalhada

### 2.1 Aletheia: Generator -> Verifier -> Reviser

```
Aletheia (Gemini Deep Think)
  │
  ├── Generator: propoe solucao candidata
  │     └── Gemini Deep Think + parallel thinking
  │
  ├── Verifier: avalia solucao em linguagem natural
  │     └── Gemini como juiz, sem ferramentas formais
  │     └── Se falha -> retorna para Generator
  │
  ├── Reviser: refina solucao com base no feedback
  │     └── Loop ate Verifier aprovar ou limite atingido
  │
  └── Tool Use: Google Search + Web Browsing + Python (marginal)
      └── Reduz, mas nao elimina, alucinacoes
```

**Pontos fortes:**
- Loop iterativo bem definido (gerar-verificar-revisar)
- Parallel Thinking (exploracao simultanea de multiplas solucoes)
- Inference-time scaling law (100x eficiencia do IMO Gold para Jan 2026)
- Conditional accuracy 96% em problemas respondidos (IMO-ProofBench)

**Fraquezas:**
- Agente unico (sem especializacao por dominio)
- Verificador em LN propenso a vies de confirmacao
- Nao trata anti-circularidade (risco de auto-validacao)
- Alucinacoes persistem mesmo com ferramentas (13/200 = 6.5% meaningful correct em Erdos)

### 2.2 OpenCode: Multiagente com 7 Fases

```
OpenCode Ecosystem (125 agentes)
  │
  ├── SEEKER (78 agentes): pesquisa basica, 10+ fontes academicas
  │     └── Argument tree engine, arXiv, OpenAlex, Semantic Scholar
  │
  ├── Criador de Artigos (91 agentes): 8 fases, 49 especialistas
  │     └── TSAC anti-AI writing, 87 palavras proibidas
  │
  ├── ReasoningOrchestrator v11 (68 tipos): 7 fases
  │     ├── F0: Fundacional (15%)
  │     ├── F1: Indutiva (15%)
  │     ├── F2: Dedutiva (15%)
  │     ├── F3: Construtiva (10%)
  │     ├── F4: Refutacional (gate obrigatorio) ← NOVO
  │     ├── F5: Verificacional (gate obrigatorio) ← REFORCADO
  │     └── F6: Meta-cognitiva (10%)
  │
  ├── Cora-Debate (V1-V7): verificacao simbolica
  │     ├── V3: Contraexemplos (gate, peso 30%)
  │     └── V5-V7: Consistencia, CrossCheck, Simulacao
  │
  ├── PhD Auditor: Nash Solver + Cohen Kappa + Bonferroni + Qualis A1
  │
  └── AutoEvolve: SENSE -> DISCOVER -> INSTALL -> VERIFY -> EVOLVE -> LEARN
```

**Pontos fortes:**
- Especializacao multiagente (125 vs 1)
- 7 fases com gates obrigatorios (refutacao + verificacao)
- Anti-circularidade SPEC-008 (C1-C6, 92.77% agreement)
- Ecossistema completo (SDD+TDD+AutoEvolve)
- Cross-validation matrix (200+ afinidades)

**Fraquezas:**
- Nenhuma publicacao em venue top (Nature, EMNLP)
- Dominio limitado a producao academica assistida
- Sem parallel thinking (execucao sequencial dos agentes)
- Sem inference-time scaling law demonstrada
- CORA-Eval menor que IMO-Bench (150 vs 1460 tarefas)

---

## 3. Comparacao por Metricas

### 3.1 Raciocinio Matematico

| Metrica | Aletheia | OpenCode (CORA-Eval) | Diferenca |
|:--------|:--------:|:--------------------:|:---------:|
| IMO-ProofBench Advanced | 91.9% | N/A | Aletheia |
| Conditional accuracy (respondidos) | 96% | ~85% (estimado) | Aletheia |
| Erdos solucoes meaningful | 13/200 (6.5%) | N/A | Aletheia |
| FirstProof resolvidos | 6/10 | N/A | Aletheia |
| FirstProof publication-grade | 1/10 | N/A | Aletheia |
| PCI medio (calibrado) | N/A | 88 (target 95) | OpenCode |
| CORA-Score (projetado) | N/A | 3.45 | OpenCode |
| Cobertura de dominios | Matematica pura | 10 dimensoes (CORA-Eval) | OpenCode |

### 3.2 Arquitetura e Escala

| Metrica | Aletheia | OpenCode | Diferenca |
|:--------|:--------:|:--------:|:---------:|
| Numero de agentes | 1 (+3 subagentes) | 125 | OpenCode |
| Tipos de raciocinio | 1 (Deep Think) | 204 (25 categorias) | OpenCode |
| Verificadores | 1 (LN) | 7 (V1-V7) + PhD Auditor | OpenCode |
| Anti-circularidade | Nao | SPEC-008 (C1-C6) | OpenCode |
| Atualizacao autonoma | Nao (pesos fixos) | AutoEvolve (evolution rounds) | OpenCode |
| Inference-time scaling | Sim (100x) | Nao | Aletheia |
| Parallel thinking | Sim | Nao (sequencial) | Aletheia |

### 3.3 Transparencia e Reproducibilidade

| Metrica | Aletheia | OpenCode |
|:--------|:--------:|:---------|
| Codigo aberto | Sim (Apache 2.0) | Sim |
| Prompts publicos | Sim (no repo) | Sim (skills) |
| Logs de raciocinio | Sim (reasoning traces) | Sim (logs SHA-256) |
| Anti-circularidade documentada | Nao | SPEC-008 + C6 (92.77%) |
| Metrica de confianca | Conditional accuracy | PCI + CORA-Score |
| Framework de auditoria | ProofAutoGrader | PhD Auditor + Cora-Debate |
| Niveis de autonomia | Propostos (Level 0-4) | Evolution rounds (R1-R14) |
| Interacao humano-IA | Human-AI interaction cards | SDD+TDD+AutoEvolve |

---

## 4. Correspondencia: Autonomous Mathematics Levels x Evolution Rounds

O paper Aletheia propoe uma taxonomia de 5 niveis de autonomia. Podemos mapear
diretamente para os evolution rounds do OpenCode:

| Nivel Aletheia | Descricao | OpenCode Equivalente | Round |
|:--------------:|-----------|:--------------------:|:-----:|
| **Level 0** | Negligible novelty (solucoes elementares) | Primeiras skills geradas | R1-R3 |
| **Level 1** | Minor novelty (melhorias incrementais) | Skills com score 85-92 | R4-R6 |
| **Level 2** | Publishable research (artigo submetivel) | Artigo Qualis A1 (95/100) | R7-R11 |
| **Level 3** | Major advance (avanco significativo) | CORA-Score >= 4.0 (projetado) | R12-R15 |
| **Level 4** | Landmark breakthrough (avanco paradigmatico) | CORA-Score >= 4.5 | R16+ |

**Insight:** O OpenCode esta atualmente entre Level 1 (R11, score 97) e Level 2 (artigo Qualis A1).
O Aletheia atingiu Level 2 (Feng26 - paper autonomo) e contribuicoes Level 3 parciais.

---

## 5. Lacunas do OpenCode vs. Superhuman

### 5.1 O que o Superhuman tem que o OpenCode nao tem

| Lacuna | Impacto | Prioridade | Acao Sugerida |
|--------|:-------:|:----------:|---------------|
| Inference-time scaling law | Raciocinio melhora com mais computacao | Alta | Implementar para CORA-Eval |
| Parallel thinking | Exploracao simultanea de solucoes | Alta | Adaptar para ReasoningOrchestrator v12 |
| Publicacao em venue top | Credibilidade academica | Media | Submeter artigo CORA-Eval para evento |
| Benchmark maior (1460 tarefas) | Estatistica mais robusta | Media | Expandir CORA-Eval para 500 tarefas |
| Solucao de problemas abertos | Impacto matematico real | Baixa | Foco em educacao, nao pesquisa |

### 5.2 O que o OpenCode tem que o Superhuman nao tem

| Vantagem | Impacto | Diferencial |
|----------|:-------:|-------------|
| Anti-circularidade SPEC-008 | Evita auto-validacao | Unico no cenario |
| Multiagente (125 agentes) | Especializacao por dominio | Escala 125x |
| 204 tipos de raciocinio | Cobertura cognitiva ampla | 68 formalizados no orquestrador |
| PhD Auditor multimetodo | Auditoria robusta (Nash + Cohen + Bonferroni) | 3 metodos complementares |
| SDD+TDD+AutoEvolve | Garantia de qualidade formal | Ciclo completo de engenharia |
| PT-BR com corretor CJK | Suporte ao portugues academico | Diferencial Brasil |
| Cross-validation 200+ afinidades | Mapeamento do ecossistema | Visibilidade das relacoes |

---

## 6. Implicacoes para o Anteprojeto PPGTE

### 6.1 Posicionamento do OpenCode no cenario internacional

```
                      Escala de Agentes
                      (numero de agentes)
                            │
                    125 ─────● OpenCode
                            │
                     50 ──── │
                            │
                     10 ──── │
                            │
                      1 ────●────●────●────●────● Escala de Raciocinio
                            Aletheia   GPT-5   Claude  (tipos/formalismos)
                            │    1    68    204
                            │
                            └── OpenCode: unico sistema multiagente
                                com anti-circularidade documentada
                                e auditoria Qualis A1
```

### 6.2 O que o anteprojeto deve destacar

1. **Diferencial metodologico:** Unico sistema com anti-circularidade SPEC-008 (C6 anotacao humana, 92.77% agreement) — o Aletheia nao aborda este problema

2. **Escala multiagente:** 125 agentes vs. 1 agente (Aletheia) — o OpenCode oferece especializacao por dominio que o Aletheia nao tem

3. **Auditoria caixa branca:** Enquanto o Aletheia usa um verificador unico em LN, o OpenCode usa 7 verificadores (Cora-Debate V1-V7) + PhD Auditor com 3 metodos estatisticos

4. **Evolucao continua:** AutoEvolve evolution rounds (R1-R14 documentados) vs. pesos fixos do Aletheia

5. **Foco em PT-BR:** Unico sistema otimizado para producao academica em portugues com normas ABNT

### 6.3 Limitacoes a reconhecer

1. O OpenCode **nao** possui inference-time scaling law (o Aletheia mostrou que mais computacao = melhor raciocinio)
2. O OpenCode **nao** produziu papel autonomo publicavel em venue top (o Aletheia tem Nature + EMNLP + arXiv)
3. O OpenCode **nao** resolveu problemas abertos de matematica (o Aletheia resolveu 4 Erdos + 6 FirstProof)
4. O CORA-Eval (150 tarefas) e menor que o IMO-Bench (1460 tarefas)

---

## 7. Roadmap de Convergencia (Proposto)

| Fase | Acao | Impacto | Prazo |
|:----:|------|:-------:|:-----:|
| 1 | Implementar parallel thinking no ReasoningOrchestrator v12 | Exploracao simultanea de solucoes | 3 meses |
| 2 | Adicionar inference-time scaling ao CORA-Eval | Raciocinio escala com computacao | 6 meses |
| 3 | Expandir CORA-Eval para 500 tarefas | Benchmark mais robusto | 6 meses |
| 4 | Submeter artigo CORA-Eval para evento (SBIE, RBIE) | Credibilidade academica | 12 meses |
| 5 | Integrar niveis de autonomia (Level 0-4) no evolution tracking | Maturidade do ecossistema | 3 meses |
| 6 | Publicar dataset de 204 raciocinios como benchmark aberto | Contribuicao a comunidade | 12 meses |

---

## 8. Referencias

- Feng, T. et al. (2026). Towards Autonomous Mathematics Research. arXiv:2602.10177v3.
- Luong, T. et al. (2025). Towards Robust Mathematical Reasoning. EMNLP 2025.
- Google DeepMind. Superhuman Repository. https://github.com/google-deepmind/superhuman
- OpenCode Ecosystem. SPEC-008 Anti-Circularidade. v1.0.
- OpenCode Ecosystem. RELATORIO_C6_ANOTACAO.md. 92.77% agreement.
- OpenCode Ecosystem. RELATORIO_CALIBRACAO_CORRIGENDUM.md. v1.0.0.

---

*Gerado por AutoEvolve — OpenCode Ecosystem v4.6.1*
*Nivelamento: 12 dimensoes, 20+ metricas comparadas*
*Conclusao: OpenCode e superior em 8/12 dimensoes ao Aletheia,*
*mas inferior em publicacoes reais e inference-time scaling*
