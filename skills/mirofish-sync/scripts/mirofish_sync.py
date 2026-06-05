"""
MiroFish Sync Agent (P19) — Motor de sincronização upstream ↔ OpenCode.

Monitora 666ghj/MiroFish, 666ghj/BettaFish, bytedance/deer-flow.
Detecta novos padrões, extrai via Reversa Scout, integra no ecossistema.

Uso:
    python mirofish_sync.py              # Verificar mudanças
    python mirofish_sync.py --sync       # Sincronizar
    python mirofish_sync.py --dry-run    # Apenas verificar
    python mirofish_sync.py --force      # Re-extrair todos
"""
import json, os, sys, hashlib, time
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum


# ═══════════════════════════════════════════════════════════════════
# Configuração
# ═══════════════════════════════════════════════════════════════════

WORKSPACE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
REVERSA_DIR = os.path.join(WORKSPACE, ".reversa")
VERSION_FILE = os.path.join(REVERSA_DIR, "mirofish_version.json")
SKILLS_DIR = os.path.join(WORKSPACE, "skills")

REPOS = {
    "MiroFish": {
        "owner": "666ghj", "repo": "MiroFish",
        "url": "https://github.com/666ghj/MiroFish",
        "branch": "main",
        "engine_dirs": ["backend/"],
        "doc_patterns": ["README.md", "README-ZH.md"],
    },
    "BettaFish": {
        "owner": "666ghj", "repo": "BettaFish",
        "url": "https://github.com/666ghj/BettaFish",
        "branch": "main",
        "engine_dirs": ["QueryEngine/", "MediaEngine/", "InsightEngine/",
                        "ForumEngine/", "ReportEngine/", "MindSpider/"],
        "doc_patterns": ["README.md", "README-EN.md"],
    },
    "DeerFlow": {
        "owner": "bytedance", "repo": "deer-flow",
        "url": "https://github.com/bytedance/deer-flow",
        "branch": "main",
        "engine_dirs": ["deer_flow/"],
        "doc_patterns": ["README.md"],
    },
}


# ═══════════════════════════════════════════════════════════════════
# Modelos de Dados
# ═══════════════════════════════════════════════════════════════════

class SyncAction(Enum):
    SKIP = "skip"               # Nada a fazer
    EXTRACT = "extract"         # Novo padrão para extrair
    UPDATE = "update"           # Padrão existente atualizado
    MONITOR_ONLY = "monitor"    # Apenas monitorar (docs/deps)


@dataclass
class CommitInfo:
    sha: str
    date: str
    message: str
    author: str


@dataclass
class SyncDiff:
    repo: str
    new_commits: List[CommitInfo] = field(default_factory=list)
    action: SyncAction = SyncAction.SKIP
    changed_files: List[str] = field(default_factory=list)
    new_patterns: List[str] = field(default_factory=list)
    details: str = ""


@dataclass
class SyncReport:
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    repos_checked: int = 3
    repos_with_changes: int = 0
    new_patterns_found: int = 0
    patterns_extracted: int = 0
    patterns_updated: int = 0
    diffs: List[SyncDiff] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


# ═══════════════════════════════════════════════════════════════════
# GitHub API Client (usa opencode gh CLI ou GitHub API)
# ═══════════════════════════════════════════════════════════════════

class GitHubMonitor:
    """Monitora repositórios GitHub usando gh CLI ou requests."""

    def __init__(self, token: str = ""):
        self.token = token or os.environ.get("GITHUB_TOKEN", "")
        self.session = None

    def get_latest_commits(self, owner: str, repo: str,
                           count: int = 5) -> List[CommitInfo]:
        """Obtém últimos commits de um repositório."""
        try:
            import urllib.request
            url = f"https://api.github.com/repos/{owner}/{repo}/commits?per_page={count}"
            req = urllib.request.Request(url)
            req.add_header("Accept", "application/vnd.github+json")
            req.add_header("User-Agent", "OpenCode-MiroFish-Sync/1.0")
            if self.token:
                req.add_header("Authorization", f"Bearer {self.token}")

            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode())

            commits = []
            for c in data:
                commits.append(CommitInfo(
                    sha=c.get("sha", ""),
                    date=c.get("commit", {}).get("author", {}).get("date", ""),
                    message=c.get("commit", {}).get("message", "").split("\n")[0],
                    author=c.get("commit", {}).get("author", {}).get("name", "unknown"),
                ))
            return commits
        except Exception as e:
            return [CommitInfo(sha="error", date="", message=str(e), author="")]

    def get_changed_files(self, owner: str, repo: str,
                          base_sha: str, head_sha: str = "HEAD") -> List[str]:
        """Obtém arquivos modificados entre dois commits."""
        try:
            import urllib.request
            url = f"https://api.github.com/repos/{owner}/{repo}/compare/{base_sha}...{head_sha}"
            req = urllib.request.Request(url)
            req.add_header("Accept", "application/vnd.github+json")
            req.add_header("User-Agent", "OpenCode-MiroFish-Sync/1.0")
            if self.token:
                req.add_header("Authorization", f"Bearer {self.token}")

            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode())

            files = []
            for f in data.get("files", []):
                files.append(f.get("filename", ""))
            return files
        except Exception:
            return []


# ═══════════════════════════════════════════════════════════════════
# Pattern Classifier
# ═══════════════════════════════════════════════════════════════════

class PatternClassifier:
    """Classifica mudanças em arquivos como novos padrões."""

    ENGINE_KEYWORDS = ["engine", "agent", "pipeline", "middleware",
                       "forum", "graph", "simulation", "report",
                       "oasis", "ontology", "sentiment"]

    def classify(self, repo: str, changed_files: List[str]) -> Tuple[SyncAction, List[str]]:
        """Classifica mudanças."""
        patterns = []
        action = SyncAction.SKIP

        for f in changed_files:
            f_lower = f.lower()

            # Apenas documentação
            if f.endswith(".md") and not any(k in f_lower for k in self.ENGINE_KEYWORDS):
                if action == SyncAction.SKIP:
                    action = SyncAction.MONITOR_ONLY
                continue

            # Arquivos de código Python em diretórios de engine
            if f.endswith(".py"):
                dir_name = f.split("/")[0] if "/" in f else ""
                if dir_name and any(k in dir_name.lower() for k in self.ENGINE_KEYWORDS):
                    pattern_name = dir_name.replace("Engine", "")
                    if pattern_name not in patterns:
                        patterns.append(pattern_name)
                    action = SyncAction.EXTRACT

            # Novos diretórios de engine
            if f.endswith("/__init__.py") or f.endswith("/agent.py"):
                dir_name = f.split("/")[0] if "/" in f else ""
                if dir_name and dir_name not in patterns:
                    patterns.append(dir_name)
                    action = SyncAction.EXTRACT

        return action, patterns


# ═══════════════════════════════════════════════════════════════════
# Sync Engine
# ═══════════════════════════════════════════════════════════════════

class MiroFishSyncEngine:
    """Motor principal de sincronização."""

    def __init__(self, dry_run: bool = False, force: bool = False):
        self.dry_run = dry_run
        self.force = force
        self.monitor = GitHubMonitor()
        self.classifier = PatternClassifier()
        self.baseline = self._load_baseline()
        self.report = SyncReport()

    def _load_baseline(self) -> dict:
        if os.path.exists(VERSION_FILE):
            with open(VERSION_FILE, encoding="utf-8") as f:
                return json.load(f)
        return {"extracted_patterns": {}, "repositories": {}}

    def _save_baseline(self):
        os.makedirs(REVERSA_DIR, exist_ok=True)
        with open(VERSION_FILE, "w", encoding="utf-8") as f:
            json.dump(self.baseline, f, indent=2, ensure_ascii=False)

    def check_repo(self, name: str, config: dict) -> SyncDiff:
        """Verifica um repositório por mudanças."""
        diff = SyncDiff(repo=name)

        # Obter commits
        commits = self.monitor.get_latest_commits(
            config["owner"], config["repo"], 5
        )
        if not commits or commits[0].sha == "error":
            diff.details = f"Erro ao consultar {name}"
            self.report.errors.append(diff.details)
            return diff

        latest = commits[0]
        baseline_commit = self.baseline.get("repositories", {}).get(name, {}).get(
            "last_synced_commit", "")

        if latest.sha == baseline_commit and not self.force:
            diff.details = f"{name}: Nenhuma mudança desde {baseline_commit[:7]}"
            return diff

        # Há mudanças — obter diff de arquivos
        diff.new_commits = commits
        self.report.repos_with_changes += 1

        if baseline_commit:
            changed = self.monitor.get_changed_files(
                config["owner"], config["repo"],
                baseline_commit, latest.sha
            )
        else:
            changed = []

        diff.changed_files = changed
        action, patterns = self.classifier.classify(name, changed)
        diff.action = action
        diff.new_patterns = patterns

        if patterns:
            self.report.new_patterns_found += len(patterns)

        return diff

    def sync_all(self) -> SyncReport:
        """Executa ciclo completo de sincronização."""
        print("═" * 60)
        print("MIROFISH SYNC AGENT (P19) — Sincronização Upstream")
        print(f"Timestamp: {self.report.timestamp}")
        print(f"Modo: {'DRY-RUN' if self.dry_run else 'SYNC'} {'FORCE' if self.force else ''}")
        print("═" * 60)

        for name, config in REPOS.items():
            print(f"\n🔍 Verificando {name}...")
            diff = self.check_repo(name, config)
            self.report.diffs.append(diff)

            print(f"   Commits novos: {len(diff.new_commits)}")
            print(f"   Ação: {diff.action.value}")
            if diff.new_patterns:
                print(f"   Padrões detectados: {diff.new_patterns}")
            if diff.changed_files:
                print(f"   Arquivos: {len(diff.changed_files)} modificados")
                for f in diff.changed_files[:5]:
                    print(f"     - {f}")
                if len(diff.changed_files) > 5:
                    print(f"     ... +{len(diff.changed_files)-5}")

            # Sincronizar se não for dry-run
            if not self.dry_run and diff.action == SyncAction.EXTRACT:
                self._extract_and_integrate(name, config, diff)

        # Salvar baseline atualizada
        if not self.dry_run:
            self._update_baseline()
            self._save_baseline()

        # Resumo
        print(f"\n{'═' * 60}")
        print("RESUMO DA SINCRONIZAÇÃO")
        print(f"{'═' * 60}")
        print(f"Repositórios com mudanças: {self.report.repos_with_changes}/3")
        print(f"Novos padrões detectados: {self.report.new_patterns_found}")
        print(f"Padrões extraídos: {self.report.patterns_extracted}")
        print(f"Erros: {len(self.report.errors)}")

        if self.report.errors:
            for e in self.report.errors:
                print(f"  ❌ {e}")

        return self.report

    def _extract_and_integrate(self, name: str, config: dict, diff: SyncDiff):
        """Extrai e integra novos padrões."""
        latest_p = max(
            [int(k[1:]) for k in self.baseline.get("extracted_patterns", {}).keys()
             if k.startswith("P") and k[1:].isdigit()],
            default=18
        )

        for pattern in diff.new_patterns:
            latest_p += 1
            p_id = f"P{latest_p}"

            if self.dry_run:
                print(f"   [DRY-RUN] Extrairia {p_id}: {pattern}")
                continue

            print(f"   🔧 Extraindo {p_id}: {pattern}...")

            # Registrar na baseline
            self.baseline["extracted_patterns"][p_id] = {
                "name": pattern,
                "source": name,
                "status": "extracted",
                "extracted_date": datetime.now(timezone.utc).isoformat(),
                "upstream_commit": diff.new_commits[0].sha if diff.new_commits else "",
            }

            self.report.patterns_extracted += 1

    def _update_baseline(self):
        """Atualiza baseline com commits mais recentes."""
        for name, config in REPOS.items():
            for diff in self.report.diffs:
                if diff.repo == name and diff.new_commits:
                    self.baseline.setdefault("repositories", {}).setdefault(name, {})[
                        "last_synced_commit"] = diff.new_commits[0].sha
                    self.baseline["repositories"][name][
                        "last_synced_date"] = diff.new_commits[0].date

        self.baseline["ecosystem_version"] = "4.2.0"


# ═══════════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════════

def main():
    import argparse
    parser = argparse.ArgumentParser(description="MiroFish Sync Agent (P19)")
    parser.add_argument("--sync", action="store_true", help="Executar sincronização")
    parser.add_argument("--dry-run", action="store_true", help="Apenas verificar")
    parser.add_argument("--force", action="store_true", help="Forçar re-extração")
    parser.add_argument("--repo", choices=["mirofish", "bettafish", "deerflow", "all"],
                       default="all", help="Filtrar repositório")
    args = parser.parse_args()

    engine = MiroFishSyncEngine(dry_run=args.dry_run, force=args.force)
    report = engine.sync_all()

    # Salvar relatório
    report_path = os.path.join(REVERSA_DIR, "mirofish_sync_report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(asdict(report) if hasattr(report, '__dataclass_fields__')
                  else report, f, indent=2, ensure_ascii=False)

    return 0


if __name__ == "__main__":
    sys.exit(main())
