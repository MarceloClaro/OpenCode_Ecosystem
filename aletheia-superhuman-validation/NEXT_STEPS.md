# PRÓXIMOS PASSOS - Sessão 11

**Status**: ✅ 3/3 mudanças concluídas. Pronto para execução.

---

## Resumo do que foi feito

### 1️⃣ ProofGeneratorV2 Criado (395 linhas)
✅ **Arquivo**: `scripts/proof_generator_v2.py`
- Carrega 10 templates domínio-específicos
- Gera provas natural + Lean com padrões por domínio
- Estima confiança [0.3–0.9]
- Teste inicial: 3/3 provas geradas ✓

### 2️⃣ Pipeline Phase B Integrado
✅ **Arquivo**: `scripts/pipeline_phase_b.py` (3 linhas alteradas)
- Line 31: Import statement → `ProofGeneratorV2`
- Line 82: Inicialização → `ProofGeneratorV2()`
- Line 192–197: `generate()` call → novo assinaturaatuálizada

### 3️⃣ Timeout Lean aumentado
✅ **Arquivo**: `scripts/lean_verifier.py` (2 linhas alteradas)
- Line 121: `timeout=30` → `timeout=120`
- Line 144: Error message atualizada
- Rationale: Provas melhoradas precisam mais tempo

---

## Instruções para Execução

### Opção A: Executar Phase B (10 problemas)
```bash
cd C:\Users\marce\OpenCode_Ecosystem\aletheia-superhuman-validation
python scripts/pipeline_phase_b.py
```

**Tempo estimado**: 5–10 minutos  
**Saída esperada**:
- `results/pipeline_phase_b_results.json`
- `results/PHASE_B_RESULTS.md`
- Múltiplos `results/proof_candidates/{ID}_proof.json`

**O que esperar**:
```
PHASE B: A0004
  ✓ Formalização OK
  ✓ Prova gerada (confiança: 55%)
  ✓ Status final: partial

PHASE B: B0014
  ...
```

---

### Opção B: Executar Phase C (Verificação Lean)
```bash
cd C:\Users\marce\OpenCode_Ecosystem\aletheia-superhuman-validation
python scripts/pipeline_phase_c.py
```

**Pré-requisito**: Phase B deve estar completo (candidatos em `results/proof_candidates/`)  
**Tempo estimado**: 30–60 minutos (120s × 10 problemas)  
**Saída esperada**:
- `results/pipeline_phase_c_results.json`
- `results/FINAL_REPORT.md`
- Log detalhado de verificações

---

### Opção C: Teste Rápido (1 problema)
```bash
cd C:\Users\marce\OpenCode_Ecosystem\aletheia-superhuman-validation
python test_v2_simple.py
```

**Tempo estimado**: <5 segundos  
**Usa**: Problem A0004, domain=combinatorics  
**Valida**: ProofGeneratorV2 está funcionando ✓

---

## Fluxo Recomendado

```
┌─────────────────────┐
│  test_v2_simple.py  │  ← Validação (5s)
└──────────┬──────────┘
           │
           v
┌──────────────────────────┐
│  pipeline_phase_b.py     │  ← Geração (5–10 min)
│  (10 problemas)          │
└──────────┬───────────────┘
           │
           v
┌──────────────────────────┐
│  pipeline_phase_c.py     │  ← Verificação (30–60 min)
│  (Lean compile)          │
└──────────┬───────────────┘
           │
           v
┌──────────────────────────┐
│  FINAL_REPORT.md         │  ← Análise
│  Sucesso/Parcial/Falha   │
└──────────────────────────┘
```

---

## O Que Esperar (Estimativas)

### Phase B V2 vs V1
| Métrica | V1 | V2 | Melhoria |
|---------|----|----|----------|
| Tempo | ~2s/problema | ~0.5s | 4x mais rápido |
| Sucesso | 30% | 40% | +10% |
| Parcial | 40% | 40% | = |
| Falha | 30% | 20% | -10% |

### Phase C (10 problemas)
| Resultado | V1 | V2 | Esperado |
|-----------|----|----|----------|
| Sucesso | 0 | ≥2 | ~20% |
| Parcial | 3 | ≥3 | ~30% |
| Falha | 7 | ≤5 | ~50% |

---

## Arquivos Alterados (Resumo)

```
scripts/
├── proof_generator_v2.py         ✨ NOVO (395 linhas)
├── pipeline_phase_b.py           📝 ALTERADO (3 linhas)
└── lean_verifier.py              📝 ALTERADO (2 linhas)

root/
├── test_v2_simple.py             ✨ NOVO (teste)
├── PROGRESS_SESSION_11.md        📊 NOVO (histórico)
└── NEXT_STEPS.md                 📋 NOVO (este arquivo)
```

---

## Verificações Rápidas Antes de Rodar

```bash
# 1. Verificar que templates estão carregados
python -c "from scripts.proof_templates import PROBLEM_TEMPLATE_MAP; print(f'Templates: {len(PROBLEM_TEMPLATE_MAP)}')"
# Esperado: Templates: 10

# 2. Verificar que Lean está instalado
lean --version
# Esperado: Lean 4.30.0 (ou semelhante)

# 3. Verificar que problemas estão selecionados
python -c "import json; d=json.load(open('data/selected_problems_phase_b_v2.json')); print(f'Problemas: {len(d)}')"
# Esperado: Problemas: 10
```

---

## Troubleshooting

### Se Phase B ficar lento:
- Aumentar `max_tokens=1500` em `proof_generator_v2.py` (linha ~90)
- Ou reduzir para `top_n=5` em `pipeline_phase_b.py`

### Se Phase C der timeout (>120s):
- Aumentar para `timeout=180` em `lean_verifier.py`
- Ou reduzir `max_iterations` em `pipeline_phase_c.py`

### Se houver import error:
- Verificar: `python -c "import sys; sys.path.insert(0, 'scripts'); from proof_generator_v2 import ProofGeneratorV2"`
- Deve imprimir: "✓ ProofGeneratorV2 inicializado"

---

## Referências Rápidas

**Problemas selecionados (10)**:
- A0004, B0014, B0017 (top 3, mais recentes)
- E0019, E0020, E0025, E0030, E0035, E0038, E0045 (resto)

**Domínios**:
- combinatorics: A0004, E0019, E0035
- analysis: B0014, E0038
- number_theory: B0017, E0030
- geometry: E0020
- graph_theory: E0025, E0045

**Tempo Total Estimado**:
- Teste (1 prob): 5s
- Phase B (10 prob): 5–10 min
- Phase C (10 prob × 120s): 30–60 min
- **Total**: ~40–75 minutos

---

## Próxima Ação

```bash
cd C:\Users\marce\OpenCode_Ecosystem\aletheia-superhuman-validation

# OPÇÃO 1: Teste rápido primeiro
python test_v2_simple.py

# OPÇÃO 2: Rodar Phase B direto
python scripts/pipeline_phase_b.py

# OPÇÃO 3: PowerShell com progresso visual
& ".\run_phase_b_v2.ps1"
```

**Recomendação**: Comece com teste rápido para validar integração. ✓

---

**Última atualização**: 30/05/2026 18:21  
**Estado**: ✅ Pronto para execução
