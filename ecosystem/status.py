"""
Status — Exibe status resumido do ecossistema.
"""

from __future__ import annotations

import json
from pathlib import Path


def show_status(json_output: bool = False) -> None:
    """Exibe status do ecossistema."""
    state_path = Path("ecosystem-state.json")

    if not state_path.exists():
        print("⚠️  ecosystem-state.json não encontrado.")
        return

    try:
        state = json.loads(state_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, IOError) as e:
        print(f"ERRO: Não foi possível ler ecosystem-state.json: {e}")
        return

    if json_output:
        print(json.dumps(state, indent=2, ensure_ascii=False))
        return

    # Formato texto
    version = state.get("version", "?")
    cycle = state.get("current_cycle", "?")
    tests = state.get("tests_passing", 0)
    total_cts = state.get("total_cts", 0)
    specs = state.get("specs_count", 0)
    agents = state.get("agents_count", 0)
    skills = state.get("skills_count", 0)
    mcps = state.get("mcps_count", 0)
    last_update = state.get("last_updated", "?")

    history = state.get("history", {})
    scores = [v for k, v in sorted(history.items()) if isinstance(v, (int, float))]
    trend = f"{scores[-1]}" if scores else "N/A"

    print("=" * 60)
    print(f"  OpenCode Ecosystem — Status do Sistema")
    print("=" * 60)
    print(f"  Versão:          {version} (ciclo {cycle})")
    print(f"  Última atualização: {last_update}")
    print(f"  Testes passando: {tests}/{total_cts} CTs ({trend}% score)")
    print(f"  SPECs:           {specs}")
    print(f"  Agentes:         {agents}")
    print(f"  Skills:          {skills}")
    print(f"  MCPs:            {mcps}")
    print("-" * 60)

    # Scanners
    scanners = state.get("scanners", {})
    if scanners:
        print("  Scanners:")
        print(f"    Noológico:         {scanners.get('noological_coverage', 'N/A')}%")
        print(f"    Potentiality V2:   {scanners.get('potentiality_v2_viable', 'N/A')} oportunidades viáveis")

    # CI/CD
    cicd = state.get("ci_cd", {})
    if cicd:
        print(f"  CI/CD:           {'✅ Ativo' if cicd.get('github_actions') else '❌ Inativo'}")

    # Self-repair
    sr = state.get("self_repair", {})
    if sr:
        print(f"  Self-Repair:     {sr.get('health_pct', 'N/A')}% saúde")

    print("=" * 60)
