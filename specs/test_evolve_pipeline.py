#!/usr/bin/env python3
"""
test_evolve_pipeline.py — SPEC-026: Evolve Pipeline TDD Suite

10 Critical Tests (CTs) para validar o pipeline evolutivo SENSE→DISCOVER→
INSTALL→VERIFY→EVOLVE→LEARN do ecossistema OpenCode.

Uso:
    python specs/test_evolve_pipeline.py
    python specs/test_evolve_pipeline.py --json    # saída JSON

CTs:
    CT-001: SENSE   — installed.json é JSON válido
    CT-002: SENSE   — memory.json tem healthHistory
    CT-003: VERIFY  — todos SKILL.md têm frontmatter (SPEC-025)
    CT-004: VERIFY  — zero caracteres CJK em SKILL.md
    CT-005: EVOLVE  — evolution/*.md têm frontmatter
    CT-006: EVOLVE  — installed.json sem órfãos ativos
    CT-007: LEARN   — observability.jsonl é JSONL válido
    CT-008: MANUS   — manus-state.json (se existe) é válido
    CT-009: MANUS   — bridge Python importa sem erro
    CT-010: SENSE   — estrutura de diretórios completa
"""

import json
import os
import re
import sys
import subprocess
from pathlib import Path
from typing import Any

# ─── Config ──────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
EVOLVE_DIR = BASE_DIR / ".evolve"
SKILLS_DIR = BASE_DIR / "skills"
EVOLUTION_DIR = BASE_DIR / "evolution"
SPECS_DIR = BASE_DIR / "specs"
PLUGINS_DIR = BASE_DIR / "plugins"

CJK_RANGES = [
    (0x4E00, 0x9FFF),   # CJK Unified Ideographs
    (0x3400, 0x4DBF),   # CJK Unified Ideographs Extension A
    (0xF900, 0xFAFF),   # CJK Compatibility Ideographs
    (0x2F800, 0x2FA1F), # CJK Compatibility Ideographs Supplement
]


def has_cjk(text: str) -> bool:
    """Detecta caracteres CJK em texto."""
    for ch in text:
        cp = ord(ch)
        for lo, hi in CJK_RANGES:
            if lo <= cp <= hi:
                return True
    return False


def parse_frontmatter(content: str) -> tuple[str, dict[str, str]]:
    """Parse minimalista de frontmatter YAML (stdlib puro)."""
    text = content.lstrip('\ufeff')
    if not text.startswith('---'):
        return text, {}
    end = text.find('---', 3)
    if end == -1:
        return text, {}
    fm_text = text[3:end].strip()
    meta: dict[str, str] = {}
    for line in fm_text.split('\n'):
        line = line.strip()
        if ':' in line:
            key, _, val = line.partition(':')
            key = key.strip()
            val = val.strip().strip('"').strip("'")
            meta[key] = val
    return text[end+3:], meta


# ─── CT Implementations ──────────────────────────────────────────────────

class CTResult:
    def __init__(self, ct_id: str, name: str, passed: bool, detail: str = "",
                 evidence: Any = None):
        self.ct_id = ct_id
        self.name = name
        self.passed = passed
        self.detail = detail
        self.evidence = evidence


def ct001_sense_installed_json() -> CTResult:
    """CT-001: installed.json é JSON válido com campo 'skills' e 'timestamp'."""
    path = EVOLVE_DIR / "installed.json"
    if not path.exists():
        return CTResult("CT-001", "SENSE: installed.json existe",
                        False, f"Arquivo não encontrado: {path}")
    try:
        with open(path, 'r', encoding='utf-8-sig') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        return CTResult("CT-001", "SENSE: installed.json é JSON válido",
                        False, f"JSON inválido: {e}")
    skills = data.get("skills", [])
    ts = data.get("timestamp", "")
    if not isinstance(skills, list):
        return CTResult("CT-001", "SENSE: installed.json.skills é array",
                        False, f"skills não é array: {type(skills)}")
    if not ts:
        return CTResult("CT-001", "SENSE: installed.json.timestamp presente",
                        False, "timestamp vazio ou ausente")
    return CTResult("CT-001", "SENSE: installed.json válido", True,
                    f"{len(skills)} skills, timestamp={ts}", skills)


def ct002_sense_memory_health() -> CTResult:
    """CT-002: memory.json tem healthHistory com ao menos 1 score."""
    path = EVOLVE_DIR / "memory.json"
    if not path.exists():
        return CTResult("CT-002", "SENSE: memory.json existe",
                        False, f"Arquivo não encontrado: {path}")
    try:
        with open(path, 'r', encoding='utf-8-sig') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        return CTResult("CT-002", "SENSE: memory.json é JSON válido",
                        False, f"JSON inválido: {e}")
    history = data.get("healthHistory", [])
    if not history:
        return CTResult("CT-002", "SENSE: memory.json.healthHistory não vazio",
                        False, "healthHistory vazio")
    scores = [h.get("score") for h in history if "score" in h]
    if not scores:
        return CTResult("CT-002", "SENSE: healthHistory contém scores",
                        False, "Nenhum score encontrado")
    return CTResult("CT-002", "SENSE: memory.json healthHistory válido", True,
                    f"{len(history)} entradas, score atual={data.get('healthScore')}",
                    {"count": len(history), "current": data.get("healthScore")})


def ct003_verify_frontmatter() -> CTResult:
    """CT-003: test_frontmatter_validator.py --summary retorna 100% PASS."""
    script = SPECS_DIR / "test_frontmatter_validator.py"
    if not script.exists():
        return CTResult("CT-003", "VERIFY: validador frontmatter existe",
                        False, f"Script não encontrado: {script}")
    try:
        result = subprocess.run(
            [sys.executable, str(script), '--json'],
            capture_output=True, text=True, timeout=60, cwd=str(BASE_DIR)
        )
    except subprocess.TimeoutExpired:
        return CTResult("CT-003", "VERIFY: validador dentro do timeout",
                        False, "Timeout 60s excedido")
    except Exception as e:
        return CTResult("CT-003", "VERIFY: validador executável",
                        False, f"Erro: {e}")

    # Parse output — the script prints summary to stdout
    stdout = result.stdout
    pass_match = re.search(r'PASS:\s*(\d+)', stdout)
    fail_match = re.search(r'FAIL:\s*(\d+)', stdout)
    total_match = re.search(r'Total:\s*(\d+)', stdout)

    if not pass_match or not fail_match:
        return CTResult("CT-003", "VERIFY: saída parseável do validador",
                        False, f"STDOUT:\n{stdout[:300]}\n\nSTDERR:\n{result.stderr[:300]}")

    passes = int(pass_match.group(1))
    fails = int(fail_match.group(1))
    total = int(total_match.group(1)) if total_match else passes + fails

    if fails > 0:
        return CTResult("CT-003", "VERIFY: 100%% frontmatter válido",
                        False, f"{fails} falhas em {total} skills")

    return CTResult("CT-003", "VERIFY: 100%% frontmatter válido", True,
                    f"{passes}/{total} PASS", {"pass": passes, "total": total})


def ct004_verify_no_cjk() -> CTResult:
    """CT-004: Nenhum SKILL.md contém caracteres CJK."""
    violations: list[str] = []
    skill_files = list(SKILLS_DIR.rglob("SKILL.md"))
    if not skill_files:
        return CTResult("CT-004", "VERIFY: SKILL.md encontrados",
                        False, "Nenhum SKILL.md encontrado em skills/")

    for skill_path in skill_files:
        try:
            with open(skill_path, 'r', encoding='utf-8-sig') as f:
                content = f.read()
        except Exception:
            continue
        if has_cjk(content):
            rel = skill_path.relative_to(BASE_DIR)
            violations.append(str(rel))

    if violations:
        return CTResult("CT-004", "VERIFY: zero CJK em SKILL.md", False,
                        f"{len(violations)} violações", violations[:10])

    return CTResult("CT-004", "VERIFY: zero CJK em SKILL.md", True,
                    f"{len(skill_files)} skills verificadas, 0 CJK")


def ct005_evolve_evolution_frontmatter() -> CTResult:
    """CT-005: evolution/evo-*.md têm frontmatter com name e description."""
    evo_files = list(EVOLUTION_DIR.glob("evo-*.md"))
    if not evo_files:
        return CTResult("CT-005", "EVOLVE: evolution/ tem arquivos",
                        False, "Nenhum evo-*.md encontrado")

    failures: list[str] = []
    for evo_path in evo_files:
        try:
            with open(evo_path, 'r', encoding='utf-8-sig') as f:
                content = f.read()
        except Exception:
            failures.append(f"{evo_path.name}: erro de leitura")
            continue

        text_after, meta = parse_frontmatter(content)
        if not meta:
            failures.append(f"{evo_path.name}: sem frontmatter")
            continue
        if 'name' not in meta:
            failures.append(f"{evo_path.name}: falta name")
        if 'description' not in meta:
            failures.append(f"{evo_path.name}: falta description")

    if failures:
        return CTResult("CT-005", "EVOLVE: evolution/*.md frontmatter", False,
                        f"{len(failures)} problemas", failures)

    return CTResult("CT-005", "EVOLVE: evolution/*.md frontmatter OK", True,
                    f"{len(evo_files)} arquivos válidos")


def ct006_evolve_no_orphans() -> CTResult:
    """CT-006: installed.json sem órfãos ativos (status != orphan-404)."""
    path = EVOLVE_DIR / "installed.json"
    if not path.exists():
        return CTResult("CT-006", "EVOLVE: installed.json existe",
                        False, f"Arquivo não encontrado: {path}")
    try:
        with open(path, 'r', encoding='utf-8-sig') as f:
            data = json.load(f)
    except json.JSONDecodeError:
        return CTResult("CT-006", "EVOLVE: installed.json parseável",
                        False, "JSON inválido")

    skills = data.get("skills", [])
    orphans = [s for s in skills if s.get("status") == "orphan-404"]
    active_orphans = [s for s in orphans if s.get("action") != "remove-next"]

    if active_orphans:
        return CTResult("CT-006", "EVOLVE: zero órfãos ativos", False,
                        f"{len(active_orphans)} órfãos sem action=remove-next",
                        active_orphans)

    return CTResult("CT-006", "EVOLVE: órfãos controlados", True,
                    f"Total: {len(skills)} skills, {len(orphans)} órfãos (todos com action=remove-next)")


def ct007_learn_observability_jsonl() -> CTResult:
    """CT-007: ecosystem-observability.jsonl é JSONL válido."""
    path = EVOLVE_DIR / "ecosystem-observability.jsonl"
    if not path.exists():
        return CTResult("CT-007", "LEARN: observability.jsonl existe",
                        False, f"Arquivo não encontrado: {path}")

    total = 0
    parse_errors = 0
    empty_lines = 0
    required_fields = ["timestamp", "event", "tool"]
    missing_fields_errors = 0

    try:
        with open(path, 'r', encoding='utf-8-sig') as f:
            for i, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    empty_lines += 1
                    continue
                total += 1
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    parse_errors += 1
                    continue
                for field in required_fields:
                    if field not in obj:
                        missing_fields_errors += 1
                        break
    except Exception as e:
        return CTResult("CT-007", "LEARN: observability.jsonl legível", False,
                        f"Erro de leitura: {e}")

    if parse_errors > 0:
        return CTResult("CT-007", "LEARN: linhas JSON válidas", False,
                        f"{parse_errors}/{total} erros de parse")

    if missing_fields_errors > 0:
        return CTResult("CT-007", "LEARN: campos obrigatórios presentes", False,
                        f"{missing_fields_errors} linhas sem campos required")

    return CTResult("CT-007", "LEARN: observability JSONL válido", True,
                    f"{total} eventos, {empty_lines} linhas vazias")


def ct008_manus_state_valid() -> CTResult:
    """CT-008: manus-state.json (se existe) é JSON válido com estrutura esperada.
    
    Aceita dois formatos:
    - Formato Plugin: {rounds, version, evolutionScore, ...}  (ManusEvolve v2.2)
    - Formato Bridge: {versao, ecossistema, evolucao, bridge, qualidade}  (Self-Healer/Bridge)
    """
    path = EVOLVE_DIR / "manus-state.json"
    if not path.exists():
        return CTResult("CT-008", "MANUS: manus-state.json existe",
                        True, "Arquivo nao encontrado — pode nao ter sido gerado ainda (skip, nao erro)")

    try:
        with open(path, 'r', encoding='utf-8-sig') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        return CTResult("CT-008", "MANUS: manus-state.json é JSON válido",
                        False, f"JSON inválido: {e}")

    # Check for Plugin format (ManusEvolve v2.2+)
    has_plugin_format = all(k in data for k in ("rounds", "version", "evolutionScore"))
    # Check for Bridge format (Self-Healer / older)
    has_bridge_format = all(k in data for k in ("versao", "ecossistema", "evolucao"))

    if has_plugin_format:
        return CTResult("CT-008", "MANUS: manus-state.json válido (plugin)", True,
                        f"rounds={len(data['rounds'])}, version={data['version']}, score={data['evolutionScore']}")
    elif has_bridge_format:
        evo = data.get("evolucao", {})
        eco = data.get("ecossistema", {})
        return CTResult("CT-008", "MANUS: manus-state.json válido (bridge)", True,
                        f"versao={data['versao']}, ciclos={evo.get('ciclos_executados', '?')}, skills={eco.get('skills', '?')}")
    else:
        missing_plugin = [k for k in ("rounds", "version", "evolutionScore") if k not in data]
        missing_bridge = [k for k in ("versao", "ecossistema", "evolucao") if k not in data]
        return CTResult("CT-008", "MANUS: manus-state.json estrutura", False,
                        f"Nem formato plugin ({', '.join(missing_plugin)}) nem bridge ({', '.join(missing_bridge)})")


def ct009_manus_bridge_importable() -> CTResult:
    """CT-009: manus_evolve_bridge.py é importável (sintaxe Python válida)."""
    path = BASE_DIR / "nexus" / "scripts" / "manus_evolve_bridge.py"
    if not path.exists():
        return CTResult("CT-009", "MANUS: bridge.py existe",
                        False, f"Arquivo não encontrado: {path}")

    try:
        with open(path, 'r', encoding='utf-8-sig') as f:
            source = f.read()
        compile(source, str(path), 'exec')
    except SyntaxError as e:
        return CTResult("CT-009", "MANUS: bridge.py compila sem erro", False,
                        f"SyntaxError: {e}")
    except Exception as e:
        return CTResult("CT-009", "MANUS: bridge.py legível", False,
                        f"Erro: {e}")

    return CTResult("CT-009", "MANUS: bridge.py sintaxe Python OK", True,
                    f"{len(source)} bytes, {source.count(chr(10))} linhas")


def ct010_sense_structure_complete() -> CTResult:
    """CT-010: Todos os diretórios críticos do pipeline existem."""
    required = {
        ".evolve": EVOLVE_DIR,
        "evolution": EVOLUTION_DIR,
        "skills": SKILLS_DIR,
        "specs": SPECS_DIR,
        "plugins": PLUGINS_DIR,
    }
    missing = [name for name, path in required.items() if not path.exists()]

    if missing:
        return CTResult("CT-010", "SENSE: estrutura de diretórios completa",
                        False, f"Faltam: {', '.join(missing)}")

    return CTResult("CT-010", "SENSE: estrutura de diretórios completa", True,
                    f"{len(required)} diretórios presentes")


# ─── Runner ──────────────────────────────────────────────────────────────

CT_LIST = [
    ct001_sense_installed_json,
    ct002_sense_memory_health,
    ct003_verify_frontmatter,
    ct004_verify_no_cjk,
    ct005_evolve_evolution_frontmatter,
    ct006_evolve_no_orphans,
    ct007_learn_observability_jsonl,
    ct008_manus_state_valid,
    ct009_manus_bridge_importable,
    ct010_sense_structure_complete,
]


def run_all(json_out: bool = False) -> dict[str, Any]:
    results = []
    for ct_func in CT_LIST:
        try:
            r = ct_func()
        except Exception as e:
            r = CTResult(ct_func.__name__, "UNKNOWN", False, f"Exceção: {e}")
        results.append(r)

    passed = sum(1 for r in results if r.passed)
    failed = sum(1 for r in results if not r.passed)

    if not json_out:
        _print_summary(results, passed, failed)

    return {
        "passed": passed,
        "failed": failed,
        "total": len(results),
        "results": [
            {
                "id": r.ct_id,
                "name": r.name,
                "passed": r.passed,
                "detail": r.detail,
                "evidence": r.evidence if r.evidence and (not r.passed or isinstance(r.evidence, (int, str))) else None,
            }
            for r in results
        ],
    }


def _print_summary(results: list[CTResult], passed: int, failed: int):
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    RESET = "\033[0m"
    BOLD = "\033[1m"

    print(f"\n{BOLD}{'=' * 80}{RESET}")
    print(f"  {BOLD}SPEC-026 Evolve Pipeline TDD Suite — {len(results)} Critical Tests{RESET}")
    print(f"  {GREEN}PASS: {passed}{RESET}  |  {RED}FAIL: {failed}{RESET}")
    print(f"{BOLD}{'=' * 80}{RESET}\n")

    for r in results:
        status = f"{GREEN}PASS{RESET}" if r.passed else f"{RED}FAIL{RESET}"
        print(f"  [{status}] {r.ct_id}: {r.name}")
        if r.detail:
            prefix = "       "
            color = GREEN if r.passed else YELLOW
            print(f"       {color}{r.detail}{RESET}")
        if r.evidence and not r.passed:
            ev = r.evidence
            if isinstance(ev, list) and len(ev) > 0:
                for item in ev[:5]:
                    print(f"         - {item}")

    print(f"\n{BOLD}{'=' * 80}{RESET}")
    pct = (passed / len(results)) * 100 if results else 0
    verdict = f"{GREEN}[APROVADO]{RESET}" if failed == 0 else f"{RED}[{failed} FALHAS]{RESET}"
    print(f"  RESULTADO: {verdict}  |  {passed}/{len(results)} ({pct:.0f}%)")
    print(f"{BOLD}{'=' * 80}{RESET}\n")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="SPEC-026 Evolve Pipeline TDD Suite")
    parser.add_argument("--json", action="store_true", help="Saída JSON")
    parser.add_argument("--ct", type=str, help="Executar CT específico (ex: CT-001)")
    args = parser.parse_args()

    if args.ct:
        for ct_func in CT_LIST:
            if ct_func.__name__.startswith(args.ct.lower().replace('-', '_')):
                r = ct_func()
                print(json.dumps({
                    "id": r.ct_id, "name": r.name, "passed": r.passed,
                    "detail": r.detail, "evidence": r.evidence
                }, indent=2, ensure_ascii=False))
                sys.exit(0 if r.passed else 1)
        print(f"CT não encontrado: {args.ct}")
        sys.exit(2)

    result = run_all(json_out=args.json)
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    sys.exit(0 if result["failed"] == 0 else 1)
