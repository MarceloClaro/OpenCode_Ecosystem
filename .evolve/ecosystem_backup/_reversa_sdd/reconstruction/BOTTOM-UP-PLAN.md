# Plano Bottom-Up de Reimplementacao — OpenCode Ecosystem

> **Gerado por:** Reversa (reconstructor)
> **Data:** 2026-05-15
> **Baseado em:** Engenharia reversa completa (100% confianca, 12/12 lacunas resolvidas)
> **Estrategia:** Strangler Fig Pattern — substituicao incremental, sem Big Bang

---

## Sumario Executivo

O OpenCode e um ecossistema de **~865 arquivos**, **12 modulos**, **118 agentes** e **97+ skills**.
A refatoracao do `core/` (singleton → DI) ja foi aplicada. Este plano cobre a reimplementacao
completa do ecossistema em **6 camadas**, do alicerce as aplicacoes.

**Esforco total estimado:** ~120h distribuídas | **Risco geral:** 🟡 Medio

---

## Camada 0: Foundation (core/) — JA CONCLUIDO

### Status: Fase 1-2 aplicadas | Fase 3 consumidores migrada | Fase 4 limpeza pendente

### O que foi feito
- core/interfaces.py — Interfaces abstratas IStateManager, IEventBus
- core/container.py — Container DI thread-safe
- core/state.py — SQLiteStateManager implementa IStateManager (refatorado)
- core/events.py — AsyncEventBus implementa IEventBus (refatorado)
- core/__init__.py — initialize_core() como entry point explicito
- core/mock_services.py — MockStateManager, MockEventBus para testes
- core/state_manager.py — UnifiedStateManager proxy (BOM UTF-8 fixado)
- tests/core/ — 18 arquivos de teste criados

### Pendente: Limpeza Fase 4
- Remover backup core.backup.20260510212614/
- Verificar from core import state_manager restantes
- Rodar suite completa de testes

---

## Camada 1: Infrastructure (plugins/, commands/, agents/)

### Prioridade: ALTA | Esforco: 20h | Risco: Medio
### Depende de: core/ (pronto)

### 1.1 plugins/
- Extrair interfaces TS para plugins/interfaces.ts (2h)
- Adicionar testes unitarios Bun (4h)
- Separar logica de validacao ciclica (2h)
- Adicionar health check endpoint (1h)
- Documentar API em ADR-010 (1h)

### 1.2 commands/
- Mapear todos os 14 comandos (1h)
- Criar dispatcher unificado (3h)
- Adicionar testes de integracao (2h)
- Documentar em ADR-011 (1h)

### 1.3 agents/
- Validar frontmatter YAML de todos os agentes (1h)
- Agrupar agentes por funcao (1h)
- Criar registro central agents/registry.json (2h)

---

## Camada 2: Skills & Knowledge (skills/, evolution/)

### Prioridade: ALTA | Esforco: 15h | Risco: Medio
### Depende de: core/, plugins/

### 2.1 skills/
- Indexar skills com metadados (3h)
- Classificar por categoria (2h)
- Verificar progressive disclosure < 2.5KB (2h)
- Detectar orfas/duplicadas (1h)
- Criar indice navegavel (2h)

### 2.2 evolution/
- Consolidar metadados dos 8 rounds (1h)
- Extrair padroes cross-round (2h)
- Criar dashboard de scores 85→98 (2h)
- Documentar gatilhos para evo-9 (1h)

---

## Camada 3: Orchestration (nexus/)

### Prioridade: ALTA | Esforco: 25h | Risco: Alto
### Depende de: core/, plugins/, commands/

### 3.1 Nucleo Nexus
- Refatorar sync_orchestrator para DI (4h)
- Refatorar self_healer para DI (3h)
- Refatorar evolution_loop para DI (2h)
- Refatorar context_offload para DI (3h)
- Adicionar testes para cada script (8h)
- Testes de integracao L0-L6 (5h)

### 3.2 Micro-Reasoning
- Refatorar micro_reasoning_types.py (2h)
- Refatorar meta_orchestrator.py (3h)
- Refatorar auto_swarm_builder.py (2h)
- Testar 120+ sync barriers (4h)

---

## Camada 4: Research (basis-research/SEEKER, docling/)

### Prioridade: Media | Esforco: 20h | Risco: Medio
### Depende de: core/, nexus/

### 4.1 SEEKER
- Extrair interfaces dos 12 agentes (3h)
- Refatorar LLM Router para DI (2h)
- Refatorar Argument Tree (2h)
- Adicionar testes de pipeline (4h)
- Documentar em ADR-012 (1h)

### 4.2 Docling
- Implementar DoclingBackend (IBM Docling SDK + PyMuPDF) (3h)
- Implementar ScrapingBackend fallback (2h)
- Criar fabrica de backends (1h)
- Testar com PDFs reais (3h)

---

## Camada 5: Production (criador-artigo/MASWOS, quantum/)

### Prioridade: Media | Esforco: 25h | Risco: Alto
### Depende de: core/, nexus/, SEEKER

### 5.1 MASWOS
- Refatorar executor.py para DI (4h)
- Refatorar seeker_bridge.py (2h)
- Refatorar iterative_correction_loop (3h)
- Refatorar auto_score_qualis.py (2h)
- Refatorar ptbr_corrector.py (1h)
- Testar pipeline completo (6h)
- Validar com artigo real (4h)

### 5.2 Quantum
- Refatorar quantum_vqc.py (2h)
- Separar simulacao do frontend (2h)
- Adicionar testes de circuito (3h)
- Refatorar frontend React (3h)

---

## Camada 6: External Tools (editais-br/)

### Prioridade: Baixa | Esforco: 15h | Risco: Medio
### Depende de: Nenhuma (projeto externo independente)

- Mapear API FastAPI + OpenAPI (2h)
- Refatorar extractors HTML/PDF (3h)
- Adicionar testes de integracao (4h)
- Atualizar Dockerfile/docker-compose (2h)
- Mover para workspace como submódulo (4h)

---

## Roadmap Consolidado

Fase 0: Foundation (core/) --- JA CONCLUIDO
Fase 1: Infrastructure ------ ALTA - 20h - plugins/, commands/, agents/
Fase 2: Skills ------------- ALTA - 15h - skills/, evolution/
Fase 3: Orchestration ------ ALTA - 25h - nexus/
Fase 4: Research ----------- MEDIA - 20h - SEEKER, docling/
Fase 5: Production --------- MEDIA - 25h - MASWOS, quantum/
Fase 6: External ----------- BAIXA - 15h - editais-br/

Total estimado: ~120h | Risco geral: Medio

---

## Matriz de Riscos

| Risco | Prob. | Impacto | Fase | Mitigacao |
|-------|:-----:|:-------:|:----:|-----------|
| Nexus quebra com DI | Media | Alto | 3 | Validar cada script individualmente |
| MASWOS 49 agentes fragil | Media | Alto | 5 | Testar pipeline completo primeiro |
| Skills externas nao indexaveis | Media | Medio | 2 | Indexar apenas as 97 core |
| Bun runtime incompativel | Baixa | Alto | 1 | Verificar bun version match |
| Dependencia circular core↔nexus | Media | Medio | 3 | Interfaces quebram o ciclo |

---

## Metricas de Sucesso

| Criterio | Atual | Alvo | Medicao |
|----------|:-----:|:----:|---------|
| Cobertura de testes core/ | ~0% | >=90% | pytest --cov=core |
| Cobertura de testes nexus/ | ~0% | >=70% | pytest --cov=nexus |
| Cobertura de testes plugins/ | 0% | >=60% | bun test --coverage |
| Modulos usando DI | 1/12 | 12/12 | grep "resolve(" |
| ADRs registrados | 8 | 12 | ls _reversa_sdd/adrs/ |
| Testes rodando em CI | 0 | >=50 | pytest exit code |

---

*Plano gerado pelo Reversa (reconstructor) — 2026-05-15*
