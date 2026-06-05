#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SEEKER → criador-artigo Bridge
Conecta outputs de pesquisa do SEEKER ao pipeline MASWOS Agent Executor.

Uso:
  python seeker_bridge.py from-seeker <seeker_artifacts_dir> --level 2
  python seeker_bridge.py from-editais <edital_id> --level 2
  python seeker_bridge.py list-seeker-runs
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional

CRIADOR_DIR = Path(__file__).resolve().parent
SEEKER_DIR = CRIADOR_DIR.parent / "basis-research"
OUTPUT_DIR = CRIADOR_DIR / "output"


class SeekerBridge:
    """Bridge entre SEEKER e criador-artigo."""

    @staticmethod
    def list_seeker_runs() -> list[dict]:
        """Lista runs disponiveis do SEEKER."""
        artifacts_dir = SEEKER_DIR / "artifacts"
        if not artifacts_dir.exists():
            return []

        runs = {}
        for f in sorted(artifacts_dir.glob("RUN-*")):
            # Extract run ID from filename
            parts = f.stem.split("_")
            run_id = f"{parts[0]}_{parts[1]}" if len(parts) >= 2 else parts[0]
            if run_id not in runs:
                runs[run_id] = {"run_id": run_id, "files": [], "first_file": f.stem}
            runs[run_id]["files"].append(f.stem)

        return list(runs.values())

    @staticmethod
    def load_seeker_outputs(run_id: Optional[str] = None) -> dict:
        """Carrega outputs de uma run do SEEKER."""
        artifacts_dir = SEEKER_DIR / "artifacts"
        if not artifacts_dir.exists():
            return {}

        outputs = {}
        for f in sorted(artifacts_dir.glob("*.md")):
            if run_id and run_id not in f.stem:
                continue
            content = f.read_text(encoding="utf-8")
            agent_type = f.stem.split("_", 2)[-1] if "_" in f.stem else f.stem
            outputs[agent_type] = {
                "file": f.name,
                "content": content[:5000],
                "size": len(content),
            }

        return outputs

    @staticmethod
    def build_article_prompt(seeker_outputs: dict, tema: str, level: int = 2) -> str:
        """Constroi um prompt de artigo combinando outputs do SEEKER."""
        parts = [
            f"# Artigo Cientifico: {tema}\n",
            f"## Nivel: {level}\n",
            "## Fontes de Pesquisa (SEEKER)\n\n",
        ]

        for agent_type, data in seeker_outputs.items():
            label = agent_type.replace("_", " ").title()
            parts.append(f"### {label}\n{data['content'][:2000]}\n\n")

        parts.append(
            "## Instrucao\n"
            "Produza um artigo cientifico completo em Portugues Brasileiro formal "
            "utilizando as pesquisas acima como fundamentacao.\n"
        )

        return "\n".join(parts)

    @staticmethod
    def feed_to_maswos(tema: str, seeker_outputs: dict, level: int = 2) -> dict:
        """Alimenta outputs do SEEKER no MASWOS Agent Executor."""
        sys.path.insert(0, str(CRIADOR_DIR))
        from executor import AgentExecutor

        executor = AgentExecutor(tema=tema, level=level)

        # Add seeker outputs as initial context
        seeker_summary = {}
        for agent_type, data in seeker_outputs.items():
            seeker_summary[agent_type] = data["content"][:3000]

        executor.state.outputs["_seeker"] = json.dumps(seeker_summary, ensure_ascii=False)

        # Run the pipeline
        result = executor.run_full()
        return result


def cmd_from_seeker(seeker_run_id: str, level: int = 2):
    """Executa pipeline a partir de outputs do SEEKER."""
    bridge = SeekerBridge()
    outputs = bridge.load_seeker_outputs(seeker_run_id)

    if not outputs:
        print(f"Nenhum output encontrado para run {seeker_run_id}")
        return

    # Try to infer tema from first output
    first = list(outputs.values())[0]
    tema = first["content"][:200].split("\n")[0] if first["content"] else "Pesquisa Academica"
    tema = tema.replace("#", "").strip()[:80]

    print(f"Run SEEKER: {seeker_run_id}")
    print(f"Agents: {len(outputs)}")
    print(f"Tema inferido: {tema}")
    print(f"Nivel: {level}")
    print()

    result = bridge.feed_to_maswos(tema, outputs, level)

    print(json.dumps({
        "status": "completed",
        "seeker_run": seeker_run_id,
        "tema": tema,
        "agents_executed": result.get("agents_executed", 0),
        "output_dir": result.get("output_dir"),
    }, ensure_ascii=False, indent=2))


def cmd_list_seeker_runs():
    """Lista runs do SEEKER."""
    runs = SeekerBridge.list_seeker_runs()
    if not runs:
        print("Nenhuma run do SEEKER encontrada.")
        return

    print(f"\nRuns do SEEKER disponiveis ({len(runs)}):")
    print("-" * 60)
    for r in runs:
        print(f"  {r['run_id']} ({len(r['files'])} arquivos)")
    print()


def cmd_from_editais(edital_id: str, level: int = 2):
    """Executa pipeline a partir de um edital especifico."""
    # Busca edital no editais-local
    import subprocess
    try:
        result = subprocess.run(
            ["editais-local", "semantic-search", edital_id, "--k", "1"],
            capture_output=True, text=True, timeout=30,
        )
        tema = f"Edital {edital_id}: {result.stdout[:100] if result.stdout else edital_id}"
    except Exception:
        tema = f"Analise de Edital: {edital_id}"

    # Create minimal seeker-style output
    seeker_outputs = {
        "editais_context": {
            "file": f"edital_{edital_id}",
            "content": f"Edital ID: {edital_id}\nContexto: {tema}",
            "size": len(tema),
        }
    }

    result = SeekerBridge.feed_to_maswos(tema, seeker_outputs, level)
    print(json.dumps(result, ensure_ascii=False, indent=2))


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return

    cmd = sys.argv[1]

    if cmd == "from-seeker":
        if len(sys.argv) < 3:
            print("Usage: seeker_bridge.py from-seeker <seeker_artifacts_dir> [--level N]")
            return
        run_id = sys.argv[2]
        level = int(sys.argv[4]) if len(sys.argv) > 4 and sys.argv[3] == "--level" else 2
        cmd_from_seeker(run_id, level)

    elif cmd == "from-editais":
        if len(sys.argv) < 3:
            print("Usage: seeker_bridge.py from-editais <edital_id> [--level N]")
            return
        edital_id = sys.argv[2]
        level = int(sys.argv[4]) if len(sys.argv) > 4 and sys.argv[3] == "--level" else 2
        cmd_from_editais(edital_id, level)

    elif cmd == "list-seeker-runs":
        cmd_list_seeker_runs()

    else:
        print(f"Unknown command: {cmd}")
        print("Available: from-seeker, from-editais, list-seeker-runs")


if __name__ == "__main__":
    main()
