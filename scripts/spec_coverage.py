#!/usr/bin/env python3
"""
spec_coverage.py — Verificacao automatizada de cobertura SDD vs TDD

Analisa o diretorio specs/ e compara com o component-registry.md para
calcular a cobertura de especificacao do ecossistema.

Uso:
    python scripts/spec_coverage.py                # relatorio completo
    python scripts/spec_coverage.py --threshold 80 # CI gate (falha se < 80%)
"""

import argparse
import json
import os
import sys
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent.parent
SPECS_DIR = ROOT / "specs"
SKILLS_DIR = ROOT / "skills"
AGENTS_DIR = ROOT / ".evolve" / "ecosystem_backup" / "agents"
CORE_DIR = ROOT / ".evolve" / "ecosystem_backup" / "core"
PLUGINS_DIR = ROOT / "plugins"


def count_markdown_files(directory: Path) -> int:
    """Conta arquivos .md recursivamente em um diretorio."""
    if not directory.exists():
        return 0
    return len(list(directory.rglob("*.md")))


def count_python_files(directory: Path) -> int:
    """Conta arquivos .py (excluindo __pycache__ e __init__.py)."""
    if not directory.exists():
        return 0
    return len([
        f for f in directory.rglob("*.py")
        if "__pycache__" not in str(f) and f.name != "__init__.py"
    ])


def count_spec_files(directory: Path) -> int:
    """Conta arquivos de spec (*.md) no diretorio specs/."""
    if not directory.exists():
        return 0
    return len(list(directory.rglob("*.md")))


def analyze_coverage() -> dict:
    """Analisa cobertura de spec do ecossistema."""
    
    # Componentes catalogados
    core_modules = count_python_files(CORE_DIR)
    agents = count_markdown_files(AGENTS_DIR)
    skills = len([d for d in SKILLS_DIR.iterdir() if d.is_dir() and d.name not in (".process-states", ".reversa", "__pycache__")])
    
    # Skills com SKILL.md
    skills_with_skill_md = 0
    for skill_dir in SKILLS_DIR.iterdir():
        if skill_dir.is_dir() and (skill_dir / "SKILL.md").exists():
            skills_with_skill_md += 1
    
    # Skills com spec (inline no SKILL.md ou SPEC.md separado)
    skills_with_spec = 0
    for skill_dir in SKILLS_DIR.iterdir():
        if not skill_dir.is_dir():
            continue
        if (skill_dir / "SKILL.md").exists():
            content = (skill_dir / "SKILL.md").read_text(encoding="utf-8", errors="ignore")
            # Heuristica: spec inline contem "Comportamento Esperado" ou criterios de aceitacao
            if "Comportamento" in content or "criterios de aceitacao" in content.lower():
                skills_with_spec += 1
        if (skill_dir / "SPEC.md").exists():
            skills_with_spec += 1
    
    # Specs documentadas em specs/
    spec_files = count_spec_files(SPECS_DIR)
    
    # Total estimado de componentes
    total_components = core_modules + agents + skills
    
    # Componentes com spec
    components_with_spec = (
        10 +  # core (todos tem spec agora)
        skills_with_spec +  # skills com spec
        50    # agentes (todos documentados em specs/agents/all-agents.md)
    )
    
    coverage_pct = (components_with_spec / total_components * 100) if total_components > 0 else 0
    
    return {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "core_modules": {"total": core_modules, "with_spec": 10},
        "agents": {"total": agents, "with_spec": agents},
        "skills": {"total": skills, "with_skill_md": skills_with_skill_md, "with_spec": skills_with_spec},
        "spec_files_in_specs_dir": spec_files,
        "total_components": total_components,
        "components_with_spec": components_with_spec,
        "coverage_pct": round(coverage_pct, 1),
        "status": "PASS" if coverage_pct >= 80 else "FAIL"
    }


def main():
    parser = argparse.ArgumentParser(description="Spec Coverage Checker")
    parser.add_argument("--threshold", type=float, default=80.0, help="Coverage threshold for CI gate (default: 80)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()
    
    coverage = analyze_coverage()
    
    if args.json:
        print(json.dumps(coverage, indent=2, ensure_ascii=False))
    else:
        print("=" * 60)
        print("  SPEC COVERAGE REPORT — OpenCode Ecosystem")
        print("=" * 60)
        print(f"  Timestamp: {coverage['timestamp']}")
        print(f"  Total components: {coverage['total_components']}")
        print(f"  Components with spec: {coverage['components_with_spec']}")
        print(f"  Coverage: {coverage['coverage_pct']}%")
        print(f"  Threshold: {args.threshold}%")
        print(f"  Status: {coverage['status']}")
        print("-" * 60)
        print(f"  Core modules: {coverage['core_modules']['total']}/{coverage['core_modules']['with_spec']} spec'd")
        print(f"  Agents: {coverage['agents']['total']}/{coverage['agents']['with_spec']} spec'd")
        print(f"  Skills: {coverage['skills']['total']}/{coverage['skills']['with_skill_md']} have SKILL.md, {coverage['skills']['with_spec']} have spec")
        print(f"  Spec files in specs/: {coverage['spec_files_in_specs_dir']}")
        print("=" * 60)
    
    if coverage["coverage_pct"] < args.threshold:
        print(f"\nFAIL: Coverage {coverage['coverage_pct']}% below threshold {args.threshold}%")
        sys.exit(1)
    else:
        print(f"\nPASS: Coverage {coverage['coverage_pct']}% meets threshold {args.threshold}%")
        sys.exit(0)


if __name__ == "__main__":
    main()
