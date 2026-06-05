#!/usr/bin/env python3
"""
Refatorador Progressive Disclosure para skills oversized (>2.5KB).
Aplica a metodologia skill-progressive-disclosure-design para extrair
conteúdo denso (tabelas, templates, CSS, wizards) em references/*.md,
reduzindo cada SKILL.md para ~2KB com ponteiros léticos.

Uso:
    python nexus/scripts/refactor_oversize_skills.py [--dry-run] [--skill NOME]

Sem --skill, processa todas as 17 skills oversized únicas.
Com --dry-run, apenas mostra o que seria feito sem alterar arquivos.
"""

import os, re, sys, shutil, json
from pathlib import Path
from typing import Optional

# Forcar UTF-8 na saida (evita UnicodeEncodeError no Windows cp1252)
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
elif hasattr(sys.stdout, 'buffer'):
    sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

BASE = Path(r"C:\Users\marce\.config\opencode")

# ─── REGRAS DE EXTRAÇÃO POR SKILL ───────────────────────────────────────────
# Cada regra define:
#   "path": caminho relativo ao BASE
#   "duplicates": lista de caminhos duplicados (mesmo conteúdo)
#   "extract": dict de { "references/arquivo.md": { "headings": [...], "patterns": [...], "lines_before": N } }
#              ou None se só precisa de poda simples
#   "keep_sections": lista de headings raiz para manter (outros são extraídos)
#   "template_replace": se True, SKILL.md é reescrito com template leve

RULES = {
    # ═══════════════════════════════════════════════════════════════════════════
    # GRUPO A: JURÍDICOS (.claude/skills/ + skills/juridico/ duplicatas)
    # ═══════════════════════════════════════════════════════════════════════════

    "pecas-juridicas-html": {
        "path": ".claude/skills/pecas-juridicas-html",
        "duplicates": ["skills/juridico/pecas-juridicas-html"],
        "extract": {
            "references/wizard-configuracao.md": {
                "headings": ["## Wizard de Configuração Inicial"],
                "include_until": "## Uso Básico",
            },
            "references/css-cores.md": {
                "headings": ["## Paleta de Cores e Estilos"],
                "include_until": "## Templates de Peças",
                "grab_until_next_heading": True,
            },
            "references/templates-html.md": {
                "headings": ["## Templates de Peças"],
                "include_until": "## Configuração do JSON",
                "grab_until_next_heading": True,
            },
            "references/dados-escritorio.md": {
                "headings": [
                    "`*` Se `dados-escritorio.json` existe e está preenchido",
                    "### Dados obrigatórios",
                    "### Dados opcionais",
                ],
                "include_until": "## Personalização",
                "grab_until_next_heading": True,
            },
        },
        "keep_only_headings": [
            "pecas-juridicas-html",
            "Quando usar",
            "Trigger",
            "Fluxo rápido",
            "Regras",
        ],
    },

    "edicao-cirurgica": {
        "path": ".claude/skills/edicao-cirurgica",
        "duplicates": ["skills/juridico/edicao-cirurgica"],
        "extract": {
            "references/exemplos.md": {
                "headings": ["### Exemplos"],
                "grab_until_next_section": True,
            },
            "references/formatos-suportados.md": {
                "headings": ["## Formatos Suportados"],
                "grab_until_next_section": True,
            },
        },
    },

    "gerador-contratos": {
        "path": ".claude/skills/gerador-contratos",
        "duplicates": ["skills/juridico/gerador-contratos"],
        "extract": {
            "references/tipos-contrato.md": {
                "headings": ["### Tipos de Contrato Suportados", "## Tipos de Contrato Suportados"],
                "grab_until_next_section": True,
            },
            "references/css-templates.md": {
                "headings": ["## Estrutura CSS e Templates", "### Templates HTML"],
                "grab_until_next_section": True,
            },
        },
    },

    "pesquisa-jurisprudencia": {
        "path": ".claude/skills/pesquisa-jurisprudencia",
        "duplicates": ["skills/juridico/pesquisa-jurisprudencia"],
        "extract": {
            "references/tribunais-fontes.md": {
                "headings": ["## Tribunais e Fontes", "### Tribunais Suportados"],
                "grab_until_next_section": True,
            },
            "references/parametros-busca.md": {
                "headings": ["## Parâmetros de Busca", "### Filtros"],
                "grab_until_next_section": True,
            },
        },
    },

    "followup-advocacia": {
        "path": ".claude/skills/followup-advocacia",
        "duplicates": ["skills/juridico/followup-advocacia"],
        "extract": {
            "references/cadencia-contato.md": {
                "headings": ["### Cadência de Contato Recomendada", "## Cadência de Contato"],
                "grab_until_next_section": True,
            },
            "references/pipeline-demandas.md": {
                "headings": ["## Pipeline de Demandas", "### Etapas do Pipeline"],
                "grab_until_next_section": True,
            },
        },
    },

    "triagem-juridica": {
        "path": ".claude/skills/triagem-juridica",
        "duplicates": ["skills/juridico/triagem-juridica"],
        "extract": {
            "references/tabela-classificacao.md": {
                "headings": ["## Classificação por Área do Direito", "### Tabela de Classificação"],
                "grab_until_next_section": True,
            },
            "references/perguntas-triagem.md": {
                "headings": ["## Roteiro de Perguntas", "### Perguntas Essenciais"],
                "grab_until_next_section": True,
            },
        },
    },

    # ═══════════════════════════════════════════════════════════════════════════
    # GRUPO B-1: CRIADOR-ARTIGO (13KB)
    # ═══════════════════════════════════════════════════════════════════════════

    "criador-artigo": {
        "path": "criador-artigo",
        "extract": {
            "references/tabelas-volume-prazo.md": {
                "headings": ["### Tabelas de Volume e Prazo", "## Prazos e Volumes"],
                "grab_until_next_section": True,
            },
            "references/rubrica-avaliacao.md": {
                "headings": ["### Rubrica de Avaliação", "## Critérios de Avaliação", "### AUTO_SCORE_QUALIS"],
                "grab_until_next_section": True,
            },
            "references/detalhes-citacoes.md": {
                "headings": ["### Citações e Referências", "## Formato de Citações"],
                "grab_until_next_section": True,
            },
        },
    },

    # ═══════════════════════════════════════════════════════════════════════════
    # GRUPO B-2: GENESIS-WRITER (22.5KB)
    # ═══════════════════════════════════════════════════════════════════════════

    "genesis-writer": {
        "path": "genesis-writer",
        "extract": {
            "references/camadas-L0-L7.md": {
                "headings": ["## Camadas do Sistema (L0-L7)"],
                "grab_until_next_heading": True,
            },
            "references/matriz-agentes.md": {
                "headings": ["## Matriz de Agentes"],
                "grab_until_next_heading": True,
            },
            "references/protocolo-busca.md": {
                "headings": ["## Protocolo de Busca", "## Estratégia de Pesquisa"],
                "grab_until_next_heading": True,
            },
            "references/esquemas-json.md": {
                "headings": ["## Esquemas JSON", "### Estrutura de Dados"],
                "grab_until_next_section": True,
            },
        },
    },

    # ═══════════════════════════════════════════════════════════════════════════
    # GRUPO B-3: NEXUS SKILL (7KB)
    # ═══════════════════════════════════════════════════════════════════════════

    "nexus": {
        "path": "nexus",
        "skill_file": "SKILL.md",  # na raiz do nexus/
        "extract": {
            "references/componentes-mcp.md": {
                "headings": ["### MCPs Registrados", "## MCPs Ativos"],
                "grab_until_next_section": True,
            },
            "references/configuracao-componentes.md": {
                "headings": ["## Configuração de Componentes", "### Parâmetros"],
                "grab_until_next_section": True,
            },
        },
    },

    # ═══════════════════════════════════════════════════════════════════════════
    # GRUPO B-4: RESEARCH SKILLS
    # ═══════════════════════════════════════════════════════════════════════════

    "academic-export-abnt": {
        "path": "skills/research/academic-export-abnt",
        "extract": {
            "references/comandos-export.md": {
                "headings": ["## Comandos de Exportação", "### PDF", "### DOCX", "### HTML"],
                "grab_until_next_section": True,
            },
            "references/parametros-formato.md": {
                "headings": ["## Parâmetros de Formatação", "### Configuração ABNT"],
                "grab_until_next_section": True,
            },
        },
    },

    "academic-ml-pipeline": {
        "path": "skills/research/academic-ml-pipeline",
        "extract": {
            "references/parametros-modelos.md": {
                "headings": ["## Parâmetros dos Modelos", "### Configuração"],
                "grab_until_next_section": True,
            },
            "references/tabelas-metricas.md": {
                "headings": ["## Métricas de Avaliação", "### Tabela de Métricas"],
                "grab_until_next_section": True,
            },
        },
    },

    # ═══════════════════════════════════════════════════════════════════════════
    # GRUPO B-5: SYSTEM + STOCK
    # ═══════════════════════════════════════════════════════════════════════════

    "descobrir-e-instalar-mcp": {
        "path": "skills/system/descobrir-e-instalar-mcp",
        "extract": {
            "references/tabela-classificacao.md": {
                "headings": ["### Fase 3: Classificação", "| Categoria | Exemplos | Tags |"],
                "grab_until_next_section": True,
            },
            "references/fontes-primarias.md": {
                "headings": ["## Fontes Primárias"],
                "grab_until_next_section": True,
            },
        },
    },

    "stock-analysis": {
        "path": "stock-analysis/stock-analysis",
        "extract": {
            "references/api-reference.md": {
                "headings": ["## Available APIs", "### Company Information", "### Trading", "### Ownership", "### Key Parameters", "### Key Data Points"],
                "grab_until_next_heading": True,
            },
            "references/workflows-completos.md": {
                "headings": ["## Common Workflows"],
                "grab_until_next_heading": True,
            },
        },
    },

    # ═══════════════════════════════════════════════════════════════════════════
    # GRUPO C: EDITAIS SKILLS
    # ═══════════════════════════════════════════════════════════════════════════

    "bugfix": {
        "path": "editais-br/.claude/skills/bugfix",
        "extract": {
            "references/template-documentacao.md": {
                "patterns": [r"```[\s\S]*?\*\*Bug:\*\*[\s\S]*?```"],
                "context_lines": 2,
            },
        },
    },

    "project-adopt": {
        "path": "editais-br/.claude/skills/project-adopt",
        "extract": {
            "references/exemplo-memory.md": {
                "patterns": [r"```markdown[\s\S]*?---[\s\S]*?project: archguard[\s\S]*?```"],
                "context_lines": 1,
            },
        },
    },

    "project-init": {
        "path": "editais-br/.claude/skills/project-init",
        "extract": {
            "references/perguntas-entrevista.md": {
                "headings": ["## Protocolo de entrevista", "### 0", "### 1", "### 2", "### 3", "### 4", "### 5", "### 6", "### 7"],
                "grab_until_next_section": True,
            },
        },
    },

    "project-seal": {
        "path": "editais-br/.claude/skills/project-seal",
        # Já está em 2.9KB (~97 linhas) — só extrair tabela de categorias
        "extract": {
            "references/tabela-categorias.md": {
                "headings": ["| Categoria | Arquivos típicos |"],
                "grab_until_next_section": True,
            },
        },
    },
}


# ─── FUNÇÕES DE PROCESSAMENTO ────────────────────────────────────────────────

def extract_sections(content: str, rules: dict) -> dict[str, str]:
    """
    Extrai seções do SKILL.md baseado nas regras de extração.
    Retorna dict { "references/arquivo.md": "conteúdo extraído" }
    """
    extracted = {}
    lines = content.split('\n')

    for ref_path, rule in rules.get("extract", {}).items():
        # Method 1: Extract by heading markers
        if "headings" in rule:
            extracted_content = []
            in_section = False
            heading_depth = 0
            heading_text = ""
            for i, line in enumerate(lines):
                stripped = line.strip()

                # Check if this line matches any target heading
                for target_h in rule["headings"]:
                    if target_h in stripped:
                        in_section = True
                        heading_depth = len(stripped.split('#')[0]) if stripped.startswith('#') else 0
                        heading_text = stripped.lstrip('#').strip()
                        extracted_content.append(line)
                        break

                if in_section and not any(target_h in stripped for target_h in rule["headings"]):
                    # Check if we hit the "until" marker
                    if "include_until" in rule and rule["include_until"] in stripped:
                        break

                    # Check grab_until_next_heading: stop at next heading of same or higher level
                    if rule.get("grab_until_next_heading") and stripped.startswith('#'):
                        # Count the heading level
                        level = len(stripped.split('#')[0]) if stripped.startswith('#') else 0
                        if level <= heading_depth:
                            break

                    # Check grab_until_next_section: stop at next ## heading
                    if rule.get("grab_until_next_section") and stripped.startswith('## ') and i > 0:
                        # Make sure we're past the initial heading
                        prev = lines[i-1].strip() if i > 0 else ""
                        if not prev.startswith('#'):
                            break

                    # Check for the old in_section end pattern
                    if in_section and not stripped:
                        continue

                    extracted_content.append(line)

            if extracted_content:
                # Clean up: remove trailing whitespace
                text = '\n'.join(extracted_content).strip()
                # Remove the source info comment
                text = re.sub(r'^.*?extraído de.*?\n', '', text)
                if text:
                    extracted[ref_path] = text

        # Method 2: Extract by regex pattern
        if "patterns" in rule:
            for pattern in rule["patterns"]:
                matches = re.findall(pattern, content, re.DOTALL)
                if matches:
                    context_lines_count = rule.get("context_lines", 0)
                    if context_lines_count:
                        # Find line context
                        for m in matches:
                            start_idx = content.find(m)
                            if start_idx >= 0:
                                lines_before = content[:start_idx].count('\n')
                                start_line = max(0, lines_before - context_lines_count)
                                end_line = lines_before + content[start_idx:].count('\n') + context_lines_count
                                excerpt_lines = lines[start_line:end_line+1]
                                extracted[ref_path] = '\n'.join(excerpt_lines)
                                break
                    else:
                        extracted[ref_path] = matches[0]

    return extracted


def create_replacement_skill(skill_name: str, original_content: str, extracted: dict[str, str], rules: dict) -> str:
    """
    Cria a versão leve do SKILL.md mantendo frontmatter, trigger,
    fluxo principal e adicionando ponteiros para references/.
    """
    lines = original_content.split('\n')

    # Extract frontmatter (YAML between ---)
    frontmatter_end = 0
    if lines[0].strip() == '---':
        for i, line in enumerate(lines[1:], 1):
            if line.strip() == '---':
                frontmatter_end = i
                break

    frontmatter = '\n'.join(lines[:frontmatter_end + 1]) if frontmatter_end else ''

    # Build the lean skill content
    new_lines = []

    # Keep frontmatter
    if frontmatter:
        new_lines.append(frontmatter)
        new_lines.append('')

    # Keep title
    title_line = ""
    for line in lines:
        if line.startswith('# ') and skill_name.replace('-', ' ') in line.lower():
            title_line = line
            break

    if title_line:
        new_lines.append(title_line)
        new_lines.append('')

    # Add "When to use" section (first paragraph after title)
    in_when = False
    when_lines = []
    for i, line in enumerate(lines):
        if line.startswith('# '):
            # Find the first paragraph after title
            for j in range(i+1, min(i+10, len(lines))):
                if lines[j].strip() and not lines[j].startswith('#'):
                    when_lines.append(lines[j])
                elif lines[j].startswith('#'):
                    break
            break

    if when_lines:
        new_lines.append('**Quando usar:**')
        for wl in when_lines:
            new_lines.append(wl)
        new_lines.append('')

    # Add trigger section
    trigger_found = False
    for line in lines:
        if re.search(r'(trigger|quando usar|comando|quando executar)', line, re.IGNORECASE) and ':' in line:
            new_lines.append(f'> {line.strip()}')
            trigger_found = True
    if not trigger_found:
        # Try to find description in frontmatter
        desc_match = re.search(r'description:\s*"(.+?)"', original_content)
        if desc_match:
            new_lines.append(f'> {desc_match.group(1)}')
    new_lines.append('')

    # Add brief description rule from original
    desc_rule = ""
    in_fim = False
    for line in lines:
        if 'Nunca apague' in line or 'Nunca modifique' in line:
            desc_rule = line.strip()
            break
    if desc_rule:
        new_lines.append(f'[REGRA] {desc_rule}')
        new_lines.append('')

    # Add pointer to references
    if extracted:
        new_lines.append('## Conteúdo de Referência')
        new_lines.append('')
        new_lines.append('Para manter esta skill leve, o conteúdo denso foi extraído para:')
        new_lines.append('')
        for ref_path in sorted(extracted.keys()):
            ref_name = Path(ref_path).stem.replace('-', ' ').title()
            new_lines.append(f'- [`{ref_path}`]({ref_path}) - {ref_name}')
        new_lines.append('')
        new_lines.append('Esses arquivos são carregados sob demanda quando o agente precisa do detalhamento.')
        new_lines.append('')

    # Keep the core flow (first few non-extracted sections)
    kept_count = 0
    for i, line in enumerate(lines):
        if i <= frontmatter_end:
            continue
        stripped = line.strip()

        # Skip sections that were extracted
        if stripped.startswith('## '):
            section_name = stripped
            # Check if this section or subsections were extracted
            skip = False
            for ref_path, ref_content in extracted.items():
                for target_line in ref_content.split('\n'):
                    if target_line.strip() == section_name:
                        skip = True
                        break
                if skip:
                    break
            if skip:
                # Skip this section and all content until next ##
                kept_count += 1
                if kept_count <= 3:  # Keep max 3 original sections
                    continue
                else:
                    # Still add the section header as a reference
                    new_lines.append(f'> *Detalhes em `references/`: {section_name}*')
                continue

        # Always add non-extracted content (but be selective for long skills)
        if kept_count <= 5:
            new_lines.append(line)

    return '\n'.join(new_lines)


def process_skill(skill_name: str, rules: dict, dry_run: bool = False) -> dict:
    """
    Processa uma skill: extrai conteúdo, cria references/, reescreve SKILL.md.
    Retorna estatísticas da operação.
    """
    stats = {"name": skill_name, "extracted": 0, "reduction_bytes": 0, "errors": []}

    base_path = BASE / rules["path"]
    skill_file = rules.get("skill_file", "SKILL.md")
    skill_path = base_path / skill_file

    if not skill_path.exists():
        stats["errors"].append(f"SKILL.md não encontrado: {skill_path}")
        return stats

    original_size = os.path.getsize(skill_path)
    original_content = skill_path.read_text(encoding='utf-8')

    # 1. Extract sections
    extracted = extract_sections(original_content, rules)

    if not extracted:
        stats["errors"].append("Nada para extrair")
        return stats

    # 2. Create references directory and write files
    ref_dir = base_path / "references"
    if not dry_run:
        ref_dir.mkdir(parents=True, exist_ok=True)

    total_extracted = 0
    for ref_path, ref_content in extracted.items():
        target = ref_dir / Path(ref_path).name
        if not dry_run:
            # Add header comment
            header = f"<!-- Conteudo extraido de {skill_name}/SKILL.md via progressive-disclosure -->\n\n"
            target.write_text(header + ref_content, encoding='utf-8')
            print(f"  [CRIADO] {target.relative_to(BASE)} ({len(ref_content)} chars)")
        total_extracted += len(ref_content)

    # 3. Create lean SKILL.md
    if not dry_run:
        new_content = create_replacement_skill(skill_name, original_content, extracted, rules)
        # Keep the original frontmatter intact
        skill_path.write_text(new_content, encoding='utf-8')

    new_size_estimate = original_size - total_extracted
    stats["extracted"] = len(extracted)
    stats["reduction_bytes"] = total_extracted
    stats["original_size"] = original_size
    stats["new_size_estimate"] = new_size_estimate

    print(f"\n[SKILL] {skill_name}: {original_size}B -> ~{new_size_estimate}B (reducao de {total_extracted}B, {len(extracted)} arquivos)")

    # 4. Handle duplicates (symlink/copy references to duplicate locations)
    if "duplicates" in rules and not dry_run:
        for dup_path in rules["duplicates"]:
            dup_base = BASE / dup_path
            dup_ref_dir = dup_base / "references"
            dup_ref_dir.mkdir(parents=True, exist_ok=True)
            dup_skill_file = dup_base / skill_file

            for ref_path in extracted.keys():
                src = ref_dir / Path(ref_path).name
                dst = dup_ref_dir / Path(ref_path).name
                if src.exists():
                    shutil.copy2(src, dst)
                    print(f"  [DUP] {dst.relative_to(BASE)}")

            # Copy the lean SKILL.md
            if skill_path.exists():
                shutil.copy2(skill_path, dup_skill_file)
                print(f"  [DUP] SKILL.md: {dup_skill_file.relative_to(BASE)}")

    return stats


def process_all(dry_run: bool = False, only_skill: Optional[str] = None):
    """Processa todas as skills ou uma específica."""
    results = []

    for skill_name, rules in RULES.items():
        if only_skill and skill_name != only_skill:
            continue

        print(f"\n{'='*60}")
        print(f"[PROC] {skill_name}")
        print(f"{'='*60}")

        try:
            stats = process_skill(skill_name, rules, dry_run)
            results.append(stats)
            if stats["errors"]:
                for err in stats["errors"]:
                    print(f"  [WARN] {err}")
        except Exception as e:
            print(f"  [ERROR] {e}")
            results.append({"name": skill_name, "error": str(e)})

    # Summary
    print(f"\n{'='*60}")
    print("[RESUMO]")
    print(f"{'='*60}")
    total_reduction = sum(r.get("reduction_bytes", 0) for r in results)
    total_skills = len(results)
    total_errors = sum(1 for r in results if r.get("errors") or r.get("error"))
    print(f"Skills processadas: {total_skills}")
    print(f"Reducao total: {total_reduction}B ({total_reduction/1024:.1f}KB)")
    print(f"Erros: {total_errors}")
    for r in results:
        errs = r.get("errors", [])
        err_str = r.get("error", "")
        if errs or err_str:
            print(f"  [FAIL] {r['name']}: {'; '.join(errs + [err_str])}")

    return results


if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv
    only_skill = None
    for arg in sys.argv[1:]:
        if arg.startswith("--skill="):
            only_skill = arg.split("=", 1)[1]
        elif arg == "--dry-run":
            pass
        else:
            only_skill = arg

    if dry_run:
        print("[DRY-RUN] Modo seco - nenhum arquivo sera alterado\n")

    process_all(dry_run=dry_run, only_skill=only_skill)
