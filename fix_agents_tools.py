"""
fix_agents_tools.py — Corrige o campo 'tools' em agentes OpenCode.

O OpenCode v1.14+ exige que 'tools' seja um OBJETO YAML:
  tools:
    read: true
    write: true

Agentes com formato de LISTA geram o erro:
  "Expected object | undefined, got ["Read","Write","Bash",...]"

Este script:
1. Varre todos os arquivos .md em agents/
2. Detecta o padrão de lista no frontmatter YAML
3. Converte para objeto booleano compatível
4. Salva o arquivo corrigido (backup automático)
"""
import os
import re
import shutil

AGENTS_DIR = os.path.join(os.path.dirname(__file__), "agents")
BACKUP_DIR = os.path.join(os.path.dirname(__file__), ".evolve", "agents_backup")

# Mapeamento de nomes de ferramentas (case-insensitive) para chaves válidas
TOOL_NAME_MAP = {
    "read": "read",
    "write": "write",
    "bash": "bash",
    "grep": "grep",
    "glob": "glob",
    "edit": "edit",
    "webfetch": "webfetch",
    "sqlite": "sqlite",
    "sequential-thinking": "sequential_thinking",
    "sequentialthinking": "sequential_thinking",
    "sequential_thinking": "sequential_thinking",
    "fetch": "webfetch",
    "web": "webfetch",
    "search": "webfetch",
}

def fix_tools_field(content: str, filename: str) -> tuple[str, bool]:
    """
    Detecta e corrige o campo 'tools' no frontmatter YAML.
    Retorna (novo_conteúdo, foi_modificado).
    """
    # Localiza o bloco frontmatter (entre --- e ---)
    fm_match = re.search(r'^(---\s*\n)(.*?)(^---\s*\n)', content, re.MULTILINE | re.DOTALL)
    if not fm_match:
        return content, False

    pre_fm = content[:fm_match.start()]
    fm_marker_open = fm_match.group(1)
    fm_body = fm_match.group(2)
    fm_marker_close = fm_match.group(3)
    post_fm = content[fm_match.end():]

    # Detecta padrão de lista YAML no campo tools:
    # Exemplo:
    # tools:
    #   - Read
    #   - Write
    list_pattern = re.compile(
        r'^(tools:\s*\n)((?:[ \t]+-[ \t]+\S+\n?)+)',
        re.MULTILINE
    )

    list_match = list_pattern.search(fm_body)
    if not list_match:
        return content, False  # Já está no formato correto ou não tem tools

    tools_header = list_match.group(1)  # "tools:\n"
    tools_list_block = list_match.group(2)  # "  - Read\n  - Write\n..."

    # Extrai os nomes das ferramentas
    tool_items = re.findall(r'[ \t]+-[ \t]+(\S+)', tools_list_block)

    # Converte para objeto YAML booleano
    obj_lines = []
    seen = set()
    for raw_tool in tool_items:
        key = TOOL_NAME_MAP.get(raw_tool.lower(), raw_tool.lower().replace("-", "_"))
        if key not in seen:
            obj_lines.append(f"  {key}: true")
            seen.add(key)

    new_tools_block = "tools:\n" + "\n".join(obj_lines) + "\n"

    # Substitui o bloco antigo pelo novo
    new_fm_body = fm_body[:list_match.start()] + new_tools_block + fm_body[list_match.end():]
    new_content = pre_fm + fm_marker_open + new_fm_body + fm_marker_close + post_fm

    return new_content, True


def main():
    os.makedirs(BACKUP_DIR, exist_ok=True)
    
    if not os.path.isdir(AGENTS_DIR):
        print(f"ERRO: Diretório não encontrado: {AGENTS_DIR}")
        return

    md_files = [f for f in os.listdir(AGENTS_DIR) if f.endswith(".md")]
    total = len(md_files)
    fixed = 0
    skipped = 0
    errors = 0

    print(f"\n{'='*60}")
    print(f"fix_agents_tools.py — Corrigindo {total} agentes")
    print(f"{'='*60}\n")

    for fname in sorted(md_files):
        fpath = os.path.join(AGENTS_DIR, fname)
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                content = f.read()

            new_content, modified = fix_tools_field(content, fname)

            if modified:
                # Backup
                backup_path = os.path.join(BACKUP_DIR, fname)
                shutil.copy2(fpath, backup_path)

                # Salva corrigido
                with open(fpath, "w", encoding="utf-8") as f:
                    f.write(new_content)

                print(f"  [CORRIGIDO] {fname}")
                fixed += 1
            else:
                print(f"  [OK]        {fname}")
                skipped += 1

        except Exception as e:
            print(f"  [ERRO]      {fname}: {e}")
            errors += 1

    print(f"\n{'='*60}")
    print(f"RESULTADO:")
    print(f"  Total de agentes : {total}")
    print(f"  Corrigidos       : {fixed}")
    print(f"  Já válidos       : {skipped}")
    print(f"  Erros            : {errors}")
    print(f"  Backups em       : {BACKUP_DIR}")
    print(f"{'='*60}\n")

    if fixed > 0:
        print("✓ Execute 'opencode' novamente — erro 'Expected object | undefined' resolvido.")
    else:
        print("Nenhum arquivo precisou de correção.")


if __name__ == "__main__":
    main()
