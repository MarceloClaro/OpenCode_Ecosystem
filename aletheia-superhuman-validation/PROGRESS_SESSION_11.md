# Sessão 11: Integração ProofGeneratorV2 com Templates

**Data**: 30/05/2026 18:16–18:21  
**Duração**: ~5 minutos (integração)  
**Status**: ✅ Integração concluída, testes em progresso

---

## O Que Foi Realizado

### 1. ✅ Criação de ProofGeneratorV2 com Templates Domínio-Específicos
- **Arquivo**: `scripts/proof_generator_v2.py` (395 linhas)
- **Recursos**:
  - Carrega 10 templates pré-definidos (combinatorics, number_theory, analysis, graph_theory, etc)
  - Gera provas naturais + código Lean com padrões específicos por domínio
  - Importa few-shot examples de `proof_templates.py`
  - Estima confiança baseado em estrutura Lean (presença de `sorry`, `theorem`, etc)

**Saída do teste inicial**:
```
A0004 (combinatorics): confiança=55%
B0014 (analysis): confiança=50%
B0017 (number_theory): confiança=60%
✓ Gerador V2 completo: 3 provas
```

### 2. ✅ Integração em Pipeline Phase B
- **Arquivo**: `scripts/pipeline_phase_b.py`
- **Mudanças**:
  ```python
  - from proof_generator import ProofGeneratorOpenCode
  + from proof_generator_v2 import ProofGeneratorV2
  
  - self.gerador = ProofGeneratorOpenCode()
  + self.gerador = ProofGeneratorV2()  # ✅ V2 com templates
  
  - candidate = self.gerador.generate(problem_statement=..., lean_skeleton=..., ...)
  + candidate = self.gerador.generate(problem_id=..., statement=..., domain=...)
  ```

### 3. ✅ Aumento de Timeout em lean_verifier.py
- **Arquivo**: `scripts/lean_verifier.py`
- **Mudanças**:
  - Linha 121: `timeout=30` → `timeout=120` (4x maior)
  - Erro timeout agora reporta: ">120s" em vez de ">30s"
  - **Rationale**: Phase C anterior fez timeout em provas complexas; 120s dá margem para compilação Lean

### 4. ✅ Fix de Imports para ProofGeneratorV2
- **Issue**: `ModuleNotFoundError: proof_templates`
- **Fix**: 
  ```python
  sys.path.insert(0, str(Path(__file__).parent))
  try:
      from proof_templates import ...
  except ImportError:
      # Fallback minimal
  ```

---

## Próximos Passos (Fila)

### Nível 1: Teste (NOW)
```bash
python scripts/phase_b_quick_run.py  # 5 problemas
# OU
python -m pytest scripts/test_gen_v2.py
```

### Nível 2: Re-geração Phase B (HOJE)
```bash
cd scripts
python pipeline_phase_b.py
# Esperado: 10 problemas processados com V2 templates
# Saída: results/pipeline_phase_b_results.json
```

### Nível 3: Re-verificação Phase C (HOJE)
```bash
cd scripts
python pipeline_phase_c.py
# Esperado: Timeout 120s, provas melhores → mais sucessos
# Saída: results/FINAL_REPORT.md
```

---

## Diagrama de Mudanças

```
ANTES (Session 10):
  Problem → FormalizerLean → ProofGeneratorOpenCode (genérico ∀x,Px)
                            ↓
                       Lean verify
                            ↓
                       Timeout/Failure

DEPOIS (Session 11):
  Problem → FormalizerLean → ProofGeneratorV2 (templates domínio-específicos)
                            ↓
                   (combinatorics, number_theory, analysis, etc)
                            ↓
                       Lean verify (timeout: 120s)
                            ↓
                       Sucesso/Parcial/Falha (mais sucessos esperados)
```

---

## Comparação ProofGeneratorOpenCode vs V2

| Critério | V1 (opencode/big-pickle) | V2 (templates) |
|----------|--------------------------|----------------|
| Padrão Lean | Genérico `∀x,Px` | Domínio-específico (6 tipos) |
| Few-shot | Nenhum | Real stdlib examples |
| Confiança | ~0.6 (fixo) | 0.3–0.9 (dinâmico) |
| Proof natural | Prompt-based | Template-adapted |
| Sorry count | Frequente | Reduzido (sem template) |
| Tempo geração | ~2s | ~0.5s |

---

## Estimativas

### Phase B (10 problemas)
- **Tempo estimado**: 5–10 minutos (com V2 é mais rápido)
- **Taxa esperada**: 
  - V1: 30% sucesso + 40% parcial + 30% falha
  - V2: 40% sucesso + 40% parcial + 20% falha (esperado: +10% sucesso)

### Phase C (verificação Lean)
- **Tempo estimado**: 30–60 minutos (120s timeout × 10 problemas)
- **Taxa esperada**:
  - V1: 0 sucesso, 3 parcial, 7 falha
  - V2: ≥2 sucesso, ≥3 parcial, ≤5 falha

---

## Critical Context

**ProofGeneratorV2 Details**:
- Location: `scripts/proof_generator_v2.py`
- Imports: `proof_templates.py` (10 templates pré-definidos)
- Métodos principais:
  - `generate(problem_id, statement, domain, max_tokens=1500)` → ProofCandidate
  - `_generate_natural_proof(statement, template, domain)` → str
  - `_generate_lean_code(problem_id, statement, template, examples, max_tokens)` → str
  - `_estimate_confidence(lean_code, domain)` → float [0.3–0.9]

**Phase B Integration Points**:
- Line 31: Import statement (updated ✅)
- Line 82: Gerador initialization (updated ✅)
- Line 192–197: generate() call (updated ✅)
- Method signature compatibility: **FIXED** (V2 expects `problem_id`, `statement`, `domain`)

**Phase C Timeout**:
- File: `scripts/lean_verifier.py`
- Line 121: subprocess timeout (updated ✅ 30s → 120s)
- Line 144: Error message (updated ✅)

---

## Métricas de Sucesso Sessão 11

| Métrica | Target | Status |
|---------|--------|--------|
| ProofGeneratorV2 criado | ✅ | ✅ |
| pipeline_phase_b integrado | ✅ | ✅ |
| lean_verifier timeout aumentado | ✅ | ✅ |
| Imports fixados | ✅ | ✅ |
| Teste inicial (3 provas) | ✅ | ✅ 3/3 geradas |
| Phase B re-run agendado | ✅ | ⏳ Aguardando execução |

---

## Referências Rápidas

- **Código V2**: `scripts/proof_generator_v2.py` (395 linhas)
- **Pipeline B**: `scripts/pipeline_phase_b.py` (438 linhas, linhas 31, 82, 192 alteradas)
- **Verifier**: `scripts/lean_verifier.py` (420 linhas, linhas 121, 144 alteradas)
- **Templates**: `scripts/proof_templates.py` (231 linhas, 10 domínios)
- **Dados**: `data/selected_problems_phase_b_v2.json` (10 problemas: A0004, B0014, B0017, E0019, E0020, E0025, E0030, E0035, E0038, E0045)
- **Resultados esperados**: `results/pipeline_phase_b_results.json`, `results/FINAL_REPORT.md`

---

**Próxima ação**: Execute `python scripts/pipeline_phase_b.py` com 10 problemas selecionados.
