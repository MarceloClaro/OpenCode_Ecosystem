#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Evolução Cycle v1.0 — Fecha o ciclo de evolução do ecossistema:

  1. Coleta métricas de todos componentes (via ecosystem_bridge)
  2. Extrai feedback/padrões do editais-local
  3. Gera novas skills via Manus Evolve bridge
  4. Poda dados stale (nexus context_offload)
  5. Atualiza pesos e estado global

Uso:
  python evolution_cycle.py run                # Ciclo completo
  python evolution_cycle.py metrics            # Coleta métricas
  python evolution_cycle.py prune              # Poda dados stale
  python evolution_cycle.py generate-skills    # Gera novas skills
  python evolution_cycle.py status             # Status do ciclo
"""

import json
import sys
import time
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import Optional

ECO_ROOT = Path(r"C:\Users\marce\.config\opencode")
NEXUS_DIR = ECO_ROOT / "nexus"
SCRIPTS_DIR = NEXUS_DIR / "scripts"
EVOLVE_DIR = ECO_ROOT / ".evolve"
EDITAIS_LOCAL_ROOT = Path(r"C:\Users\marce\editais-local")
BRIDGE_STATE = EVOLVE_DIR / "bridge-state.json"
CYCLE_STATE = EVOLVE_DIR / "evolution-cycle.json"


class EvolutionCycle:
    def __init__(self):
        self.metrics = {}
        self.cycle_start = datetime.now(timezone.utc)

    # ─── Metric Collection ───────────────────────────────────

    def collect_metrics(self) -> dict:
        """Coleta metricas de todos os componentes."""
        print("Coletando metricas do ecossistema...")

        # 1. Bridge health
        bridge_health = self._get_bridge_health()

        # 2. Editais-local stats
        editais_stats = self._get_editais_stats()

        # 3. Nexus context offload stats
        nexus_stats = self._get_nexus_stats()

        # 4. Criador-artigo stats
        artigo_stats = self._get_artigo_stats()

        # 5. SEEKER stats
        seeker_stats = self._get_seeker_stats()

        self.metrics = {
            "collected_at": self.cycle_start.isoformat(),
            "bridge": bridge_health,
            "editais": editais_stats,
            "nexus": nexus_stats,
            "criador_artigo": artigo_stats,
            "seeker": seeker_stats,
        }

        print(f"  Bridge health: {bridge_health.get('overall_health', '?')}%")
        print(f"  Editais no banco: {editais_stats.get('total', 0)}")
        print(f"  Nexus sessions: {nexus_stats.get('total_sessions', 0)}")
        print(f"  Artigo agents: {artigo_stats.get('agents', 0)}")
        print(f"  SEEKER runs: {seeker_stats.get('runs', 0)}")

        self._save_cycle_state()
        return self.metrics

    def _get_bridge_health(self) -> dict:
        if not BRIDGE_STATE.exists():
            return {"overall_health": 0, "components": {}}
        try:
            data = json.loads(BRIDGE_STATE.read_text(encoding="utf-8"))
            return {
                "overall_health": data.get("overall_health", 0),
                "components": {k: {"score": v.get("score", 0), "status": v.get("status")}
                              for k, v in data.get("components", {}).items()},
            }
        except Exception:
            return {"overall_health": 0}

    def _get_editais_stats(self) -> dict:
        try:
            sys.path.insert(0, str(EDITAIS_LOCAL_ROOT))
            from editais_local.database import SessionLocal, init_db
            from editais_local.models import Edital, Portal
            init_db()
            db = SessionLocal()
            try:
                total = db.query(Edital).count()
                abertos = db.query(Edital).filter(Edital.status_inscricao == "aberto").count()
                portais = db.query(Portal).count()
                feedback_file = EDITAIS_LOCAL_ROOT / "data" / "scheduler-state.json"
                scheduled = 0
                if feedback_file.exists():
                    sched_data = json.loads(feedback_file.read_text(encoding="utf-8"))
                    scheduled = len(sched_data.get("jobs", []))
                return {"total": total, "abertos": abertos, "portais": portais, "scheduled_jobs": scheduled}
            finally:
                db.close()
        except Exception as e:
            return {"error": str(e)}

    def _get_nexus_stats(self) -> dict:
        offload_dir = NEXUS_DIR / "context_offload"
        total_sessions = 0
        total_size = 0
        if offload_dir.exists():
            for d in offload_dir.iterdir():
                if d.is_dir():
                    total_sessions += 1
                    for f in d.rglob("*"):
                        if f.is_file():
                            total_size += f.stat().st_size

        scripts_count = len(list(SCRIPTS_DIR.glob("*.py"))) if SCRIPTS_DIR.exists() else 0
        return {"total_sessions": total_sessions, "total_size_kb": round(total_size / 1024, 1), "scripts": scripts_count}

    def _get_artigo_stats(self) -> dict:
        agents_dir = ECO_ROOT / "criador-artigo" / "agents"
        agents = len(list(agents_dir.glob("*.md"))) if agents_dir.exists() else 0
        output_dir = ECO_ROOT / "criador-artigo" / "output"
        runs = len([d for d in output_dir.iterdir() if d.is_dir()]) if output_dir.exists() else 0
        return {"agents": agents, "completed_runs": runs}

    def _get_seeker_stats(self) -> dict:
        artifacts_dir = ECO_ROOT / "basis-research" / "artifacts"
        runs = 0
        if artifacts_dir.exists():
            runs = len(set(f.stem.split("_")[0] + "_" + f.stem.split("_")[1]
                          for f in artifacts_dir.glob("RUN-*.md") if "_" in f.stem))
        return {"runs": runs}

    # ─── Stale Data Pruning ──────────────────────────────────

    def prune_stale_data(self, max_age_days: int = 90) -> dict:
        """Poda dados stale do ecossistema."""
        print(f"\nPodando dados stale (>{max_age_days} dias)...")
        pruned = {"nexus_sessions": 0, "size_freed_kb": 0, "errors": []}

        # Nexus context_offload sessions
        offload_dir = NEXUS_DIR / "context_offload"
        if offload_dir.exists():
            cutoff = datetime.now(timezone.utc) - timedelta(days=max_age_days)
            for d in list(offload_dir.iterdir()):
                if not d.is_dir():
                    continue
                try:
                    # Check session age from directory name or mtime
                    mtime = datetime.fromtimestamp(d.stat().st_mtime, tz=timezone.utc)
                    if mtime < cutoff:
                        size = sum(f.stat().st_size for f in d.rglob("*") if f.is_file())
                        import shutil
                        shutil.rmtree(d)
                        pruned["nexus_sessions"] += 1
                        pruned["size_freed_kb"] += round(size / 1024, 1)
                        print(f"  Removida sessao stale: {d.name} ({size / 1024:.0f}KB)")
                except Exception as e:
                    pruned["errors"].append(str(e))

        # Old output dirs in criador-artigo (>30 days)
        artigo_output = ECO_ROOT / "criador-artigo" / "output"
        if artigo_output.exists():
            cutoff = datetime.now(timezone.utc) - timedelta(days=30)
            for d in list(artigo_output.iterdir()):
                if not d.is_dir():
                    continue
                try:
                    mtime = datetime.fromtimestamp(d.stat().st_mtime, tz=timezone.utc)
                    if mtime < cutoff:
                        size = sum(f.stat().st_size for f in d.rglob("*") if f.is_file())
                        import shutil
                        shutil.rmtree(d)
                        print(f"  Removido output antigo: {d.name}")
                except Exception:
                    pass

        print(f"  Total: {pruned['nexus_sessions']} sessoes removidas, {pruned['size_freed_kb']}KB liberados")
        return pruned

    # ─── Skill Generation ────────────────────────────────────

    def generate_skills_from_patterns(self) -> list[dict]:
        """Gera novas skills baseadas em padroes observados."""
        print("\nAnalisando padroes para geracao de skills...")
        new_skills = []

        # Padrao 1: Se feedback do editais-local existe, gera skill de busca
        feedback_file = EDITAIS_LOCAL_ROOT / "data" / "editais.db"
        if feedback_file.exists():
            try:
                sys.path.insert(0, str(EDITAIS_LOCAL_ROOT))
                from editais_local.feedback import obter_estatisticas
                stats = obter_estatisticas()
                total_feedback = stats.get("total_feedback", 0)
                if total_feedback > 0:
                    skill = self._create_skill(
                        name=f"evo-9-feedback-optimization",
                        title="Otimizacao de Busca por Feedback",
                        content=(
                            "Skill gerada automaticamente pelo Evolution Cycle.\n\n"
                            f"Baseada em {total_feedback} feedbacks de busca.\n"
                            "Ajusta pesos das dimensoes de busca semântica\n"
                            "com base no historico de relevancia dos usuarios.\n"
                        ),
                        category="evolution",
                    )
                    new_skills.append(skill)
            except Exception:
                pass

        # Padrao 2: Se SEEKER tem runs recentes, gera skill de integracao
        seeker_runs = self._get_seeker_stats().get("runs", 0)
        if seeker_runs >= 2:
            skill = self._create_skill(
                name=f"evo-10-seeker-integration",
                title="Integracao SEEKER-MASWOS",
                content=(
                    "Skill gerada automaticamente pelo Evolution Cycle.\n\n"
                    f"Baseada em {seeker_runs} runs do SEEKER.\n"
                    "Fluxo: Pesquisa SEEKER -> Alimentacao MASWOS -> Artigo Qualis A1\n"
                ),
                category="research",
            )
            new_skills.append(skill)

        # Padrao 3: Se bridge health > 80, gera skill de autonomia
        bridge = self._get_bridge_health()
        if bridge.get("overall_health", 0) > 80:
            skill = self._create_skill(
                name=f"evo-11-autonomous-operation",
                title="Operacao Autonoma do Ecossistema",
                content=(
                    "Skill gerada automaticamente pelo Evolution Cycle.\n\n"
                    "Habilita operacao autonomo: scheduler -> coleta -> pesquisa -> artigo -> evolucao\n"
                    "Ciclo completo sem intervencao manual.\n"
                ),
                category="system",
            )
            new_skills.append(skill)

        print(f"  {len(new_skills)} novas skills geradas")
        return new_skills

    def _create_skill(self, name: str, title: str, content: str, category: str = "evolution") -> dict:
        """Cria um arquivo de skill no diretorio apropriado."""
        skill_dir = ECO_ROOT / "skills" / category
        skill_dir.mkdir(parents=True, exist_ok=True)

        skill_file = skill_dir / f"{name}.md"
        if not skill_file.exists():
            skill_file.write_text(
                f"# {title}\n\n{content}\n\n"
                f"---\n*Gerado por Evolution Cycle em {datetime.now().isoformat()}*\n",
                encoding="utf-8",
            )
            print(f"  Skill criada: {skill_file}")
        else:
            print(f"  Skill ja existe: {skill_file}")

        return {"name": name, "path": str(skill_file), "category": category}

    # ─── Cycle Execution ──────────────────────────────────────

    def run_full_cycle(self) -> dict:
        """Executa o ciclo completo de evolucao."""
        print("=" * 60)
        print("CICLO DE EVOLUCAO DO ECOSSISTEMA")
        print("=" * 60)
        print()

        # Step 1: Collect metrics
        metrics = self.collect_metrics()

        # Step 2: Prune stale data
        pruned = self.prune_stale_data()

        # Step 3: Generate skills
        new_skills = self.generate_skills_from_patterns()

        # Step 4: Notify ecosystem bridge
        self._notify_bridge()

        cycle_result = {
            "status": "completed",
            "started_at": self.cycle_start.isoformat(),
            "completed_at": datetime.now(timezone.utc).isoformat(),
            "metrics": metrics,
            "pruned": pruned,
            "new_skills": new_skills,
        }

        # Save cycle result
        CYCLE_STATE.parent.mkdir(parents=True, exist_ok=True)
        CYCLE_STATE.write_text(json.dumps(cycle_result, ensure_ascii=False, indent=2), encoding="utf-8")

        print(f"\n{'='*60}")
        print(f"Ciclo concluido")
        print(f"Novas skills: {len(new_skills)}")
        print(f"Dados podados: {pruned['nexus_sessions']} sessoes, {pruned['size_freed_kb']}KB")
        print(f"{'='*60}")

        return cycle_result

    def _notify_bridge(self):
        bridge_script = SCRIPTS_DIR / "ecosystem_bridge.py"
        if bridge_script.exists():
            try:
                import subprocess
                subprocess.run(
                    ["python", str(bridge_script), "health"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    timeout=30,
                )
            except Exception:
                pass

    def _save_cycle_state(self):
        CYCLE_STATE.parent.mkdir(parents=True, exist_ok=True)
        CYCLE_STATE.write_text(
            json.dumps({"last_metrics": self.metrics, "last_run": self.cycle_start.isoformat()},
                       ensure_ascii=False, indent=2),
            encoding="utf-8",
        )


def cmd_run():
    cycle = EvolutionCycle()
    result = cycle.run_full_cycle()
    print(json.dumps(result, ensure_ascii=False, indent=2)[:500] + "...")


def cmd_metrics():
    cycle = EvolutionCycle()
    metrics = cycle.collect_metrics()
    print(json.dumps(metrics, ensure_ascii=False, indent=2))


def cmd_prune():
    cycle = EvolutionCycle()
    result = cycle.prune_stale_data()
    print(json.dumps(result, ensure_ascii=False, indent=2))


def cmd_generate_skills():
    cycle = EvolutionCycle()
    skills = cycle.generate_skills_from_patterns()
    print(json.dumps(skills, ensure_ascii=False, indent=2))


def cmd_status():
    if not CYCLE_STATE.exists():
        print("Nenhum ciclo executado ainda.")
        return
    data = json.loads(CYCLE_STATE.read_text(encoding="utf-8"))
    print(json.dumps(data, ensure_ascii=False, indent=2)[:1000])


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return

    cmd = sys.argv[1]
    commands = {
        "run": cmd_run,
        "metrics": cmd_metrics,
        "prune": cmd_prune,
        "generate-skills": cmd_generate_skills,
        "status": cmd_status,
    }

    if cmd in commands:
        commands[cmd]()
    else:
        print(f"Unknown command: {cmd}")
        print("Available: run, metrics, prune, generate-skills, status")


if __name__ == "__main__":
    main()
