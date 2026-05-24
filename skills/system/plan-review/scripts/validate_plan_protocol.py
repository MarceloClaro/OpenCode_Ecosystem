import re
import sys
import argparse
from pathlib import Path

def validar_plano(caminho_plano: Path) -> dict:
    relatorio = {
        "has_yaml_frontmatter": False,
        "has_goal": False,
        "has_context_decisions": False,
        "phases_status_ok": True,
        "hierarchical_numbering": True,
        "one_current_task": False,
        "errors": []
    }
    
    try:
        content = caminho_plano.read_text(encoding="utf-8", errors="ignore")
    except Exception as e:
        relatorio["errors"].append(f"Nao foi possivel ler o arquivo: {str(e)}")
        return relatorio

    # 1. Validar YAML Frontmatter
    if content.startswith("---"):
        end_frontmatter = content.find("---", 3)
        if end_frontmatter != -1:
            frontmatter_text = content[3:end_frontmatter]
            if "status:" in frontmatter_text and "phase:" in frontmatter_text and "updated:" in frontmatter_text:
                relatorio["has_yaml_frontmatter"] = True
            else:
                relatorio["errors"].append("YAML Frontmatter incompleto. Deve conter 'status', 'phase' e 'updated'.")
        else:
            relatorio["errors"].append("YAML Frontmatter nao fechado com '---'.")
    else:
        relatorio["errors"].append("YAML Frontmatter inicial '---' ausente.")

    # 2. Validar ## Goal
    if re.search(r"^##\s+Goal", content, re.M | re.I):
        relatorio["has_goal"] = True
    else:
        relatorio["errors"].append("Secao '## Goal' ausente.")

    # 3. Validar ## Context & Decisions
    if re.search(r"^##\s+Context\s+&\s+Decisions", content, re.M | re.I):
        relatorio["has_context_decisions"] = True
    else:
        relatorio["errors"].append("Secao '## Context & Decisions' ausente.")

    # 4. Validar fases e tarefas
    lines = content.splitlines()
    current_tasks_count = 0
    task_pattern = re.compile(r"^\s*[-*]\s+\[\s*\]\s+(\d+\.\d+)\s+")
    
    for idx, line in enumerate(lines, 1):
        # Verificar marcador de tarefa atual
        if "← CURRENT" in line:
            current_tasks_count += 1
        
        # Verificar status das fases
        if "Phase" in line or "Fase" in line:
            if not any(status in line for status in ["[COMPLETE]", "[IN PROGRESS]", "[PENDING]"]):
                relatorio["phases_status_ok"] = False
                relatorio["errors"].append(f"Linha {idx}: Fase sem marcador de status valido ([COMPLETE], [IN PROGRESS], [PENDING]).")
        
        # Verificar numeracao hierarquica
        if "task" in line.lower() or "tarefa" in line.lower():
            # Se for uma linha de item de tarefa, tentar encontrar numeracao (ex: 1.1)
            if any(char.isdigit() for char in line) and "." not in line:
                relatorio["hierarchical_numbering"] = False
                relatorio["errors"].append(f"Linha {idx}: Possivel tarefa sem numeracao hierarquica (ex: 1.1, 1.2).")

    if current_tasks_count == 1:
        relatorio["one_current_task"] = True
    else:
        relatorio["errors"].append(f"Quantidade incorreta de tarefas ativas (← CURRENT): {current_tasks_count}. Deve haver exatamente 1.")

    return relatorio

def main():
    parser = argparse.ArgumentParser(description="Validador automatico de conformidade com o Plan Protocol")
    parser.add_argument("plano", help="Caminho do arquivo markdown do plano")
    args = parser.parse_args()

    caminho = Path(args.plano)
    if not caminho.is_file():
        print(f"Erro: O arquivo '{caminho}' nao existe.")
        sys.exit(1)

    print(f"Analisando plano: {caminho.name}...\n")
    rel = validar_plano(caminho)

    print("=== CHECKLIST DE CONFORMIDADE ===")
    print(f"[{'OK' if rel['has_yaml_frontmatter'] else 'FAIL'}] YAML Frontmatter (status, phase, updated)")
    print(f"[{'OK' if rel['has_goal'] else 'FAIL'}] Secao ## Goal")
    print(f"[{'OK' if rel['has_context_decisions'] else 'FAIL'}] Secao ## Context & Decisions")
    print(f"[{'OK' if rel['phases_status_ok'] else 'FAIL'}] Status das Fases ([COMPLETE]/[IN PROGRESS]/[PENDING])")
    print(f"[{'OK' if rel['hierarchical_numbering'] else 'FAIL'}] Numeracao Hierarquica das Tarefas")
    print(f"[{'OK' if rel['one_current_task'] else 'FAIL'}] Exatamente UMA tarefa ativa (← CURRENT)")
    print()

    if rel["errors"]:
        print("=== DETALHES DAS INCONFORMIDADES ===")
        for err in rel["errors"]:
            print(f"- {err}")
        print("\nO plano nao esta em total conformidade com o Plan Protocol.")
        sys.exit(1)
    else:
        print("Sucesso: O plano atende a todas as exigencias do Plan Protocol!")
        sys.exit(0)

if __name__ == "__main__":
    main()
