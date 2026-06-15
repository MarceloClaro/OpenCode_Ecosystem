import pytest
import os
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).parent.parent.parent
AGENTS_DIR = BASE_DIR / "agents"
SPECS_DIR = BASE_DIR / "specs"
COMMANDS_DIR = BASE_DIR / "command"

class TestMarceloClaroOrchestrator:
    """
    TDD Suite for the Marcelo Claro Supreme Orchestrator (SPEC-042).
    Validates the existence, correct configurations, trigger mapping, and SDD alignment.
    """

    def test_ct4201_agent_exists_and_properly_configured(self):
        """CT-4201: Verifica se o agente marceloclaro existe e possui o escopo e metadados corretos."""
        agent_path = AGENTS_DIR / "marceloclaro.md"
        assert agent_path.exists(), "O agente marceloclaro não foi encontrado."
        
        content = agent_path.read_text(encoding="utf-8")
        assert "name: marceloclaro" in content, "Nome incorreto no frontmatter do agente."
        assert "mode: agent" in content, "O agente marceloclaro deve atuar como agent principal."
        assert "task: true" in content, "O agente marceloclaro deve ter permissão de orquestração (task)."

    def test_ct4202_command_exists_and_registered(self):
        """CT-4202: Garante que o comando de terminal /marceloclaro existe e está mapeado."""
        cmd_path = COMMANDS_DIR / "marceloclaro.md"
        assert cmd_path.exists(), "O comando marceloclaro não foi encontrado no diretório command/."
        
        content = cmd_path.read_text(encoding="utf-8")
        assert "/marceloclaro" in content, "O comando /marceloclaro deve estar explicitado na documentação do comando."

    def test_ct4203_spec_documentation_exists(self):
        """CT-4203: Verifica a presença da SPEC-042 garantindo a conformidade e rastreabilidade SDD."""
        spec_path = SPECS_DIR / "SPEC-042-MARCELOCLARO-ORCHESTRATOR.md"
        assert spec_path.exists(), "A SPEC-042 não foi encontrada em specs/."
        
        content = spec_path.read_text(encoding="utf-8")
        assert "SPEC-042" in content
        assert "Marcelo Claro" in content
        assert "CT-4201" in content
        assert "CT-4202" in content

    def test_ct4204_four_pillars_explicitly_mapped(self):
        """CT-4204: Garante que os quatro pilares essenciais de orquestração estejam explicitados no agente."""
        agent_path = AGENTS_DIR / "marceloclaro.md"
        content = agent_path.read_text(encoding="utf-8")
        
        assert "Pilar 1" in content or "Rigor Científico" in content, "Pilar 1 (TDD) deve estar mapeado."
        assert "Pilar 2" in content or "Contenção de Desvios" in content, "Pilar 2 (TrustEngine) deve estar mapeado."
        assert "Pilar 3" in content or "Viabilidade de Negócio" in content, "Pilar 3 (SaaS/Token) deve estar mapeado."
        assert "Pilar 4" in content or "Unificação de CLIs" in content, "Pilar 4 (CLIs/Motores) deve estar mapeado."
        
        assert "master-orchestrator" in content, "Falta delegação para o master-orchestrator."
        assert "antigravity-orchestrator" in content, "Falta delegação para o antigravity-orchestrator."
