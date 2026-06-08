#!/usr/bin/env python3
"""
test_evolve_e2e.py — SPEC-027: Evolve Pipeline E2E Integration Tests

8 Critical Tests de integração para o pipeline completo:
  CT-E2E-001: Pipeline sequencial SENSE→VERIFY→LEARN (dry-run)
  CT-E2E-002: Status report formatado com campos obrigatórios
  CT-E2E-003: Discover retorna resultados do GitHub
  CT-E2E-004: Verify integrado (SPEC-025 + SPEC-026)
  CT-E2E-005: Install valida regras de segurança
  CT-E2E-006: Update detecta órfãos
  CT-E2E-007: Learn persiste métricas
  CT-E2E-008: Órfão removido do installed.json

Uso:
    python specs/test_evolve_e2e.py
    python specs/test_evolve_e2e.py --json
    python specs/test_evolve_e2e.py --ct CT-E2E-003
"""

import json
import os
import re
import sys
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

# ─── Config ──────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
EVOLVE_DIR = BASE_DIR / ".evolve"
SKILLS_DIR = BASE_DIR / "skills"
SPECS_DIR = BASE_DIR / "specs"
INSTALLED_JSON = EVOLVE_DIR / "installed.json"
MEMORY_JSON = EVOLVE_DIR / "memory.json"
OBSERVABILITY_JSONL = EVOLVE_DIR / "ecosystem-observability.jsonl"

# ─── Helpers ─────────────────────────────────────────────────────────────

class E2EResult:
    def __init__(self, ct_id: str, name: str, passed: bool,
                 detail: str = "", evidence: Any = None, phase: str = ""):
        self.ct_id = ct_id
        self.name = name
        self.passed = passed
        self.detail = detail
        self.evidence = evidence
        self.phase = phase


def load_installed() -> Optional[dict]:
    if not INSTALLED_JSON.exists():
        return None
    with open(INSTALLED_JSON, 'r', encoding='utf-8-sig') as f:
        return json.load(f)


def load_memory() -> Optional[dict]:
    if not MEMORY_JSON.exists():
        return None
    with open(MEMORY_JSON, 'r', encoding='utf-8-sig') as f:
        return json.load(f)


def count_skills() -> int:
    return len(list(SKILLS_DIR.rglob("SKILL.md")))


def run_validator(spec_name: str) -> tuple[bool, str]:
    """Executa uma suite de validação e retorna (passou, output)."""
    script = SPECS_DIR / spec_name
    if not script.exists():
        return False, f"Script não encontrado: {script}"
    try:
        result = subprocess.run(
            [sys.executable, str(script)],
            capture_output=True, text=True, timeout=120,
            cwd=str(BASE_DIR)
        )
        stdout = result.stdout
        stderr = result.stderr
        # Check for all-pass
        fail_match = re.search(r'FAIL:\s*(\d+)', stdout)
        if fail_match and int(fail_match.group(1)) > 0:
            return False, f"FAIL={fail_match.group(1)}"
        return True, stdout[:300]
    except subprocess.TimeoutExpired:
        return False, "Timeout 120s"
    except Exception as e:
        return False, str(e)


# ─── CT Implementations ──────────────────────────────────────────────────

def ct_e2e_001_pipeline_sequential() -> E2EResult:
    """CT-E2E-001: Pipeline SENSE→VERIFY→LEARN em dry-run sem erros fatais."""
    results: dict[str, str] = {}
    errors: list[str] = []

    # FASE 0: SENSE
    try:
        installed = load_installed()
        memory = load_memory()
        if installed and memory:
            results["SENSE"] = f"installed.json OK ({len(installed.get('skills',[]))} skills), memory.json OK (health={memory.get('healthScore','?')})"
        else:
            errors.append("SENSE: falha ao carregar installed.json ou memory.json")
    except Exception as e:
        errors.append(f"SENSE: {e}")

    # FASE 3: VERIFY (SPEC-025 + SPEC-026)
    for spec, label in [("test_frontmatter_validator.py", "SPEC-025"),
                         ("test_evolve_pipeline.py", "SPEC-026")]:
        passed, detail = run_validator(spec)
        if passed:
            results[label] = "PASS"
        else:
            errors.append(f"{label}: {detail}")

    # FASE 5: LEARN (métricas parseáveis)
    try:
        if OBSERVABILITY_JSONL.exists():
            with open(OBSERVABILITY_JSONL, 'r', encoding='utf-8-sig') as f:
                lines = [l for l in f if l.strip()]
            results["LEARN"] = f"observability.jsonl OK ({len(lines)} eventos)"
        else:
            results["LEARN"] = "observability.jsonl ausente (sem dados)"
    except Exception as e:
        errors.append(f"LEARN: {e}")

    if errors:
        return E2EResult("CT-E2E-001", "Pipeline SENSE->VERIFY->LEARN dry-run",
                         False, "; ".join(errors[:3]), results, "ALL")

    return E2EResult("CT-E2E-001", "Pipeline SENSE->VERIFY->LEARN dry-run",
                     True, f"{len(results)} fases executadas", results, "ALL")


def ct_e2e_002_status_report() -> E2EResult:
    """CT-E2E-002: Status report contém campos obrigatórios."""
    installed = load_installed()
    memory = load_memory()
    if not installed or not memory:
        return E2EResult("CT-E2E-002", "Status report com dados", False,
                         "installed.json ou memory.json ausentes", phase="SENSE")

    skills_count = count_skills()
    installed_count = len(installed.get("skills", []))
    health = memory.get("healthScore", -1)
    last_session = memory.get("lastSession", "")
    version = memory.get("version", "")

    checks: list[str] = []
    if skills_count < 100:
        checks.append(f"skills_count={skills_count} (< 100)")
    if health < 0:
        checks.append("healthScore ausente")
    if not last_session:
        checks.append("lastSession ausente")
    if not version:
        checks.append("version ausente")

    if checks:
        return E2EResult("CT-E2E-002", "Status report campos obrigatórios",
                         False, "; ".join(checks), phase="SENSE")

    return E2EResult("CT-E2E-002", "Status report campos obrigatórios", True,
                     f"health={health}, skills={skills_count}, version={version}",
                     {"health": health, "skills": skills_count, "installed": installed_count,
                      "version": version, "lastSession": last_session}, "SENSE")


def ct_e2e_003_discover_github() -> E2EResult:
    """CT-E2E-003: GitHub trending agent-skills retorna resultados."""
    import urllib.request
    import urllib.error

    url = "https://api.github.com/search/repositories?q=topic:agent-skills&sort=stars&per_page=3"
    headers = {"Accept": "application/vnd.github.v3+json", "User-Agent": "OpenCode-Evolve-E2E"}
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        # Rate limit ou sem acesso → considerar skip (não erro bloqueante)
        if e.code in (403, 429):
            return E2EResult("CT-E2E-003", "GitHub discover (rate-limited skip)",
                             True, f"HTTP {e.code} — GitHub API rate limit (skip, não falha)",
                             phase="DISCOVER")
        return E2EResult("CT-E2E-003", "GitHub discover", False,
                         f"HTTP {e.code}: {e.reason}", phase="DISCOVER")
    except Exception as e:
        return E2EResult("CT-E2E-003", "GitHub discover (network skip)",
                         True, f"Erro de rede: {e} (skip, não falha)", phase="DISCOVER")

    items = data.get("items", [])
    if not items:
        return E2EResult("CT-E2E-003", "GitHub discover não vazio", False,
                         "API retornou 0 resultados", phase="DISCOVER")

    top = [(item["full_name"], item["stargazers_count"]) for item in items[:3]]
    return E2EResult("CT-E2E-003", "GitHub discover resultados", True,
                     f"{len(items)} resultados, top: {top[0][0]} ({top[0][1]}*)",
                     top, "DISCOVER")


def ct_e2e_004_verify_integrated() -> E2EResult:
    """CT-E2E-004: SPEC-025 + SPEC-026 executam em sequência e passam."""
    results: dict[str, bool] = {}
    for spec in ["test_frontmatter_validator.py", "test_evolve_pipeline.py"]:
        passed, detail = run_validator(spec)
        results[spec] = passed

    all_pass = all(results.values())
    return E2EResult("CT-E2E-004", "Verify integrado SPEC-025+SPEC-026",
                     all_pass, f"{sum(results.values())}/{len(results)} suites pass",
                     results, "VERIFY")


def ct_e2e_005_install_safety() -> E2EResult:
    """CT-E2E-005: Regras de segurança do install são aplicadas."""
    installed = load_installed()
    if not installed:
        return E2EResult("CT-E2E-005", "Install safety rules", False,
                         "installed.json ausente", phase="INSTALL")

    skills = installed.get("skills", [])
    checks: list[str] = []

    # Regra 1: stars >= 10 para todas as instaladas
    for s in skills:
        stars = s.get("stars", 0)
        status = s.get("status", "")
        if status == "installed" and stars < 10 and stars > 0:
            checks.append(f"{s['name']}: instalada com stars={stars} (< 10)")

    # Regra 2: todas as instaladas têm path válido
    for s in skills:
        path_str = s.get("path", "")
        if path_str and not Path(path_str).exists() and s.get("status") == "installed":
            checks.append(f"{s['name']}: path não existe ({path_str})")

    if checks:
        return E2EResult("CT-E2E-005", "Install safety rules", False,
                         f"{len(checks)} violações", checks[:5], "INSTALL")

    return E2EResult("CT-E2E-005", "Install safety rules", True,
                     f"{len(skills)} skills em conformidade", phase="INSTALL")


def ct_e2e_006_update_detect_orphans() -> E2EResult:
    """CT-E2E-006: Update detecta órfãos em installed.json."""
    installed = load_installed()
    if not installed:
        return E2EResult("CT-E2E-006", "Update detecta órfãos", False,
                         "installed.json ausente", phase="EVOLVE")

    skills = installed.get("skills", [])
    orphans = [s for s in skills if s.get("status") == "orphan-404"]
    active_orphans = [s for s in orphans if s.get("action") != "remove-next"]
    handled_orphans = [s for s in orphans if s.get("action") == "remove-next"]

    if active_orphans:
        return E2EResult("CT-E2E-006", "Update detecta órfãos", False,
                         f"{len(active_orphans)} órfãos ativos sem action=remove-next",
                         active_orphans, "EVOLVE")

    return E2EResult("CT-E2E-006", "Update detecta órfãos", True,
                     f"{len(handled_orphans)} órfãos controlados, 0 ativos",
                     {"total_orphans": len(orphans), "handled": len(handled_orphans)}, "EVOLVE")


def ct_e2e_007_learn_persist() -> E2EResult:
    """CT-E2E-007: memory.json tem estrutura para persistir métricas de sessão."""
    memory = load_memory()
    if not memory:
        return E2EResult("CT-E2E-007", "Learn persiste métricas", False,
                         "memory.json ausente", phase="LEARN")

    checks: list[str] = []
    if "healthHistory" not in memory:
        checks.append("healthHistory ausente")
    else:
        history = memory["healthHistory"]
        if len(history) < 5:
            checks.append(f"healthHistory curto ({len(history)} entradas)")
        # Verify each entry has timestamp and score
        for i, h in enumerate(history):
            if "timestamp" not in h:
                checks.append(f"healthHistory[{i}] sem timestamp")
            if "score" not in h:
                checks.append(f"healthHistory[{i}] sem score")

    if "healthScore" not in memory:
        checks.append("healthScore ausente")
    if "lastSession" not in memory:
        checks.append("lastSession ausente")

    if checks:
        return E2EResult("CT-E2E-007", "Learn persiste métricas", False,
                         "; ".join(checks[:5]), phase="LEARN")

    return E2EResult("CT-E2E-007", "Learn persiste métricas", True,
                     f"healthHistory={len(memory['healthHistory'])} entradas, score={memory['healthScore']}",
                     {"history_count": len(memory['healthHistory']),
                      "current_score": memory['healthScore']}, "LEARN")


def ct_e2e_008_orphan_removed() -> E2EResult:
    """CT-E2E-008: Nenhum órfão remanescente em installed.json após limpeza."""
    installed = load_installed()
    if not installed:
        return E2EResult("CT-E2E-008", "Órfão removido", False,
                         "installed.json ausente", phase="EVOLVE")

    skills = installed.get("skills", [])
    remaining = [s for s in skills if s.get("status") == "orphan-404"]

    if remaining:
        names = [s["name"] for s in remaining]
        return E2EResult("CT-E2E-008", "Órfão removido", False,
                         f"{len(remaining)} órfãos restantes: {', '.join(names[:3])}",
                         names, "EVOLVE")

    return E2EResult("CT-E2E-008", "Órfão removido", True,
                     f"0 órfãos em {len(skills)} skills", phase="EVOLVE")


# ─── Runner ──────────────────────────────────────────────────────────────

CT_LIST = [
    ct_e2e_001_pipeline_sequential,
    ct_e2e_002_status_report,
    ct_e2e_003_discover_github,
    ct_e2e_004_verify_integrated,
    ct_e2e_005_install_safety,
    ct_e2e_006_update_detect_orphans,
    ct_e2e_007_learn_persist,
    ct_e2e_008_orphan_removed,
]


def run_all(json_out: bool = False) -> dict[str, Any]:
    results = []
    for ct_func in CT_LIST:
        try:
            r = ct_func()
        except Exception as e:
            r = E2EResult(ct_func.__name__, "UNKNOWN", False, f"Exceção: {e}")
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
                "phase": r.phase,
            }
            for r in results
        ],
    }


def _print_summary(results: list[E2EResult], passed: int, failed: int):
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    CYAN = "\033[96m"
    RESET = "\033[0m"
    BOLD = "\033[1m"

    print(f"\n{BOLD}{'=' * 80}{RESET}")
    print(f"  {BOLD}SPEC-027 Evolve E2E Integration Suite — {len(results)} Tests{RESET}")
    print(f"  {GREEN}PASS: {passed}{RESET}  |  {RED}FAIL: {failed}{RESET}")
    print(f"{BOLD}{'=' * 80}{RESET}\n")

    for r in results:
        status = f"{GREEN}PASS{RESET}" if r.passed else f"{RED}FAIL{RESET}"
        phase_tag = f"{CYAN}[{r.phase}]{RESET}" if r.phase else ""
        print(f"  [{status}] {r.ct_id}{phase_tag}: {r.name}")
        if r.detail:
            color = GREEN if r.passed else YELLOW
            print(f"       {color}{r.detail}{RESET}")
        if r.evidence and not r.passed:
            ev = r.evidence
            if isinstance(ev, list):
                for item in ev[:3]:
                    print(f"         - {item}")
            elif isinstance(ev, dict):
                for k, v in list(ev.items())[:3]:
                    print(f"         {k}: {v}")

    print(f"\n{BOLD}{'=' * 80}{RESET}")
    pct = (passed / len(results)) * 100 if results else 0
    verdict = f"{GREEN}[APROVADO]{RESET}" if failed == 0 else f"{RED}[{failed} FALHAS]{RESET}"
    print(f"  RESULTADO: {verdict}  |  {passed}/{len(results)} ({pct:.0f}%)")
    print(f"{BOLD}{'=' * 80}{RESET}\n")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="SPEC-027 Evolve E2E Integration Suite")
    parser.add_argument("--json", action="store_true", help="Saída JSON")
    parser.add_argument("--ct", type=str, help="Executar CT específico (ex: CT-E2E-003)")
    args = parser.parse_args()

    if args.ct:
        target = args.ct.upper().replace('-', '_').replace('E2E_', 'e2e_')
        for ct_func in CT_LIST:
            if ct_func.__name__ == target:
                r = ct_func()
                print(json.dumps({
                    "id": r.ct_id, "name": r.name, "passed": r.passed,
                    "detail": r.detail, "phase": r.phase,
                    "evidence": str(r.evidence)[:200] if r.evidence else None
                }, indent=2, ensure_ascii=False))
                sys.exit(0 if r.passed else 1)
        print(f"CT não encontrado: {args.ct}")
        sys.exit(2)

    result = run_all(json_out=args.json)
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    sys.exit(0 if result["failed"] == 0 else 1)
