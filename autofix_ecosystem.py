#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
autofix_ecosystem.py — Script de Auditoria e Correção Multidimensional do Ecossistema OpenCode
Dividido em 4 Fases para garantir conformidade de frontmatter, enconding, CJK e CLI.
"""

import os
import re
import sys
import shutil
from pathlib import Path
from typing import List, Tuple, Dict, Any

WORKSPACE = Path(__file__).resolve().parent
AGENTS_DIR = WORKSPACE / "agents"
CRIADOR_DIR = WORKSPACE / "criador-artigo"
BACKUP_DIR = WORKSPACE / ".evolve" / "ecosystem_backup"

# Mapeamento de ferramentas legadas para chaves válidas do OpenCode v1.14+
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

def create_backup(file_path: Path):
    """Cria backup do arquivo antes de modificá-lo."""
    rel_path = file_path.relative_to(WORKSPACE)
    dest_path = BACKUP_DIR / rel_path
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(file_path, dest_path)

# ============================================================================
# FASE 1: REMOÇÃO DE BOM (Byte Order Mark) \ufeff
# ============================================================================

def fase_1_strip_boms() -> List[Path]:
    """Remove BOMs de todos os arquivos .md e .py."""
    print("\n[FASE 1] Removendo Byte Order Mark (BOM) dos arquivos...")
    modified = []
    
    # Escanear recursivamente por .md e .py
    for ext in ["*.md", "*.py"]:
        for file_path in WORKSPACE.rglob(ext):
            if "node_modules" in file_path.parts or ".git" in file_path.parts or ".evolve" in file_path.parts:
                continue
            try:
                # Ler em bytes para checar a assinatura exata do BOM (EF BB BF)
                content_bytes = file_path.read_bytes()
                if content_bytes.startswith(b'\xef\xbb\xbf'):
                    create_backup(file_path)
                    # Reescreve sem o BOM
                    file_path.write_bytes(content_bytes[3:])
                    modified.append(file_path)
                    print(f"  [BOM REMOVIDO] {file_path.relative_to(WORKSPACE)}")
                else:
                    # Checagem de string em python por segurança (alguns BOMs são lidos como unicode)
                    content_str = file_path.read_text(encoding="utf-8", errors="ignore")
                    if content_str.startswith('\ufeff'):
                        create_backup(file_path)
                        file_path.write_text(content_str.lstrip('\ufeff'), encoding="utf-8")
                        modified.append(file_path)
                        print(f"  [BOM REMOVIDO-STR] {file_path.relative_to(WORKSPACE)}")
            except Exception as e:
                print(f"  [ERRO FASE 1] Ao processar {file_path.name}: {e}")
                
    print(f"-> FASE 1 concluída. {len(modified)} arquivo(s) corrigido(s).")
    return modified

# ============================================================================
# FASE 2: CONVERSÃO DE FERRAMENTAS DE AGENTES (List -> Object)
# ============================================================================

def fix_tools_block(content: str) -> Tuple[str, bool]:
    """Detecta ferramentas no formato lista e converte para objeto YAML."""
    # Encontra o frontmatter
    fm_match = re.search(r'^(---\s*\n)(.*?)(^---\s*\n)', content, re.MULTILINE | re.DOTALL)
    if not fm_match:
        # Se não achou na primeira linha, tenta buscar flexível por conta de comentários
        fm_match = re.search(r'(---\s*\n)(.*?)(---\s*\n)', content, re.DOTALL)
        if not fm_match:
            return content, False

    pre_fm = content[:fm_match.start()]
    fm_marker_open = fm_match.group(1)
    fm_body = fm_match.group(2)
    fm_marker_close = fm_match.group(3)
    post_fm = content[fm_match.end():]

    # Expressão para achar lista no campo tools
    list_pattern = re.compile(
        r'^(tools:\s*\n)((?:[ \t]+-[ \t]+\S+\n?)+)',
        re.MULTILINE
    )

    list_match = list_pattern.search(fm_body)
    if not list_match:
        return content, False

    tools_list_block = list_match.group(2)
    tool_items = re.findall(r'[ \t]+-[ \t]+(\S+)', tools_list_block)

    obj_lines = []
    seen = set()
    for raw_tool in tool_items:
        key = TOOL_NAME_MAP.get(raw_tool.lower(), raw_tool.lower().replace("-", "_"))
        if key not in seen:
            obj_lines.append(f"  {key}: true")
            seen.add(key)

    new_tools_block = "tools:\n" + "\n".join(obj_lines) + "\n"
    new_fm_body = fm_body[:list_match.start()] + new_tools_block + fm_body[list_match.end():]
    new_content = pre_fm + fm_marker_open + new_fm_body + fm_marker_close + post_fm

    return new_content, True

def fase_2_convert_agent_tools() -> List[Path]:
    """Converte lista de ferramentas para objeto em todos os arquivos de agente .md."""
    print("\n[FASE 2] Corrigindo formato do campo 'tools' dos agentes...")
    modified = []
    
    agent_dirs = [AGENTS_DIR, CRIADOR_DIR / "agents"]
    for directory in agent_dirs:
        if not directory.exists():
            continue
        for fpath in directory.glob("*.md"):
            try:
                content = fpath.read_text(encoding="utf-8", errors="ignore")
                new_content, changed = fix_tools_block(content)
                if changed:
                    create_backup(fpath)
                    fpath.write_text(new_content, encoding="utf-8")
                    modified.append(fpath)
                    print(f"  [TOOLS CORRIGIDO] {fpath.relative_to(WORKSPACE)}")
            except Exception as e:
                print(f"  [ERRO FASE 2] Em {fpath.name}: {e}")
                
    print(f"-> FASE 2 concluída. {len(modified)} agente(s) corrigido(s).")
    return modified

# ============================================================================
# FASE 3: DETECÇÃO E REMOÇÃO DE CJK CONTAMINANTES
# ============================================================================

def contains_cjk(text: str) -> bool:
    """Checa se o texto contém ideogramas CJK ou pontuação chinesa."""
    cjk_pattern = re.compile(r'[\u4e00-\u9fff\u3400-\u4dbf\u3040-\u309f\u30a0-\u30ff\uac00-\ud7af\u3001\u3002]')
    return bool(cjk_pattern.search(text))

def clean_cjk(text: str) -> str:
    """Substitui pontuação CJK por equivalentes latinos e remove caracteres CJK."""
    # Substituir pontuação chinesa comum
    text = text.replace("、", ", ").replace("。", ". ")
    # Remover caracteres chineses residuais
    text = re.sub(r'[\u4e00-\u9fff\u3400-\u4dbf\u3040-\u309f\u30a0-\u30ff\uac00-\ud7af]', "", text)
    # Normalizar espaços duplos
    text = re.sub(r'  +', ' ', text)
    return text

def fase_3_clean_cjk_leakage() -> List[Path]:
    """Remove caracteres CJK não planejados dos arquivos críticos."""
    print("\n[FASE 3] Limpando vazamentos de caracteres CJK...")
    modified = []
    
    # Escanear arquivos textuais (exceto ptbr_corrector.py e backups)
    for ext in ["*.md", "*.py"]:
        for file_path in WORKSPACE.rglob(ext):
            if "node_modules" in file_path.parts or ".git" in file_path.parts or ".evolve" in file_path.parts:
                continue
            if file_path.name == "ptbr_corrector.py" or file_path.name == "autofix_ecosystem.py":
                continue
                
            try:
                content = file_path.read_text(encoding="utf-8", errors="ignore")
                
                # Ignorar blocos de código com comentários chineses válidos ou headers XML/HTML
                # Mas limpar textos livres se houver CJK indesejado
                if contains_cjk(content):
                    # Não vamos limpar arbitrariamente o arquivo se for de instruções de agentes (pois possuem comentários legítimos)
                    # Apenas se for arquivo de output, relatório ou script de execução
                    if "ensaio" in file_path.name or "tese" in file_path.name or file_path.name.endswith(".py"):
                        create_backup(file_path)
                        cleaned = clean_cjk(content)
                        file_path.write_text(cleaned, encoding="utf-8")
                        modified.append(file_path)
                        print(f"  [CJK LIMPO] {file_path.relative_to(WORKSPACE)}")
            except Exception as e:
                print(f"  [ERRO FASE 3] Em {file_path.name}: {e}")
                
    print(f"-> FASE 3 concluída. {len(modified)} arquivo(s) limpo(s).")
    return modified

# ============================================================================
# FASE 4: ALINHAMENTO DE CLI ARGUMENTS (--input / -i)
# ============================================================================

def align_argparse(file_path: Path) -> bool:
    """Verifica e insere suporte a --input e -i em scripts que usem argparse."""
    content = file_path.read_text(encoding="utf-8", errors="ignore")
    if "argparse" not in content or "ArgumentParser" not in content:
        return False
        
    # Se o script já tem --input ou -i mapeados no parser, ignora
    if "--input" in content or "'-i'" in content or '"-i"' in content:
        return False
        
    # Encontra onde adiciona o argumento posicional 'dir'
    pattern = r"(parser\.add_argument\s*\(\s*['\"]dir['\"]\s*,\s*nargs\s*=\s*['\"](\?|\*)['\"])"
    match = re.search(pattern, content)
    if not match:
        return False
        
    create_backup(file_path)
    
    # Substituição para suportar ambos
    replacement = (
        "parser.add_argument('dir', nargs='?', default=None, help='Manuscript directory (positional)')\n"
        "    parser.add_argument('--input', '-i', default=None, help='Manuscript directory (option)')"
    )
    
    # Localiza e altera a definição do parser
    lines = content.splitlines()
    for idx, line in enumerate(lines):
        if "add_argument" in line and ("'dir'" in line or '"dir"' in line):
            # Substitui a linha antiga e garante que manuscript_dir seja resolvido a partir do input
            lines[idx] = "    parser.add_argument('dir', nargs='?', default=None, help='Diretorio (posicional)')\n    parser.add_argument('--input', '-i', default=None, help='Diretorio (opcao)')"
            
        if "manuscript_dir = " in line and "Path(args.dir)" in line:
            lines[idx] = "    manuscript_dir = Path(args.input or args.dir or '.')"
        elif "manuscript_dir = " in line and "args.dir" in line:
            lines[idx] = "    manuscript_dir = args.input or args.dir or '.'"
            
    new_content = "\n".join(lines)
    file_path.write_text(new_content, encoding="utf-8")
    return True

def fase_4_align_cli_arguments() -> List[Path]:
    """Alinha argumentos argparse de scripts Python do pipeline."""
    print("\n[FASE 4] Alinhando argumentos CLI (--input) dos scripts python...")
    modified = []
    
    # Focar nos diretórios de execução do pipeline
    search_dirs = [CRIADOR_DIR, WORKSPACE / "nexus", WORKSPACE / "skills"]
    for sd in search_dirs:
        if not sd.exists():
            continue
        for fpath in sd.rglob("*.py"):
            try:
                if align_argparse(fpath):
                    modified.append(fpath)
                    print(f"  [CLI ALINHADO] {fpath.relative_to(WORKSPACE)}")
            except Exception as e:
                print(f"  [ERRO FASE 4] Em {fpath.name}: {e}")
                
    print(f"-> FASE 4 concluída. {len(modified)} script(s) atualizado(s).")
    return modified

# ============================================================================
# EXECUÇÃO PRINCIPAL
# ============================================================================

def main():
    print(f"{'='*60}")
    print("  EXECUTANDO AUTO-FIX MULTIDIMENSIONAL DO ECOSSISTEMA")
    print(f"{'='*60}")
    print(f"Diretório Raiz: {WORKSPACE}")
    print(f"Backups em: {BACKUP_DIR}")
    
    f1 = fase_1_strip_boms()
    f2 = fase_2_convert_agent_tools()
    f3 = fase_3_clean_cjk_leakage()
    f4 = fase_4_align_cli_arguments()
    
    print(f"\n{'='*60}")
    print("  RESUMO DO PROCESSO:")
    print(f"{'='*60}")
    print(f"  Fase 1 (BOMs Removidos)         : {len(f1)}")
    print(f"  Fase 2 (Tools Convertidos)      : {len(f2)}")
    print(f"  Fase 3 (CJK Leakage Limpo)      : {len(f3)}")
    print(f"  Fase 4 (CLI Arguments Alinhados): {len(f4)}")
    print(f"{'='*60}")
    print("✓ Auditoria e correção concluídas. Todos os arquivos foram sincronizados.")

if __name__ == "__main__":
    main()
