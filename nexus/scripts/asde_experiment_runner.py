# -*- coding: utf-8 -*-
"""
ASDE Cognitive Experiment Runner — SPEC-063
===========================================
Executa simulações de experimentos de descoberta científica com
tomada de decisão sob incerteza e Teoria dos Jogos integrada.

SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL
"""

import os
import sys
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any

# Adicionar caminhos para os imports
SCRIPTS_DIR = Path(__file__).resolve().parent
ECOSYSTEM_ROOT = SCRIPTS_DIR.parent.parent
sys.path.insert(0, str(SCRIPTS_DIR))
sys.path.insert(0, str(ECOSYSTEM_ROOT / "nexus"))

from asde_engine import ASDEEngine
from game_theory_models import GameTheorySolver
from active_inference_controller import ActiveInferenceController, CognitivePrior
from metacognitive_search import MetacognitiveSearchEngine

logger = logging.getLogger("asde-experiment-runner")


class ASDECognitiveExperimentRunner:
    """Orquestrador de experimentos científicos acoplados com FEP e Teoria dos Jogos."""

    def __init__(self):
        self.asde = ASDEEngine()
        self.controller = ActiveInferenceController()
        self.mse = MetacognitiveSearchEngine(max_depth=3, branch_factor=2)
        self.log_file = ECOSYSTEM_ROOT / "cache" / "asde_experiment_log.json"

    def run_experiment(self, scientific_problem: str, domain: str = "cognicao") -> Dict[str, Any]:
        """Executa o pipeline completo de descoberta científica acoplado a tomadas de decisão cognitivas."""
        logger.info(f"Iniciando experimento ASDE para: {scientific_problem}")
        
        # 1. Executar o pipeline base do ASDE (OQS, RLT, RUMI, OPUS)
        asde_res = self.asde.run_pipeline(scientific_problem, domain, num_ideas=1)
        if not asde_res.get("ideas"):
            raise ValueError("O pipeline ASDE falhou em gerar ideias de pesquisa.")
        
        best_idea = asde_res["best_idea"]
        
        # 2. Teoria dos Jogos (Decidir cooperação em validação experimental)
        # Modelamos como uma Caça ao Cervo (Stag Hunt): Cooperação de risco vs Egoísmo seguro
        game_res = GameTheorySolver.solve_stag_hunt(stag_val=8.0, hare_val=4.0, stag_fail=0.0)
        
        # 3. Inferência Ativa (Calibrar a decisão de cooperação baseado nos priors cognitivos)
        priors = {
            "logic_coherence": CognitivePrior(metric_name="logic_coherence", target_value=0.9, tolerance=0.1, precision=0.9),
            "social_welfare": CognitivePrior(metric_name="social_welfare", target_value=0.8, tolerance=0.15, precision=0.8)
        }
        self.controller.priors = priors
        
        # Observações em caso de cooperação bem sucedida vs deserção egoísta
        obs_cooperar = {
            "logic_coherence": 0.85,
            "social_welfare": 0.90
        }
        obs_desertar = {
            "logic_coherence": 0.60,
            "social_welfare": 0.30
        }
        
        vfe_coop = self.controller.calculate_free_energy(obs_cooperar)
        vfe_des = self.controller.calculate_free_energy(obs_desertar)
        
        decisao = "Cooperar (Co-autoria da Descoberta)" if vfe_coop < vfe_des else "Desertar (Publicação Solo)"
        
        # 4. Metacognitive Search Engine (Explorar e deduzir a lógica formal da decisão científica)
        # O gerador retorna passos de prova com base no domínio
        def mock_generator(ctx: str, k: int) -> List[str]:
            import hashlib
            sentences = [
                f"Fatoramos a relacao entre os conceitos da ideia '{best_idea['title']}'.",
                "Mapeamos o comportamento dos agentes simulados sob regras de interacao de Nash.",
                "Deduzimos que a cooperacao minimiza a energia livre variacional do sistema social.",
                "Verificamos que a taxa de falsos positivos no teste de hipotese causal e menor que 0.05.",
                "Concluimos o relatorio IMRaD endossando a validacao empirica colaborativa."
            ]
            idx = int(hashlib.md5(ctx.encode("utf-8")).hexdigest(), 16)
            return [sentences[(idx + i) % len(sentences)] for i in range(k)]

        search_res = self.mse.search(scientific_problem, mock_generator)
        
        # 5. Consolidar Resultados
        experiment_data = {
            "scientific_problem": scientific_problem,
            "domain": domain,
            "best_idea": best_idea,
            "game_theory_resolution": game_res,
            "active_inference": {
                "vfe_cooperation": round(vfe_coop, 4),
                "vfe_desertion": round(vfe_des, 4),
                "selected_policy": decisao
            },
            "logical_proof": search_res,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        # Persistir logs de experimentos
        self.save_log(experiment_data)
        
        return experiment_data

    def save_log(self, data: Dict[str, Any]) -> None:
        """Salva o resultado no arquivo de log do ecossistema."""
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        try:
            self.log_file.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        except Exception as e:
            logger.error(f"Erro ao salvar log de experimento ASDE: {e}")

    def get_latest_results(self) -> Optional[Dict[str, Any]]:
        """Retorna o último log gerado."""
        if self.log_file.exists():
            try:
                return json.loads(self.log_file.read_text(encoding="utf-8"))
            except Exception:
                pass
        return None


if __name__ == "__main__":
    runner = ASDECognitiveExperimentRunner()
    res = runner.run_experiment("Explorar se o aprendizado ativo reduz a latencia cognitiva de agentes")
    print(json.dumps(res, indent=2, ensure_ascii=False))
