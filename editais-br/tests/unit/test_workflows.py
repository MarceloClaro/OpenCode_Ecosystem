"""Testes de validação dos workflows GitHub Actions — Issue #17."""

from pathlib import Path

import yaml

WORKFLOWS_DIR = Path(__file__).parents[2] / ".github" / "workflows"


def test_workflows_dir_existe():
    """Diretório .github/workflows deve existir."""
    assert WORKFLOWS_DIR.is_dir(), f"{WORKFLOWS_DIR} não encontrado"


def test_ci_workflow_existe():
    """ci.yml deve existir."""
    ci = WORKFLOWS_DIR / "ci.yml"
    assert ci.exists(), "ci.yml não encontrado"


def test_ci_workflow_valido():
    """ci.yml deve ser YAML válido com jobs de test e lint."""
    ci = yaml.safe_load((WORKFLOWS_DIR / "ci.yml").read_text())
    assert "name" in ci
    # YAML interpreta "on" como True (booleano)
    trigger = ci.get("on") or ci.get(True)
    assert trigger is not None, "ci.yml precisa de gatilho 'on'"
    assert "jobs" in ci

    jobs = ci["jobs"]
    assert "test" in jobs, "ci.yml deve ter job 'test'"


def test_ci_tem_lint():
    """ci.yml deve ter job de lint."""
    ci = yaml.safe_load((WORKFLOWS_DIR / "ci.yml").read_text())
    assert "lint" in ci["jobs"], "ci.yml deve ter job 'lint'"


def test_deploy_workflow_existe():
    """deploy.yml deve existir."""
    deploy = WORKFLOWS_DIR / "deploy.yml"
    assert deploy.exists(), "deploy.yml não encontrado"


def test_deploy_workflow_valido():
    """deploy.yml deve ter job de deploy."""
    deploy = yaml.safe_load((WORKFLOWS_DIR / "deploy.yml").read_text())
    assert "name" in deploy
    trigger = deploy.get("on") or deploy.get(True)
    assert trigger is not None, "deploy.yml precisa de gatilho 'on'"
    assert "jobs" in deploy

    jobs = deploy["jobs"]
    assert "deploy" in jobs, "deploy.yml deve ter job 'deploy'"

    # Deve disparar com push na main
    branches = trigger.get("push", {}).get("branches", [])
    assert "main" in branches, "deploy deve disparar com push na main"
