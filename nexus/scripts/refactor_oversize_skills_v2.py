#!/usr/bin/env python3
"""
Refatorador Progressive Disclosure v2 - abordagem mais robusta.
Para cada skill oversized:
  1. Le SKILL.md completo
  2. Identifica secoes por heading (##, ###)
  3. Move secoes densas (tabelas, code blocks, wizards) para references/*.md
  4. Reescreve SKILL.md com versao leve (~2KB) + ponteiros

Uso:
    python nexus/scripts/refactor_oversize_skills_v2.py [--dry-run] [skill_name]
"""

import os, re, sys, shutil
from pathlib import Path

# Config encoding for Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE = Path(r"C:\Users\marce\.config\opencode")

def read_file_utf8(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def write_file_utf8(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

def get_heading_level(line):
    """Returns (level, text) for a heading line, or None."""
    stripped = line.strip()
    m = re.match(r'^(#{1,6})\s+(.+)$', stripped)
    if m:
        return len(m.group(1)), m.group(2).strip()
    return None

def split_sections(content):
    """
    Divide o conteudo em secoes baseadas em headings ##.
    Retorna lista de (heading_text, lines_list, is_top_level)
    """
    lines = content.split('\n')
    sections = []
    current_heading = "HEADER"
    current_lines = []
    
    for line in lines:
        hl = get_heading_level(line)
        if hl and hl[0] == 2:  # ## heading
            if current_lines:
                sections.append((current_heading, current_lines))
            current_heading = hl[1]
            current_lines = [line]
        else:
            current_lines.append(line)
    
    if current_lines:
        sections.append((current_heading, current_lines))
    
    return sections

def estimate_section_size(section_lines):
    """Estimate the byte size of a section."""
    return len('\n'.join(section_lines).encode('utf-8'))

def is_reference_section(heading_text, content_joined):
    """
    Determina se uma secao contem dados de referencia extraiveis.
    Returns True se a secao tem tabelas grandes, code blocks, ou configs.
    """
    # Check for large tables
    table_lines = [l for l in content_joined.split('\n') if l.strip().startswith('|') and '|' in l.strip()[1:]]
    if len(table_lines) > 5:
        return True
    
    # Check for large code blocks
    code_blocks = re.findall(r'```[\s\S]*?```', content_joined)
    total_code_chars = sum(len(cb) for cb in code_blocks)
    if total_code_chars > 500:
        return True
    
    # Check for lists of items (configs, examples)
    list_items = [l for l in content_joined.split('\n') if l.strip().startswith(('- ', '* ', '1. ', '2. '))]
    if len(list_items) > 10 and total_code_chars > 200:
        return True
    
    # Keywords indicating reference data
    ref_keywords = ['tabela', 'templates', 'parametro', 'configuracao', 'exemplo',
                    'referencia', 'api', 'schema', 'formato', 'categoria',
                    'wizard', 'css', 'html', 'dados']
    heading_lower = heading_text.lower()
    if any(kw in heading_lower for kw in ref_keywords):
        if estimate_section_size(content_joined.split('\n') if isinstance(content_joined, str) else content_joined) > 300:
            return True
    
    return False

def create_ref_pointer(heading_text, ref_filename):
    """Create a pointer line for the reference file."""
    return f"\n> *Detalhes em [`references/{ref_filename}`](references/{ref_filename})*\n"

# ─── REGRAS DE REFATORACAO POR SKILL ──────────────────────────────────────
# Estrutura: { "skill_name": { "path": "...", "keep_sections": [...], "ref_sections": {...}, "duplicates": [...] } }
# "keep_sections": lista de headings ## que DEVEM permanecer (parcial match)
# "ref_sections": dict { "references/file.md": ["heading1", "heading2"] }

SKILL_CONFIGS = {
    # ══════════════════════════════════════════════════════════════
    # GRUPO A: JURIDICOS (.claude/skills/)
    # ══════════════════════════════════════════════════════════════
    "pecas-juridicas-html": {
        "path": ".claude/skills/pecas-juridicas-html",
        "duplicates": ["skills/juridico/pecas-juridicas-html"],
        "keep_sections": [
            "pecas-juridicas-html",
            "Quando usar",
            "Trigger",
            "Fluxo rapido",
            "Regras importantes",
            "Constraint",
        ],
        "ref_sections": {
            "wizard-configuracao.md": ["Wizard de Configura"],
            "css-cores.md": ["Paleta de Cores"],
            "templates-html.md": ["Templates de Pecas"],
            "dados-escritorio.md": ["dados-escritorio", "Dados obrigatorios", "Dados opcionais"],
        },
    },
    "edicao-cirurgica": {
        "path": ".claude/skills/edicao-cirurgica",
        "duplicates": ["skills/juridico/edicao-cirurgica"],
        "keep_sections": [
            "edicao-cirurgica",
            "Quando usar",
            "Quando NAO usar",
            "Regra de ouro",
            "Trigger",
            "Nunca",
            "Regra absoluta",
        ],
        "ref_sections": {
            "formatos-suportados.md": ["Formatos Suportados"],
            "exemplos.md": ["Exemplos"],
        },
    },
    "gerador-contratos": {
        "path": ".claude/skills/gerador-contratos",
        "duplicates": ["skills/juridico/gerador-contratos"],
        "keep_sections": [
            "gerador-contratos",
            "Quando usar",
            "Trigger",
            "Fluxo de uso",
            "Regras",
        ],
        "ref_sections": {
            "tipos-contrato.md": ["Tipos de Contrato"],
            "css-templates.md": ["CSS", "Templates HTML"],
        },
    },
    "pesquisa-jurisprudencia": {
        "path": ".claude/skills/pesquisa-jurisprudencia",
        "duplicates": ["skills/juridico/pesquisa-jurisprudencia"],
        "keep_sections": [
            "pesquisa-jurisprudencia",
            "Quando usar",
            "Trigger",
            "Fluxo de pesquisa",
        ],
        "ref_sections": {
            "tribunais-fontes.md": ["Tribunais", "Fontes"],
            "parametros-busca.md": ["Parametros", "Filtros"],
        },
    },
    "followup-advocacia": {
        "path": ".claude/skills/followup-advocacia",
        "duplicates": ["skills/juridico/followup-advocacia"],
        "keep_sections": [
            "followup-advocacia",
            "Quando usar",
            "Trigger",
            "Fluxo",
            "Metricas",
        ],
        "ref_sections": {
            "cadencia-contato.md": ["Cadencia"],
            "pipeline-demandas.md": ["Pipeline"],
        },
    },
    "triagem-juridica": {
        "path": ".claude/skills/triagem-juridica",
        "duplicates": ["skills/juridico/triagem-juridica"],
        "keep_sections": [
            "triagem-juridica",
            "Quando usar",
            "Trigger",
            "Fluxo",
        ],
        "ref_sections": {
            "tabela-classificacao.md": ["Classificacao", "Area do Direito"],
            "perguntas-triagem.md": ["Perguntas", "Roteiro"],
        },
    },
    
    # ══════════════════════════════════════════════════════════════
    # GRUPO B: CRIADOR-ARTIGO + GENESIS-WRITER + NEXUS
    # ══════════════════════════════════════════════════════════════
    "criador-artigo": {
        "path": "criador-artigo",
        "keep_sections": [
            "criador-artigo",
            "Quando usar",
            "Pipeline",
            "Fluxo",
            "Trigger",
            "Regras",
        ],
        "ref_sections": {
            "tabelas-volume-prazo.md": ["Volume", "Prazo"],
            "rubrica-avaliacao.md": ["Avaliacao", "Rubrica", "AUTO_SCORE", "score"],
            "detalhes-citacoes.md": ["Citacoes", "Referencias", "ABNT"],
        },
    },
    "genesis-writer": {
        "path": "genesis-writer",
        "keep_sections": [
            "genesis-writer", 
            "Gênesis",
            "Genesis",
            "Quando usar",
            "Trigger",
            "Fluxo",
            "Pipeline",
            "Regras",
        ],
        "ref_sections": {
            "camadas-L0-L7.md": ["Camadas", "L0", "L1", "L2", "L3", "L4", "L5", "L6", "L7"],
            "matriz-agentes.md": ["Matriz", "Agentes"],
            "protocolo-busca.md": ["Protocolo", "Busca", "Pesquisa"],
        },
    },
    "nexus": {
        "path": "nexus",
        "skill_file": "SKILL.md",
        "keep_sections": [
            "Nexus",
            "Quando usar",
            "Trigger",
            "Arquitetura",
            "Fluxo",
            "Sincronizacao",
        ],
        "ref_sections": {
            "componentes-mcp.md": ["MCP", "Componentes"],
            "configuracao.md": ["Configuracao"],
        },
    },
    
    # ══════════════════════════════════════════════════════════════
    # GRUPO C: RESEARCH SKILLS
    # ══════════════════════════════════════════════════════════════
    "academic-export-abnt": {
        "path": "skills/research/academic-export-abnt",
        "keep_sections": [
            "academic-export-abnt",
            "Quando usar",
            "Trigger",
            "Fluxo",
        ],
        "ref_sections": {
            "comandos-exportacao.md": ["Comandos", "Export"],
            "parametros-formato.md": ["Parametros", "Formato"],
        },
    },
    "academic-ml-pipeline": {
        "path": "skills/research/academic-ml-pipeline",
        "keep_sections": [
            "academic-ml-pipeline",
            "Quando usar",
            "Trigger",
            "Pipeline",
            "Fluxo",
        ],
        "ref_sections": {
            "parametros-modelos.md": ["Parametros", "Modelos"],
            "metricas-avaliacao.md": ["Metricas", "Avaliacao"],
        },
    },
    
    # ══════════════════════════════════════════════════════════════
    # GRUPO D: SYSTEM + STOCK
    # ══════════════════════════════════════════════════════════════
    "descobrir-e-instalar-mcp": {
        "path": "skills/system/descobrir-e-instalar-mcp",
        "keep_sections": [
            "descobrir-e-instalar-mcp",
            "Quando usar",
            "Workflow",
            "Best Practices",
        ],
        "ref_sections": {
            "tabela-classificacao.md": ["Classificac"],
            "fontes-primarias.md": ["Fontes Primarias"],
        },
    },
    "stock-analysis": {
        "path": "stock-analysis/stock-analysis",
        "keep_sections": [
            "Stock Analysis",
            "When to Use",
        ],
        "ref_sections": {
            "api-reference.md": ["Available APIs", "Key Parameters", "Key Data Points"],
            "workflows-completos.md": ["Common Workflows", "Workflows"],
        },
    },
    
    # ══════════════════════════════════════════════════════════════
    # GRUPO E: EDITAIS SKILLS
    # ══════════════════════════════════════════════════════════════
    "bugfix": {
        "path": "editais-br/.claude/skills/bugfix",
        "keep_sections": [
            "bugfix",
            "Quando usar",
            "Triage",
            "Stop-the-line",
        ],
        "ref_sections": {
            "template-documentacao.md": ["Template", "documentacao"],
        },
    },
    "project-adopt": {
        "path": "editais-br/.claude/skills/project-adopt",
        "keep_sections": [
            "project-adopt",
            "Quando executar",
            "Diferenca",
            "Protocolo",
        ],
        "ref_sections": {
            "fases-detalhadas.md": ["Fase 1", "Fase 2", "Fase 3"],
            "exemplo-memory.md": ["Exemplo", "MEMORY"],
        },
    },
    "project-init": {
        "path": "editais-br/.claude/skills/project-init",
        "keep_sections": [
            "project-init",
            "Quando executar",
            "Objetivo",
        ],
        "ref_sections": {
            "protocolo-entrevista.md": ["Protocolo de entrevista", "0 ", "1 ", "2 ", "3 ", "4 ", "5 ", "6 ", "7 "],
            "acoes-pos-entrevista.md": ["Acoes apos", "acoes após", "Finalize o git"],
        },
    },
    "project-seal": {
        "path": "editais-br/.claude/skills/project-seal",
        "keep_sections": [
            "project-seal",
            "Quando executar",
            "Objetivo",
        ],
        "ref_sections": {
            "protocolo-detalhado.md": ["Protocolo", "Diagnostico", "Revisao", "Commit", "Push", "Confirmac"],
        },
    },
}


def process_skill(skill_name, config, dry_run=False):
    """Processa uma skill: extrai secoes e reescreve SKILL.md."""
    print(f"\n{'='*60}")
    print(f"[SKILL] {skill_name}")
    print(f"{'='*60}")
    
    base_path = BASE / config["path"]
    skill_file = config.get("skill_file", "SKILL.md")
    skill_path = base_path / skill_file
    
    if not skill_path.exists():
        print(f"  [ERRO] SKILL.md nao encontrado: {skill_path}")
        return {"name": skill_name, "error": "File not found"}
    
    original_content = read_file_utf8(skill_path)
    original_size = len(original_content.encode('utf-8'))
    print(f"  Lido: {skill_path.relative_to(BASE)} ({original_size}B)")
    
    # 1. Split into sections by ## headings
    sections = split_sections(original_content)
    print(f"  Secoes encontradas: {len(sections)}")
    for h, lines in sections:
        sz = estimate_section_size(lines)
        print(f"    - [{sz:4d}B] {h[:60]}")
    
    # 2. Identify sections to extract to references
    extracted_total = 0
    new_sections = []
    ref_data = {}  # filename -> content
    
    for heading_text, section_lines in sections:
        content_joined = '\n'.join(section_lines)
        section_hash = heading_text.lower().strip()
        
        # Check if this section should be extracted to references
        extracted = False
        for ref_file, search_terms in config.get("ref_sections", {}).items():
            should_extract = any(term.lower() in section_hash or section_hash.startswith(term.lower()) for term in search_terms)
            if should_extract:
                # Verify this section has substantial content (>300B)
                if estimate_section_size(section_lines) > 200:
                    if ref_file not in ref_data:
                        ref_data[ref_file] = []
                    ref_data[ref_file].append(content_joined)
                    extracted = True
                    ext_size = estimate_section_size(section_lines)
                    extracted_total += ext_size
                    print(f"  -> Extraindo para references/{ref_file}: {heading_text[:50]} ({ext_size}B)")
                    break
        
        if not extracted:
            new_sections.append((heading_text, section_lines))
    
    # 3. Write references files
    if ref_data and not dry_run:
        ref_dir = base_path / "references"
        ref_dir.mkdir(parents=True, exist_ok=True)
        
        for ref_file, contents in ref_data.items():
            merged = '\n\n---\n\n'.join(contents)
            header = f"<!-- Conteudo extraido de {skill_name}/SKILL.md via progressive-disclosure -->\n\n"
            ref_path = ref_dir / ref_file
            write_file_utf8(ref_path, header + merged)
            print(f"  [CRIADO] references/{ref_file} ({len(merged)} chars)")
    
    # 4. Build lean SKILL.md
    if not dry_run:
        lean_lines = []
        
        # Keep frontmatter (first --- ... --- block)
        frontmatter_end = 0
        first_line = original_content.split('\n')[0].strip()
        if first_line == '---':
            lines = original_content.split('\n')
            for i, line in enumerate(lines[1:], 1):
                lean_lines.append(line)
                if line.strip() == '---':
                    frontmatter_end = i
                    break
        
        # Add blank line after frontmatter
        lean_lines.append('')
        
        # Extract and rewrite first heading + description
        for heading_text, section_lines in new_sections:
            if heading_text == "HEADER":
                # Keep preamble content but trim
                for line in section_lines:
                    lean_lines.append(line)
                break
        
        # Add references section if we extracted content
        if ref_data:
            lean_lines.append('')
            lean_lines.append('## Conteudo de Referencia')
            lean_lines.append('')
            lean_lines.append('Para manter esta skill leve, dados densos foram movidos para arquivos de referencia:')
            lean_lines.append('')
            for ref_file in sorted(ref_data.keys()):
                ref_name = Path(ref_file).stem.replace('-', ' ').title()
                lean_lines.append(f'- [`references/{ref_file}`](references/{ref_file}) — {ref_name}')
        
        # Add key remaining sections (keep first 3-4 non-extracted sections)
        kept_count = 0
        for heading_text, section_lines in new_sections:
            if heading_text == "HEADER":
                continue  # Already handled above
            
            # Skip very long remaining sections that are reference-like
            section_str = '\n'.join(section_lines)
            section_size = len(section_str.encode('utf-8'))
            
            # Check if this remaining section is still reference-density
            if is_reference_section(heading_text, section_str) and section_size > 500:
                # Add a pointer instead
                safe_name = heading_text.lower().replace(' ', '-')[:30]
                lean_lines.append('')
                lean_lines.append(f'> *Detalhes de "{heading_text}" em `references/`*')
                lean_lines.append('')
                continue
            
            lean_lines.append('')
            for line in section_lines:
                lean_lines.append(line)
            
            kept_count += 1
            if kept_count >= 4 and not heading_text.lower().startswith('#'):
                break
        
        # Write the lean SKILL.md
        new_content = '\n'.join(lean_lines)
        new_size = len(new_content.encode('utf-8'))
        skill_path.write_text(new_content, encoding='utf-8')
        print(f"  [REESCRITO] SKILL.md: {original_size}B -> {new_size}B (reducao: {original_size - new_size}B)")
    else:
        new_size = original_size - extracted_total
    
    # 5. Handle duplicates
    if "duplicates" in config and not dry_run:
        for dup_rel in config["duplicates"]:
            dup_path = BASE / dup_rel
            dup_path.mkdir(parents=True, exist_ok=True)
            # Copy SKILL.md
            shutil.copy2(skill_path, dup_path / skill_file)
            # Copy references dir
            src_ref = base_path / "references"
            dst_ref = dup_path / "references"
            if src_ref.exists():
                if dst_ref.exists():
                    shutil.rmtree(dst_ref)
                shutil.copytree(src_ref, dst_ref)
            print(f"  [DUPLICADO] {dup_rel}")
    
    return {
        "name": skill_name,
        "status": "ok",
        "original_bytes": original_size,
        "new_bytes": new_size if not dry_run else (original_size - extracted_total),
        "reduction": extracted_total,
        "ref_files": len(ref_data),
    }


def main():
    dry_run = "--dry-run" in sys.argv
    only_skill = None
    for arg in sys.argv[1:]:
        if arg == "--dry-run":
            continue
        only_skill = arg
    
    if dry_run:
        print("[DRY-RUN] Modo seco - nenhum arquivo sera alterado\n")
    
    results = []
    for skill_name, config in SKILL_CONFIGS.items():
        if only_skill and skill_name != only_skill:
            continue
        try:
            result = process_skill(skill_name, config, dry_run)
            results.append(result)
        except Exception as e:
            print(f"  [ERRO] {e}")
            results.append({"name": skill_name, "error": str(e)})
    
    # Summary
    print(f"\n{'='*60}")
    print("[RESUMO]")
    print(f"{'='*60}")
    total_ok = sum(1 for r in results if r.get("status") == "ok")
    total_err = sum(1 for r in results if r.get("error"))
    total_red = sum(r.get("reduction", 0) for r in results)
    total_ref = sum(r.get("ref_files", 0) for r in results)
    print(f"  Skills processadas: {total_ok + total_err}")
    print(f"  Sucesso: {total_ok}")
    print(f"  Erros: {total_err}")
    print(f"  Reducao total: {total_red}B ({total_red/1024:.1f}KB)")
    print(f"  Arquivos de referencia criados: {total_ref}")
    
    for r in results:
        if r.get("error"):
            print(f"  [FAIL] {r['name']}: {r['error']}")
        elif dry_run:
            print(f"  [OK] {r['name']}: -{r['reduction']}B estimados")


if __name__ == "__main__":
    main()
