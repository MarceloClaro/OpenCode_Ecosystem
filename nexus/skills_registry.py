#!/usr/bin/env python3
"""skills_registry.py — Registro centralizado de skills do ecossistema.

Escaneia workspace-wide todos os SKILL.md, coleta métricas (tamanho,
frontmatter, CJK, categoria) e persiste em skills_registry.json + state_manager.

Uso:
    python nexus/skills_registry.py              # Scan + persist
    python nexus/skills_registry.py --report     # Apenas exibe relatório
    python nexus/skills_registry.py --sync       # Only sync to state_manager
"""

import sys, json, re, hashlib
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field, asdict
from typing import Optional

WORKSPACE = Path(__file__).parent.parent.resolve()
REGISTRY_PATH = WORKSPACE / "nexus" / "skills_registry.json"


@dataclass
class SkillEntry:
    name: str
    path: str  # relativo ao workspace
    category: str  # "system", "juridico", "research", "criador-artigo", etc.
    bytes: int
    has_frontmatter: bool
    has_name: bool
    has_description: bool
    cjk_count: int
    is_oversize: bool  # > 2500 bytes
    oversize_by: int = 0  # bytes acima do limite
    md5: str = ""
    last_checked: str = ""


def _infer_category(rel_path: str) -> str:
    """Infere categoria baseada no caminho relativo."""
    p = rel_path.replace("\\", "/")
    if p.startswith("skills/"):
        parts = p.split("/")
        return parts[1] if len(parts) > 2 else "uncategorized"
    if p.startswith(".claude/skills/"):
        parts = p.split("/")
        return f"dotclaude-{parts[2]}" if len(parts) > 2 else "dotclaude"
    if p.startswith("editais-br/"):
        return "editais-br"
    if p.startswith("stock-analysis/"):
        return "stock-analysis"
    if p.startswith("criador-artigo/"):
        return "criador-artigo"
    if p.startswith("genesis-writer/"):
        return "genesis-writer"
    if p.startswith("nexus/"):
        return "nexus"
    return "other"


def scan_all_skills() -> list[SkillEntry]:
    """Escaneia TODOS os SKILL.md no workspace (recursivo)."""
    entries = []
    seen = set()

    for md_file in sorted(WORKSPACE.rglob("SKILL.md")):
        rel = str(md_file.relative_to(WORKSPACE))
        if rel in seen:
            continue
        seen.add(rel)

        content = md_file.read_text(encoding="utf-8", errors="ignore")
        size = len(content.encode("utf-8"))
        md5_hash = hashlib.md5(content.encode()).hexdigest()

        # Frontmatter check
        has_fm = content.lstrip().startswith("---")
        has_name = "name:" in content[:300] if has_fm else False
        has_desc = "description:" in content[:300] if has_fm else False

        # CJK check
        cjk = len(re.findall(r'[\u4e00-\u9fff]+', content))

        # Oversize
        oversize = size > 2500
        over_by = size - 2500 if oversize else 0

        entries.append(SkillEntry(
            name=md_file.parent.name,
            path=rel,
            category=_infer_category(rel),
            bytes=size,
            has_frontmatter=has_fm,
            has_name=has_name,
            has_description=has_desc,
            cjk_count=cjk,
            is_oversize=oversize,
            oversize_by=over_by,
            md5=md5_hash,
            last_checked=datetime.now().isoformat(),
        ))

    return entries


def build_registry() -> dict:
    """Constrói o registro completo."""
    skills = scan_all_skills()
    oversize = [s for s in skills if s.is_oversize]
    healthy = [s for s in skills if not s.is_oversize]

    registry = {
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "workspace": str(WORKSPACE),
        "summary": {
            "total_skills": len(skills),
            "oversize_count": len(oversize),
            "healthy_count": len(healthy),
            "total_bytes": sum(s.bytes for s in skills),
            "categories": {},
        },
        "skills": [asdict(s) for s in skills],
    }

    # Summary por categoria
    for s in skills:
        cat = s.category
        if cat not in registry["summary"]["categories"]:
            registry["summary"]["categories"][cat] = {"total": 0, "oversize": 0, "bytes": 0}
        registry["summary"]["categories"][cat]["total"] += 1
        registry["summary"]["categories"][cat]["bytes"] += s.bytes
        if s.is_oversize:
            registry["summary"]["categories"][cat]["oversize"] += 1

    return registry


def save_registry(registry: dict):
    """Persiste o registro em JSON."""
    REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
    REGISTRY_PATH.write_text(
        json.dumps(registry, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )
    print(f"[registry] Salvo: {REGISTRY_PATH} ({len(registry['skills'])} skills)")


def sync_to_state_manager(registry: dict):
    """Sincroniza com o state_manager do core."""
    try:
        from core import initialize_core
        from core.container import Container
        initialize_core()
        sm = Container.instance().resolve("state_manager")
        sm.set("skills_registry:last_scan", registry)
        sm.set("skills_registry:oversize_count", registry["summary"]["oversize_count"])
        sm.set("skills_registry:total_skills", registry["summary"]["total_skills"])
        # Mantém histórico dos últimos 10 scans
        hist = sm.get("skills_registry:history", default=[])
        if not isinstance(hist, list):
            hist = []
        hist.append({
            "timestamp": registry["timestamp"],
            "total": registry["summary"]["total_skills"],
            "oversize": registry["summary"]["oversize_count"],
            "healthy": registry["summary"]["healthy_count"],
        })
        if len(hist) > 10:
            hist = hist[-10:]
        sm.set("skills_registry:history", hist)
        print(f"[registry] Sincronizado com state_manager")
    except Exception as e:
        print(f"[registry] Aviso: state_manager não disponível ({e})")


def print_report(registry: dict):
    """Exibe relatório formatado."""
    s = registry["summary"]
    print(f"\n{'='*50}")
    print(f"📋 SKILLS REGISTRY — {s['total_skills']} skills")
    print(f"{'='*50}")
    print(f"  Total:    {s['total_skills']}")
    print(f"  Saudáveis: {s['healthy_count']} (≤2.5KB)")
    print(f"  Oversize: {s['oversize_count']} (>2.5KB)")
    print(f"  Total em disco: {s['total_bytes']:,} bytes")
    print()
    print(f"  Por categoria:")
    for cat, stats in sorted(s["categories"].items()):
        bar = "🟡" if stats["oversize"] > 0 else "🟢"
        print(f"    {bar} {cat}: {stats['total']} skills ({stats['oversize']} oversize, {stats['bytes']:,} bytes)")

    if s["oversize_count"] > 0:
        print(f"\n  Skills >2.5KB:")
        for sk in registry["skills"]:
            if sk["is_oversize"]:
                flag = "🔴" if sk["bytes"] > 10000 else "🟡"
                print(f"    {flag} [{sk['category']}] {sk['path']}")
                print(f"         {sk['bytes']:,} bytes ({(sk['bytes']-2500):,} acima) | frontmatter={sk['has_frontmatter']} | CJK={sk['cjk_count']}")


def main():
    args = set(sys.argv[1:])
    only_report = "--report" in args
    only_sync = "--sync" in args

    if not only_sync:
        registry = build_registry()
        save_registry(registry)
        if only_report:
            print_report(registry)
            return

    # Sempre tenta sincronizar com state_manager
    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8")) if REGISTRY_PATH.exists() else build_registry()
    sync_to_state_manager(registry)
    print_report(registry)


if __name__ == "__main__":
    main()
