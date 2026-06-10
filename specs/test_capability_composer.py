#!/usr/bin/env python3
"""
test_capability_composer.py — SPEC-033: Composição Unitária do Conhecimento TDD Suite

8 Critical Tests:
  COMP-001: Validação sintática de CognitiveInput (tipo inválido rejeitado)
  COMP-002: Validação sintática de CapabilityUnit (frontier automático para vazio)
  COMP-003: Biblioteca carrega de JSON (cognitive_library.json)
  COMP-004: Validação semântica — inputs do template são relevantes ao domínio
  COMP-005: Bootstrap de evo-*.md extrai ferramentas e métodos
  COMP-006: Bootstrap de skills extrai ferramentas
  COMP-007: Unicidade de input_id (add duplicado --> ValueError)
  COMP-008: Serialização idempotente (to_dict --> from_dict --> to_dict)

Uso: python specs/test_capability_composer.py
"""

import json
import sys
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parent.parent
SCANNER_DIR = BASE_DIR / "skills" / "system" / "academic-audit"
sys.path.insert(0, str(SCANNER_DIR))

from capability_composer import (
    CognitiveInput,
    CapabilityUnit,
    InputNode,
    CognitiveLibrary,
    CapabilityComposer,
    COMPOSITION_TEMPLATES,
    VALID_INPUT_TYPES,
    create_composer_with_seed_library,
)


class CTResult:
    def __init__(self, ct_id: str, name: str, passed: bool,
                 detail: str = "", evidence: Any = None):
        self.ct_id = ct_id
        self.name = name
        self.passed = passed
        self.detail = detail
        self.evidence = evidence


# ═══════════════════════════════════════════════════════════════════════════
# CT IMPLEMENTATIONS
# ═══════════════════════════════════════════════════════════════════════════

def comp_001_validate_cognitive_input() -> CTResult:
    """COMP-001: CognitiveInput rejeita input_type inválido."""
    try:
        CognitiveInput(
            input_id="x.y",
            name="Teste",
            input_type="invalid_type",
            description="desc",
        )
        return CTResult("COMP-001", "CognitiveInput rejeita tipo inválido", False,
                        "Deveria ter levantado ValueError para input_type='invalid_type'")
    except ValueError as e:
        valid = "invalid_type" in str(e) and "input_type" in str(e)
        return CTResult("COMP-001", "CognitiveInput rejeita tipo inválido", valid,
                        str(e)[:120])


def comp_001b_validate_empty_input_id() -> CTResult:
    """COMP-001b: CognitiveInput rejeita input_id sem '.'."""
    try:
        CognitiveInput(
            input_id="sem_ponto",
            name="Teste",
            input_type="concept",
            description="desc",
        )
        return CTResult("COMP-001b", "CognitiveInput rejeita input_id sem ponto", False,
                        "Deveria ter levantado ValueError")
    except ValueError as e:
        return CTResult("COMP-001b", "CognitiveInput rejeita input_id sem ponto", True,
                        str(e)[:120])


def comp_001c_validate_all_types_accepted() -> CTResult:
    """COMP-001c: Todos os 6 tipos válidos são aceitos."""
    errors = []
    for t in sorted(VALID_INPUT_TYPES):
        try:
            CognitiveInput(
                input_id=f"{t}.teste",
                name=f"Teste {t}",
                input_type=t,
                description="desc",
            )
        except ValueError as e:
            errors.append(f"{t}: {e}")
    ok = len(errors) == 0
    return CTResult("COMP-001c", f"Todos os {len(VALID_INPUT_TYPES)} tipos aceitos", ok,
                    "; ".join(errors) if errors else f"{len(VALID_INPUT_TYPES)}/6 OK")


def comp_002_validate_capability_unit_empty() -> CTResult:
    """COMP-002: CapabilityUnit vazia => frontier=True, cost=1.0."""
    unit = CapabilityUnit(capability_id="teste.X", capability_name="Teste")
    if not unit.frontier:
        return CTResult("COMP-002", "CapabilityUnit vazia => frontier", False,
                        f"frontier={unit.frontier}, esperado=True")
    if unit.construction_cost != 1.0:
        return CTResult("COMP-002", "CapabilityUnit vazia => cost=1.0", False,
                        f"cost={unit.construction_cost}, esperado=1.0")
    return CTResult("COMP-002", "CapabilityUnit vazia => frontier=True, cost=1.0", True,
                    f"frontier={unit.frontier}, cost={unit.construction_cost}")


def comp_002b_validate_all_inputs() -> CTResult:
    """COMP-002b: CapabilityUnit.all_inputs combina todos os tipos."""
    unit = CapabilityUnit(
        capability_id="teste.Y",
        capability_name="Teste Y",
        concepts=["concept.a", "concept.b"],
        methods=["method.x"],
        tools=["tool.z"],
        external_domains=["domain.w"],
        validations=["valid.v"],
    )
    all_in = unit.all_inputs
    expected = 2 + 1 + 1 + 1 + 1  # 6 total
    if len(all_in) != expected:
        return CTResult("COMP-002b", "CapabilityUnit.all_inputs conta corretamente", False,
                        f"{len(all_in)} != {expected}")
    # Verifica que cada tipo está presente
    for iid in ["concept.a", "method.x", "tool.z", "domain.w", "valid.v"]:
        if iid not in all_in:
            return CTResult("COMP-002b", f"all_inputs contém {iid}", False, str(all_in))
    return CTResult("COMP-002b", "CapabilityUnit.all_inputs completo", True,
                    f"{len(all_in)} inputs em 5 categorias")


def comp_003_load_library_from_json() -> CTResult:
    """COMP-003: CognitiveLibrary carrega de JSON."""
    lib = CognitiveLibrary()
    json_path = SCANNER_DIR / "cognitive_library.json"
    if not json_path.exists():
        return CTResult("COMP-003", "Biblioteca JSON existe", False,
                        f"Arquivo não encontrado: {json_path}")

    count = lib.load_json(json_path)
    if count == 0:
        return CTResult("COMP-003", "Biblioteca carrega > 0 inputs", False,
                        f"Carregou {count} inputs")
    if lib.size != count:
        return CTResult("COMP-003", "lib.size == count carregado", False,
                        f"size={lib.size}, count={count}")

    # Verifica tipos presentes
    stats = lib.stats()
    types_present = set(stats.keys())
    min_expected = {"concept", "method", "tool", "external_domain", "validation"}
    missing = min_expected - types_present
    if missing:
        return CTResult("COMP-003", "Biblioteca tem todos os tipos esperados", False,
                        f"Faltando: {missing}. Stats: {stats}")

    return CTResult("COMP-003", f"Biblioteca carrega {count} inputs", True,
                    f"size={count}, tipos={sorted(types_present)}")


def comp_004_template_relevance() -> CTResult:
    """COMP-004: Templates geram inputs relevantes (cross-check com biblioteca)."""
    lib = CognitiveLibrary()
    json_path = SCANNER_DIR / "cognitive_library.json"
    if json_path.exists():
        lib.load_json(json_path)

    composer = CapabilityComposer(lib)

    # Testa 3 categorias diferentes
    test_cases = [
        ("metodos.Quantitativo experimental", "metodos"),
        ("raciocinio.Probabilístico", "raciocinio"),
        ("teoria_jogos.Equilíbrio de Nash", "teoria_jogos"),
    ]

    errors = []
    for cap_id, expected_cat in test_cases:
        unit = composer.decompose(cap_id)
        cat = composer._extract_category(cap_id)
        if cat != expected_cat:
            errors.append(f"{cap_id}: categoria={cat}, esperado={expected_cat}")
        if unit.frontier:
            errors.append(f"{cap_id}: frontier=True (template deveria ter coberto)")
        if unit.total_input_count == 0:
            errors.append(f"{cap_id}: 0 inputs gerados")

    ok = len(errors) == 0
    return CTResult("COMP-004", "Templates geram inputs para 3 categorias", ok,
                    "; ".join(errors) if errors else "3/3 categorias decompostas com sucesso")


def comp_005_bootstrap_from_evos() -> CTResult:
    """COMP-005: Bootstrap de evo-*.md extrai ferramentas e métodos."""
    evo_dir = BASE_DIR / "evolution"
    if not evo_dir.exists():
        return CTResult("COMP-005", "Diretório evolution/ existe", False,
                        f"Não encontrado: {evo_dir}")

    lib = CognitiveLibrary.bootstrap_from_evos(evo_dir)
    if lib.size == 0:
        return CTResult("COMP-005", "Bootstrap extrai > 0 inputs", False,
                        f"0 inputs extraídos de {evo_dir}")

    tools = lib.by_type("tool")
    methods = lib.by_type("method")

    # Deve ter pelo menos algumas ferramentas (websearch, code-runner, etc.)
    if len(tools) < 3:
        return CTResult("COMP-005", "Bootstrap extrai >= 3 tools", False,
                        f"Apenas {len(tools)} tools")

    return CTResult("COMP-005", f"Bootstrap extrai {lib.size} inputs de evo-*.md", True,
                    f"tools={len(tools)}, methods={len(methods)}, total={lib.size}")


def comp_006_bootstrap_from_skills() -> CTResult:
    """COMP-006: Bootstrap de skills extrai ferramentas."""
    skills_dir = BASE_DIR / "skills"
    if not skills_dir.exists():
        return CTResult("COMP-006", "Diretório skills/ existe", False,
                        f"Não encontrado: {skills_dir}")

    lib = CognitiveLibrary.bootstrap_from_skills(skills_dir, max_skills=20)
    if lib.size == 0:
        return CTResult("COMP-006", "Bootstrap extrai > 0 skills", False,
                        f"0 skills extraídas de {skills_dir}")

    tools = lib.by_type("tool")
    return CTResult("COMP-006", f"Bootstrap extrai {lib.size} skills", True,
                    f"tools={len(tools)}")


def comp_007_unique_input_id() -> CTResult:
    """COMP-007: add() com input_id duplicado --> ValueError."""
    lib = CognitiveLibrary()
    inp1 = CognitiveInput(
        input_id="concept.teste_unico",
        name="Teste Único",
        input_type="concept",
        description="Primeiro",
    )
    inp2 = CognitiveInput(
        input_id="concept.teste_unico",
        name="Teste Único Duplicado",
        input_type="concept",
        description="Segundo (duplicado)",
    )

    lib.add(inp1)
    try:
        lib.add(inp2)
        return CTResult("COMP-007", "add duplicado --> ValueError", False,
                        "Deveria ter levantado ValueError")
    except ValueError as e:
        return CTResult("COMP-007", "add duplicado --> ValueError", True, str(e)[:120])


def comp_007b_search_and_remove() -> CTResult:
    """COMP-007b: search e remove funcionam corretamente."""
    lib = CognitiveLibrary()
    inp = CognitiveInput(
        input_id="concept.busca_teste",
        name="Busca Teste",
        input_type="concept",
        description="Teste de busca e remoção",
    )
    lib.add(inp)

    # Search
    results = lib.search("busca")
    if len(results) != 1 or results[0].input_id != "concept.busca_teste":
        return CTResult("COMP-007b", "search encontra input", False,
                        f"results={[r.input_id for r in results]}")

    # Remove
    lib.remove("concept.busca_teste")
    if lib.has("concept.busca_teste"):
        return CTResult("COMP-007b", "remove deleta input", False,
                        "Input ainda existe após remove()")

    # Remove inexistente
    try:
        lib.remove("concept.inexistente")
        return CTResult("COMP-007b", "remove inexistente --> KeyError", False,
                        "Deveria ter levantado KeyError")
    except KeyError:
        pass

    return CTResult("COMP-007b", "search + remove funcionam", True, "OK")


def comp_008_serialization_idempotent() -> CTResult:
    """COMP-008: to_dict --> from_dict --> to_dict produz o mesmo JSON."""
    original = CognitiveInput(
        input_id="method.teste_serial",
        name="Teste Serialização",
        input_type="method",
        description="Teste de idempotência de serialização",
        maturity="established",
        references=["ref1", "ref2"],
        source="curated",
        validation_cts=["CT-001", "CT-002"],
    )

    d1 = original.to_dict()
    reconstructed = CognitiveInput.from_dict(d1)
    d2 = reconstructed.to_dict()

    # Compara campos
    diffs = []
    for key in d1:
        if d1[key] != d2.get(key):
            diffs.append(f"{key}: {d1[key]} != {d2.get(key)}")

    if diffs:
        return CTResult("COMP-008", "Serialização idempotente (CognitiveInput)", False,
                        "; ".join(diffs))

    # Testa também CapabilityUnit
    unit_original = CapabilityUnit(
        capability_id="teste.Z",
        capability_name="Teste Z",
        concepts=["concept.a"],
        methods=["method.b"],
        tools=["tool.c"],
        external_domains=["domain.d"],
        validations=["valid.e"],
        internal_deps={"concept.a": ["method.b"]},
        missing_inputs=["tool.inexistente"],
        construction_cost=0.33,
        frontier=False,
    )
    u1 = unit_original.to_dict()
    unit_reconstructed = CapabilityUnit.from_dict(u1)
    u2 = unit_reconstructed.to_dict()

    for key in u1:
        if u1[key] != u2.get(key):
            diffs.append(f"Unit.{key}: {u1[key]} != {u2.get(key)}")

    ok = len(diffs) == 0
    return CTResult("COMP-008", "Serialização idempotente (CognitiveInput + CapabilityUnit)", ok,
                    "; ".join(diffs) if diffs else "Ambos idempotentes")


def comp_008b_library_save_load_roundtrip() -> CTResult:
    """COMP-008b: save_json --> load_json produz mesma biblioteca."""
    lib1 = CognitiveLibrary()
    inp = CognitiveInput(
        input_id="concept.roundtrip",
        name="Roundtrip",
        input_type="concept",
        description="Teste de roundtrip da biblioteca",
    )
    lib1.add(inp)

    tmp_path = BASE_DIR / "specs" / "_test_roundtrip.json"
    try:
        lib1.save_json(tmp_path)
        lib2 = CognitiveLibrary()
        lib2.load_json(tmp_path)

        if lib2.size != lib1.size:
            return CTResult("COMP-008b", "Roundtrip: mesmo tamanho", False,
                            f"{lib2.size} != {lib1.size}")

        inp2 = lib2.get("concept.roundtrip")
        if inp2 is None:
            return CTResult("COMP-008b", "Roundtrip: input recuperado", False,
                            "get() retornou None")

        if inp2.name != inp.name or inp2.description != inp.description:
            return CTResult("COMP-008b", "Roundtrip: campos idênticos", False,
                            f"name={inp2.name}, desc={inp2.description[:30]}")

        return CTResult("COMP-008b", "save_json --> load_json roundtrip OK", True, "OK")
    finally:
        if tmp_path.exists():
            tmp_path.unlink()


# ═══════════════════════════════════════════════════════════════════════════
# RUNNER
# ═══════════════════════════════════════════════════════════════════════════

def run_all() -> tuple[list[CTResult], int, int]:
    cts = [
        comp_001_validate_cognitive_input(),
        comp_001b_validate_empty_input_id(),
        comp_001c_validate_all_types_accepted(),
        comp_002_validate_capability_unit_empty(),
        comp_002b_validate_all_inputs(),
        comp_003_load_library_from_json(),
        comp_004_template_relevance(),
        comp_005_bootstrap_from_evos(),
        comp_006_bootstrap_from_skills(),
        comp_007_unique_input_id(),
        comp_007b_search_and_remove(),
        comp_008_serialization_idempotent(),
        comp_008b_library_save_load_roundtrip(),
    ]
    passed = sum(1 for ct in cts if ct.passed)
    failed = sum(1 for ct in cts if not ct.passed)
    return cts, passed, failed


def main():
    import argparse
    parser = argparse.ArgumentParser(description="SPEC-033 TDD Suite")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    cts, passed, failed = run_all()

    if args.json:
        output = {
            "spec": "SPEC-033",
            "total": len(cts),
            "passed": passed,
            "failed": failed,
            "results": [
                {
                    "ct_id": ct.ct_id,
                    "name": ct.name,
                    "passed": ct.passed,
                    "detail": ct.detail,
                }
                for ct in cts
            ],
        }
        print(json.dumps(output, indent=2, ensure_ascii=False))
    else:
        print(f"\n{'='*80}")
        print(f"  SPEC-033 Composição Unitária do Conhecimento — TDD Suite")
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
