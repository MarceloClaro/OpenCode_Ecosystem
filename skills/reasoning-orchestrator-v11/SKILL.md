---
name: reasoning-orchestrator-v11
description: "Orquestrador de Raciocinio Multiagente v11.0 — 68 tipos de raciocinio em 12 categorias. Coordena agentes especializados (Inductor, BaseCase, Contradiction, LemmaTracker, CrossRef, StressTest, HypothesisTester, PrecedentAnalyzer, RiskAssessor, ProofHealth) em pipeline de 7 fases. Integrado com Cora-Debate V1-V6 para verificacao simbolica. Use para resolver problemas que exigem raciocinio cientifico verificavel com cadeia logica rastreavel."
version: 11.0.0
author: ecosystem
tags: [reasoning, proof, verification, multiagent, orchestration, taxonomy, pci]
compatibility: all models
dependencies:
  - cora-debate
  - agent-forum
  - swarm-review
  - sequential-thinking
---

# ReasoningOrchestrator v11.0 — Pipeline de Raciocinio Multiagente

## Visao Geral

O ReasoningOrchestrator v11.0 expande a versao anterior (v9, 38 raciocinios) para
**68 tipos de raciocinio em 12 categorias**, organizados em pipeline de 7 fases
sequenciais com verificacao cruzada entre agentes.

Diferentemente da v9 (que apenas catalogava raciocinios), a v11 **implementa agentes
concretos** para cada tipo de raciocinio, com:
- Dependencias explicitas entre agentes (LemmaGraph)
- Propagacao automatica de falhas
- Proof Confidence Index (PCI) de 0-100
- Integracao com Cora-Debate V1-V6 para consistencia algebrica

## Arquitetura

```
PROBLEMA
  │
  ├── FASE 1: FUNDACIONAL (R01-R05)
  │   └── NotationAgent, AbstractionAgent, DecompositionAgent
  │
  ├── FASE 2: INDUTIVA/REDUTIVA (R12-R16) ← NOVA
  │   └── InductorAgent, BaseCaseAgent, InvariantAgent
  │
  ├── FASE 3: DEDUTIVA (R06-R11)
  │   └── LemmaTrackerAgent, SilogisticAgent, BackwardChainAgent
  │
  ├── FASE 4: CONSTRUTIVA (R17-R21)
  │   └── ConstructorAgent, StressTestAgent
  │
  ├── FASE 5: REFUTACIONAL (R22-R26) ← NOVA
  │   └── ContradictionAgent, ContraexemploAgent, ConsistencyAgent
  │
  ├── FASE 6: VERIFICACIONAL (R27-R30)
  │   └── ExhaustiveAgent, CrossRefAgent, Cora-Debate V1-V6
  │
  └── FASE 7: META-COGNITIVA (R31-R34) ← NOVA
      └── ProofHealthAgent (PCI 0-100)
```

## Agentes Implementados

| Agente | Raciocinio | Arquivo |
|--------|-----------|---------|
| InductorAgent | R13 (Reducao Estrutural) | `agents/critical_agents.py` |
| BaseCaseAgent | R15 (Caso Base) | `agents/critical_agents.py` |
| ContraexemploAgent | R22 (Contraexemplo) | `agents/critical_agents.py` |
| ContradictionAgent | R24 (Contradicao Interna) | `agents/critical_agents.py` |
| StressTestAgent | R26 (Teste de Estresse) | `agents/critical_agents.py` |
| ExhaustiveAgent | R27 (Exaustao Computacional) | `agents/critical_agents.py` |
| CrossRefAgent | R28 (Cross-Reference) | `agents/critical_agents.py` |
| LemmaTrackerAgent | R31 (Dependencia Logica) | `agents/critical_agents.py` |
| HypothesisTester | R35 (Hipotetico-Dedutivo) | `agents/domain_agents.py` |
| PrecedentAnalyzer | R42 (Precedente-Analogico) | `agents/domain_agents.py` |
| RiskAssessor | R50 (Risco-Incerteza) | `agents/domain_agents.py` |
| ProofHealthAgent | R31+R32+R33 (PCI) | `agents/domain_agents.py` |

## Comandos Slash

| Comando | Acao |
|---------|------|
| `/reason <problema>` | Executa pipeline completo de raciocinio |
| `/lemma-graph` | Exibe grafo de dependencias entre lemas |
| `/pci` | Calcula Proof Confidence Index (0-100) |
| `/cross-ref <id>` | Compara resposta com fontes externas |
| `/stress-test <n>` | Testa construcao para n especifico |
| `/exhaustive <n>` | Busca exaustiva para n pequeno |

## Integracao com Cora-Debate

A camada V1-V6 (Cora-Debate) opera na Fase 6, verificando consistencia algebrica
e numerica das conclusoes dos agentes das Fases 1-5. A camada P20-P23 opera nas
Fases 2, 5, 6, e 7, verificando a ESTRUTURA LOGICA da prova.

## Referencias

| Arquivo | Conteudo |
|---------|----------|
| `agents/framework.py` | Framework base + registro dos 68 raciocinios |
| `agents/critical_agents.py` | 8 agentes criticos (prova matematica) |
| `agents/domain_agents.py` | 4 agentes de dominio (cientifico, juridico, economico) |
| `TAXONOMIA_RACIOCINIOS.md` | Taxonomia original (34 raciocinios, 7 categorias) |
| `TAXONOMIA_RACIOCINIOS_AMPLIADA.md` | Taxonomia ampliada (68 raciocinios, 12 categorias, 58 refs) |
