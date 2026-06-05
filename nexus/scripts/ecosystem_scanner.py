"""ecosystem_scanner.py - Scanner autonomo do ecossistema OpenCode.

Auto-descobre todos os componentes, gera manifesto JSON com metricas,
detecta anomalias e sugere acoes corretivas.

Uso:
    python nexus/scripts/ecosystem_scanner.py --scan
    python nexus/scripts/ecosystem_scanner.py --manifest
    python nexus/scripts/ecosystem_scanner.py --diff ciclo_anterior.json
"""

import json
import os
import re
import hashlib
import sys
from pathlib import Path
from datetime import datetime
from typing import Any

WORKSPACE = Path(__file__).parent.parent.parent.resolve()
SCAN_DIRS = ["skills", "nexus", "plugins", "evals", "basis-research", "quantum", "criador-artigo"]
MANIFEST_PATH = WORKSPACE / "cache" / "ecosystem_manifest.json"
HISTORY_PATH = WORKSPACE / "cache" / "ecosystem_history.json"


def scan_skills() -> list[dict]:
    skills = []
    for skill_md in (WORKSPACE / "skills").rglob("SKILL.md"):
        content = skill_md.read_text(encoding="utf-8", errors="ignore")
        lines = content.splitlines()
        scripts_dir = skill_md.parent / "scripts"
        skills.append({
            "name": skill_md.parent.name,
            "path": str(skill_md.relative_to(WORKSPACE)),
            "bytes": len(content),
            "lines": len(lines),
            "frontmatter": content.startswith("---"),
            "has_name": "name:" in content[:200],
            "has_description": "description:" in content[:200],
            "cjk_leak": bool(re.search(r'[\u4e00-\u9fff]', content)),
            "scripts": [
                str(s.relative_to(WORKSPACE)) for s in scripts_dir.rglob("*.py")
            ] if scripts_dir.exists() else [],
        })
    return skills


def _parse_imports(content: str) -> list[str]:
    """Extrai todos os modulos importados, incluindo import a, b, c."""
    imports = []
    for line in content.splitlines():
        line = line.strip()
        if line.startswith("import "):
            # import a, b, c  ou  import a as b
            mods = line[7:].split(",")
            for m in mods:
                m = m.strip().split()[0]  # pega 'a' de 'a as b'
                if m:
                    imports.append(m)
        elif line.startswith("from "):
            parts = line.split()
            if len(parts) > 1:
                imports.append(parts[1])
    return imports


def scan_scripts() -> list[dict]:
    scripts = []
    for sd in SCAN_DIRS:
        base = WORKSPACE / sd
        if base.exists():
            for f in sorted(base.rglob("*.py")):
                if "temp" in str(f):
                    continue
                content = f.read_text(encoding="utf-8", errors="ignore")
                is_init = f.name == "__init__.py"
                has_entrypoint = "def main()" in content or "if __name__" in content
                # Detecta se ha codigo module-level com side effects (nao apenas imports/defs/class)
                has_side_effects = False
                for line in content.splitlines():
                    st = line.strip()
                    if not st or st.startswith("#") or st.startswith("import ") or st.startswith("from ") or \
                       st.startswith("def ") or st.startswith("class ") or st.startswith("@") or \
                       st.startswith('"""') or st.startswith("'''") or st in ('"""', "'''"):
                        continue
                    has_side_effects = True
                    break
                needs_entrypoint = not is_init and has_side_effects
                scripts.append({
                    "name": f.name,
                    "path": str(f.relative_to(WORKSPACE)),
                    "lines": len(content.splitlines()),
                    "bytes": len(content),
                    "hash": hashlib.md5(content.encode()).hexdigest()[:12],
                    "imports": _parse_imports(content),
                    "functions": re.findall(r'^def\s+(\w+)', content, re.M),
                    "classes": re.findall(r'^class\s+(\w+)', content, re.M),
                    "is_init": is_init,
                    "needs_entrypoint": needs_entrypoint,
                    "has_entrypoint": has_entrypoint,
                })
    return scripts


def scan_plugins() -> list[dict]:
    plugins = []
    base = WORKSPACE / "plugins"
    if base.exists():
        for f in base.glob("*.ts"):
            content = f.read_text(encoding="utf-8", errors="ignore")
            plugins.append({
                "name": f.stem,
                "path": str(f.relative_to(WORKSPACE)),
                "bytes": len(content),
                "lines": len(content.splitlines()),
                "hash": hashlib.md5(content.encode()).hexdigest()[:12],
            })
    return plugins


def scan_agents() -> list[dict]:
    agents = []
    # Agentes Python do basis-research
    for base_dir in ["basis-research/agents", "basis-research/core"]:
        d = WORKSPACE / base_dir
        if d.exists():
            for f in d.glob("*.py"):
                content = f.read_text(encoding="utf-8", errors="ignore")
                agents.append({
                    "name": f.stem,
                    "path": str(f.relative_to(WORKSPACE)),
                    "lines": len(content.splitlines()),
                    "type": "core" if "core" in str(f) else "agent",
                    "functions": len(re.findall(r'^def\s+(\w+)', content, re.M)),
                })
    # Definicoes de agentes do sistema (arquivos .md)
    agents_dir = WORKSPACE / "agents"
    if agents_dir.exists():
        for f in agents_dir.glob("*.md"):
            content = f.read_text(encoding="utf-8", errors="ignore")
            agents.append({
                "name": f.stem,
                "path": str(f.relative_to(WORKSPACE)),
                "lines": len(content.splitlines()),
                "type": "system_agent",
                "functions": 0,
            })
    return agents


def scan_evals() -> list[dict]:
    evals = []
    d = WORKSPACE / "evals"
    if d.exists():
        for f in d.glob("*.md"):
            content = f.read_text(encoding="utf-8", errors="ignore")
            score = re.search(r'overall_health:\s*(\d+)', content)
            evals.append({
                "name": f.stem,
                "path": str(f.relative_to(WORKSPACE)),
                "bytes": len(content),
                "health": int(score.group(1)) if score else None,
            })
    return evals


def scan_git() -> dict:
    git_dir = WORKSPACE / ".git"
    if not git_dir.exists():
        return {"status": "no_git_repo"}
    try:
        import subprocess
        r = subprocess.run(["git", "log", "--oneline", "-1"], capture_output=True, text=True, cwd=str(WORKSPACE))
        last_commit = r.stdout.strip() if r.returncode == 0 else "no_commits"
        r2 = subprocess.run(["git", "status", "--short"], capture_output=True, text=True, cwd=str(WORKSPACE))
        dirty = len(r2.stdout.strip().splitlines()) if r2.stdout.strip() else 0
        return {"last_commit": last_commit, "dirty_files": dirty}
    except:
        return {"status": "git_error"}


def scan_health(skills: list[dict], scripts: list[dict]) -> dict:
    scores = {}
    scores["skills_under_2500b"] = sum(1 for s in skills if s["bytes"] <= 2500)
    scores["skills_total"] = len(skills)
    scores["frontmatter_ok"] = sum(1 for s in skills if s["frontmatter"] and s["has_name"] and s["has_description"])
    scores["cjk_leaks"] = sum(1 for s in skills if s["cjk_leak"])
    scores["py_compile_ok"] = "nao_verificado"
    scores["scripts_total"] = len(scripts)
    scores["scripts_needing_entrypoint"] = sum(1 for s in scripts if s["needs_entrypoint"] and not s["has_entrypoint"])
    scores["scripts_with_main"] = sum(1 for s in scripts if s["has_entrypoint"])
    scores["total_lines_py"] = sum(s["lines"] for s in scripts)
    return scores


def scan() -> dict:
    skills = scan_skills()
    scripts = scan_scripts()
    plugins = scan_plugins()
    agents = scan_agents()
    evals = scan_evals()
    git = scan_git()
    health = scan_health(skills, scripts)

    manifest = {
        "timestamp": datetime.now().isoformat(),
        "version": "3.5",
        "ciclo": "7.3",
        "git": git,
        "health": health,
        "components": {
            "skills": skills,
            "scripts": scripts,
            "plugins": plugins,
            "agents": agents,
            "evals": evals,
        },
        "totals": {
            "skills": len(skills),
            "scripts": len(scripts),
            "plugins": len(plugins),
            "agents": len(agents),
            "evals": len(evals),
            "total_lines_py": health["total_lines_py"],
        },
        "anomalies": detect_anomalies(skills, scripts, health),
        "recommendations": generate_recommendations(skills, scripts, health),
    }
    return manifest


def detect_anomalies(skills, scripts, health) -> list[dict]:
    anomalies = []
    for s in skills:
        if s["cjk_leak"]:
            anomalies.append({"type": "cjk_leak", "component": s["name"], "severity": "high",
                              "msg": f"CJK detectado em {s['name']}/SKILL.md"})
        if s["bytes"] > 2500:
            anomalies.append({"type": "skill_over_limit", "component": s["name"], "severity": "medium",
                              "msg": f"SKILL.md {s['bytes']}B > 2500B"})
        if not s["frontmatter"]:
            anomalies.append({"type": "missing_frontmatter", "component": s["name"], "severity": "high",
                              "msg": f"Sem frontmatter YAML"})

    # Check script import consistency
    imported = set()
    for s in scripts:
        for imp in s["imports"]:
            imported.add(imp)
    for s in scripts:
        if s["name"] == "edital_search.py":
            for expected in ["argparse", "asyncio", "hashlib", "json", "re", "sqlite3", "subprocess"]:
                if expected not in str(s["imports"]):
                    anomalies.append({"type": "missing_import", "component": s["name"], "severity": "low",
                                      "msg": f"Import {expected} ausente"})

    return anomalies


def generate_recommendations(skills, scripts, health) -> list[dict]:
    recs = []
    if health["cjk_leaks"] > 0:
        recs.append({"area": "qualidade", "acao": "executar ptbr_corrector.py",
                     "impacto": f"{health['cjk_leaks']} skills com CJK"})
    if health["skills_total"] > 0 and health["frontmatter_ok"] < health["skills_total"]:
        recs.append({"area": "qualidade", "acao": "adicionar frontmatter faltante",
                     "impacto": f"{health['skills_total'] - health['frontmatter_ok']} skills sem frontmatter"})
    if health["scripts_needing_entrypoint"] > 0:
        recs.append({"area": "arquitetura", "acao": "adicionar entrypoint main()",
                     "impacto": f"{health['scripts_needing_entrypoint']} scripts sem entrypoint"})

    # Check if any skill has no scripts
    for s in skills:
        if s["name"] in ("editais-br", "docling-pdf-extraction") and not s["scripts"]:
            recs.append({"area": "integracao", "acao": f"verificar scripts em {s['name']}",
                         "impacto": "Skill sem scripts vinculados"})

    # Expansion opportunities
    recs.append({"area": "expansao", "acao": "adicionar integracao com CAPES API",
                 "impacto": "Dados oficiais de bolsas em tempo real"})
    recs.append({"area": "expansao", "acao": "adicionar integracao com CNPq API (Lattes)",
                 "impacto": "Dados curriculares para scoring de perfil"})

    return recs


def salvar_historico(manifest: dict):
    hist = {"snapshots": []}
    if HISTORY_PATH.exists():
        try:
            hist = json.loads(HISTORY_PATH.read_text(encoding="utf-8"))
        except:
            pass
    # Extract key metrics for history
    snapshot = {
        "timestamp": manifest["timestamp"],
        "ciclo": manifest["ciclo"],
        "health": {k: v for k, v in manifest["health"].items() if isinstance(v, (int, float))},
        "totals": manifest["totals"],
        "anomalies": len(manifest["anomalies"]),
        "recommendations": len(manifest["recommendations"]),
    }
    hist["snapshots"].append(snapshot)
    HISTORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    HISTORY_PATH.write_text(json.dumps(hist, ensure_ascii=False, indent=2), encoding="utf-8")


def diff_snapshots(anterior_path: str) -> dict:
    """Compara manifesto atual com snapshot anterior."""
    if not Path(anterior_path).exists():
        return {"error": f"Arquivo {anterior_path} nao encontrado"}
    anterior = json.loads(Path(anterior_path).read_text(encoding="utf-8"))
    atual = scan()
    delta = {
        "timestamp": datetime.now().isoformat(),
        "skills_diff": len(atual["components"]["skills"]) - len(anterior.get("components", {}).get("skills", [])),
        "scripts_diff": len(atual["components"]["scripts"]) - len(anterior.get("components", {}).get("scripts", [])),
        "new_anomalies": len(atual["anomalies"]) - len(anterior.get("anomalies", [])),
        "health_delta": {},
    }
    for k in atual["health"]:
        if isinstance(atual["health"][k], (int, float)) and k in anterior.get("health", {}):
            delta["health_delta"][k] = atual["health"][k] - anterior["health"][k]
    return delta


def gerar_relatorio(manifest: dict) -> str:
    h = manifest["health"]
    tots = manifest["totals"]
    anoms = manifest["anomalies"]
    recs = manifest["recommendations"]
    lines = []
    lines.append("# Relatorio de Scan Autonomo do Ecossistema")
    lines.append(f"**Data**: {manifest['timestamp']}")
    lines.append(f"**Ciclo**: {manifest['ciclo']}  |  **Version**: {manifest['version']}")
    lines.append("")
    lines.append("## Metricas")
    lines.append(f"| Metrica | Valor |")
    lines.append(f"|---------|-------|")
    lines.append(f"| Skills | {tots['skills']} ({h['skills_under_2500b']}/{h['skills_total']} under 2.5KB) |")
    lines.append(f"| Scripts Python | {tots['scripts']} ({tots['total_lines_py']} linhas) |")
    lines.append(f"| Plugins TS | {tots['plugins']} |")
    lines.append(f"| Agentes | {tots['agents']} |")
    lines.append(f"| Frontmatter OK | {h['frontmatter_ok']}/{h['skills_total']} |")
    lines.append(f"| CJK Leaks | {h['cjk_leaks']} |")
    lines.append(f"| Anomalias | {len(anoms)} |")
    lines.append(f"| Recomendacoes | {len(recs)} |")
    lines.append("")
    if anoms:
        lines.append("## Anomalias Detectadas")
        for a in anoms:
            lines.append(f"- [{a['severity'].upper()}] {a['msg']}")
        lines.append("")
    if recs:
        lines.append("## Recomendacoes")
        for r in recs:
            lines.append(f"- **{r['area']}**: {r['acao']} ({r['impacto']})")
        lines.append("")
    lines.append("## Componentes")
    for s in manifest["components"]["skills"]:
        lines.append(f"- **{s['name']}**: {s['bytes']}B, {s['lines']} linhas, scripts={len(s['scripts'])}")
    lines.append("")
    lines.append("_Gerado automaticamente por ecosystem_scanner.py_")
    return "\n".join(lines)


def main():
    import argparse
    p = argparse.ArgumentParser(description="Scanner autonomo do ecossistema")
    p.add_argument("--scan", action="store_true", help="Escaneia ecossistema e salva manifesto")
    p.add_argument("--report", action="store_true", help="Gera relatorio markdown")
    p.add_argument("--diff", metavar="SNAPSHOT_JSON", help="Compara com snapshot anterior")
    p.add_argument("--manifest", action="store_true", help="Exibe manifesto como JSON")
    args = p.parse_args()

    if args.diff:
        d = diff_snapshots(args.diff)
        print(json.dumps(d, ensure_ascii=False, indent=2))
        return

    manifest = scan()

    if args.manifest:
        print(json.dumps(manifest, ensure_ascii=False, indent=2))

    if args.scan or args.report or not any([args.diff, args.manifest]):
        MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
        MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        salvar_historico(manifest)
        print(f"[scanner] Manifesto salvo em {MANIFEST_PATH}")
        print(f"[scanner] {len(manifest['anomalies'])} anomalias, {len(manifest['recommendations'])} recomendacoes")

    if args.report:
        report = gerar_relatorio(manifest)
        report_path = WORKSPACE / "evals" / f"scan_{datetime.now().strftime('%Y%m%d_%H%M')}.md"
        report_path.write_text(report, encoding="utf-8")
        print(f"[scanner] Relatorio salvo em {report_path}")


if __name__ == "__main__":
    main()
