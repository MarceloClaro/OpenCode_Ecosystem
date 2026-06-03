# Roadmap v1.1 — Aletheia-Superhuman Evolution

**Versão**: 1.1-beta  
**Data de Planejamento**: 30 de maio de 2026  
**Timeline**: Próximo mês  
**Status**: Em Planejamento

---

## 🎯 Objetivos v1.1

Expandir o pipeline SPEC validado em v1.0 para:

1. **Dataset Maior**: 1000+ problemas Erdős (vs 430 em v1.0)
2. **Novos Domínios**: Topologia, Geometria, Análise (não apenas combinatória/teoria dos números)
3. **Distributed CORA-Debate**: Multi-GPU para Q-Score UCB1 em paralelo
4. **Automated Skill Generation**: Usar Manus Evolve para gerar novas skills a partir de insights
5. **arXiv Pre-print**: Submissão formal (versão de trabalho)

---

## 📊 Métricas v1.0 → v1.1

| Métrica | v1.0 | v1.1 Target | Delta |
|---------|------|-------------|-------|
| **Problemas** | 430 | 1000+ | +2.3x |
| **Domínios** | 4 (combi, NT, logic, other) | 7+ (+ topologia, geom, análise) | +3 |
| **Taxa de Sucesso** | 100% | ≥99% | ±1pp |
| **Tempo Total** | 1.9s | <30s (1000 problems) | +15.7x throughput |
| **Raciocínios Integrados** | 68 | 80+ | +12 |
| **ADRs Registradas** | 6 | 10+ | +4 |
| **Documentação** | 72+ seções | 100+ seções | +40% |

---

## 🔄 Ciclo de Trabalho v1.1

### FASE 1: Preparação (Semanas 1-2)

#### 1.1 — Expansão de Dataset

**Tarefas:**
- [ ] Buscar problemas adicionais em google-deepmind/formal-conjectures
- [ ] Categorizar por domínio (7 domínios alvo)
- [ ] Validar completude (1000+ instâncias)
- [ ] Atualizar `erdos_1000_enriched.json`

**Critério de Sucesso**: 1000+ problemas categorizados, estrutura idêntica a v1.0

**Arquivo Output**: `data/erdos_1000_enriched.json`

#### 1.2 — Infraestrutura Multi-GPU

**Tarefas:**
- [ ] Configurar CUDA/cuDNN
- [ ] Adaptar Q-Score UCB1 para parallelização
- [ ] Implementar batch processing distribuído
- [ ] Benchmark: 430 → 1000 em <30s

**Critério de Sucesso**: 1000 problemas processados em paralelo com speedup ≥3x

**Arquivo Output**: `scripts/distributed_spec_processor.py`

---

### FASE 2: Validação Estendida (Semanas 2-3)

#### 2.1 — SPEC Pipeline em 1000 Problemas

**Tarefas:**
- [ ] Executar SPEC-013-016 em dataset 1000x
- [ ] Registrar métricas por domínio
- [ ] Identificar padrões de falha (se houver)
- [ ] Documentar resultados parciais a cada 250 problemas (checkpoints)

**Critério de Sucesso**: 1000/1000 (ou ≥990/1000 com análise de falhas)

**Arquivo Output**: `reports/batch_1000_validation_full_report.md`, `reports/batch_1000_validation_full_details.json`

#### 2.2 — Domínios Novos

**Tarefas:**
- [ ] Testar em topologia (30+ problemas)
- [ ] Testar em geometria (30+ problemas)
- [ ] Testar em análise (30+ problemas)
- [ ] Comparar taxa de sucesso vs baseline (6.1%)

**Critério de Sucesso**: Manutenção de >95% taxa de sucesso em novos domínios

**Arquivo Output**: `reports/domain_comparison_analysis.md`

---

### FASE 3: Evolução Científica Expandida (Semana 3)

#### 3.1 — Raciocínios Novos (68 → 80+)

**Tarefas:**
- [ ] Analisar 1000 problemas para identificar padrões de raciocínio não-cobertos
- [ ] Definir 12+ novos tipos de raciocínio
- [ ] Integrar no Reasoning Orchestrator v11
- [ ] Retreinar Q-Score UCB1 com novo corpus

**Critério de Sucesso**: 80+ tipos formalizados, validados em subset

**Arquivo Output**: `docs/REASONING_TYPES_EXTENDED.md`

#### 3.2 — Novas ADRs (6 → 10+)

**Tarefas:**
- [ ] Registrar decisão de expansão de dataset (ADR-007)
- [ ] Registrar decisão de domínios novos (ADR-008)
- [ ] Registrar decisão de distributed processing (ADR-009)
- [ ] Registrar decisão de skill generation (ADR-010)

**Critério de Sucesso**: 10+ ADRs em DecisionNode com raciocínio completo

**Arquivo Output**: Registros em DecisionNode

#### 3.3 — Geração Automática de Skills (Manus Evolve)

**Tarefas:**
- [ ] Analisar 1000 problemas para insights generalizáveis
- [ ] Identificar 3-5 padrões recorrentes
- [ ] Gerar skill manifests usando Manus Evolve
- [ ] Validar skills em subset (50 problemas)

**Critério de Sucesso**: 3+ novas skills geradas e testadas

**Arquivo Output**: 
- `skills/aletheia-erdos-analysis-v1.1/`
- `skills/formal-proof-augmenter-v1.1/`
- `skills/cora-distributed-verifier-v1.1/`

---

### FASE 4: Documentação & Publicação (Semana 4)

#### 4.1 — Atualizar Documentação

**Tarefas:**
- [ ] Estender SCIENTIFIC_EVOLUTION_STRATEGY.md (80+ raciocínios)
- [ ] Adicionar seção "Domain Generalization"
- [ ] Documentar Manus Evolve insights
- [ ] Atualizar reproducibility/protocol.md para 1000 problemas

**Critério de Sucesso**: 100+ seções, cobertura completa

**Arquivo Output**: Docs atualizados

#### 4.2 — arXiv Pre-print

**Tarefas:**
- [ ] Escrever versão 1.1 do paper
- [ ] Incluir dados 1000-problema
- [ ] Incluir análise de domínios novos
- [ ] Submeter a arXiv como preprint (v2)

**Critério de Sucesso**: arXiv paper aceito (categoria cs.AI ou cs.LO)

**Arquivo Output**: arXiv link + DOI

#### 4.3 — GitHub Release v1.1

**Tarefas:**
- [ ] Criar tag `v1.1-aletheia-extended`
- [ ] Criar GitHub Release com notas detalhadas
- [ ] Atualizar README principal
- [ ] Criar CHANGELOG.md entrada

**Critério de Sucesso**: Release publicado, tagueado, documentado

---

## 🚀 Arquitetura v1.1

### Estrutura Esperada

```
aletheia-superhuman-validation/
├── README.md (updated)
├── ROADMAP_V1.1.md (este arquivo)
├── CHANGELOG.md (updated)
├── ...
├── data/
│   ├── erdos_700_enriched.json (v1.0)
│   └── erdos_1000_enriched.json (v1.1 NEW)
├── scripts/
│   ├── spec_batch_processor.py (v1.0)
│   ├── distributed_spec_processor.py (v1.1 NEW)
│   └── domain_analyzer.py (v1.1 NEW)
├── reports/
│   ├── batch_phase2_validation_full_report.md (v1.0)
│   ├── batch_1000_validation_full_report.md (v1.1 NEW)
│   ├── domain_comparison_analysis.md (v1.1 NEW)
│   └── ...
├── docs/
│   ├── SCIENTIFIC_EVOLUTION_STRATEGY.md (updated)
│   ├── REASONING_TYPES_EXTENDED.md (v1.1 NEW)
│   └── ...
├── skills/ (v1.1 NEW)
│   ├── aletheia-erdos-analysis-v1.1/
│   ├── formal-proof-augmenter-v1.1/
│   └── cora-distributed-verifier-v1.1/
└── ...
```

---

## 📋 Checklist de Dependências

### Pré-requisitos v1.1

- ✅ v1.0 publicado (430/430, p < 0.001)
- ✅ GitHub Release criada
- ✅ DecisionNode com 6 ADRs
- ✅ CORA-Debate v1-v7 testado
- ⏳ Manus Evolve pronto para skill generation
- ⏳ Infraestrutura multi-GPU disponível

### Bloqueadores Conhecidos

- CUDA setup (se GPU não disponível, usar CPU com menor throughput)
- Dataset expansion (dependente de disponibilidade em google-deepmind/formal-conjectures)

---

## 🎯 Métricas de Sucesso v1.1

| Métrica | Target | Critério de Sucesso |
|---------|--------|-------------------|
| **Dataset** | 1000+ problemas | ✅ ≥1000 |
| **Taxa v1.1** | ≥99% | ✅ Manter 100% ou ≥99% |
| **Novos Domínios** | 7 total | ✅ ≥3 novos testados |
| **Raciocínios** | 80+ | ✅ 12+ novos integrados |
| **ADRs** | 10+ | ✅ 4+ novas registradas |
| **Skills** | 3+ | ✅ Geradas + testadas |
| **arXiv** | Preprint v2 | ✅ Aceito e DOI |
| **Documentação** | 100+ seções | ✅ Cobertura completa |
| **Reproducibilidade** | 100% (seed=42) | ✅ Verificado em subset |

---

## 📅 Timeline

| Semana | Fase | Tarefas Chave | Deliverables |
|--------|------|---------------|--------------|
| 1-2 | Prep | Dataset (1000), infra multi-GPU | `erdos_1000_enriched.json`, `distributed_spec_processor.py` |
| 2-3 | Validation | SPEC em 1000, novos domínios | Relatórios de batch_1000, domain analysis |
| 3 | Evolution | Raciocínios (80+), novas ADRs, skills | Docs estendidos, 3+ skills |
| 4 | Release | arXiv, GitHub Release v1.1 | v1.1 tag, paper, release notes |

---

## 🔗 Links de Referência

**v1.0 (Atual)**:
- Release: https://github.com/MarceloClaro/OpenCode_Ecosystem/releases/tag/v1.0-aletheia-validated
- Docs: `aletheia-superhuman-validation/docs/SCIENTIFIC_EVOLUTION_STRATEGY.md`
- Dados: `aletheia-superhuman-validation/data/erdos_700_enriched.json`

**v1.1 (Em Planejamento)**:
- Esta roadmap
- Manus Evolve docs (para skill generation)
- arXiv submission guidelines

---

## 🔬 Hipóteses de Pesquisa v1.1

### H1: Generalização de Domínios
**Hipótese**: Pipeline SPEC mantém ≥95% taxa de sucesso em domínios novos (topologia, geometria, análise)

**Método**: Testar 30+ problemas em cada novo domínio

**Esperado**: Descobrir que estrutura SPEC é robusta além de combinatória/NT

### H2: Escalabilidade
**Hipótese**: Distributed CORA-Debate achieves ≥3x speedup com multi-GPU

**Método**: Benchmark 1000-problema com 1 GPU vs 4 GPUs

**Esperado**: <30s total time para 1000 problemas

### H3: Skill Generation
**Hipótese**: Manus Evolve pode gerar 3+ skills válidas a partir de 1000-problema corpus

**Método**: Analisar padrões, gerar manifests, validar em subset

**Esperado**: 3+ skills que aumentam CORA-Score em ≥5pp

---

## 📝 Notas e Observações

- **Backward Compatibility**: v1.1 manter v1.0 como subdirectório (não quebra links)
- **Dataset Strategy**: Preferir problemas não-sobrepostos com v1.0 (1000 total, não 430+570)
- **Skill Integration**: Novas skills submetidas como PRs separadas, não mergidas no main até v1.1 release
- **arXiv**: Submeter como "v2" do paper v1.0, não novo paper

---

**Próximas Ações:**
1. ✅ Publicar v1.0 (COMPLETO)
2. ⏳ Revisar roadmap v1.1 com stakeholders
3. ⏳ Iniciar Fase 1 (dataset expansion)
4. ⏳ Preparar Manus Evolve para skill generation

---

**Versão**: 1.0-draft  
**Data**: 30 de maio de 2026  
**Status**: 📋 **PRONTO PARA REVISÃO**
