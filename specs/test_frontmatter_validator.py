#!/usr/bin/env python3
"""
test_frontmatter_validator.py — SPEC-025: Frontmatter Validation Suite

Valida todos os SKILL.md no ecossistema OpenCode quanto a:
- Frontmatter YAML válido (delimitadores ---)
- Campos obrigatórios: name, description
- Ausência de chaves YAML duplicadas
- Ausência de caracteres CJK
- Tamanho do arquivo (oversize > 2500 bytes)

Uso:
    python test_frontmatter_validator.py              # varre skills/ inteiro
    python test_frontmatter_validator.py --json       # saída JSON em tempfile
    python test_frontmatter_validator.py --fix        # modo reparo (fase 2+)

Saída: stdout tabular + JSON em tempfile (--json)
"""

import os
import re
import json
import sys
import tempfile
from pathlib import Path

# ─── Config ──────────────────────────────────────────────────────────────
SKILLS_BASE = Path(__file__).resolve().parent.parent / "skills"
OVERSIZE_BYTES = 2500
REQUIRED_FIELDS = ["name", "description"]
CJK_PATTERN = re.compile(r'[\u4e00-\u9fff\u3400-\u4dbf\uff00-\uffef\u3000-\u303f]')

# ─── YAML parser minimal (stdlib, sem pyyaml) ────────────────────────────
def parse_frontmatter(text: str):
    """Extrai frontmatter YAML entre --- delimitadores.
    Retorna (linhas_dict, raw_lines, error_msg, has_duplicates).
    """
    text = text.lstrip('\ufeff')  # Remove BOM (Python 3.12 no Windows)
    lines = text.split('\n')
    if not lines or lines[0].strip() != '---':
        return None, [], 'NO_FRONTMATTER: missing opening ---', False

    end_idx = None
    for i in range(1, len(lines)):
        if lines[i].strip() == '---':
            end_idx = i
            break

    if end_idx is None:
        return None, [], 'NO_FRONTMATTER: missing closing ---', False

    raw = lines[1:end_idx]
    parsed = {}
    has_duplicates = False
    seen_keys = {}

    for lineno, line in enumerate(raw, start=2):
        stripped = line.strip()
        if not stripped or stripped.startswith('#'):
            continue
        match = re.match(r'^([a-zA-Z_][a-zA-Z0-9_-]*)\s*:\s*(.*)', stripped)
        if match:
            key = match.group(1)
            value = match.group(2).strip().strip('"').strip("'")
            if key in seen_keys:
                has_duplicates = True
            seen_keys[key] = (lineno, value)
            parsed[key] = value

    # Check for duplicate keys that appeared before (detect via count)
    key_count = {}
    for line in raw:
        m = re.match(r'^([a-zA-Z_][a-zA-Z0-9_-]*)\s*:', line.strip())
        if m:
            k = m.group(1)
            key_count[k] = key_count.get(k, 0) + 1
    if any(c > 1 for c in key_count.values()):
        has_duplicates = True

    return parsed, raw, None, has_duplicates


def has_cjk(text: str) -> bool:
    """Retorna True se o texto contiver caracteres CJK."""
    return bool(CJK_PATTERN.search(text))


# ─── Validação individual ────────────────────────────────────────────────
def validate_skill(path: Path) -> dict:
    """Valida um único SKILL.md. Retorna dict com resultados."""
    rel = path.relative_to(SKILLS_BASE.parent.parent if SKILLS_BASE.parent.name == 'opencode' else SKILLS_BASE.parent)
    
    result = {
        'path': str(path),
        'relative': str(rel),
        'bytes': path.stat().st_size,
        'oversize': path.stat().st_size > OVERSIZE_BYTES,
        'oversize_by': max(0, path.stat().st_size - OVERSIZE_BYTES),
        'has_frontmatter': False,
        'has_name': False,
        'has_description': False,
        'has_duplicate_keys': False,
        'has_cjk': False,
        'errors': [],
        'warnings': [],
    }

    text = path.read_text(encoding='utf-8')

    # CJK check
    if has_cjk(text):
        result['has_cjk'] = True
        result['warnings'].append('CJK characters detected')

    # Frontmatter
    fm, raw_lines, fm_error, has_dups = parse_frontmatter(text)
    
    if fm_error or fm is None:
        result['errors'].append(fm_error or 'UNKNOWN_FRONTMATTER_ERROR')
        return result
    
    result['has_frontmatter'] = True
    result['has_duplicate_keys'] = has_dups
    if has_dups:
        result['errors'].append('DUPLICATE_KEYS: YAML keys appear more than once')

    # Required fields
    for field in REQUIRED_FIELDS:
        if field not in fm or not fm[field].strip():
            result['errors'].append(f'MISSING_{field.upper()}: frontmatter lacks "{field}"')
        else:
            if field == 'name':
                result['has_name'] = True
            elif field == 'description':
                result['has_description'] = True
    
    return result


def fix_skill(path: Path, dry_run: bool = True) -> str:
    """Tenta corrigir problemas de frontmatter.
    Retorna descrição da correção aplicada ou 'NO_FIX_NEEDED' / 'CANNOT_FIX'.
    """
    result = validate_skill(path)
    if not result['errors'] and not result['warnings']:
        return 'NO_FIX_NEEDED'
    
    text = path.read_text(encoding='utf-8')
    lines = text.split('\n')
    
    # Caso 1: Sem frontmatter nenhum
    if not result['has_frontmatter']:
        # Tenta extrair nome da pasta
        dir_name = path.parent.name
        name = dir_name.replace('-', ' ').title()
        
        frontmatter = f'---\nname: {dir_name}\ndescription: {name} skill for the OpenCode ecosystem\n---\n\n'
        new_text = frontmatter + text
        
        if not dry_run:
            path.write_text(new_text, encoding='utf-8')
        return f'ADDED_FRONTMATTER: inserted --- name={dir_name} ---'
    
    # Caso 2: Has frontmatter mas faltam campos
    if result['has_frontmatter']:
        fm, raw_lines, _, has_dups = parse_frontmatter(text)
        assert fm is not None, "has_frontmatter=True but parse returned None"
        
        if has_dups:
            if not dry_run:
                # Remove linhas duplicadas
                seen = {}
                new_raw = []
                for line in raw_lines:
                    m = re.match(r'^([a-zA-Z_][a-zA-Z0-9_-]*)\s*:', line.strip())
                    if m:
                        k = m.group(1)
                        if k in seen:
                            continue  # skip duplicate
                        seen[k] = True
                    new_raw.append(line)
                
                # Reconstruir
                header = '---\n'
                footer = '\n---'
                after_fm = '\n'.join(lines[len(raw_lines)+2:])  # skip --- + raw + ---
                new_text = header + '\n'.join(new_raw) + footer + '\n' + after_fm
                path.write_text(new_text, encoding='utf-8')
            return 'REMOVED_DUPLICATE_KEYS'
        
        missing = []
        for field in REQUIRED_FIELDS:
            if field not in fm:
                dir_name = path.parent.name
                val = dir_name if field == 'name' else f'{dir_name.replace("-", " ").title()} skill for the OpenCode ecosystem'
                missing.append(field)
                
                if not dry_run:
                    # Insert after last frontmatter line
                    insert_pos = len(raw_lines) + 1  # after ---\n
                    lines.insert(insert_pos, f'{field}: {val}')
                    path.write_text('\n'.join(lines), encoding='utf-8')
        
        if missing:
            return f'ADDED_FIELDS: {", ".join(missing)}'
    
    return 'CANNOT_FIX'


def scan_all() -> list:
    """Varre skills/ recursivamente, valida cada SKILL.md."""
    results = []
    for skmd in sorted(SKILLS_BASE.rglob('SKILL.md')):
        results.append(validate_skill(skmd))
    return results


def print_report(results: list):
    """Imprime relatório tabular."""
    total = len(results)
    passed = sum(1 for r in results if not r['errors'] and not r['warnings'])
    failed = total - passed

    print(f"{'='*80}")
    print(f"  SPEC-025 Frontmatter Validator — {total} skills scanned")
    print(f"  PASS: {passed}  |  FAIL: {failed}  |  OVERSIZE: {sum(1 for r in results if r['oversize'])}")
    print(f"{'='*80}\n")

    # Tabela compacta
    header = f"{'STATUS':7} {'BYTES':6} {'FM':4} {'NM':4} {'DS':4} {'DUP':4} {'CJK':4} {'PATH'}"
    print(header)
    print('-' * len(header))

    for r in results:
        has_err = bool(r['errors'])
        status = 'FAIL' if has_err or r['warnings'] else 'PASS'
        fm = 'Y' if r['has_frontmatter'] else 'N'
        nm = 'Y' if r['has_name'] else 'N'
        ds = 'Y' if r['has_description'] else 'N'
        dup = 'Y' if r['has_duplicate_keys'] else 'N'
        cjk = 'Y' if r['has_cjk'] else 'N'
        err_tag = ''
        if has_err:
            codes = [e.split(':')[0][:10] for e in r['errors']]
            err_tag = '  [' + '+'.join(codes) + ']'
        elif r['warnings']:
            err_tag = '  [WARN]'
        
        sz = str(r['bytes']).rjust(6)
        print(f"{status:7} {sz} {fm:4} {nm:4} {ds:4} {dup:4} {cjk:4} {r['relative'][:80]}{err_tag}")

    print(f"\n{'='*80}")
    print(f"  Total: {total}  |  PASS: {passed}  |  FAIL: {failed}")
    if failed > 0:
        print(f"\n  --- DETAILED ERRORS ---")
        for r in results:
            if r['errors']:
                print(f"\n  [{r['relative']}]")
                for e in r['errors']:
                    print(f"    ERROR: {e}")
            if r['warnings']:
                print(f"    WARN: {'; '.join(r['warnings'])}")
    print()


def main():
    args = set(sys.argv[1:])
    do_json = '--json' in args
    do_fix = '--fix' in args
    dry_run = '--dry-run' in args or not do_fix

    results = scan_all()

    if do_fix:
        print("FIX MODE — dry_run =", dry_run)
        for r in results:
            if r['errors'] or r['warnings']:
                fix_msg = fix_skill(Path(r['path']), dry_run=dry_run)
                print(f"  {fix_msg:45} {r['relative']}")
        print()
        # Re-scan after fix
        if not dry_run:
            results = scan_all()

    print_report(results)

    if do_json:
        tmp = Path(tempfile.mkstemp(suffix='.json')[1])
        tmp.write_text(json.dumps({
            'summary': {
                'total': len(results),
                'passed': sum(1 for r in results if not r['errors'] and not r['warnings']),
                'failed': sum(1 for r in results if bool(r['errors'] or r['warnings'])),
                'oversize': sum(1 for r in results if r['oversize']),
            },
            'results': results,
        }, indent=2, ensure_ascii=False), encoding='utf-8')
        print(f"JSON output: {tmp}")


if __name__ == '__main__':
    main()
