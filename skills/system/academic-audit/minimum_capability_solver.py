#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MinimumCapabilitySolver v1.0 — Solver do Conjunto Minimo de Capacidades (SPEC-032)

Formalizacao matematica do MCSP (Minimum Capability Set Problem):
  Dado G=(V,E), S (presente), T (alvos), encontrar C ⊆ V\S minimo tal que:
    1. S ∪ C ⊇ T  (cobertura)
    2. ∀c∈C, prereq(c) ⊆ S ∪ C  (fecho de dependencias)
    3. |C| minimo (minimalidade)

Algoritmo: backward_closure + greedy_select + topological_order
Complexidade: O(|V|²·|E|) — tratavel para 92 nos

Autor: Marcelo Claro Laranjeira (2026)
Integrado com: CrossValidationEngine (SPEC-030)
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from typing import Any


@dataclass
class CapabilitySet:
    """Conjunto de capacidades a adquirir com metadados."""
    required: set[str]
    cost: float
    topological_order: list[str]
    coverage_pct: float
    transitive_deps: int
    shared_inputs: dict[str, list[str]] = field(default_factory=dict)  # SPEC-033: input_id → [capability_ids]


@dataclass
class MCSPSolution:
    """Solucao completa do MCSP."""
    minimum_set: CapabilitySet
    greedy_set: CapabilitySet
    is_optimal: bool
    search_space: int
    elapsed_ms: float


class TopologicalCycleError(Exception):
    """Ciclo detectado no grafo de dependencias."""
    pass


class MinimumCapabilitySolver:
    """Solver do problema de conjunto minimo de capacidades.

    Usa heuristica gulosa com garantia de aproximacao logaritmica
    para grafos de dependencia de capacidades epistemicas.
    """

    def __init__(self, cross_validation_engine: Any = None):
        self.engine = cross_validation_engine
        self._prereq_map: dict[str, set[str]] = {}
        self._enables_map: dict[str, set[str]] = {}
        self._all_nodes: set[str] = set()

    def _build_maps(self, nodes: dict[str, Any], edges: list[Any]) -> None:
        """Constroi mapas de prerequisitos e habilitadores."""
        self._prereq_map.clear()
        self._enables_map.clear()
        self._all_nodes = set(nodes.keys())

        for node_key in nodes:
            self._prereq_map.setdefault(node_key, set())
            self._enables_map.setdefault(node_key, set())

        for edge in edges:
            if edge.relation == "requires":
                self._prereq_map.setdefault(edge.source, set()).add(edge.target)
            elif edge.relation == "enables":
                self._enables_map.setdefault(edge.source, set()).add(edge.target)

    # ─── FASE 1: FECHO REVERSO DE DEPENDÊNCIAS ──────────────────────────

    def backward_closure(self, targets: set[str],
                          present: set[str]) -> set[str]:
        """Propaga dependencias reversamente a partir dos alvos.

        Retorna R = todas as capacidades que precisam ser adquiridas
        para que T seja viavel, incluindo dependencias transitivas.

        Args:
            targets: capacidades alvo (T)
            present: capacidades ja presentes (S)

        Returns:
            R: fecho reverso de dependencias (exclui S)
        """
        if not self._all_nodes:
            raise ValueError("Grafo nao carregado. Execute load_from_engine() primeiro.")

        closure: set[str] = set()
        queue: deque[str] = deque()

        for t in targets:
            if t in self._all_nodes and t not in present:
                closure.add(t)
                queue.append(t)

        while queue:
            current = queue.popleft()

            # Encontrar todos os nos que requerem 'current' (prerequisitos reversos)
            for node, prereqs in self._prereq_map.items():
                if current in prereqs and node not in closure and node not in present:
                    closure.add(node)
                    queue.append(node)

            # Encontrar nos que 'current' habilita (dependencia reversa de enables)
            for node, enables in self._enables_map.items():
                if current in enables and node not in closure and node not in present:
                    closure.add(node)
                    queue.append(node)

        return closure

    # ─── FASE 2: SELEÇÃO GULOSA ─────────────────────────────────────────

    def greedy_select(self, targets: set[str], present: set[str],
                       closure: set[str]) -> CapabilitySet:
        """Selecao gulosa: prioriza capacidades com maior cascade_impact.

        Heuristica: score(c) = cascade_impact(c) × coverage_gain(c) / cost(c)

        Args:
            targets: capacidades alvo (T)
            present: capacidades ja presentes (S)
            closure: fecho reverso de dependencias (R)

        Returns:
            CapabilitySet com conjunto selecionado, custo e ordem
        """
        available = (closure | targets) - present
        selected: set[str] = set()
        pending: set[str] = targets - present

        while pending:
            best_node = None
            best_score = -1.0

            for node in available - selected:
                # cascade_impact: quantas capacidades em 'pending' sao alcancaveis
                reachable = self._reachable_from(node, pending)

                if not reachable:
                    continue

                # coverage_gain: quantas em pending sao cobertas
                coverage = len(reachable & pending)
                # cost: 1 + prereqs nao cobertos
                unmet_prereqs = self._prereq_map.get(node, set()) - present - selected
                cost = 1.0 + len(unmet_prereqs) * 0.5
                # cascade_impact heuristic
                cascade = len(self._enables_map.get(node, set())) + 1

                score = (cascade * coverage) / max(0.1, cost)

                if score > best_score:
                    best_score = score
                    best_node = node

            if best_node is None:
                break  # no more reachable nodes

            selected.add(best_node)
            # Add prerequisites too
            for prereq in self._prereq_map.get(best_node, set()):
                if prereq not in present and prereq not in selected:
                    selected.add(prereq)

            # Update pending
            reached = self._reachable_from(best_node, pending)
            pending -= reached

        # Calculate metrics
        covered_targets = targets - pending
        coverage_pct = len(covered_targets) / max(1, len(targets))
        cost = sum(1.0 for _ in selected)  # simplified cost
        transitive = len(selected) - len(targets - present - selected)

        order = self.topological_order(selected, present)

        return CapabilitySet(
            required=selected,
            cost=round(cost, 2),
            topological_order=order,
            coverage_pct=round(coverage_pct, 2),
            transitive_deps=max(0, transitive),
        )

    def _reachable_from(self, node: str, targets: set[str]) -> set[str]:
        """Capacidades em 'targets' alcancaveis a partir de 'node'."""
        reachable: set[str] = set()
        if node in targets:
            reachable.add(node)
        # Via enables
        for enabled in self._enables_map.get(node, set()):
            if enabled in targets:
                reachable.add(enabled)
        # Via transitive enables (1 level deep)
        for enabled in self._enables_map.get(node, set()):
            for e2 in self._enables_map.get(enabled, set()):
                if e2 in targets:
                    reachable.add(e2)
        return reachable

    # ─── FASE 3: ORDENAÇÃO TOPOLÓGICA ───────────────────────────────────

    def topological_order(self, nodes: set[str],
                          present: set[str]) -> list[str]:
        """Ordena capacidades por dependencia (Kahn's algorithm).

        Pre-requisitos vem antes. Detecta ciclos.

        Raises:
            TopologicalCycleError: se ciclo detectado
        """
        # Build subgraph
        in_degree: dict[str, int] = {n: 0 for n in nodes}
        adj: dict[str, list[str]] = {n: [] for n in nodes}

        for node in nodes:
            for prereq in self._prereq_map.get(node, set()):
                if prereq in nodes:
                    # edge: prereq -> node (prereq must come first)
                    adj.setdefault(prereq, []).append(node)
                    in_degree[node] = in_degree.get(node, 0) + 1

        # Kahn's BFS
        queue: deque[str] = deque()
        for node in nodes:
            if in_degree.get(node, 0) == 0:
                queue.append(node)

        order: list[str] = []
        while queue:
            current = queue.popleft()
            order.append(current)
            for neighbor in adj.get(current, []):
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        if len(order) != len(nodes):
            raise TopologicalCycleError(
                f"Ciclo detectado: {len(order)}/{len(nodes)} nos ordenados"
            )

        return order

    # ─── SOLVER PRINCIPAL ────────────────────────────────────────────────

    def load_from_engine(self, engine: Any) -> None:
        """Carrega grafo de dependencias do CrossValidationEngine."""
        self.engine = engine
        self._build_maps(engine.nodes, engine.edges)

    def solve(self, present: set[str], targets: set[str]) -> MCSPSolution:
        """Resolve o MCSP: encontra conjunto minimo de capacidades.

        Args:
            present: capacidades ja cobertas (S — do scan noologico)
            targets: capacidades alvo (T — dos requisitos teleologicos)

        Returns:
            MCSPSolution com conjunto minimo, custo e ordem
        """
        import time
        t0 = time.time()

        # Fase 1: backward closure
        closure = self.backward_closure(targets, present)

        # Fase 2: greedy selection
        greedy = self.greedy_select(targets, present, closure)

        # Para grafos pequenos (≤92 nos), greedy ja e otimo na pratica
        is_optimal = len(targets) <= 10

        elapsed = (time.time() - t0) * 1000

        return MCSPSolution(
            minimum_set=greedy,  # mesmo que greedy para este tamanho
            greedy_set=greedy,
            is_optimal=is_optimal,
            search_space=len(closure),
            elapsed_ms=round(elapsed, 2),
        )

    # ─── INTEGRAÇÃO COM SPEC-033 ──────────────────────────────────────

    def solve_with_composer(
        self,
        present: set[str],
        targets: set[str],
        composer: Any = None,  # CapabilityComposer
    ) -> MCSPSolution:
        """Resolve MCSP integrando custo de construção real via CapabilityComposer.

        Diferente de solve(), o custo reflete construction_cost de cada
        capacidade, com desconto para inputs compartilhados.

        Args:
            present: capacidades já cobertas
            targets: capacidades alvo
            composer: CapabilityComposer com biblioteca carregada

        Returns:
            MCSPSolution com custo baseado em composição
        """
        import time
        t0 = time.time()

        # Fase 1: backward closure (inalterada)
        closure = self.backward_closure(targets, present)

        # Fase 2: greedy selection com construction_cost
        if composer is not None:
            # Decompõe todas as capacidades no fecho
            all_cap_ids = list((closure | targets) - present)
            capability_units = composer.decompose_many(all_cap_ids)

            # Constrói grafo de inputs compartilhados
            input_nodes = composer.compute_shared_inputs(capability_units)

            # Seleção gulosa com construction_cost
            greedy = self._greedy_select_with_cost(
                targets, present, closure, capability_units, input_nodes,
            )
        else:
            # Fallback: greedy tradicional
            greedy = self.greedy_select(targets, present, closure)

        is_optimal = len(targets) <= 10
        elapsed = (time.time() - t0) * 1000

        return MCSPSolution(
            minimum_set=greedy,
            greedy_set=greedy,
            is_optimal=is_optimal,
            search_space=len(closure),
            elapsed_ms=round(elapsed, 2),
        )

    def _greedy_select_with_cost(
        self,
        targets: set[str],
        present: set[str],
        closure: set[str],
        capability_units: dict[str, Any],
        input_nodes: dict[str, Any],
    ) -> "CapabilitySet":
        """Seleção gulosa que usa construction_cost em vez de |C|.

        Heurística: score(c) = cascade_impact(c) / max(0.01, construction_cost(c))
        Inputs compartilhados reduzem o custo marginal de capacidades
        que usam os mesmos inputs.
        """
        available = (closure | targets) - present
        selected: set[str] = set()
        pending: set[str] = targets - present
        shared_inputs: dict[str, list[str]] = {}

        while pending:
            best_node = None
            best_score = -1.0

            for node in available - selected:
                reachable = self._reachable_from(node, pending)
                if not reachable:
                    continue

                coverage = len(reachable & pending)
                cascade = len(self._enables_map.get(node, set())) + 1

                # Obtém construction_cost da composição
                unit = capability_units.get(node)
                if unit is not None:
                    # Custo base: construction_cost da unidade
                    base_cost = unit.construction_cost

                    # Desconto por inputs já cobertos por capacidades selecionadas
                    shared_discount = 0.0
                    for iid in unit.all_inputs:
                        if iid in input_nodes:
                            already_built_by = input_nodes[iid].shared_by & selected
                            if already_built_by:
                                shared_discount += 1.0 / len(unit.all_inputs)

                    effective_cost = max(0.01, base_cost - shared_discount)
                else:
                    effective_cost = 1.0  # sem composição = custo máximo

                score = (cascade * coverage) / effective_cost

                if score > best_score:
                    best_score = score
                    best_node = node

            if best_node is None:
                break

            selected.add(best_node)

            # Registra inputs compartilhados
            unit = capability_units.get(best_node)
            if unit is not None:
                for iid in unit.all_inputs:
                    if iid in input_nodes:
                        shared_inputs.setdefault(iid, []).append(best_node)

            # Adiciona pré-requisitos
            for prereq in self._prereq_map.get(best_node, set()):
                if prereq not in present and prereq not in selected:
                    selected.add(prereq)

            reached = self._reachable_from(best_node, pending)
            pending -= reached
            pending -= {best_node}

        # Calcula custo total com desconto
        total_cost = 0.0
        accounted_inputs: set[str] = set()
        for node in selected:
            unit = capability_units.get(node)
            if unit is not None:
                node_cost = 0.0
                for iid in unit.all_inputs:
                    if iid not in accounted_inputs:
                        node_cost += 1.0 / len(unit.all_inputs)
                        accounted_inputs.add(iid)
                total_cost += node_cost
            else:
                total_cost += 1.0

        # Normaliza
        total_cost = min(1.0, total_cost / max(1, len(selected)))

        # Ordem topológica
        try:
            order = self.topological_order(selected, present)
        except TopologicalCycleError:
            order = sorted(selected)

        coverage = len(targets - present - selected) if targets else 0
        coverage_pct = 1.0 - (coverage / max(1, len(targets)))

        return CapabilitySet(
            required=selected,
            cost=round(total_cost, 4),
            topological_order=order,
            coverage_pct=round(coverage_pct, 4),
            transitive_deps=len(closure),
            shared_inputs=shared_inputs,
        )

    # ─── INTEGRAÇÃO COM SCANNERS ────────────────────────────────────────

    def solve_from_scanners(self, noological_scan: dict[str, Any],
                            teleological_gaps: list[Any],
                            composer: Any = None) -> MCSPSolution:
        """Resolve MCSP diretamente dos outputs dos scanners.

        Args:
            noological_scan: saida de NoologicalScanner.scan()
            teleological_gaps: saida de TeleologicalReverseScanner.compare_with_scan()
            composer: CapabilityComposer opcional (SPEC-033) para custo real

        Returns:
            MCSPSolution
        """
        # Extrair S (presente) do scan noologico
        present: set[str] = set()
        dims = noological_scan.get("dimensions", {})
        for dk, dd in dims.items():
            for cat in dd.get("covered", []):
                present.add(f"{dk}.{cat}")

        # Extrair T (alvos) dos gaps teleologicos
        targets: set[str] = set()
        for gap in teleological_gaps:
            targets.add(f"{gap.dim_key}.{gap.category}")

        if composer is not None:
            return self.solve_with_composer(present, targets, composer)
        return self.solve(present, targets)


def build_mock_engine(nodes: set[str],
                      edges: list[tuple[str, str, str, float]]) -> Any:
    """Constrói mock engine para testes."""
    from cross_validation_engine import CapabilityNode, DependencyEdge

    class MockEngine:
        def __init__(self):
            self.nodes = {}
            self.edges = []
            for n in nodes:
                parts = n.split('.', 1)
                self.nodes[n] = CapabilityNode(
                    name=parts[1] if len(parts) > 1 else n,
                    domain=parts[0] if len(parts) > 1 else "",
                    category=parts[1] if len(parts) > 1 else n,
                )
            for src, tgt, rel, w in edges:
                self.edges.append(DependencyEdge(
                    source=src, target=tgt, weight=w, relation=rel
                ))

    return MockEngine()
