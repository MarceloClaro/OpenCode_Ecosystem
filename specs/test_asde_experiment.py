# -*- coding: utf-8 -*-
"""
test_asde_experiment.py — SPEC-063: TDD Test Suite para ASDE Cognitive Experiments
===================================================================================
12 Casos de Teste (CT) para validar a execução integrada de descoberta científica,
Teoria dos Jogos, Minimização de Energia Livre e Raciocínio Metacognitivo.

Uso:
    python -m pytest specs/test_asde_experiment.py -v
"""

import sys
import json
from pathlib import Path
import pytest

# Configurar path dos módulos
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / "nexus" / "scripts"))
sys.path.insert(0, str(BASE_DIR / "nexus"))

from asde_experiment_runner import ASDECognitiveExperimentRunner
from dashboard_server import gerar_html_estatico


class TestASDECognitiveExperiment:

    @pytest.fixture(scope="class")
    def runner(self):
        return ASDECognitiveExperimentRunner()

    def test_ct_063_001_runner_initialization(self, runner):
        """CT-063-001: Validar propriedades básicas do runner."""
        assert runner.asde is not None
        assert runner.controller is not None
        assert runner.mse is not None
        assert runner.log_file.name == "asde_experiment_log.json"

    def test_ct_063_002_run_experiment_structure(self, runner):
        """CT-063-002: Validar o esquema de dados retornado por um experimento completo."""
        res = runner.run_experiment("Explorar a relacao entre polimatia e resiliencia cognitiva", domain="cognicao")
        assert "scientific_problem" in res
        assert "best_idea" in res
        assert "game_theory_resolution" in res
        assert "active_inference" in res
        assert "logical_proof" in res
        assert "timestamp" in res

    def test_ct_063_003_game_theory_resolution(self, runner):
        """CT-063-003: Validar a modelagem de Teoria dos Jogos no experimento (Stag Hunt)."""
        res = runner.run_experiment("Testar o efeito do sono no aprendizado consolidado", domain="aprendizado")
        gt = res["game_theory_resolution"]
        assert gt["game"] == "Stag Hunt"
        assert ("Cervo", "Cervo") in gt["nash_equilibria_pure"]
        assert ("Lebre", "Lebre") in gt["nash_equilibria_pure"]

    def test_ct_063_004_active_inference_fep(self, runner):
        """CT-063-004: Validar o cálculo de VFE e a política de cooperação selecionada pelo FEP."""
        res = runner.run_experiment("Investigar o impacto do estresse no córtex pré-frontal", domain="neurociencia")
        ai = res["active_inference"]
        # Cooperação deve ter menor VFE por satisfazer priors de bem-estar social e consistência
        assert ai["vfe_cooperation"] < ai["vfe_desertion"]
        assert "Cooperar" in ai["selected_policy"]

    def test_ct_063_005_logical_proof(self, runner):
        """CT-063-005: Validar a prova lógica deduzida pelo Metacognitive Search Engine."""
        res = runner.run_experiment("Análise de plasticidade sináptica sob estimulação elétrica", domain="neurociencia")
        proof = res["logical_proof"]
        assert proof["status"] == "sucesso"
        assert len(proof["best_path_nodes"]) == 4

    def test_ct_063_006_log_persistence(self, runner):
        """CT-063-006: Validar que os resultados do experimento são persistidos em JSON."""
        if runner.log_file.exists():
            runner.log_file.unlink()
        runner.run_experiment("Problema de teste de persistencia", domain="cognicao")
        assert runner.log_file.exists()
        
        data = json.loads(runner.log_file.read_text(encoding="utf-8"))
        assert data["scientific_problem"] == "Problema de teste de persistencia"

    def test_ct_063_007_get_latest_results(self, runner):
        """CT-063-007: Validar a recuperação dos últimos resultados persistidos."""
        runner.run_experiment("Recuperacao de dados de teste", domain="cognicao")
        latest = runner.get_latest_results()
        assert latest is not None
        assert latest["scientific_problem"] == "Recuperacao de dados de teste"

    def test_ct_063_008_invalid_input(self, runner):
        """CT-063-008: Validar que o runner falha adequadamente com problemas vazios."""
        with pytest.raises(Exception):
            runner.run_experiment("", domain="cognicao")

    def test_ct_063_009_different_domains(self, runner):
        """CT-063-009: Validar a execução do experimento em diferentes domínios cognitivos."""
        res_comp = runner.run_experiment("Otimização de arquitetura de rede neural", domain="computacao")
        assert res_comp["domain"] == "computacao"
        assert res_comp["best_idea"] is not None

    def test_ct_063_010_active_inference_priorities(self, runner):
        """CT-063-010: Validar a calibração de priors e seu efeito no cálculo da Energia Livre."""
        # Se alterarmos as observações para algo muito distante dos priors, a VFE deve subir
        obs_ruim = {"logic_coherence": 0.1, "social_welfare": 0.1}
        vfe_ruim = runner.controller.calculate_free_energy(obs_ruim)
        
        obs_boa = {"logic_coherence": 0.9, "social_welfare": 0.8}
        vfe_boa = runner.controller.calculate_free_energy(obs_boa)
        
        assert vfe_ruim > vfe_boa

    def test_ct_063_011_dashboard_integration(self, runner):
        """CT-063-011: Validar que a geração estática do dashboard compila após o experimento."""
        runner.run_experiment("Integração estática do dashboard", domain="cognicao")
        gerar_html_estatico()
        dest_file = Path(BASE_DIR) / "nexus" / "dashboard" / "index.html"
        assert dest_file.exists()

    def test_ct_063_012_mcp_routing_check(self, runner):
        """CT-063-012: Validar o roteamento lógico da ferramenta de experimento (lógica do wrapper)."""
        # Apenas checa se os métodos chamados pelo capabilities server estão disponíveis e lógicos
        assert hasattr(runner, "run_experiment")
        assert hasattr(runner, "get_latest_results")
