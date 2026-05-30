#!/usr/bin/env python3
"""
refactor_oversize_skills_v3.py — Segunda passagem.
Corrige frontmatter duplicado e extrai secoes pesadas para references/.
Uso: python3 refactor_oversize_skills_v3.py [--dry-run]
"""

import sys, re, shutil
from pathlib import Path

BASE = Path(r"C:\Users\marce\.config\opencode")
dry_run = "--dry-run" in sys.argv

def log(msg):
    print(msg.encode('ascii', errors='replace').decode('ascii'))

def fix_dup_frontmatter(content):
    parts = content.split('---')
    if len(parts) >= 4:
        fm1, fm2 = parts[1].strip(), parts[2].strip()
        n1 = re.search(r'name:\s*(.+)', fm1)
        n2 = re.search(r'name:\s*(.+)', fm2)
        if n1 and n2 and n1.group(1).strip() == n2.group(1).strip():
            return '---' + parts[1] + '---' + '---'.join(parts[3:]), True
    return content, False

def extract_headings_to_refs(content, headings_map):
    """
    Extract sections by heading keyword. 
    headings_map: {substring_to_match: ref_filename}
    A section ends at the next heading of ANY level (## or ###) or --- divider.
    """
    lines = content.split('\n')
    refs = []
    result_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        
        # Check if this line matches any target heading
        matched = False
        for hs, ref_fn in headings_map.items():
            if hs in stripped and stripped.startswith('#'):
                # Extract the section: from this heading to next ## or ###
                ref_clines = [line]
                i += 1
                while i < len(lines):
                    nl = lines[i]
                    ns = nl.strip()
                    # Break at any heading (## or ###) or --- divider
                    if re.match(r'^#{2,3}\s', ns) or ns.startswith('---'):
                        break
                    ref_clines.append(nl)
                    i += 1
                
                refs.append((ref_fn, '\n'.join(ref_clines)))
                result_lines.append(f"> *Detalhes em `references/{ref_fn}`*")
                matched = True
                break
        
        if not matched:
            result_lines.append(line)
            i += 1
    
    return '\n'.join(result_lines), refs

def extract_content_to_ref(content, ref_filename, start_marker, end_marker=None):
    """Extract content between markers."""
    lines = content.split('\n')
    start_idx = None
    for i, line in enumerate(lines):
        if start_marker in line:
            start_idx = i
            break
    if start_idx is None:
        return content, None
    
    end_idx = len(lines)
    if end_marker:
        for i in range(start_idx + 1, len(lines)):
            if end_marker in lines[i]:
                end_idx = i
                break
    else:
        for i in range(start_idx + 1, len(lines)):
            s = lines[i].strip()
            if re.match(r'^#{2,3}\s', s) or s.startswith('---'):
                end_idx = i
                break
    
    extracted = '\n'.join(lines[start_idx:end_idx])
    new_lines = lines[:start_idx] + [f"> *Detalhes em `references/{ref_filename}`*"] + lines[end_idx:]
    return '\n'.join(new_lines), extracted

def save_refs(skill_dir, refs):
    if not refs:
        return False
    ref_dir = skill_dir / "references"
    if not ref_dir.exists() and not dry_run:
        ref_dir.mkdir(parents=True, exist_ok=True)
    any_w = False
    for ref_name, ref_content in refs:
        ref_path = ref_dir / ref_name
        old_sz = len(ref_path.read_bytes()) if ref_path.exists() else 0
        if not dry_run:
            ref_path.write_text(ref_content.strip() + '\n', encoding='utf-8')
        new_sz = len(ref_content.encode('utf-8'))
        act = "ATUALIZADO" if old_sz > 0 else "CRIADO"
        log(f"  [REF {act}] {ref_name} ({old_sz}B -> {new_sz}B)")
        any_w = True
    return any_w

def process_skill(rel_path):
    sp = BASE / rel_path
    if not sp.exists():
        log(f"\n[SKIP] {rel_path}")
        return False, False
    
    orig_sz = len(sp.read_bytes())
    log(f"\n{'='*55}")
    log(f"[SKILL] {rel_path} ({orig_sz}B)")
    
    content = sp.read_text(encoding='utf-8')
    orig_content = content
    all_refs = []
    
    # Always fix duplicate frontmatter
    content, deduped = fix_dup_frontmatter(content)
    if deduped:
        log(f"  [DEDUP] Frontmatter duplicado removido")
    
    # Per-skill extraction
    if "edicao-cirurgica" in rel_path and ".claude" in rel_path:
        hm = {
            "### C\u00f3digo (JS": "regras-codigo.md",
            "### Workflows n8n (JSON)": "regras-n8n.md",
            "### HTML/CSS": "regras-html-css.md",
            "### Skills (SKILL.md)": "regras-skills.md",
            "### Documentos jur\u00eddicos": "regras-juridico.md",
        }
        content, refs = extract_headings_to_refs(content, hm)
        if refs:
            log(f"  [EXTRAIDO] {len(refs)} secoes de regras")
            all_refs.extend(refs)
    
    elif "pecas-juridicas-html" in rel_path and ".claude" in rel_path:
        content, extracted = extract_content_to_ref(content, "regras-criticas.md",
            "\u26a0 REGRAS CR\u00cdTICAS",  # ⚠ REGRAS CRÍTICAS
            "## Fluxo de Trabalho")
        if extracted:
            log(f"  [EXTRAIDO] Regras cr\u00edticas")
            all_refs.append(("regras-criticas.md", extracted))
    
    elif "academic-ml-pipeline" in rel_path:
        hm = {
            "### Etapa 1:": "etapa1.md",
            "### Etapa 2:": "etapa2.md",
            "### Etapa 3:": "etapa3.md",
            "### Etapa 4:": "etapa4.md",
            "### Etapa 5:": "etapa5.md",
            "### Etapa 6:": "etapa6.md",
            "### Etapa 7:": "etapa7.md",
        }
        content, refs = extract_headings_to_refs(content, hm)
        if refs:
            log(f"  [EXTRAIDO] {len(refs)} etapas do workflow")
            all_refs.extend(refs)
    
    elif "bugfix" in rel_path:
        content, extracted = extract_content_to_ref(content, "etapas-triage.md",
            "### 1. Reproduzir", "Stop-the-line")
        if extracted:
            log(f"  [EXTRAIDO] Etapas de triage (6 passos)")
            all_refs.append(("etapas-triage.md", extracted))
    
    # Compact blank lines (max 1 consecutive)
    lines = content.split('\n')
    cleaned = []
    prev_b = False
    for line in lines:
        b = line.strip() == ''
        if b and prev_b:
            continue
        cleaned.append(line)
        prev_b = b
    content = '\n'.join(cleaned)
    
    changed = content != orig_content
    if changed:
        new_sz = len(content.encode('utf-8'))
        red = orig_sz - new_sz
        if not dry_run:
            sp.write_text(content, encoding='utf-8')
        log(f"  [SKILL] {orig_sz}B -> {new_sz}B (reducao: {red}B)")
    
    refs_w = save_refs(sp.parent, all_refs)
    return changed, refs_w

def sync_dups():
    log(f"\n{'='*55}")
    log(f"[SYNC] skills/juridico/ <- .claude/skills/")
    pairs = [
        (".claude/skills/pecas-juridicas-html", "skills/juridico/pecas-juridicas-html"),
        (".claude/skills/edicao-cirurgica", "skills/juridico/edicao-cirurgica"),
        (".claude/skills/followup-advocacia", "skills/juridico/followup-advocacia"),
        (".claude/skills/gerador-contratos", "skills/juridico/gerador-contratos"),
        (".claude/skills/pesquisa-jurisprudencia", "skills/juridico/pesquisa-jurisprudencia"),
        (".claude/skills/triagem-juridica", "skills/juridico/triagem-juridica"),
    ]
    for sr, dr in pairs:
        src = BASE / sr; dst = BASE / dr
        if not src.is_dir() or not dst.is_dir():
            continue
        ss = src / "SKILL.md"; ds = dst / "SKILL.md"
        if ss.exists() and ds.exists():
            ssz = len(ss.read_bytes()); dsz = len(ds.read_bytes())
            if ssz != dsz:
                if not dry_run:
                    shutil.copy2(ss, ds)
                log(f"  [SYNC] {dr}/SKILL.md ({dsz}B -> {ssz}B)")
        sref = src / "references"; dref = dst / "references"
        if sref.exists():
            if not dref.exists() and not dry_run:
                dref.mkdir(parents=True, exist_ok=True)
            for f in sref.iterdir():
                if f.is_file():
                    df = dref / f.name
                    sz = len(f.read_bytes()); dsz2 = len(df.read_bytes()) if df.exists() else 0
                    if sz != dsz2:
                        if not dry_run:
                            shutil.copy2(f, df)
                        log(f"  [SYNC] {dr}/references/{f.name} ({dsz2}B -> {sz}B)")

def main():
    if dry_run:
        print("=" * 55)
        print("[DRY-RUN] Nenhuma alteracao em disco")
        print("=" * 55)
    
    targets = [
        ".claude/skills/edicao-cirurgica/SKILL.md",
        ".claude/skills/pecas-juridicas-html/SKILL.md",
        "skills/research/academic-ml-pipeline/SKILL.md",
        "editais-br/.claude/skills/bugfix/SKILL.md",
        "genesis-writer/SKILL.md",
        "nexus/SKILL.md",
    ]
    
    sc, rw = 0, 0
    for t in targets:
        try:
            a, b = process_skill(t)
            if a: sc += 1
            if b: rw += 1
        except Exception as e:
            log(f"\n[ERRO] {t}: {e}")
            import traceback
            traceback.print_exc()
    
    sync_dups()
    log(f"\n{'='*55}")
    log(f"[RESUMO] Skills alteradas: {sc}, Refs escritas: {rw}")
    if dry_run:
        log("[CONCLUIDO] Execute sem --dry-run para aplicar")
    else:
        log("[CONCLUIDO] OK")

if __name__ == "__main__":
    main()
