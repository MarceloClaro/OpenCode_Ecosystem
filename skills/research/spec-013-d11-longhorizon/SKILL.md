---
name: spec-013-d11-longhorizon
description: "Suite TDD para D11 (Raciocinio de Longo Horizonte em DAG) do CORA-Eval. 150 CTs em 5 dominios (Logica, Matematica, Planejamento, Fluxo de Codigo, Cientifico) x 4 niveis (N1-N4). Validacao via pytest com engine DAG propria. Use quando precisar validar raciocinio de longo horizonte com propagacao em grafos aciclicos dirigidos."
spec: "SPEC-013"
version: "1.0"
category: research
tags: [cora-eval, d11, longhorizon, dag, raciocinio-estendido]
dependencies: [CORA-Eval]
tdd_suite: "artigo/evaluations/tests/test_d11_longhorizon.py"
ct_count: 150
status: active
---

# SPEC-013 — Suite D11: Raciocínio de Longo Horizonte (DAG)

## Objetivo
Validar a capacidade de raciocínio de longo horizonte em grafos acíclicos
dirigidos (DAG), onde cada nó individual é tratável mas a propagação
correta através do grafo exige raciocínio estendido.

## Fundamento Teórico
Inspirado por "The Power of Reasoning in Long-Horizon Tasks" (2604.14140v1),
que demonstra que tarefas DAG com nós de baixa dificuldade individual
exigem raciocínio de horizonte estendido para propagação correta.

## CTs (150 tarefas, 5 domínios × 4 níveis)

### Distribuição

| Domínio | N1 | N2 | N3 | N4 | Total |
|---------|----|----|----|----|-------|
| Lógica (DAG-L) | 5 | 7 | 8 | 10 | 30 |
| Matemática (DAG-M) | 5 | 7 | 8 | 10 | 30 |
| Planejamento (DAG-P) | 5 | 7 | 8 | 10 | 30 |
| Fluxo de Código (DAG-C) | 5 | 7 | 8 | 10 | 30 |
| Científico (DAG-S) | 5 | 7 | 8 | 10 | 30 |
| **Total** | **25** | **35** | **40** | **50** | **150** |

### N1 — Básico (DAGs de 2-3 nós)
Propagação booleana (AND, OR, NOT), expressões aritméticas simples,
cadeias de dependência linear, árvores de expressão.

### N2 — Graduação (DAGs de 4-6 nós)
Implicação multi-nível, operações matriciais encadeadas,
alocação de recursos, fluxo de controle condicional.

### N3 — Pós-Graduação (DAGs de 7-10 nós)
Satisfatibilidade booleana, composição funcional aninhada,
satisfação de restrições, propagação de parâmetros multi-etapa.

### N4 — Pesquisa (DAGs de 11-20 nós)
Lógica de predicados com quantificadores, cadeias de prova,
planejamento temporal interdependente, execução simbólica multi-módulo.

## Execução
```bash
cd artigo/evaluations/tests
python -m pytest test_d11_longhorizon.py -v
```

## Integração CORA-Eval
D11 é a décima primeira dimensão do CORA-Eval, focada em raciocínio
de longo horizonte. Peso: 7%. Verificadores: V1-V7.
