# -*- coding: utf-8 -*-
"""
SELF HEALER v2.1-DI - Sistema de auto-cura autonomo refatorado com DI.

Mudancas:
- Toda logica encapsulada na classe SelfHealer
- SelfHealer aceita state_manager e event_bus via construtor
- Fallback para Container.instance().resolve() para compatibilidade
- Preserva 100% da logica de negocio original

Uso:
    python nexus/self_healer.py --check
    python nexus/self_healer.py --fix
    python nexus/self_healer.py --auto
"""

import re
import sys
import json
import hashlib
import asyncio
import subprocess
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError
from typing import Optional

from core.config import settings
from core.container import Container
from core.interfaces import IStateManager, IEventBus


class SelfHealer:
    """Sistema de auto-cura autonomo com injecao de dependencia."""

    # Paths centralizados via core.config
    SYNTAX_CACHE_PATH = settings.CACHE_DIR / "syntax_cache.json"
    SYNTAX_TIMEOUT = 10
    MAX_WORKERS = 4

    def __init__(self, state_manager: Optional[IStateManager] = None, event_bus: Optional[IEventBus] = None):
        self._sm = state_manager or Container.instance().resolve('state_manager')
        self._eb = event_bus or Container.instance().resolve('event_bus')
        self.WORKSPACE = settings.ECO_ROOT

    def check_cjk_leaks(self) -> list[dict]:
        """Detecta CJK leaks em SKILL.md."""
        findings = []
        for md_file in self.WORKSPACE.rglob("SKILL.md"):
            content = md_file.read_text(encoding="utf-8", errors="ignore")
            cjk = re.findall(r'[\u4e00-\u9fff]+', content)
            if cjk:
                findings.append({
                    "path": str(md_file.relative_to(self.WORKSPACE)),
                    "count": len(cjk),
                    "samples": list(set(cjk))[:5],
                })
        return findings

    def fix_cjk_leaks(self, findings: list[dict]) -> int:
        """Remove CJK de SKILL.md. Retorna numero de arquivos alterados."""
        fixed = 0
        for f in findings:
            path = self.WORKSPACE / f["path"]
            content = path.read_text(encoding="utf-8", errors="ignore")
            cleaned = re.sub(r'[\u4e00-\u9fff]+', '', content)
            cleaned = re.sub(r'\n{4,}', '\n\n\n', cleaned)
            if cleaned != content:
                path.write_text(cleaned, encoding="utf-8")
                fixed += 1
                print(f"[healer] CJK removido de {f['path']}")
        return fixed

    def check_frontmatter(self) -> list[dict]:
        """Verifica frontmatter YAML em SKILL.md."""
        findings = []
        for md_file in self.WORKSPACE.rglob("SKILL.md"):
            content = md_file.read_text(encoding="utf-8", errors="ignore")
            issues = []
            if not content.startswith("---"):
                issues.append("sem_frontmatter")
            else:
                if "name:" not in content[:200]:
                    issues.append("sem_name")
                if "description:" not in content[:200]:
                    issues.append("sem_description")
            if issues:
                findings.append({
                    "path": str(md_file.relative_to(self.WORKSPACE)),
                    "issues": issues,
                })
        return findings

    def fix_frontmatter(self, findings: list[dict]) -> int:
        """Adiciona frontmatter basico onde faltante."""
        fixed = 0
        for f in findings:
            path = self.WORKSPACE / f["path"]
            content = path.read_text(encoding="utf-8", errors="ignore")
            if "sem_frontmatter" in f["issues"]:
                name = path.parent.name
                new_content = f"""---
name: {name}
description: "Skill do ecossistema OpenCode - {name}"
---

{content}
"""
                path.write_text(new_content, encoding="utf-8")
                fixed += 1
                print(f"[healer] Frontmatter adicionado em {f['path']}")
        return fixed

    def check_skill_sizes(self) -> list[dict]:
        """Verifica SKILL.md > 2.5KB."""
        findings = []
        for md_file in self.WORKSPACE.rglob("SKILL.md"):
            size = len(md_file.read_text(encoding="utf-8", errors="ignore"))
            if size > 2500:
                findings.append({
                    "path": str(md_file.relative_to(self.WORKSPACE)),
                    "bytes": size,
                    "over_by": size - 2500,
                })
        return findings

    def _carregar_cache_syntax(self) -> dict:
        if self.SYNTAX_CACHE_PATH.exists():
            try:
                return json.loads(self.SYNTAX_CACHE_PATH.read_text(encoding="utf-8"))
            except Exception:
                pass
        return {}

    def _salvar_cache_syntax(self, cache: dict):
        self.SYNTAX_CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
        self.SYNTAX_CACHE_PATH.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")

    def _check_single_file(self, py_file: Path, cache: dict) -> dict | None:
        """Verifica syntax de um unico arquivo, usando cache se inalterado."""
        content = py_file.read_bytes()
        h = hashlib.md5(content).hexdigest()
        rel = str(py_file.relative_to(self.WORKSPACE))

        if rel in cache and cache[rel] == h:
            return None

        try:
            r = subprocess.run(
                [sys.executable, "-m", "py_compile", str(py_file)],
                capture_output=True, text=True, timeout=self.SYNTAX_TIMEOUT
            )
            if r.returncode == 0:
                cache[rel] = h
                return None
            return {"path": rel, "error": r.stderr.strip()[:200]}
        except subprocess.TimeoutExpired:
            return {"path": rel, "error": f"timeout apos {self.SYNTAX_TIMEOUT}s"}

    def check_scripts_syntax(self) -> list[dict]:
        """Verifica syntax dos scripts Python com cache e execucao paralela."""
        cache = self._carregar_cache_syntax()
        findings = []
        files_to_check = [f for f in self.WORKSPACE.rglob("*.py") if "temp" not in str(f)]

        with ThreadPoolExecutor(max_workers=self.MAX_WORKERS) as executor:
            futuros = {executor.submit(self._check_single_file, f, cache): f for f in files_to_check}
            for futuro in as_completed(futuros):
                try:
                    resultado = futuro.result(timeout=self.SYNTAX_TIMEOUT + 2)
                    if resultado:
                        findings.append(resultado)
                except TimeoutError:
                    findings.append({
                        "path": str(futuros[futuro].relative_to(self.WORKSPACE)),
                        "error": "timeout no pool",
                    })

        self._salvar_cache_syntax(cache)
        return findings

    def check_and_report(self) -> dict:
        """Varre todas as anomalias, persiste via state_manager e retorna relatorio."""
        report = {
            "timestamp": datetime.now().isoformat(),
            "cjk_leaks": self.check_cjk_leaks(),
            "frontmatter_issues": self.check_frontmatter(),
            "skill_over_sizes": self.check_skill_sizes(),
            "syntax_errors": self.check_scripts_syntax(),
        }
        report["totals"] = {
            "cjk": len(report["cjk_leaks"]),
            "frontmatter": len(report["frontmatter_issues"]),
            "oversize": len(report["skill_over_sizes"]),
            "syntax": len(report["syntax_errors"]),
            "total": sum(len(v) for k, v in report.items() if k not in ("timestamp", "totals")),
        }
        self._sm.set("self_healer:last_report", report)
        hist = self._sm.get("self_healer:history", default=[])
        if not isinstance(hist, list):
            hist = []
        hist.append({
            "timestamp": report["timestamp"],
            "total": report["totals"]["total"],
            "cjk": report["totals"]["cjk"],
            "frontmatter": report["totals"]["frontmatter"],
            "oversize": report["totals"]["oversize"],
            "syntax": report["totals"]["syntax"],
        })
        if len(hist) > 50:
            hist[:] = hist[-50:]
        self._sm.set("self_healer:history", hist)
        return report

    def auto_fix(self, report: dict) -> dict:
        """Corrige automaticamente tudo que for viavel."""
        result = {"correcoes": {}}
        if report["cjk_leaks"]:
            n = self.fix_cjk_leaks(report["cjk_leaks"])
            result["correcoes"]["cjk_fixed"] = n
        if report["frontmatter_issues"]:
            n = self.fix_frontmatter(report["frontmatter_issues"])
            result["correcoes"]["frontmatter_fixed"] = n
        if report["syntax_errors"]:
            result["correcoes"]["syntax_errors"] = len(report["syntax_errors"])
            result["aviso"] = "Erros de sintaxe requerem correcao manual"
        if report["skill_over_sizes"]:
            result["correcoes"]["oversize_warning"] = len(report["skill_over_sizes"])
            result["aviso_oversize"] = "Skills >2.5KB requerem revisao manual de conteudo"
        result["timestamp"] = datetime.now().isoformat()
        self._sm.set("self_healer:last_fix", result)
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(
                self._eb.publish("self_healer.fix", data=result, source="self_healer")
            )
        except RuntimeError:
            pass
        return result


def main():
    import argparse
    p = argparse.ArgumentParser(description="Auto-cura do ecossistema (DI)")
    p.add_argument("--check", action="store_true", help="Verifica anomalias")
    p.add_argument("--fix", action="store_true", help="Corrige anomalias automaticamente")
    p.add_argument("--auto", action="store_true", help="Auto: check + fix integrado")
    args = p.parse_args()

    from core import initialize_core
    initialize_core()
    settings.ensure_dirs()

    healer = SelfHealer()
    report = healer.check_and_report()

    if args.check or args.auto or not args.fix:
        print(f"[healer] Check: {report['totals']['total']} anomalias encontradas")
        for k in ["cjk", "frontmatter", "oversize", "syntax"]:
            if report["totals"][k] > 0:
                print(f"  {k}: {report['totals'][k]}")
        for cat in ["cjk_leaks", "frontmatter_issues"]:
            for item in report.get(cat, []):
                print(f"    - {item['path']}")
        for item in report.get("syntax_errors", []):
            print(f"    ! {item['path']}: {item['error'][:80]}")

    if args.fix or args.auto:
        result = healer.auto_fix(report)
        fixes = result.get("correcoes", {})
        n = sum(v for v in fixes.values() if isinstance(v, int))
        print(f"[healer] {n} correcoes aplicadas")
        for k, v in fixes.items():
            if isinstance(v, int) and v > 0:
                print(f"  {k}: {v}")

    if args.auto and report["totals"]["total"] == 0:
        print("[healer] Ecossistema saudavel: nenhuma anomalia encontrada")

    try:
        loop = asyncio.get_running_loop()
        loop.create_task(
            healer._eb.publish("self_healer.check", data={
                "total": report["totals"]["total"],
                "timestamp": report["timestamp"],
            }, source="self_healer")
        )
    except RuntimeError:
        pass


if __name__ == "__main__":
    main()
