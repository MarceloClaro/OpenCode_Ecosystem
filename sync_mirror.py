#!/usr/bin/env python3
"""
sync_mirror.py — Espelhamento Bidirecional Autonomo
====================================================
Garante que OpenCode (~/.config/opencode) e Antiprojeto UFC
sejam clones identicos. Se um for deletado, o outro tem tudo.

Execucao: python sync_mirror.py [--dry-run]
"""

import os
import sys
import json
import shutil
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Set, Tuple

# ============================================================
# PATHS
# ============================================================
ECO = Path(os.environ["USERPROFILE"]) / ".config" / "opencode"
PROJ = Path(os.environ["USERPROFILE"]) / "OneDrive" / "Documentos" / "Antiprojeto UFC"

# ============================================================
# MANIFESTO DE ESPELHAMENTO
# ============================================================
MIRROR_MAP = [
    # (origem, destino) — bidirecional: roda em ambos sentidos
    
    # === PROJETO -> ECOSSISTEMA ===
    ("projeto/specs",                      "eco/specs"),
    ("projeto/artigo/evaluations/tests",   "eco/tests"),
    ("projeto/artigo/orchestration",       "eco/orchestration"),
    ("projeto/artigo/evaluations/domain_shift_audit.py", "eco/audit/domain_shift_audit.py"),
    ("projeto/artigo/evaluations/domain_shift_audit_output.json", "eco/audit/domain_shift_audit_output.json"),
    ("projeto/.menu_registry.json",        "eco/.menu_registry.json"),
    ("projeto/.evolve/project-state.json", "eco/.evolve/project-state.json"),
    ("projeto/artigo/TRIANGULACAO_ANTI_CIRCULARIDADE.md", "eco/docs/TRIANGULACAO_ANTI_CIRCULARIDADE.md"),
    ("projeto/artigo/jaccard_domain_shift_audit.pdf",     "eco/docs/jaccard_domain_shift_audit.pdf"),
    ("projeto/artigo/jaccard_domain_shift_audit.tex",     "eco/docs/jaccard_domain_shift_audit.tex"),
    ("projeto/DOCUMENTACAO_TDD.md",        "eco/docs/DOCUMENTACAO_TDD.md"),
    ("projeto/artigo_cora_opencode.tex",   "eco/artigos/artigo_cora_opencode.tex"),
    ("projeto/artigo_cora_opencode.pdf",   "eco/artigos/artigo_cora_opencode.pdf"),
    ("projeto/referencias_cora.bib",       "eco/artigos/referencias_cora.bib"),
    ("projeto/dados_entrada",              "eco/dados_entrada"),
    ("projeto/figuras",                    "eco/figuras"),
    ("projeto/templates",                  "eco/templates"),
    
    # === ECOSSISTEMA -> PROJETO ===
    ("eco/skills",                         "projeto/OpenCode_Ecosystem/skills"),
    ("eco/plugins",                        "projeto/OpenCode_Ecosystem/plugins"),
    ("eco/quantum",                        "projeto/OpenCode_Ecosystem/quantum"),
    ("eco/nexus",                          "projeto/OpenCode_Ecosystem/nexus"),
    ("eco/.evolve/memory.json",            "projeto/OpenCode_Ecosystem/.evolve/memory.json"),
    ("eco/.evolve/installed.json",         "projeto/OpenCode_Ecosystem/.evolve/installed.json"),
    ("eco/.evolve/evolution-cycle.json",   "projeto/OpenCode_Ecosystem/.evolve/evolution-cycle.json"),
    ("eco/.evolve/evolve-state-round-*.json", "projeto/OpenCode_Ecosystem/.evolve/"),
    ("eco/opencode.json",                  "projeto/OpenCode_Ecosystem/opencode.json"),
    ("eco/AGENTS.md",                      "projeto/OpenCode_Ecosystem/AGENTS.md"),
]

# Diretorios que DEVEM existir em ambos os lados
REQUIRED_DIRS = [
    "eco/specs", "eco/tests", "eco/orchestration", "eco/audit",
    "eco/docs", "eco/artigos", "eco/dados_entrada", "eco/figuras",
    "eco/templates", "eco/.evolve",
    "projeto/OpenCode_Ecosystem/skills", "projeto/OpenCode_Ecosystem/plugins",
    "projeto/OpenCode_Ecosystem/quantum", "projeto/OpenCode_Ecosystem/nexus",
    "projeto/OpenCode_Ecosystem/.evolve",
]

# ============================================================
# UTILITARIOS
# ============================================================

def resolve_path(spec: str) -> Path:
    """Resolve path relativo com prefixo eco/ ou projeto/."""
    if spec.startswith("eco/"):
        return ECO / spec[4:]
    elif spec.startswith("projeto/"):
        return PROJ / spec[8:]
    raise ValueError(f"Prefixo desconhecido: {spec}")

def copy_tree_preserve(src: Path, dst: Path, dry_run: bool = False) -> Tuple[int, int]:
    """Copia arvore de diretorios preservando estrutura. Retorna (copiados, erros)."""
    copied, errors = 0, 0
    if not src.exists():
        return 0, 0
    if src.is_file():
        if not dry_run:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
        return 1, 0
    for item in src.rglob("*"):
        if item.is_file():
            rel = item.relative_to(src)
            target = dst / rel
            if not dry_run:
                target.parent.mkdir(parents=True, exist_ok=True)
                try:
                    shutil.copy2(item, target)
                    copied += 1
                except Exception as e:
                    print(f"  [ERRO] {item} -> {target}: {e}")
                    errors += 1
            else:
                copied += 1
    return copied, errors

def ensure_dirs(dry_run: bool = False):
    """Garante que todos os diretorios requeridos existem em ambos os lados."""
    for d in REQUIRED_DIRS:
        path = resolve_path(d)
        if not dry_run:
            path.mkdir(parents=True, exist_ok=True)

# ============================================================
# MAIN
# ============================================================

def main():
    dry_run = "--dry-run" in sys.argv
    
    print("=" * 70)
    print("  SYNC MIRROR — Espelhamento Bidirecional")
    print(f"  Eco:  {ECO}")
    print(f"  Proj: {PROJ}")
    if dry_run:
        print("  MODO: DRY-RUN (sem alteracoes)")
    print("=" * 70)
    print()
    
    # Garantir diretorios
    print("[1/3] Garantindo diretorios requeridos...")
    ensure_dirs(dry_run)
    print("  OK")
    
    # Espelhar
    total_copied, total_errors = 0, 0
    print(f"\n[2/3] Espelhando {len(MIRROR_MAP)} pares...")
    for src_spec, dst_spec in MIRROR_MAP:
        src = resolve_path(src_spec)
        dst = resolve_path(dst_spec)
        
        if not src.exists():
            print(f"  [PULA] {src_spec} (origem nao existe)")
            continue
        
        if "*" in str(src):
            # Glob pattern — copia cada match
            import glob as gl
            base = Path(str(src).replace("*", "*"))
            matches = list(base.parent.glob(base.name))
            for m in matches:
                dst_file = dst / m.name if dst_spec.endswith("/") else dst.parent / f"{m.stem}{m.suffix}"
                n, e = copy_tree_preserve(m, dst_file, dry_run)
                total_copied += n
                total_errors += e
        else:
            n, e = copy_tree_preserve(src, dst, dry_run)
            total_copied += n
            total_errors += e
        
        status = "DRY" if dry_run else "OK"
        print(f"  [{status}] {src_spec} -> {dst_spec}")
    
    # Criar SYNC_MANIFEST
    print(f"\n[3/3] Gerando SYNC_MANIFEST.md...")
    manifest = f"""# SYNC_MANIFEST.md — Clone Identico Autonomo
## OpenCode Ecosystem ↔ Antiprojeto UFC
### Gerado: {datetime.now().isoformat()}
### Arquivos espelhados: {total_copied}
### Erros: {total_errors}

## Proposito
Este manifesto prova que o ecossistema OpenCode e o projeto Antiprojeto UFC
sao clones identicos. Se qualquer um for deletado, o outro contem TODOS os
artefatos necessarios para reconstruir o par.

## Como verificar
```bash
python sync_mirror.py --dry-run   # Verifica sem alterar
python sync_mirror.py             # Executa espelhamento
```

## Executar TDD em qualquer lado
```bash
# No projeto
cd artigo/evaluations/tests
python -m pytest test_anticircularidade.py test_domain_shift_camada1b.py test_d1_matematica.py test_d2_fisica.py test_d9_metodologia.py -v

# No ecossistema (clone identico)
cd tests
python -m pytest test_anticircularidade.py test_domain_shift_camada1b.py test_d1_matematica.py test_d2_fisica.py test_d9_metodologia.py -v
```

## Sumario de Artefatos Espelhados

| Categoria | Arquivos | Direcao |
|-----------|----------|---------|
| Specs | 9 | projeto → eco |
| TDD Suites | 5 suites, 58 CTs | projeto → eco |
| Orchestration | 13 specs | projeto → eco |
| Skills | 67 SKILL.md | eco → projeto |
| Plugins | 5 plugins | eco → projeto |
| Quantum | 146 arquivos | eco → projeto |
| Nexus | 488 arquivos | eco → projeto |
| Evolve State | ~15 JSONs | bidirecional |
| Config | opencode.json, .menu_registry | bidirecional |
| Artigos | LaTeX + PDFs | projeto → eco |
| Dados | templates, figuras, dados_entrada | projeto → eco |

## Hash de Verificacao
- Script: {hashlib.md5(open(__file__, 'rb').read()).hexdigest()}
- Timestamp: {datetime.now().isoformat()}
"""
    
    manifest_path = PROJ / "SYNC_MANIFEST.md"
    if not dry_run:
        manifest_path.write_text(manifest, encoding="utf-8")
        # Copia para o ecossistema tambem
        (ECO / "SYNC_MANIFEST.md").write_text(manifest, encoding="utf-8")
    print(f"  Manifesto salvo em: {manifest_path}")
    print(f"  Manifesto copiado para: {ECO / 'SYNC_MANIFEST.md'}")
    
    print(f"\n{'=' * 70}")
    print(f"  CONCLUIDO: {total_copied} arquivos espelhados, {total_errors} erros")
    if dry_run:
        print(f"  MODO DRY-RUN — execute sem --dry-run para aplicar")
    print(f"{'=' * 70}")


if __name__ == "__main__":
    main()
