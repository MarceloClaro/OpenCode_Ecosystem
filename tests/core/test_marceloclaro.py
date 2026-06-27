"""
TDD Suite for Marcelo Claro Supreme Orchestrator (SPEC-047).
Validates agent configuration, five pillars, delegation chain,
TrustEngine integration, LaTeX directive, traceability, and persona.

TDD Cycle: RED → GREEN → REFACTOR
"""
import pytest
import re
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).parent.parent.parent
AGENTS_DIR = BASE_DIR / "agents"
SPECS_DIR = BASE_DIR / "specs"
COMMANDS_DIR = BASE_DIR / "command"
PLUGINS_DIR = BASE_DIR / "plugins"
ECOSYSTEM_STATE = BASE_DIR / "ecosystem-state.json"


class TestMarceloClaroAgentConfig:
    """CT-4701 to CT-4703: Agent metadata, tools, permissions."""

    def test_ct4701_agent_exists_and_metadata_correct(self):
        """CT-4701: Agente existe com name, mode, temperature corretos."""
        agent_path = AGENTS_DIR / "marceloclaro.md"
        assert agent_path.exists(), "Arquivo agents/marceloclaro.md nao encontrado."

        content = agent_path.read_text(encoding="utf-8")

        # name
        assert re.search(r"name:\s*marceloclaro", content), \
            "Frontmatter deve conter 'name: marceloclaro'."

        # mode
        assert re.search(r"mode:\s*agent", content), \
            "Frontmatter deve conter 'mode: agent'."

        # temperature
        temp_match = re.search(r"temperature:\s*([\d.]+)", content)
        assert temp_match, "Frontmatter deve conter 'temperature'."
        temp = float(temp_match.group(1))
        assert temp <= 0.2, \
            f"Temperature deve ser baixa (deterministica). Atual: {temp}."

    def test_ct4702_all_required_tools_enabled(self):
        """CT-4702: Ferramentas bash, read, write, edit, task habilitadas."""
        agent_path = AGENTS_DIR / "marceloclaro.md"
        content = agent_path.read_text(encoding="utf-8")

        required_tools = ["bash", "read", "write", "edit", "task"]
        for tool in required_tools:
            # Must appear under tools: section with true
            pattern = rf"{tool}:\s*true"
            assert re.search(pattern, content), \
                f"Ferramenta '{tool}' deve estar habilitada (true)."

    def test_ct4703_security_permissions_configured(self):
        """CT-4703: Permissoes de seguranca: allow *, deny rm-rf, deny sudo."""
        agent_path = AGENTS_DIR / "marceloclaro.md"
        content = agent_path.read_text(encoding="utf-8")

        # Wildcard allow
        assert re.search(r'["\']?\*["\']?\s*:\s*["\']allow["\']', content), \
            "Permissao 'bash.*: allow' nao encontrada."

        # Deny rm -rf (key is quoted: "rm -rf *": "deny")
        assert re.search(r'["\']rm\s+-rf\s+\*["\']\s*:\s*["\']deny["\']', content), \
            "Permissao 'rm -rf *: deny' nao encontrada."

        # Deny sudo (key is quoted: "sudo *": "deny")
        assert re.search(r'["\']sudo\s+\*["\']\s*:\s*["\']deny["\']', content), \
            "Permissao 'sudo *: deny' nao encontrada."


class TestMarceloClaroFivePillars:
    """CT-4704: Cinco Pilares mapeados no agente."""

    def test_ct4704_five_pillars_explicitly_mapped(self):
        """CT-4704: Todos os 5 pilares documentados com nomes identificaveis."""
        agent_path = AGENTS_DIR / "marceloclaro.md"
        content = agent_path.read_text(encoding="utf-8")

        pillars = [
            ("Pilar 1", "Rigor Cientifico", ["TDD", "testes"]),
            ("Pilar 2", "Contencao de Desvios", ["TrustEngine", "Goal Drift", "Guardrails"]),
            ("Pilar 3", "Viabilidade de Negocio", ["Token", "SaaS", "Pay-as-you-go"]),
            ("Pilar 4", "Unificacao de CLIs", ["Ollama", "OpenCode", "Antigravity"]),
            ("Pilar 5", "Descoberta de Potenciais", ["Potentiality Scanner", "latente"]),
        ]

        for pilar_num, pilar_name, keywords in pillars:
            found_pilar = pilar_num in content or pilar_name in content
            assert found_pilar, \
                f"{pilar_num} ({pilar_name}) nao encontrado no agente."

            found_keyword = any(kw in content for kw in keywords)
            assert found_keyword, \
                f"Nenhuma keyword {keywords} encontrada para {pilar_num}."


class TestMarceloClaroDelegationChain:
    """CT-4705: Cadeia de delegacao documentada."""

    def test_ct4705_delegation_to_suborchestrators(self):
        """CT-4705: Mencoes a master, stage e antigravity orchestrators."""
        agent_path = AGENTS_DIR / "marceloclaro.md"
        content = agent_path.read_text(encoding="utf-8")

        suborchestrators = [
            "master-orchestrator",
            "stage-orchestrator",
            "antigravity-orchestrator",
        ]

        for sub in suborchestrators:
            assert sub in content, \
                f"Suborquestrador '{sub}' nao encontrado na cadeia de delegacao."

        # Must mention delegation explicitly
        delegation_keywords = ["delega", "delegacao", "delegar"]
        found_delegation = any(kw in content.lower() for kw in delegation_keywords)
        assert found_delegation, \
            "Agente deve mencionar explicitamente 'delegacao'."


class TestMarceloClaroTrustEngine:
    """CT-4706: Integracao com TrustEngine."""

    def test_ct4706_trust_engine_integration(self):
        """CT-4706: Referencia a SPEC-038, Goal Drift, Guardrails, <15ms."""
        agent_path = AGENTS_DIR / "marceloclaro.md"
        content = agent_path.read_text(encoding="utf-8")

        assert "SPEC-038" in content, \
            "Referencia a SPEC-038 (TrustEngine) nao encontrada."
        assert "Goal Drift" in content, \
            "Conceito 'Goal Drift' nao documentado."
        assert "Guardrails" in content or "Guardrail" in content, \
            "Conceito 'Guardrails' nao documentado."
        assert "15ms" in content, \
            "Meta de latencia <15ms nao documentada."


class TestMarceloClaroLatexDirective:
    """CT-4707: Diretiva de template LaTeX documentada."""

    def test_ct4707_latex_template_directive_exists(self):
        """CT-4707: Secao de templates LaTeX com categorias Livro/Tese/CV."""
        agent_path = AGENTS_DIR / "marceloclaro.md"
        content = agent_path.read_text(encoding="utf-8")

        # Must have the directive section
        assert "template" in content.lower() or "latex" in content.lower(), \
            "Secao de templates LaTeX nao encontrada."

        # Must list at least 3 template categories
        categories = ["Livro", "Tese", "Dissertacao", "Monografia", "CV", "Curriculo"]
        found_categories = sum(1 for cat in categories if cat.lower() in content.lower())
        assert found_categories >= 3, \
            f"Apenas {found_categories} categorias de template encontradas. Minimo: 3."

        # Must mention the question tool
        assert "question" in content, \
            "Ferramenta 'question' deve ser mencionada para perguntar template."

        # Must have mandatory requirement language
        mandatory_keywords = ["MANDATORIO", "OBRIGATORIO", "SEMPRE", "SEM EXCECAO"]
        found_mandatory = any(kw in content for kw in mandatory_keywords)
        assert found_mandatory, \
            "Linguagem obrigatoria (MANDATORIO/SEMPRE) nao encontrada."


class TestMarceloClaroTraceability:
    """CT-4708: Rastreabilidade via ecosystem-state.json."""

    def test_ct4708_ecosystem_state_reference(self):
        """CT-4708: Referencia explicita a ecosystem-state.json."""
        agent_path = AGENTS_DIR / "marceloclaro.md"
        content = agent_path.read_text(encoding="utf-8")

        assert "ecosystem-state.json" in content, \
            "Referencia a 'ecosystem-state.json' nao encontrada."

        # Must link decisions to state logging
        traceability_keywords = [
            "rastreabilidade", "log", "registro", "decisao",
            "estado", "auditoria", "reproduzivel"
        ]
        found = sum(1 for kw in traceability_keywords if kw in content.lower())
        assert found >= 2, \
            f"Apenas {found} keywords de rastreabilidade encontradas. Minimo: 2."


class TestMarceloClaroTokenEconomy:
    """CT-4709: Token Economy monitoramento."""

    def test_ct4709_token_economy_monitored(self):
        """CT-4709: Mencao a tokens, Pay-as-you-go, TaaS."""
        agent_path = AGENTS_DIR / "marceloclaro.md"
        content = agent_path.read_text(encoding="utf-8")

        assert "Token" in content or "token" in content, \
            "Conceito 'Token' nao documentado."
        assert "Pay-as-you-go" in content or "pay-as-you-go" in content, \
            "Modelo 'Pay-as-you-go' nao documentado."
        assert "TaaS" in content or "Trust-as-a-Service" in content, \
            "Modelo 'TaaS' nao documentado."


class TestMarceloClaroPotentialityScanner:
    """CT-4710: Integracao com Potentiality Scanner."""

    def test_ct4710_potentiality_scanner_referenced(self):
        """CT-4710: Referencia a potentiality_scanner.py e SPEC-043."""
        agent_path = AGENTS_DIR / "marceloclaro.md"
        content = agent_path.read_text(encoding="utf-8")

        assert "potentiality_scanner" in content or "Potentiality Scanner" in content, \
            "Referencia a 'Potentiality Scanner' nao encontrada."
        assert "SPEC-043" in content, \
            "Referencia a 'SPEC-043' nao encontrada."


class TestMarceloClaroCommand:
    """CT-4711: Comando /marceloclaro registrado."""

    def test_ct4711_command_file_exists(self):
        """CT-4711: Arquivo command/marceloclaro.md existe e documenta o comando."""
        cmd_path = COMMANDS_DIR / "marceloclaro.md"
        assert cmd_path.exists(), \
            "Arquivo command/marceloclaro.md nao encontrado."

        content = cmd_path.read_text(encoding="utf-8")
        assert "/marceloclaro" in content, \
            "Comando '/marceloclaro' deve estar documentado."


class TestMarceloClaroSpec42:
    """CT-4712: SPEC-042 existente e valida."""

    def test_ct4712_spec42_exists(self):
        """CT-4712: Arquivo SPEC-042-MARCELOCLARO-ORCHESTRATOR.md existe."""
        spec_path = SPECS_DIR / "SPEC-042-MARCELOCLARO-ORCHESTRATOR.md"
        assert spec_path.exists(), \
            "SPEC-042 nao encontrada em specs/."

        content = spec_path.read_text(encoding="utf-8")
        assert "SPEC-042" in content, \
            "SPEC-042 deve conter seu proprio identificador."
        assert "Marcelo Claro" in content or "marceloclaro" in content, \
            "SPEC-042 deve mencionar Marcelo Claro."


class TestMarceloClaroBridgeIntegration:
    """CT-4713: Bridge TypeScript integracao."""

    def test_ct4713_bridge_typescript_recognizes_marceloclaro(self):
        """CT-4713: antigravity-bridge.ts menciona marceloclaro e supreme-orchestration."""
        bridge_path = PLUGINS_DIR / "antigravity-bridge.ts"
        assert bridge_path.exists(), \
            "Arquivo plugins/antigravity-bridge.ts nao encontrado."

        content = bridge_path.read_text(encoding="utf-8")
        assert "marceloclaro" in content, \
            "Bridge deve reconhecer 'marceloclaro'."
        assert "supreme-orchestration" in content or "supreme" in content.lower(), \
            "Bridge deve registrar categoria 'supreme-orchestration'."


class TestMarceloClaroDeterministicTemperature:
    """CT-4714: Temperatura deterministica."""

    def test_ct4714_temperature_is_deterministic(self):
        """CT-4714: temperature: 0.1 (baixa entropia para orquestracao suprema)."""
        agent_path = AGENTS_DIR / "marceloclaro.md"
        content = agent_path.read_text(encoding="utf-8")

        temp_match = re.search(r"temperature:\s*([\d.]+)", content)
        assert temp_match, "Temperature nao encontrada no frontmatter."

        temp = float(temp_match.group(1))
        assert temp == 0.1, \
            f"Temperature deve ser 0.1 (deterministica). Atual: {temp}."


class TestMarceloClaroPersona:
    """CT-4715: Persona autoritaria documentada."""

    def test_ct4715_persona_section_with_three_rules(self):
        """CT-4715: Secao 2 (Padrao de Comportamento) com 3 regras."""
        agent_path = AGENTS_DIR / "marceloclaro.md"
        content = agent_path.read_text(encoding="utf-8")

        # Must have persona section
        assert "Padrao de Comportamento" in content or "Persona" in content, \
            "Secao de persona/comportamento nao encontrada."

        # Must have at least 3 behavioral rules
        rule_keywords = [
            "Autoridade", "Delegacao", "Rastreabilidade",
            "Clareza", "Log", "Imediata"
        ]
        found = sum(1 for kw in rule_keywords if kw in content)
        assert found >= 3, \
            f"Apenas {found} regras de persona encontradas. Minimo: 3."


class TestMarceloClaroInvocationInstructions:
    """CT-4716: Instrucoes de Invocacao Interna."""

    def test_ct4716_invocation_steps_documented(self):
        """CT-4716: Secao 3 com 5 passos de invocacao."""
        agent_path = AGENTS_DIR / "marceloclaro.md"
        content = agent_path.read_text(encoding="utf-8")

        # Must have invocation section (with or without accents)
        invocation_keywords = ["Invocação", "Invocacao", "invocação", "invocacao", "Invocação Interna"]
        found_invocation = any(kw in content for kw in invocation_keywords)
        assert found_invocation, \
            "Secao de invocacao nao encontrada."

        # Must have at least 5 numbered steps
        steps = re.findall(r"^\s*\d+\.\s", content, re.MULTILINE)
        assert len(steps) >= 5, \
            f"Apenas {len(steps)} passos de invocacao encontrados. Minimo: 5."


class TestMarceloClaroCLIUnification:
    """CT-4717: CLI Unificacao referenciada."""

    def test_ct4717_cli_unification_documented(self):
        """CT-4717: Pilar 4 menciona Ollama, OpenCode CLI, Antigravity CLI."""
        agent_path = AGENTS_DIR / "marceloclaro.md"
        content = agent_path.read_text(encoding="utf-8")

        clis = ["Ollama", "OpenCode", "Antigravity"]
        for cli in clis:
            assert cli in content, \
                f"CLI '{cli}' nao mencionado na unificacao (Pilar 4)."


class TestMarceloClaroDissertationTraceability:
    """CT-4718: Dissertacao rastreabilidade."""

    def test_ct4718_dissertation_reference(self):
        """CT-4718: Referencia a dissertacao de mestrado e reprodutibilidade."""
        agent_path = AGENTS_DIR / "marceloclaro.md"
        content = agent_path.read_text(encoding="utf-8")

        assert "dissertacao" in content.lower(), \
            "Referencia a 'dissertacao' nao encontrada."
        # Check for reprodutivel/reproduzivel with or without accents
        reprodutibilidade = [
            "reprodutível", "reprodutivel", "reproduzível", "reproduzivel",
            "reprodutibilidade", "reproducibilidade"
        ]
        found_reprod = any(kw in content.lower() for kw in reprodutibilidade)
        assert found_reprod, \
            "Conceito de 'reprodutibilidade' nao documentado."


class TestMarceloClaroDelegationConstraint:
    """CT-4719: Modo de delegacao: usuario nunca coordena."""

    def test_ct4719_user_never_coordinates(self):
        """CT-4719: Constraint 'Nunca peca ao usuario para coordenar subagentes'."""
        agent_path = AGENTS_DIR / "marceloclaro.md"
        content = agent_path.read_text(encoding="utf-8")

        # Must explicitly forbid user coordination
        assert "nunca peca" in content.lower() or \
               "nunca peça" in content.lower() or \
               "Nunca peça" in content or \
               "nunca peça ao usuario" in content.lower(), \
            "Constraint de delegacao (usuario nunca coordena) nao encontrada."


class TestMarceloClaroTDDSDDMandatory:
    """CT-4720: TDD/SDD obrigatorio."""

    def test_ct4720_tdd_sdd_mandatory(self):
        """CT-4720: Constraint 'Use sempre TDD e SDD'."""
        agent_path = AGENTS_DIR / "marceloclaro.md"
        content = agent_path.read_text(encoding="utf-8")

        assert "TDD" in content, \
            "Constraint TDD nao encontrada."
        assert "SDD" in content, \
            "Constraint SDD nao encontrada."

        # Must be mandatory language
        mandatory = ["sempre", "SEMPRE", "obrigatorio", "MANDATORIO"]
        found = any(mw in content for mw in mandatory)
        assert found, \
            "Linguagem obrigatoria para TDD/SDD nao encontrada."
