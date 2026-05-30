# -*- coding: utf-8 -*-
# SAÃDA OBRIGATÃ“RIA: PORTUGUÃŠS BRASILEIRO FORMAL
# Toda resposta ao usuÃ¡rio DEVE ser em portuguÃªs do Brasil formal.
# Contexto em chinÃªs para eficiÃªncia de tokens (densidade +40%%).
# Modelo: big-pickle (OpenCode Zen, 200K ctx, 128K out, gratuito)

#!/usr/bin/env python3
"""
Git Sync Barrier: Mandatory versioning and audit trail.

Enforces:
- Automatic commits at phase boundaries
- Standardized commit message format: [TMA-Phase]
- Git history auditing
- Rollback capabilities
- Lineage tracking
"""

import subprocess
import sys
import os
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from datetime import datetime, timezone
import json


@dataclass
class CommitRecord:
    """Record of a git commit."""
    phase: str
    message: str
    commit_hash: str
    timestamp: str
    author: str
    files_changed: int


class GitSyncBarrier:
    """Manager for git-based synchronization barriers."""
    
    def __init__(self, repo_path: str = "."):
        self.repo_path = repo_path
        self.audit_file = os.path.join(repo_path, ".tma_audit.json")
        self.audit_log = self._load_audit_log()
    
    def _run_git_command(self, command: List[str]) -> Optional[str]:
        """Execute a git command and return output."""
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=True,
                cwd=self.repo_path
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            print(f"Git Error: {e.stderr}")
            return None
    
    def _load_audit_log(self) -> Dict[str, Any]:
        """Load audit log from file."""
        if os.path.exists(self.audit_file):
            try:
                with open(self.audit_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        
        return {
            "version": "1.0",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "commits": []
        }
    
    def _save_audit_log(self) -> None:
        """Save audit log to file."""
        with open(self.audit_file, 'w') as f:
            json.dump(self.audit_log, f, indent=2)
    
    def is_git_repo(self) -> bool:
        """Check if directory is a git repository."""
        return os.path.exists(os.path.join(self.repo_path, ".git"))
    
    def get_status(self) -> Optional[str]:
        """Get git status."""
        return self._run_git_command(["git", "status", "--porcelain"])
    
    def has_changes(self) -> bool:
        """Check if there are uncommitted changes."""
        status = self.get_status()
        return bool(status)
    
    def stage_all(self) -> bool:
        """Stage all changes."""
        result = self._run_git_command(["git", "add", "."])
        return result is not None
    
    def get_current_user(self) -> str:
        """Get current git user."""
        name = self._run_git_command(["git", "config", "user.name"]) or "unknown"
        email = self._run_git_command(["git", "config", "user.email"]) or "unknown"
        return f"{name} <{email}>"
    
    def get_files_changed_count(self) -> int:
        """Get number of files changed in staging area."""
        status = self._run_git_command(["git", "diff", "--cached", "--name-only"])
        if not status:
            return 0
        return len(status.split('\n'))
    
    def enforce_sync_barrier(
        self,
        phase_name: str,
        message: str,
        allow_empty: bool = False
    ) -> bool:
        """
        Enforce a synchronization barrier by creating a git commit.
        
        Args:
            phase_name: TMA phase name (e.g., "Embedding", "Attention")
            message: Commit message
            allow_empty: Allow commit even if no changes
        
        Returns:
            True if successful, False otherwise
        """
        print(f"\n--- Enforcing Sync Barrier: {phase_name} ---")
        
        # Check if git repo
        if not self.is_git_repo():
            print("âœ— Error: Not a git repository")
            return False
        
        # Check for changes
        has_changes = self.has_changes()
        
        if not has_changes and not allow_empty:
            print(f"âœ“ No changes for {phase_name}. Skipping commit.")
            return True
        
        # Stage changes
        if has_changes:
            if not self.stage_all():
                print("âœ— Error: Failed to stage changes")
                return False
        
        # Create commit
        commit_msg = f"[TMA-{phase_name}] {message}"
        
        cmd = ["git", "commit"]
        if allow_empty:
            cmd.append("--allow-empty")
        cmd.extend(["-m", commit_msg])
        
        result = self._run_git_command(cmd)
        
        if result is None:
            print(f"âœ— Error: Failed to create commit")
            return False
        
        # Get commit hash
        commit_hash = self._run_git_command(["git", "rev-parse", "HEAD"])
        
        # Record in audit log
        record = {
            "phase": phase_name,
            "message": message,
            "commit_hash": commit_hash,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "author": self.get_current_user(),
            "files_changed": self.get_files_changed_count() if has_changes else 0
        }
        
        self.audit_log["commits"].append(record)
        self._save_audit_log()
        
        print(f"âœ“ Barrier {phase_name} enforced")
        print(f"  Commit: {commit_hash[:8]} - {commit_msg}")
        print(f"  Author: {record['author']}")
        
        return True
    
    def get_phase_history(self, phase_name: str) -> List[CommitRecord]:
        """Get commit history for a specific phase."""
        return [
            commit for commit in self.audit_log["commits"]
            if commit["phase"] == phase_name
        ]
    
    def get_all_phases(self) -> List[str]:
        """Get list of all phases that have been committed."""
        return sorted(set(
            commit["phase"] for commit in self.audit_log["commits"]
        ))
    
    def export_audit_report(self, filepath: str) -> None:
        """Export audit report to JSON."""
        report = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_commits": len(self.audit_log["commits"]),
            "phases": {},
            "commits": self.audit_log["commits"]
        }
        
        for phase in self.get_all_phases():
            commits = self.get_phase_history(phase)
            report["phases"][phase] = {
                "commit_count": len(commits),
                "first_commit": commits[0]["timestamp"],
                "last_commit": commits[-1]["timestamp"],
                "authors": list(set(c["author"] for c in commits))
            }
        
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2)
    
    def get_commit_log(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent commits from audit log."""
        return self.audit_log["commits"][-limit:]


def main():
    """Command-line interface."""
    if len(sys.argv) < 3:
        print("Usage: python git_sync_barrier.py <phase_name> <commit_message>")
        print("       python git_sync_barrier.py --audit <output_file>")
        print("       python git_sync_barrier.py --status")
        sys.exit(1)
    
    if sys.argv[1] == "--audit" and len(sys.argv) > 2:
        barrier = GitSyncBarrier()
        output_file = sys.argv[2]
        barrier.export_audit_report(output_file)
        print(f"Audit report exported to {output_file}")
        sys.exit(0)
    
    if sys.argv[1] == "--status":
        barrier = GitSyncBarrier()
        if not barrier.is_git_repo():
            print("âœ— Not a git repository")
            sys.exit(1)
        
        print(f"Git Status:")
        status = barrier.get_status()
        if status:
            print(f"  Changes: {len(status.split(chr(10)))} files")
        else:
            print(f"  Changes: None")
        
        print(f"  Phases committed: {', '.join(barrier.get_all_phases())}")
        sys.exit(0)
    
    # Normal barrier enforcement
    phase = sys.argv[1]
    msg = sys.argv[2]
    
    barrier = GitSyncBarrier()
    
    if not barrier.is_git_repo():
        print("âœ— Error: Directory is not a git repository")
        sys.exit(1)
    
    if barrier.enforce_sync_barrier(phase, msg):
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
