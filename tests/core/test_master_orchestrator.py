import pytest
import os
import json
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).parent.parent.parent
AGENTS_DIR = BASE_DIR / "agents"
SPECS_DIR = BASE_DIR / "specs"

class TestMasterOrchestrator:
    """
    TDD Suite for the MasterOrchestrator (SPEC-036).
    Validates existence, correct structure, and expected behavior.
    """

    def test_ct3601_agent_exists_and_properly_configured(self):
        """CT-3601: Verifica se o MasterOrchestrator existe e possui o escopo correto (SDD)."""
        agent_path = AGENTS_DIR / "master-orchestrator.md"
        assert agent_path.exists(), "O agente MasterOrchestrator não foi encontrado."
        
        content = agent_path.read_text(encoding="utf-8")
        assert "name: MasterOrchestrator" in content, "Nome incorreto no frontmatter."
        assert "mode: agent" in content, "O MasterOrchestrator deve atuar como agent principal."
        assert "task: true" in content, "O MasterOrchestrator DEVE ter permissão para invocar tasks (subagentes)."

    def test_ct3602_spec_documentation_exists(self):
        """CT-3602: Verifica a presença da SPEC-036 garantindo a rastreabilidade SDD."""
        spec_path = SPECS_DIR / "SPEC-036-MASTER-ORCHESTRATOR.md"
        assert spec_path.exists(), "A SPEC-036 para o MasterOrchestrator não foi encontrada."
        
        content = spec_path.read_text(encoding="utf-8")
        assert "Master Orchestrator" in content
        assert "CT-3601" in content
        assert "CT-3602" in content

    def test_ct3603_delegation_capabilities_mapped(self):
        """CT-3603: Garante que o MasterOrchestrator preveja delegação ao StageOrchestrator e AntigravityOrchestrator."""
        agent_path = AGENTS_DIR / "master-orchestrator.md"
        content = agent_path.read_text(encoding="utf-8")
        
        # O agente mestre precisa saber invocar os agentes de nivel inferio
        assert "StageOrchestrator" in content, "Falta integração com o StageOrchestrator."
        assert "AntigravityOrchestrator" in content, "Falta integração com o AntigravityOrchestrator."

    def test_ct3604_audit_and_reproducibility_focus(self):
        """CT-3604: Valida foco explícito em auditoria (dissertação) e reprodutibilidade (TDD)."""
        agent_path = AGENTS_DIR / "master-orchestrator.md"
        content = agent_path.read_text(encoding="utf-8")
        
        assert "TDD" in content or "Desenvolvimento Orientado a Testes" in content, "A especificação deve exigir TDD."
        assert "SDD" in content, "A especificação deve exigir planejamento SDD prévio."
        assert "ecosystem-state.json" in content, "Deve haver referência explícita de log de estado (auditoria)."
