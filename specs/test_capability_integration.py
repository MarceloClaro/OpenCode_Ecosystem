#!/usr/bin/env python3
"""
test_capability_integration.py — SPEC-035: Integração Composição Unitária ao Pipeline TDD Suite

6 Critical Tests:
  INT-001: CapabilityNode.composition populado após pipeline
  INT-002: EvolutionaryScenario.required_inputs preenchido
  INT-003: MCSP com construction_cost via solve_with_composer()
  INT-004: Desconto por inputs compartilhados reduz custo total
  INT-005: EvolutionaryRoadmap inclui capability_units + total_construction_cost
  INT-006: Pipeline completo sem erro (NooScan -> TeloScan -> Compose -> CrossVal -> MCSP)

Uso: python specs/test_capability_integration.py
"""

import json
import sys
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parent.parent
SCANNER_DIR = BASE_DIR / "skills" / "system" / "academic-audit"
sys.path.insert(0, str(SCANNER_DIR))

from capability_composer import (
    CognitiveInput, CapabilityUnit, CognitiveLibrary, CapabilityComposer,
)
from cross_validation_engine import CapabilityNode, CrossValidationEngine
from minimum_capability_solver import (
    MinimumCapabilitySolver, MCSPSolution, build_mock_engine,
)
from noological_scanner import NoologicalScanner


class CTResult:
    def __init__(self, ct_id: str, name: str, passed: bool,
                 detail: str = "", evidence: Any = None):
        self.ct_id = ct_id; self.name = name; self.passed = passed
        self.detail = detail; self.evidence = evidence


# ═══════════════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════════════

class MockAuditTrail:
    def __init__(self, text: str = ""):
        self.paragraphs = {}
        self.citation_map = []

    class MockParagraph:
        def __init__(self, t): self.text = t


def make_rich_audit_trail():
    """Cria audit trail com texto cobrindo múltiplas dimensões."""
    trail = MockAuditTrail()
    trail.paragraphs = {
        "p1": MockAuditTrail.MockParagraph(
            "Este estudo utiliza métodos quantitativos experimentais com randomização "
            "e grupo controle. A análise estatística emprega regressão linear, ANOVA "
            "e correlação de Pearson. O desenho fatorial 2x2 considera interações "
            "entre tratamento e gênero. Dados longitudinais foram coletados ao longo "
            "de 24 meses com follow-up trimestral. A população do estudo inclui "
            "participantes de contexto clínico e comunitário."
        ),
        "p2": MockAuditTrail.MockParagraph(
            "Do ponto de vista epistemológico, adotamos um paradigma pragmatista "
            "com métodos mistos sequenciais. A teoria dos jogos informa a análise "
            "de interações estratégicas entre agentes, incluindo equilíbrio de Nash "
            "e jogos evolutivos. O raciocínio contrafactual é usado para modelar "
            "cenários alternativos. A abordagem sistêmica considera múltiplos níveis "
            "de análise: individual, organizacional e político."
        ),
        "p3": MockAuditTrail.MockParagraph(
            "Realizamos meta-análise de 47 estudos anteriores e revisão sistemática "
            "da literatura. Dados comparativos cross-cultural incluem amostras do "
            "Brasil, México e Índia. A neurociência cognitiva fornece o referencial "
            "teórico para interpretar os mecanismos subjacentes."
        ),
    }
    trail.citation_map = ["doi:10.1000/test.001", "doi:10.1000/test.002"]
    return trail


# ═══════════════════════════════════════════════════════════════════════════
# CT IMPLEMENTATIONS
# ═══════════════════════════════════════════════════════════════════════════

def int_001_capability_node_composition() -> CTResult:
    """INT-001: CapabilityNode.composition é populado após decomposição."""
    # Carrega biblioteca
    lib = CognitiveLibrary()
    lib_path = SCANNER_DIR / "cognitive_library.json"
    if lib_path.exists():
        lib.load_json(lib_path)

    composer = CapabilityComposer(lib)

    # Cria CapabilityNode e associa composição
    node = CapabilityNode(
        name="Quantitativo experimental",
        domain="metodos",
        category="Quantitativo experimental",
    )

    unit = composer.decompose("metodos.Quantitativo experimental")
    node.composition = unit

    if node.composition is None:
        return CTResult("INT-001", "CapabilityNode.composition populado", False,
                        "composition é None")
    if node.composition.frontier:
        return CTResult("INT-001", "CapabilityNode.composition não-frontier", False,
                        "frontier=True inesperado")
    if node.composition.total_input_count == 0:
        return CTResult("INT-001", "CapabilityNode.composition tem inputs", False,
                        "0 inputs")

    return CTResult("INT-001", "CapabilityNode.composition populado", True,
                    f"{node.composition.total_input_count} inputs, cost={node.composition.construction_cost}")


def int_002_evolutionary_scenario_required_inputs() -> CTResult:
    """INT-002: EvolutionaryScenario.required_inputs preenchido."""
    from evolutionary_pipeline import EvolutionaryScenario

    # Cria cenário com required_inputs populado
    scenario = EvolutionaryScenario(
        category="Quantitativo experimental",
        domain="metodos",
        scenario_type="foundation",
        priority_score=0.85,
        cascade_impact=3.0,
        prerequisites=[],
        required_inputs=["concept.causalidade", "method.randomizacao",
                        "knowledge_base.artigos_cientificos"],
    )

    if len(scenario.required_inputs) == 0:
        return CTResult("INT-002", "required_inputs preenchido", False,
                        "Lista vazia")
    if len(scenario.required_inputs) != 3:
        return CTResult("INT-002", "required_inputs tem 3 elementos", False,
                        f"{len(scenario.required_inputs)} elementos")

    return CTResult("INT-002", "EvolutionaryScenario.required_inputs preenchido", True,
                    f"{len(scenario.required_inputs)} inputs: {scenario.required_inputs}")


def int_003_mcsp_with_construction_cost() -> CTResult:
    """INT-003: MCSP solve_with_composer usa construction_cost real."""
    lib = CognitiveLibrary()
    lib_path = SCANNER_DIR / "cognitive_library.json"
    if lib_path.exists():
        lib.load_json(lib_path)

    composer = CapabilityComposer(lib)

    # Grafo simples: A requer B, ambos são targets
    nodes = {"metodos.A", "raciocinio.B"}
    edges = [("metodos.A", "raciocinio.B", "requires", 0.8)]
    engine = build_mock_engine(nodes, edges)

    solver = MinimumCapabilitySolver()
    solver.load_from_engine(engine)

    present = set()
    targets = {"metodos.A", "raciocinio.B"}

    # Sem composer
    sol_no_composer = solver.solve(present, targets)

    # Com composer (construction_cost)
    sol_with_composer = solver.solve_with_composer(present, targets, composer)

    if sol_with_composer.minimum_set.cost == sol_no_composer.minimum_set.cost:
        return CTResult("INT-003", "MCSP com composer tem custo diferente", False,
                        f"Ambos={sol_no_composer.minimum_set.cost}")

    # Verifica que o custo com composer é mais informativo
    if sol_with_composer.minimum_set.cost > 1.0 or sol_with_composer.minimum_set.cost < 0.0:
        return CTResult("INT-003", "MCSP cost entre 0 e 1", False,
                        f"cost={sol_with_composer.minimum_set.cost}")

    return CTResult("INT-003", "MCSP com construction_cost integrado", True,
                    f"sem_composer={sol_no_composer.minimum_set.cost}, "
                    f"com_composer={sol_with_composer.minimum_set.cost}")


def int_004_shared_inputs_discount() -> CTResult:
    """INT-004: Inputs compartilhados reduzem custo total."""
    lib = CognitiveLibrary()
    lib_path = SCANNER_DIR / "cognitive_library.json"
    if lib_path.exists():
        lib.load_json(lib_path)

    composer = CapabilityComposer(lib)

    # Decompõe 3 capacidades da mesma categoria (compartilham inputs)
    cap_ids = [
        "metodos.Quantitativo experimental",
        "metodos.Quantitativo correlacional",
        "metodos.Meta-analise",
    ]
    units = composer.decompose_many(cap_ids)

    # Custo individual somado
    individual_sum = sum(u.construction_cost for u in units.values())

    # Custo com compartilhamento
    shared_cost = composer.compute_total_construction_cost(units)

    if shared_cost >= individual_sum:
        return CTResult("INT-004", "shared_cost < individual_sum", False,
                        f"shared={shared_cost}, individual_sum={individual_sum}")

    # Verifica que há inputs compartilhados
    input_nodes = composer.compute_shared_inputs(units)
    shared_count = sum(1 for n in input_nodes.values() if len(n.shared_by) > 1)

    if shared_count == 0:
        return CTResult("INT-004", "Inputs compartilhados detectados", False,
                        "0 inputs compartilhados")

    return CTResult("INT-004", "Desconto por inputs compartilhados", True,
                    f"shared_cost={shared_cost}, individual_sum={individual_sum}, "
                    f"shared_inputs={shared_count}")


def int_005_roadmap_includes_capability_units() -> CTResult:
    """INT-005: EvolutionaryRoadmap inclui capability_units + total_construction_cost."""
    from evolutionary_pipeline import EvolutionaryRoadmap

    lib = CognitiveLibrary()
    lib_path = SCANNER_DIR / "cognitive_library.json"
    if lib_path.exists():
        lib.load_json(lib_path)
    composer = CapabilityComposer(lib)

    # Decompõe algumas capacidades
    cap_ids = ["metodos.Quantitativo experimental", "raciocinio.Probabilistico"]
    units = composer.decompose_many(cap_ids)
    total_cost = composer.compute_total_construction_cost(units)

    roadmap = EvolutionaryRoadmap(
        noological_coverage=0.65,
        teleological_score=0.72,
        bottlenecks=["raciocinio.Probabilistico"],
        analogies=[],
        scenarios=[],
        routes=[],
        total_gaps=2,
        quick_wins=1,
        foundations=1,
        frontiers=0,
        convergents=0,
        capability_units=list(units.values()),
        total_construction_cost=total_cost,
    )

    if len(roadmap.capability_units) != 2:
        return CTResult("INT-005", "capability_units tem 2 elementos", False,
                        f"{len(roadmap.capability_units)}")

    if roadmap.total_construction_cost == 0.0 and total_cost > 0.0:
        return CTResult("INT-005", "total_construction_cost != 0", False,
                        f"roadmap={roadmap.total_construction_cost}, computed={total_cost}")

    # Verifica que as units têm os campos esperados
    for unit in roadmap.capability_units:
        if not hasattr(unit, 'concepts') or not hasattr(unit, 'construction_cost'):
            return CTResult("INT-005", "capability_units são CapabilityUnit", False,
                            f"Tipo: {type(unit).__name__}")

    return CTResult("INT-005", "Roadmap inclui capability_units + cost", True,
                    f"units={len(roadmap.capability_units)}, cost={roadmap.total_construction_cost}")


def int_006_full_pipeline_no_error() -> CTResult:
    """INT-006: Pipeline completo sem erro (Noo -> Telo -> Compose -> CrossVal -> MCSP)."""
    from teleological_scanner import TeleologicalReverseScanner, TeleologicalGoal
    from evolutionary_pipeline import EvolutionaryScannerPipeline

    # Prepara entrada
    trail = make_rich_audit_trail()
    goals = [
        TeleologicalGoal("Efeito causal de X sobre Y", "causal", 1.0),
        TeleologicalGoal("Explorar fenômeno Z em profundidade", "exploratory", 0.8),
    ]

    try:
        # Pipeline completo
        pipeline = EvolutionaryScannerPipeline()
        roadmap = pipeline.scan(trail, goals, domain="psicologia")

        # Verificações básicas
        checks = []
        if not hasattr(roadmap, 'capability_units'):
            checks.append("roadmap.capability_units ausente")
        if not hasattr(roadmap, 'total_construction_cost'):
            checks.append("roadmap.total_construction_cost ausente")
        if roadmap.total_gaps == 0:
            checks.append("total_gaps=0 (esperado >0)")

        # Verifica se algum cenário tem required_inputs
        has_inputs = any(len(s.required_inputs) > 0 for s in roadmap.scenarios)
        if not has_inputs and roadmap.total_gaps > 0:
            checks.append("Nenhum cenário tem required_inputs (composição não fluiu)")

        if checks:
            return CTResult("INT-006", "Pipeline completo sem erro", False,
                            "; ".join(checks))

        return CTResult("INT-006", "Pipeline completo integrado", True,
                        f"gaps={roadmap.total_gaps}, units={len(roadmap.capability_units)}, "
                        f"cost={roadmap.total_construction_cost}, "
                        f"scenarios_with_inputs={sum(1 for s in roadmap.scenarios if s.required_inputs)}")

    except Exception as e:
        return CTResult("INT-006", "Pipeline completo sem erro", False,
                        f"Exception: {type(e).__name__}: {str(e)[:150]}")


# ═══════════════════════════════════════════════════════════════════════════
# RUNNER
# ═══════════════════════════════════════════════════════════════════════════

def run_all() -> tuple[list[CTResult], int, int]:
    cts = [
        int_001_capability_node_composition(),
        int_002_evolutionary_scenario_required_inputs(),
        int_003_mcsp_with_construction_cost(),
        int_004_shared_inputs_discount(),
        int_005_roadmap_includes_capability_units(),
        int_006_full_pipeline_no_error(),
    ]
    passed = sum(1 for ct in cts if ct.passed)
    failed = sum(1 for ct in cts if not ct.passed)
    return cts, passed, failed


def main():
    import argparse
    parser = argparse.ArgumentParser(description="SPEC-035 Integration TDD Suite")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    cts, passed, failed = run_all()

    if args.json:
        output = {
            "spec": "SPEC-035",
            "total": len(cts),
            "passed": passed,
            "failed": failed,
            "results": [
                {"ct_id": ct.ct_id, "name": ct.name, "passed": ct.passed, "detail": ct.detail}
                for ct in cts
            ],
        }
        print(json.dumps(output, indent=2, ensure_ascii=False))
    else:
        print(f"\n{'='*80}")
        print(f"  SPEC-035 Integracao Composicao Unitária ao Pipeline — TDD Suite")
        print(f"  \033[92mPASS: {passed}\033[0m  |  \033[91mFAIL: {failed}\033[0m  |  Total: {len(cts)}")
        print(f"{'='*80}\n")
        for ct in cts:
            status = "\033[92mPASS\033[0m" if ct.passed else "\033[91mFAIL\033[0m"
            print(f"  [{status}] {ct.ct_id}: {ct.name}")
            if ct.detail:
                print(f"       {ct.detail}")
        print(f"\n{'='*80}")
        if failed == 0:
            print(f"  RESULTADO: \033[92m[APROVADO]\033[0m  |  {passed}/{len(cts)} (100%)")
        else:
            print(f"  RESULTADO: \033[91m[{failed} FALHAS]\033[0m  |  {passed}/{len(cts)} ({passed*100//len(cts)}%)")
        print(f"{'='*80}\n")

    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
