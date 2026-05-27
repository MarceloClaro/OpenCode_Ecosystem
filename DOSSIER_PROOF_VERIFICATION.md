---
title: "DOSSIER — Arquitetura de Verificacao Formal para Raciocinio Matematico no OpenCode Ecosystem"
subtitle: "Licoes do Problema 1 da IMO 2025 e Rota para Verificacao de Provas"
version: "1.0.0"
date: "2026-05-25"
status: "Proposta de Implementacao — P20, P21, P22, P23"
trigger: "Falha das Abordagens A, B e C em detectar erro na resposta do Problema 1"
principio: "Em matematica, um unico lema falso invalida toda a cadeia dedutiva"
---

# DOSSIER: Verificacao Formal de Provas Matematicas

> **Principio fundador**: Em um problema de exatas, basta um pequeno erro em algum lema
> para invalidar todo o resto. O Cora-Debate V1-V6 verificou formulas — nao provas.
> Precisamos de uma nova camada que verifique a **cadeia logica**, nao apenas a
> **consistencia algebrica**.

---

## 1. Diagnostico: O Que Faltou

### 1.1 O Que o Cora-Debate V1-V6 Verificou (e por que nao bastou)

| Verificador | O que faz | Por que falhou no Problema 1 |
|------------|-----------|---------------------------|
| V1 (Dimensional) | Consistencia de unidades | Problema adimensional — irrelevante |
| V2 (Algebrico) | $k(3k-2n+1) \leq 0$ via SymPy | Verificou uma **formula assumida**, nao sua **derivacao** |
| V3 (Contraexemplos) | Busca randomizada para $n=3..50$ | Testou o **limitante**, nao a **construcao** |
| V4 (Estatistico) | Correlacao de Pearson | Correlacao != correcao |
| V5 (Numerico) | Precisao IEEE 754 | Irrelevante para combinatoria |
| V6 (PDE/EDO) | SymPy dsolve | Nao aplicavel |

**Diagnostico**: Os verificadores V1-V6 formam uma **camada de consistencia** — checam se
as pecas se encaixam. Mas nao verificam se a **estrutura da prova** e valida. E como
verificar se um edificio tem paredes retas e janelas do tamanho certo, sem verificar se
os alicerces existem.

### 1.2 As Cinco Falhas Especificas que Nenhum Verificador Detectou

| # | Falha | Tipo | O que deveria ter detectado |
|---|-------|------|---------------------------|
| F1 | "Pigeonhole generalizado" nao demonstrado | **Claim nao-justificada** | LemmaGraph: dependencia quebrada |
| F2 | Construcao $m_j = -1-1/j$ falha para $n=4,k=2$ | **Contraexemplo na construcao** | ExhaustiveBaseChecker: teste exaustivo |
| F3 | Erro de indice: $k+1$ vs $k$ anti-diagonais restantes | **Erro aritmetico** | ProofStepVerifier: verificacao passo a passo |
| F4 | Invariante com $|p+q|=1$ contradiz a si mesmo | **Contradicao interna** | ContradictionDetector |
| F5 | Resposta nao confere com referencias externas | **Cross-check ausente** | ExternalReferenceValidator |

---

## 2. Nova Arquitetura: Camada de Verificacao de Provas (P20-P23)

```
┌─────────────────────────────────────────────────────────────────┐
│              CAMADA DE VERIFICACAO DE PROVAS                     │
│                                                                  │
│  P20: LemmaGraph        P21: InductionVerifier                  │
│  (Grafo de dependencias  (Verificador de reducao/inducao)       │
│   entre lemas)                                                  │
│                                                                  │
│  P22: ExhaustiveBase     P23: CrossReferenceValidator           │
│  (Verificacao exaustiva  (Validacao contra fontes externas)     │
│   de casos base)                                                │
│                                                                  │
│  Integracao: Camada acima do Cora-Debate V1-V6 existente        │
│  V1-V6 verificam consistencia; P20-P23 verificam VALIDADE       │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. P20 — LemmaGraph: Grafo de Dependencias entre Lemas

### 3.1 Conceito

Cada afirmacao na prova (lema, teorema, corolario) e um **no** no grafo.
Cada dependencia ("Lema 2 usa Lema 1") e uma **aresta direcionada**.
Se um no e invalidado, **todos os seus descendentes** sao automaticamente marcados
como nao-confiables.

### 3.2 Estrutura de Dados

```python
class LemmaNode:
    id: str                    # "L1", "L2", "T1"
    statement: str             # enunciado do lema
    status: "unverified" | "verified" | "contradicted" | "assumed"
    proof_steps: List[str]     # passos da demonstracao
    depends_on: List[str]      # IDs dos lemas que este lema usa
    verified_by: List[str]     # V1-V6, P21, P22, P23 — quais verificadores passaram
    counterexample: Optional[Any]  # contraexemplo se encontrado
```

### 3.3 Algoritmo de Propagacao de Falha

```
funcao invalidate(node_id):
    node = graph[node_id]
    node.status = "contradicted"
    para cada child em graph.get_children(node_id):
        invalidate(child)  # recursivo: todos os dependentes caem
```

### 3.4 Aplicacao ao Problema 1

```
L1 (Restricao de Colinearidade) ──┐
                                   ├──> L2 (Limitante Superior) ──> T1 (Teorema Final)
                                   │
                                   └──> L3 (Construcao) ──────────> T1 (Teorema Final)
```

Se L2 falha (como aconteceu — pigeonhole nao justificado), T1 e automaticamente
invalidado. Se L3 falha (construcao quebrada para $n=4,k=2$), T1 tambem cai —
**independentemente** de L2 estar correto ou nao.

### 3.5 Implementacao

| Componente | Tecnologia | Descricao |
|-----------|-----------|-----------|
| `skills/proof-verifier/SKILL.md` | Skill | Instrucoes para construcao e verificacao do LemmaGraph |
| `skills/proof-verifier/lemma_graph.py` | Python | Motor do grafo de dependencias |
| `plugins/lemma-graph.ts` | TypeScript | Plugin que expoe `/lemma-status`, `/lemma-invalidate` |

---

## 4. P21 — InductionVerifier: Verificador de Reducao/Inducao

### 4.1 Conceito

Muitas provas olimpicas usam inducao ou reducao ($n \to n-1$). O InductionVerifier
verifica que:

1. **Passo de reducao e valido**: remover um elemento preserva as propriedades
2. **Invariante e preservado**: a quantidade $k$ nao se altera na reducao
3. **Caso base e verificado**: o menor $n$ foi checado exaustivamente

### 4.2 Aplicacao ao Problema 1 (Rota Correta)

A rota correta (Evan Chen / DeepMind) usa:

```
Teorema da Reta Longa de Borda:
  Para n >= 4, existe uma reta NAO-ensolarada contendo n pontos de S_n
  (y=1, x=1, ou x+y=n+1)

Reducao:
  Remova essa reta -> problema reduz de n para n-1
  k (numero de ensolaradas) NAO se altera (a reta removida e nao-ensolarada)

Inducao:
  Repita ate n=3 -> k deve ser viavel para n=3

Caso base (n=3):
  Verificacao exaustiva -> k in {0, 1, 3}
```

### 4.3 O Que o InductionVerifier Checa

```python
def verify_induction(n_initial, reduction_fn, invariant_fn, base_checker):
    # 1. Verificar que a reducao preserva o invariante
    for n in range(4, n_initial + 1):
        assert invariant_fn(n) == invariant_fn(n - 1), \
            f"Invariante nao preservado na reducao n={n} -> n-1"
    
    # 2. Verificar o caso base
    base_result = base_checker(3)
    
    # 3. Propagar para todos os n
    return {n: base_result for n in range(3, n_initial + 1)}
```

### 4.4 Implementacao

| Componente | Descricao |
|-----------|-----------|
| `skills/proof-verifier/induction_verifier.py` | Motor de verificacao de inducao |
| Comando `/verify-induction` | Interface para o usuario |
| Integracao com P22 (ExhaustiveBase) | Caso base e delegado ao verificador exaustivo |

---

## 5. P22 — ExhaustiveBaseChecker: Verificacao Exaustiva de Casos Base

### 5.1 Conceito

Para $n$ pequeno (tipico $n \leq 5$), e possivel enumerar **todas** as configuracoes
de $n$ retas e verificar quais valores de $k$ sao viaveis. Isso fornece uma **verdade
computacional** que nao depende de nenhuma prova humana.

### 5.2 Algoritmo

```python
def exhaustive_check(n, max_k=None):
    """Enumera todas as configuracoes de n retas e retorna os k viaveis"""
    if max_k is None:
        max_k = n
    
    valid_k = set()
    
    # Gerar todas as combinacoes de n retas
    # (na pratica, usar heurísticas para reduzir o espaco de busca)
    
    for config in generate_all_configs(n):
        k = count_sunny(config)
        if covers_all_points(config, n) and k <= max_k:
            valid_k.add(k)
    
    return valid_k
```

### 5.3 Aplicacao ao Problema 1

Para $n=3$, o verificador exaustivo enumera:
- Todas as escolhas de 3 retas (horizontais, verticais, diagonais, ensolaradas)
- Para cada escolha, verifica se cobre $S_3$ (6 pontos)
- Conta $k$ (numero de ensolaradas)
- Resultado: $k \in \{0, 1, 3\}$

Este resultado e uma **verdade computacional** — nao depende de lemas, provas ou
raciocinio humano. E o "gold standard" contra o qual qualquer prova deve ser conferida.

### 5.4 Por Que Isso Teria Detectado o Erro

Se o ExhaustiveBaseChecker tivesse sido executado **antes** de construir a prova geral:

1. Para $n=3$: $k \in \{0, 1, 3\}$ (confirmado)
2. Para $n=4$: $k \in \{0, 1, 3\}$ (confirmado por busca)
3. A resposta $k \in \{0, 1, \dots, \lfloor(2n-1)/3\rfloor\}$ seria **imediatamente refutada** porque prediz $k=2$ para $n=4$, mas a busca exaustiva mostra que $k=2$ e impossivel.

### 5.5 Implementacao

| Componente | Descricao |
|-----------|-----------|
| `skills/proof-verifier/exhaustive_checker.py` | Motor de busca exaustiva |
| Comando `/exhaustive-check <n>` | Interface |
| Cache de resultados | `.evolve/exhaustive-cache.json` |

---

## 6. P23 — CrossReferenceValidator: Validacao contra Fontes Externas

### 6.1 Conceito

Antes de considerar uma prova como "validada", o sistema deve consultar **fontes
externas independentes** que possam ter resolvido o mesmo problema.

### 6.2 Fontes Configuradas

| Fonte | Tipo | Acesso |
|-------|------|--------|
| Evan Chen — IMO Solution Notes | PDF | `https://web.evanchen.cc/exams/` |
| Google DeepMind — IMO Solutions | PDF | `https://storage.googleapis.com/deepmind-media/gemini/` |
| AoPS (Art of Problem Solving) | Forum | `https://artofproblemsolving.com/community/c6h_imo` |
| arXiv | Preprints | `https://arxiv.org` |

### 6.3 Algoritmo

```python
def cross_validate(problem_id, claimed_answer):
    """Compara a resposta com fontes externas"""
    external_answers = []
    
    for source in SOURCES:
        answer = fetch_answer(source, problem_id)
        if answer:
            external_answers.append((source, answer))
    
    matches = [a for s, a in external_answers if a == claimed_answer]
    
    if not matches and external_answers:
        return {
            "status": "CONFLICT",
            "claimed": claimed_answer,
            "external_consensus": external_answers[0][1],
            "sources": external_answers
        }
    
    return {"status": "CONSISTENT", "matches": len(matches)}
```

### 6.4 Aplicacao ao Problema 1

Se o CrossReferenceValidator tivesse sido executado:

```
CONFLICT DETECTED:
  Claimed: k in {0, 1, 2, ..., floor((2n-1)/3)}
  Evan Chen: k in {0, 1, 3}
  DeepMind: k in {0, 1, 3}
  ACTION: Revisar prova antes de considerar validada
```

---

## 7. Integracao com o Ecossistema Existente

### 7.1 Pipeline de Verificacao Completo

```
Problema → [P23: CrossReference] → Alerta se conflito com fontes externas
         → [P22: ExhaustiveBase] → Verdade computacional para n pequeno
         → [P20: LemmaGraph]     → Construir grafo de dependencias
         → [P21: InductionCheck] → Verificar reducao/inducao
         → [V1-V6: Cora-Debate]  → Consistencia algebrica e numerica
         → Resultado final com indice de confianca
```

### 7.2 Novos Comandos Slash

| Comando | Componente | Acao |
|---------|-----------|------|
| `/lemma-graph` | P20 | Exibe grafo de dependencias entre lemas |
| `/lemma-verify <id>` | P20 | Verifica um lema especifico |
| `/verify-induction` | P21 | Verifica passo de inducao |
| `/exhaustive-check <n>` | P22 | Busca exaustiva para n pequeno |
| `/cross-ref <problem>` | P23 | Compara com fontes externas |
| `/proof-health` | P20-P23 | Indice de saude da prova (0-100) |

### 7.3 Indice de Confianca da Prova (Proof Confidence Index)

```python
def proof_confidence():
    score = 0
    
    # P23: Cross-reference (peso 30%)
    if cross_ref_status == "CONSISTENT":
        score += 30
    
    # P22: Base case exhaustivo (peso 25%)
    if exhaustive_base_passes:
        score += 25
    
    # P20: Lemma graph completo (peso 25%)
    score += 25 * (verified_lemmas / total_lemmas)
    
    # P21: Inducao verificada (peso 10%)
    if induction_verified:
        score += 10
    
    # V1-V6: Consistencia (peso 10%)
    score += 2 * cora_pass_count  # max 10 com 5 verificadores
    
    return min(score, 100)
```

---

## 8. Roadmap de Implementacao

| Fase | Componente | Esforco | Prazo |
|------|-----------|---------|-------|
| **Fase 1** | P22 (ExhaustiveBaseChecker) | 3 dias | Imediato |
| **Fase 2** | P23 (CrossReferenceValidator) | 2 dias | Imediato |
| **Fase 3** | P20 (LemmaGraph) | 5 dias | Q3 2026 |
| **Fase 4** | P21 (InductionVerifier) | 5 dias | Q3 2026 |
| **Fase 5** | Integracao com Cora-Debate | 3 dias | Q3 2026 |
| **Fase 6** | Proof Confidence Index | 2 dias | Q3 2026 |

---

## 9. O Que Faltou para os Multiagentes, Skills e Hooks

### 9.1 Diagnostico

| Componente | O que fez | O que faltou |
|-----------|-----------|-------------|
| **Agentes** (reasoning-orchestrator) | Selecionou 38 tipos de raciocinio | Nenhum raciocinio de **inducao/ reducao estrutural** |
| **Skills** (cora-debate) | Orquestrou verificacao V1-V6 | Nao verificou a **cadeia logica** entre lemas |
| **Hooks** (ecosystem-sync) | Sincronizou componentes | Nao sincronizou com **fontes externas** de verdade |
| **Plugins** (cora-qscore) | Selecionou debatedores | Nao selecionou **verificadores de prova** |
| **MCPs** (sequential-thinking) | Raciocinio em cadeia | Nao implementou **backtracking** quando um lema falha |

### 9.2 O Que os Agentes Deveriam Ter Feito (e Farao com P20-P23)

1. **Agente Indutor**: "Este problema admite reducao $n \to n-1$? Se sim, verifique o invariante."
2. **Agente BaseChecker**: "Para $n=3$, enumere TODAS as configuracoes. Nao confie em prova — verifique."
3. **Agente CrossReferencer**: "Consulte Evan Chen e DeepMind. A resposta confere?"
4. **Agente LemmaTracker**: "O Lema 2 depende do Lema 1? O Lema 1 foi provado? Se nao, Lema 2 e suspeito."
5. **Agente ContradictionDetector**: "O texto diz $|p+q|=1 \Rightarrow m \in \{0,\infty\}$ mas depois da $m=-2$ com $|p+q|=1$. Contradicao detectada."

---

> **Licao final**: A verificacao simbolica (V1-V6) e necessaria mas nao suficiente.
> A camada P20-P23 introduz o que realmente faltou: **verificacao da estrutura logica
> da prova**, nao apenas da consistencia das suas formulas.
