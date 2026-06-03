
# CICLO 5 — Relatório de Correções e Resultados

## 1. Bugs Encontrados e Corrigidos

### Bug 1: Falso Positivo na Detecção de Domínio (B5-T6)
**Problema**: `"api" in "what is the capital of france?"` retornava `True` porque a substring `"api"` está contida dentro de `"capital"`. Isso fazia o domínio ser classificado como `"code"` em vez de `"general"`, resultando em `"weighted_vote"` em vez de `"best_of"`.

**Correção**: Substituir `kw in problem_lower` por `re.search(rf'\b{re.escape(kw)}\b', problem_lower)` em `full_pipeline.py`:
```python
import re
# Antes:
if any(kw in problem_lower for kw in self._CODE_KEYWORDS):
# Depois:
if any(re.search(rf'\b{re.escape(kw)}\b', problem_lower) for kw in self._CODE_KEYWORDS):
```

### Bug 2: Precedência Incorreta de Estratégia (B5-T5)
**Problema**: `select_strategy` verificava `STRATEGY_RULES[domain]` antes de `COMPLEXITY_MAP[complexity]`. Para `ProblemProfile(complexity="research", domain="physics")`, `STRATEGY_RULES["physics"]="weighted_vote"` era retornado antes que a regra de complexidade `"research" → "ensemble"` fosse considerada.

**Correção**: Inverter a ordem — verificar `complexity == "research"` → retornar `"ensemble"` e `complexity == "high"` → retornar `"debate"` antes de consultar as regras de domínio.

### Bug 3: Faixa PCI Incorreta no Teste (B5-T9)
**Problema**: Assert `assert 0 <= result.mean_pci <= 1` usava teto [0,1], mas o motor interno de PCI (`orchestrator_v12.py:393`) calcula `pci = min(100.0, max(0.0, raw_pci * 25.0))`, resultando em range [0,100].

**Correção**: `<= 1` → `<= 100` em `test_benchmark_c5.py`.

## 2. Alterações Realizadas

### Arquivos Modificados

| Arquivo | Linhas | Mudança | Motivo |
|---------|--------|---------|--------|
| `agents/full_pipeline.py` | 1 (import) + 1 (lógica) | `re.search` com word boundaries | Falso positivo "api" em "capital" |
| `agents/full_pipeline.py` | ~5 linhas | Reordenar `select_strategy` | Precedência research/high |
| `tests/test_benchmark_c5.py` | 1 linha | `<= 1` → `<= 100` | Faixa PCI real [0,100] |

## 3. Resultados dos Testes

### 12/12 Testes Passando

```
test_speedup_w1_near_one ........... PASSED  (B5-T1)
test_speedup_w2_greater_than_w1 ... PASSED  (B5-T2)
test_speedup_w4_greater_than_w2 ... PASSED  (B5-T3)
test_efficiency_positive ........... PASSED  (B5-T4)
test_strategy_code ................. PASSED  (B5-T5)
test_strategy_debate ............... PASSED  (B5-T5)
test_strategy_simple ............... PASSED  (B5-T6) ← corrigido
test_strategy_research ............. PASSED  (B5-T5) ← corrigido
test_benchmark_result_structure .... PASSED  (B5-T7)
test_benchmark_values_in_range ..... PASSED  (B5-T9) ← corrigido
test_domain_strategy_consistency ... PASSED  (B5-T8)
test_all_profiles_produce_strategies PASSED (B5-T10)
```

### Speedup Empírico (4 cadeias, ProcessPoolExecutor)

| Workers | Speedup | Eficiência | Overhead |
|---------|---------|------------|----------|
| W=1 | ~1.0x base | 100% | ~0ms |
| W=2 | ~1.6-1.9x | ~80-95% | ~100-400ms |
| W=4 | ~2.0-2.2x | ~50-55% | ~300-800ms |

Speedup menor que linear devido ao overhead de spawn de processos no Windows.

### Hierarquia de Decisão de Estratégia (Final)

```
entra em select_strategy(profile):
 1. complexity == "research" → ensemble        (sobrescreve domínio)
 2. complexity == "high"     → debate           (sobrescreve domínio)
 3. domain in STRATEGY_RULES → weighted_vote (code, math, physics)
                                 debate      (debate)
                                 ensemble    (creative, exploration)
                                 best_of     (simple)
 4. complexity in COMPLEXITY_MAP → best_of (low)
                                   weighted_vote (medium)
                                   ensemble (high — fallback)
 5. fallback → best_of
```

### Thresholds de Complexidade

| Contagem de Palavras | Complexidade | Estratégia Padrão |
|---------------------|-------------|-------------------|
| < 10 | low | best_of |
| < 30 | medium | weighted_vote |
| < 60 | high | debate |
| >= 60 | research | ensemble |

## 4. Lições Aprendidas

1. **Substring matching vs word boundaries**: `in` operator em Python causa falsos positivos em detecção de domínio. Sempre usar `\b` regex para palavras-chave curtas ou genéricas.
2. **Precedência de regras**: Regras mais específicas (complexidade) devem ser verificadas antes de regras mais gerais (domínio). A hierarquia "complexidade → domínio → fallback" garante comportamento intuitivo.
3. **Range de métricas**: Sempre verificar a faixa real de saída do motor (PCI [0,100]) antes de escrever asserts de teste. A divisão por 100 para obter confidence [0,1] acontece apenas na interface externa.
