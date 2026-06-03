# Phase 3 SDD: Multi-Agent Proof Orchestration Pipeline

## 1. Visão Geral
Orquestração de múltiplos agentes especializados + raciocínios formais + MCPs para validação robusta de provas matemáticas contra benchmark IMO real.

**Objetivos**:
- Escalar V7 Verifier com debate estruturado (Cora-Debate V1-V7)
- Integrar ReasoningOrchestrator-v11 (68 tipos de raciocínio)
- Usar MCPs para enriquecimento (busca de literatura, símbolos, contexto)
- TDD + SDD em todo o pipeline

---

## 2. Arquitetura de Agentes

```
[IMO Problem] 
    ↓
[1. Prover Agent]        → Gera múltiplas provas (estratégias diferentes)
    ↓
[2. Verifier Agent V7]   → Avalia cada prova (D11Assessment)
    ↓
[3. Cora-Debate Forum]   → Debate entre V1-V7 verificadores
    ├─ V1: Rigor Matemático
    ├─ V2: Elegância
    ├─ V3: Clareza Pedagógica
    ├─ V4: Compacidade
    ├─ V5: Inovação
    ├─ V6: Completude
    └─ V7: Síntese (Nash Solver)
    ↓
[4. Reasoning Orchestrator V11] → 68 raciocínios em 12 categorias
    ├─ Lógica (5 tipos)
    ├─ Dialética (5 tipos)
    ├─ Teoria dos Jogos (10 tipos)
    ├─ Decisão (5 tipos)
    ├─ Estratégia (5 tipos)
    └─ Inovação (8 tipos)
    ↓
[5. Refiner Agent]       → Melhora prova com feedback
    ↓
[6. MCP Enrichment]      → Busca literatura, símbolos, contexto
    ├─ scihub-mcp (papers)
    ├─ websearch-mcp (documentação)
    ├─ code-runner-mcp (validação simbólica)
    └─ sequential-thinking-mcp (raciocínio profundo)
    ↓
[Final D11 + Reasoning Report] → JSON export
```

---

## 3. Interfaces & Contratos (TDD)

### 3.1 ProverAgent
```python
class ProverAgent:
    def generate_proofs(
        self, 
        problem: IMOProblem, 
        num_strategies: int = 3
    ) -> List[ProofAttempt]:
        """Gerar múltiplas provas com estratégias diferentes"""
        # Estratégia 1: Direto (forward)
        # Estratégia 2: Por contradição
        # Estratégia 3: Indução/Recursão
        ...
```

### 3.2 DebateArena (Cora-Debate)
```python
class DebateArena:
    def orchestrate_debate(
        self,
        proof: ProofAttempt,
        verifiers: List[VerifierAgent],  # V1-V7
        reasoning_orchestrator: ReasoningOrchestratorV11
    ) -> DebateResult:
        """
        4 fases:
        OPEN → DISCUSS → SYNTHESIZE → CONCLUDE
        """
        ...
```

### 3.3 RefinementAgent
```python
class RefinementAgent:
    def refine_proof(
        self,
        proof: ProofAttempt,
        debate_feedback: DebateResult,
        mcp_enrichment: Dict
    ) -> ImprovedProof:
        """Refinar prova com feedback do debate + MCPs"""
        ...
```

---

## 4. Raciocínios Integrados (ReasoningOrchestrator-v11)

| Categoria | Tipos | Aplicação |
|-----------|-------|-----------|
| **Lógica** | 5 | Validação de passos (válido/inválido) |
| **Dialética** | 5 | Debate V1-V7 (tese/antítese/síntese) |
| **Teoria dos Jogos** | 10 | Seleção de estratégia de prova (minimax) |
| **Decisão** | 5 | Escolha entre múltiplas provas |
| **Estratégia** | 5 | Planejamento de refinamento |
| **Inovação** | 8 | Descoberta de novas técnicas |

---

## 5. MCPs Integrados

| MCP | Função |
|-----|--------|
| **scihub-mcp** | Buscar papers relacionados ao problema |
| **websearch-mcp** | Contexto histórico, soluções conhecidas |
| **code-runner-mcp** | Validação simbólica com SymPy/Sage |
| **sequential-thinking-mcp** | Raciocínio profundo multi-turno |
| **memory-mcp** | Persistência de insights |

---

## 6. Pipeline de Dados

```
IMO Problem (JSON)
    ↓ [ProverAgent]
ProofAttempt[] (3-5 estratégias)
    ↓ [VerifierV7]
D11Assessment[] (elegância, clareza, etc.)
    ↓ [DebateArena + ReasoningOrchestrator]
DebateResult (4 fases OASC)
    ↓ [RefinementAgent + MCPs]
ImprovedProof + EnrichmentData
    ↓ [Final Report]
{
  problem_id: "PB-Basic-001",
  original_proof_d11: 3.99,
  debate_insights: [...],
  reasoning_applied: [68 tipos],
  mcp_enrichment: {...},
  final_d11: 7.45,
  status: "ELEGANT"
}
```

---

## 7. Casos de Teste (TDD)

### Test 1: ProverAgent gera 3+ estratégias distintas
```python
def test_prover_generates_multiple_strategies(problem: IMOProblem):
    agent = ProverAgent()
    proofs = agent.generate_proofs(problem, num_strategies=3)
    assert len(proofs) >= 3
    assert len(set(p.strategy for p in proofs)) == 3
```

### Test 2: DebateArena executa 4 fases (OASC)
```python
def test_debate_arena_4_phases(proof: ProofAttempt):
    arena = DebateArena(verifiers=V1_TO_V7)
    result = arena.orchestrate_debate(proof, ...)
    assert result.phases == ["OPEN", "DISCUSS", "SYNTHESIZE", "CONCLUDE"]
```

### Test 3: RefinementAgent melhora D11 score
```python
def test_refinement_improves_score(proof: ProofAttempt, debate: DebateResult):
    agent = RefinementAgent(mcps=[scihub, websearch, code_runner])
    improved = agent.refine_proof(proof, debate, ...)
    assert improved.d11_score > proof.d11_score
```

### Test 4: ReasoningOrchestrator seleciona raciocínios apropriados
```python
def test_reasoning_selection(proof: ProofAttempt, problem: IMOProblem):
    ro = ReasoningOrchestratorV11()
    reasoning_selected = ro.select_reasoning(proof, problem)
    assert len(reasoning_selected) >= 5  # Mínimo 5 tipos
```

---

## 8. Benchmarking

- **Dataset**: 60 problemas IMO-ProofBench v2 (GitHub google-deepmind/superhuman)
- **Validação**: Correlação D11 final vs IMO difficulty (esperado: r > 0.7)
- **Tempo**: <5s por prova (all-in)
- **Recall**: 90%+ de provas melhoradas

---

## 9. Constraints & Decisions

- **Windows cp1252**: Sem emojis/Unicode especial em prints
- **Async**: MCPs em paralelo (asyncio)
- **Persistência**: JSON export de cada estágio
- **Auditoria**: Cada decisão de agente registrada

