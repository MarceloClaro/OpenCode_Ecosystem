# -*- coding: utf-8 -*-
"""
Manus Evolve <-> Evolution Loop Bridge
Conecta o Manus Evolve Plugin (TypeScript/Bun) ao Evolution Loop (Python)
Permite que outcomes do Manus alimentem o feedback loop de evolucao
"""
import json
import sys
from pathlib import Path
from typing import Optional

from ecosystem_config import ECO_ROOT; BASE_DIR = ECO_ROOT
EVOLVE_DIR = BASE_DIR / ".evolve"
MANUS_STATE_FILE = EVOLVE_DIR / "manus-state.json"

sys.path.insert(0, str(BASE_DIR / "nexus" / "scripts"))
from evolution_loop import EvolutionLoopRunner, FeedbackLoopEngine


class ManusEvolveBridge:
    """
    Bridge entre Manus Evolve (TypeScript) e Evolution Loop (Python).
    
    Responsabilidades:
    1. Ler estado do Manus Evolve (manus-state.json)
    2. Extrair outcomes e learnings
    3. Alimentar FeedbackLoopEngine com dados do Manus
    4. Gerar skills baseadas em padroes do Manus
    """

    def __init__(self):
        self.fb = FeedbackLoopEngine()
        self.evolve_runner = EvolutionLoopRunner()

    def load_manus_state(self) -> Optional[dict]:
        """Carrega estado atual do Manus Evolve."""
        if not MANUS_STATE_FILE.exists():
            return None
        try:
            with open(MANUS_STATE_FILE, "r", encoding="utf-8-sig") as f:
                return json.load(f)
        except Exception as e:
            print(f"Erro ao carregar Manus state: {e}")
            return None

    def sync_manus_to_evolution_loop(self) -> dict:
        """
        Sincroniza outcomes do Manus Evolve para o Evolution Loop.
        Retorna resumo da sincronizacao.
        """
        manus_state = self.load_manus_state()
        if not manus_state:
            return {"status": "no_manus_state", "synced": 0}

        synced = 0
        rounds = manus_state.get("rounds", [])

        for round_data in rounds:
            # Registrar outcome do Manus no feedback loop
            self.fb.record_outcome(
                component="manus_evolve",
                action=f"round_{round_data.get('round', 0)}",
                success=round_data.get("score", 0) > 50,
                score=float(round_data.get("score", 0)),
                duration_ms=0,
                context=json.dumps({
                    "plan": round_data.get("plan", "")[:200],
                    "actions_count": len(round_data.get("actions", [])),
                    "learnings_count": len(round_data.get("learnings", [])),
                    "corrections_applied": round_data.get("correctionsApplied", 0),
                    "tokens_saved": round_data.get("tokensSaved", 0)
                })
            )
            synced += 1

        # Extrair learnings do Manus
        manus_learnings = []
        for round_data in rounds:
            manus_learnings.extend(round_data.get("learnings", []))

        # Registrar learnings consolidados
        if manus_learnings:
            self.fb.record_learning(
                pattern="manus_evolve_consolidated",
                confidence=0.85,
                category="skill_generation",
                source_outcomes=[f"manus_round_{r.get('round')}" for r in rounds],
                effectiveness=float(manus_state.get("evolutionScore", 0)) / 100
            )

        return {
            "status": "synced",
            "synced_rounds": synced,
            "total_learnings": len(manus_learnings),
            "manus_score": manus_state.get("evolutionScore", 0),
            "skills_generated": manus_state.get("totalSkillsGenerated", 0)
        }

    def trigger_evolution_from_manus(self) -> dict:
        """
        Dispara ciclo de evolucao baseado em dados do Manus.
        Usa padroes do Manus para informar diagnostico e healing.
        """
        sync_result = self.sync_manus_to_evolution_loop()

        if sync_result.get("synced", 0) == 0:
            return {"status": "no_data_to_evolve", "sync": sync_result}

        # Executar ciclo de evolucao com contexto do Manus
        cycle = self.evolve_runner.run_cycle()

        return {
            "status": "evolution_triggered",
            "sync": sync_result,
            "cycle_id": cycle.cycle_id,
            "health_before": cycle.health_before,
            "health_after": cycle.health_after,
            "actions_taken": cycle.actions_taken
        }

    def get_combined_state(self) -> dict:
        """Retorna estado combinado do Manus + Evolution Loop."""
        manus_state = self.load_manus_state()
        evolution_state = {"cycles": len(self.fb.cycles), "outcomes": len(self.fb.outcomes), "learnings": len(self.fb.learnings)}

        return {
            "manus": {
                "rounds": len(manus_state.get("rounds", [])) if manus_state else 0,
                "score": manus_state.get("evolutionScore", 0) if manus_state else 0,
                "skills": manus_state.get("totalSkillsGenerated", 0) if manus_state else 0,
                "version": manus_state.get("version", "unknown") if manus_state else "unknown"
            },
            "evolution": evolution_state,
            "bridge_status": "active"
        }


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Manus Evolve <-> Evolution Loop Bridge")
    parser.add_argument("--sync", action="store_true", help="Sync Manus to Evolution Loop")
    parser.add_argument("--evolve", action="store_true", help="Trigger evolution from Manus data")
    parser.add_argument("--state", action="store_true", help="Show combined state")
    args = parser.parse_args()

    bridge = ManusEvolveBridge()

    if args.sync:
        result = bridge.sync_manus_to_evolution_loop()
        print("Sync Result:", result)
    elif args.evolve:
        result = bridge.trigger_evolution_from_manus()
        print("Evolution Result:", result)
    elif args.state:
        state = bridge.get_combined_state()
        print("Combined State:", json.dumps(state, indent=2))
    else:
        print("Use --sync, --evolve, or --state")

