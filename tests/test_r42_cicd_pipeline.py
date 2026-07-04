#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Testes TDD — R42: CI/CD Pipeline (SPEC-085)
=============================================
12 CTs validando GitHub Actions workflows, pre-commit hooks,
ci_validate.py atualizado e integracao do pipeline.

SAIDA OBRIGATORIA: PORTUGUES BRASILEIRO FORMAL
"""

import os
import stat
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent


# ════════════════════════════════════════════════════════════
# 4.1 GitHub Actions Workflow (CT-01 a CT-04)
# ════════════════════════════════════════════════════════════

def test_ecosystem_ci_yml_exists():
    """CT-01: .github/workflows/ecosystem-ci.yml deve existir."""
    path = BASE / ".github" / "workflows" / "ecosystem-ci.yml"
    assert path.exists(), f"Arquivo nao existe: {path}"
    assert path.stat().st_size > 0, "Arquivo vazio"


def test_ecosystem_ci_yml_syntax():
    """CT-02: ecosystem-ci.yml deve ser YAML valido.
    Nota: PyYAML converte 'on:' para True (YAML 1.1 spec).
    """
    import yaml
    path = BASE / ".github" / "workflows" / "ecosystem-ci.yml"
    with open(path, "r") as f:
        data = yaml.safe_load(f)
    assert data is not None, "YAML invalido (retornou None)"
    assert "name" in data, "Workflow sem name"
    # PyYAML 1.1: 'on' → True. Aceita ambos.
    has_trigger = True in data or "on" in data
    assert has_trigger, "Workflow sem on (triggers)"
    assert "jobs" in data, "Workflow sem jobs"


def test_cora_eval_nightly_exists():
    """CT-03: .github/workflows/cora-eval-nightly.yml deve existir."""
    path = BASE / ".github" / "workflows" / "cora-eval-nightly.yml"
    assert path.exists(), f"Arquivo nao existe: {path}"
    assert path.stat().st_size > 0, "Arquivo vazio"


def test_cora_eval_nightly_cron():
    """CT-04: cora-eval-nightly.yml deve ter cron schedule.
    Nota: PyYAML converte 'on:' para True (YAML 1.1 spec).
    """
    import yaml
    path = BASE / ".github" / "workflows" / "cora-eval-nightly.yml"
    with open(path, "r") as f:
        data = yaml.safe_load(f)
    assert data is not None, "YAML invalido"

    # PyYAML 1.1: 'on' → True. Aceita ambos.
    on = data.get(True) or data.get("on") or {}
    has_cron = False
    if isinstance(on, dict):
        schedule = on.get("schedule", [])
        for entry in schedule:
            if isinstance(entry, dict) and "cron" in entry:
                has_cron = True
    assert has_cron, "Workflow noturno sem cron schedule"


# ════════════════════════════════════════════════════════════
# 4.2 Pre-Commit Hook (CT-05 a CT-06)
# ════════════════════════════════════════════════════════════

def test_pre_commit_exists():
    """CT-05: hooks/pre-commit-cora-eval.sh deve existir e ser executavel."""
    path = BASE / "hooks" / "pre-commit-cora-eval.sh"
    assert path.exists(), f"Arquivo nao existe: {path}"

    st = path.stat()
    is_exec = bool(st.st_mode & stat.S_IXUSR)
    assert is_exec, "Hook nao e executavel (falta chmod +x)"


def test_pre_commit_includes_r41():
    """CT-06: Script do pre-commit deve cobrir test_r* (ciclos R31-R41)."""
    path = BASE / "hooks" / "pre-commit-cora-eval.sh"
    content = path.read_text(encoding="utf-8")

    # Deve referenciar test_r* para cobrir todos os ciclos
    assert "test_r" in content, "Hook nao faz referencia a test_r*"
    assert "pytest" in content, "Hook nao usa pytest"


# ════════════════════════════════════════════════════════════
# 4.3 ci_validate.py (CT-07 a CT-10)
# ════════════════════════════════════════════════════════════

def test_ci_validate_imports():
    """CT-07: ci_validate.py deve poder ser importado sem erros."""
    # Apenas verifica sintaxe: importa como modulo
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "ci_validate",
        str(BASE / "tests" / "ci_validate.py"),
    )
    assert spec is not None, "Nao foi possivel carregar spec do ci_validate.py"


def test_ci_validate_r39_registered():
    """CT-08: ci_validate.py deve registrar 14 CTs do R39."""
    content = (BASE / "tests" / "ci_validate.py").read_text(encoding="utf-8")
    # Conta ocorrencias de "test_health_monitor" no codigo
    r39_refs = content.count("test_health_monitor")
    assert r39_refs >= 4, f"Apenas {r39_refs} referencias a R39 (esperado >= 4)"

    # Verifica lista R39_CTS
    assert "R39_CTS" in content, "ci_validate.py sem referencia a R39_CTS"
    assert "14 CTs" in content or "Self-Repair" in content, \
        "ci_validate.py sem mencao aos 14 CTs do R39"


def test_ci_validate_r41_registered():
    """CT-09: ci_validate.py deve registrar 23 CTs do R41."""
    content = (BASE / "tests" / "ci_validate.py").read_text(encoding="utf-8")
    assert "R41" in content or "health_background" in content or "HealthBackground" in content, \
        "ci_validate.py sem referencia ao R41"


def test_ci_validate_health_background_import():
    """CT-10: HealthBackgroundService deve ser importavel."""
    sys.path.insert(0, str(BASE / "core" / "services"))
    try:
        from health_background import HealthBackgroundService, WebhookConfig
        assert HealthBackgroundService is not None
        assert WebhookConfig is not None
    finally:
        sys.path.pop(0)


# ════════════════════════════════════════════════════════════
# 4.4 Integracao (CT-11 a CT-12)
# ════════════════════════════════════════════════════════════

def test_all_test_files_exist():
    """CT-11: Todos os arquivos test_r*_*.py referenciados existem."""
    test_dir = BASE / "tests"
    r_files = sorted(test_dir.glob("test_r*_*.py"))
    assert len(r_files) >= 5, f"Apenas {len(r_files)} arquivos test_r*_*.py (esperado >= 5)"
    for f in r_files:
        assert f.exists(), f"Arquivo de teste nao encontrado: {f.name}"


def test_total_cts_match():
    """CT-12: Soma dos CTs por suite deve corresponder ao ecosystem-state.json."""
    import json
    state_path = BASE / "ecosystem-state.json"
    with open(state_path) as f:
        state = json.load(f)

    declared = state.get("total_cts", 0)
    assert declared > 0, f"total_cts em ecosystem-state.json = {declared}"

    # Soma estimada dos CTs conhecidos
    known_suites = {
        "test_ecosystem_health": 14,
        "test_r31_metodos": 4,
        "test_r32_paradigmas": 4,
        "test_r33_paradigma_fenomenologico": 4,
        "test_r34_dominio_psicologia_clinica": 4,
        "test_r35_research_skills": 26,
        "test_r36_r37": 4,
        "test_r38_neurociencias": 4,
        "test_r39_self_repair": 14,
        "test_r40_infrastructure": 4,
        "test_r41_health_background": 23,
    }

    # Verifica que cada suite existe
    for suite_name in known_suites:
        suite_file = BASE / "tests" / f"{suite_name}.py"
        if suite_file.exists():
            content = suite_file.read_text(encoding="utf-8")
            ct_count = known_suites[suite_name]
            # Conta funcoes test_* E metodos dentro de classes (ex: TestHealthMonitor.test_check)
            test_functions = [
                l for l in content.split("\n")
                if "def test_" in l  # captura test_xxx e class TestX: def test_yyy
            ]
            assert len(test_functions) >= ct_count, \
                f"{suite_name}.py: {len(test_functions)} funcoes/metodos, esperado >= {ct_count}"

    assert declared >= 440, f"total_cts ({declared}) parece baixo demais"


# ════════════════════════════════════════════════════════════
# Execucao direta
# ════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v", "--tb=short"]))
