#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
nexus/scripts/context_offload.py (refatorado) - DI via Container.
Mantém API original inalterada para compatibilidade retroativa.
"""
import json, os, time, hashlib, logging
from pathlib import Path
from typing import Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from core.container import Container

from dataclasses import dataclass, field, asdict
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class ContextEntry:
    entry_id: str
    session_id: str
    content: str
    content_type: str
    timestamp: float
    priority: int = 0
    is_compressed: bool = False
    original_size: int = 0


@dataclass
class SessionState:
    session_id: str
    project_id: Optional[str] = None
    created_at: float = field(default_factory=time.time)
    last_active: float = field(default_factory=time.time)
    entry_count: int = 0
    total_size: int = 0
    summary: str = ""
    behavioral_fingerprint: dict = field(default_factory=dict)


class ContextOffloadManager:
    def __init__(self, base_dir: str = None, max_context_size: int = 50000,
                 summary_threshold: int = 10, compression_enabled: bool = True, container=None):
        self._container = container
        self.base_dir = Path(base_dir or os.path.join(os.getcwd(), "nexus", "context_offload"))
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.max_context_size = max_context_size
        self.summary_threshold = summary_threshold
        self.compression_enabled = compression_enabled
        self.sessions: dict[str, SessionState] = {}
        self.active_session: Optional[str] = None
        self._entry_index: dict[str, ContextEntry] = {}

    @classmethod
    def from_container(cls, container: 'Container', **kwargs) -> 'ContextOffloadManager':
        """Factory: cria ContextOffloadManager com deps do Container."""
        return cls(container=container, **kwargs)

    def create_session(self, session_id: str = None, project_id: str = None) -> str:
        sid = session_id or f"session-{int(time.time())}"
        self.sessions[sid] = SessionState(session_id=sid, project_id=project_id)
        session_dir = self._session_dir(sid)
        session_dir.mkdir(parents=True, exist_ok=True)
        (session_dir / "intermediate").mkdir(exist_ok=True)
        (session_dir / "summaries").mkdir(exist_ok=True)
        (session_dir / "context").mkdir(exist_ok=True)
        self.active_session = sid
        return sid

    def add_entry(self, content: str, content_type: str = "text", priority: int = 5) -> str:
        if not self.active_session:
            raise ValueError("No active session. Call create_session() first.")
        sid = self.active_session
        entry_id = hashlib.md5(f"{sid}-{time.time()}-{content[:50]}".encode()).hexdigest()[:12]
        entry = ContextEntry(entry_id=entry_id, session_id=sid, content=content,
            content_type=content_type, timestamp=time.time(), priority=priority,
            original_size=len(content.encode()))
        self._entry_index[entry_id] = entry
        self._save_entry(entry)
        session = self.sessions[sid]
        session.entry_count += 1
        session.total_size += entry.original_size
        session.last_active = time.time()
        if session.entry_count >= self.summary_threshold:
            self._summarize_session(sid)
        if session.total_size > self.max_context_size:
            self._compress_context(sid)
        return entry_id

    def add_intermediate_result(self, task_name: str, result: Any) -> str:
        data = json.dumps(result, default=str) if not isinstance(result, str) else result
        return self.add_entry(data, content_type="intermediate_result", priority=7)

    def get_session_context(self, session_id: str = None, max_entries: int = 20) -> list[str]:
        sid = session_id or self.active_session
        if not sid or sid not in self.sessions:
            return []
        session_dir = self._session_dir(sid)
        context_file = session_dir / "context" / "active.json"
        if context_file.exists():
            with open(context_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data.get("entries", [])
        entries = sorted(self._entry_index.values(), key=lambda e: e.timestamp, reverse=True)[:max_entries]
        return [e.content for e in entries]

    def get_session_summary(self, session_id: str = None) -> str:
        sid = session_id or self.active_session
        if not sid or sid not in self.sessions:
            return ""
        session_dir = self._session_dir(sid)
        summary_file = session_dir / "summaries" / "latest.md"
        if summary_file.exists():
            return summary_file.read_text(encoding="utf-8")
        return self.sessions[sid].summary

    def create_behavioral_fingerprint(self, session_id: str = None) -> dict:
        sid = session_id or self.active_session
        if not sid or sid not in self.sessions:
            return {}
        session = self.sessions[sid]
        entries = [e for e in self._entry_index.values() if e.session_id == sid]
        all_text = " ".join(e.content for e in entries)
        words = all_text.lower().split()
        term_freq = {}
        for w in words:
            term_freq[w] = term_freq.get(w, 0) + 1
        top_terms = dict(sorted(term_freq.items(), key=lambda x: x[1], reverse=True)[:50])
        constraint_keywords = ["must", "should", "cannot", "do not", "never", "always", "required", "constraint"]
        constraints = [kw for kw in constraint_keywords if kw in all_text.lower()]
        fingerprint = {"term_frequency": top_terms, "constraints": constraints,
            "entry_count": len(entries), "total_tokens": len(words),
            "session_duration": time.time() - session.created_at}
        session.behavioral_fingerprint = fingerprint
        self._save_fingerprint(sid, fingerprint)
        return fingerprint

    def check_resume_consistency(self, session_id: str, current_text: str) -> dict:
        sid = session_id or self.active_session
        if not sid or sid not in self.sessions:
            return {"drift_score": 0, "ghost_terms": [], "status": "no_fingerprint"}
        session = self.sessions[sid]
        fp = session.behavioral_fingerprint
        if not fp or not fp.get("term_frequency"):
            return {"drift_score": 0, "ghost_terms": [], "status": "no_fingerprint"}
        current_words = current_text.lower().split()
        current_set = set(current_words)
        prior_terms = set(fp["term_frequency"].keys())
        ghost_terms = [t for t in prior_terms if t not in current_set]
        drift_score = len(ghost_terms) / max(len(prior_terms), 1)
        return {"drift_score": round(drift_score, 2), "ghost_terms": ghost_terms[:20],
            "status": "consistent" if drift_score < 0.3 else "drift_detected",
            "prior_terms": len(prior_terms), "current_terms": len(current_set)}

    def _summarize_session(self, session_id: str) -> None:
        entries = sorted([e for e in self._entry_index.values() if e.session_id == session_id],
            key=lambda e: e.timestamp)
        summary_parts = []
        for e in entries[-self.summary_threshold:]:
            preview = e.content[:200] if len(e.content) > 200 else e.content
            summary_parts.append(f"[{e.content_type}] {preview}")
        summary = "\n---\n".join(summary_parts)
        self.sessions[session_id].summary = f"Session Summary ({len(entries)} entries):\n{summary}"
        session_dir = self._session_dir(session_id)
        summary_file = session_dir / "summaries" / "latest.md"
        with open(summary_file, "w", encoding="utf-8") as f:
            f.write(self.sessions[session_id].summary)

    def _compress_context(self, session_id: str) -> None:
        entries = [e for e in self._entry_index.values() if e.session_id == session_id]
        low_priority = [e for e in entries if e.priority < 5]
        for entry in low_priority:
            if not entry.is_compressed:
                compressed = entry.content[:100] + "..." if len(entry.content) > 100 else entry.content
                entry.content = compressed
                entry.is_compressed = True
                self._save_entry(entry)

    def _save_entry(self, entry: ContextEntry) -> None:
        session_dir = self._session_dir(entry.session_id)
        if entry.content_type == "intermediate_result":
            target = session_dir / "intermediate" / f"{entry.entry_id}.json"
            with open(target, "w", encoding="utf-8") as f:
                json.dump({"entry_id": entry.entry_id, "content": entry.content,
                    "timestamp": entry.timestamp, "priority": entry.priority}, f)
        else:
            target = session_dir / "context" / f"{entry.entry_id}.txt"
            with open(target, "w", encoding="utf-8") as f:
                f.write(entry.content)

    def _save_fingerprint(self, session_id: str, fingerprint: dict) -> None:
        session_dir = self._session_dir(session_id)
        fp_file = session_dir / "fingerprint.json"
        with open(fp_file, "w", encoding="utf-8") as f:
            json.dump(fingerprint, f, indent=2)

    def _session_dir(self, session_id: str) -> Path:
        return self.base_dir / session_id

    def get_session_state(self, session_id: Optional[str] = None) -> Optional[dict]:
        sid = session_id or self.active_session
        if not sid or sid not in self.sessions:
            return None
        s = self.sessions[sid]
        return {"session_id": s.session_id, "project_id": s.project_id,
            "entry_count": s.entry_count, "total_size": s.total_size,
            "summary_length": len(s.summary), "has_fingerprint": bool(s.behavioral_fingerprint)}

    def list_sessions(self) -> list[dict]:
        return [self.get_session_state(sid) for sid in self.sessions if self.get_session_state(sid)]  # type: ignore[return-value]


def register_context_offload_di() -> None:
    """Registra ContextOffloadManager no Container (chamar apos initialize_core)."""
    from core.container import Container
    if not Container.instance().is_registered('context_offload'):
        Container.instance().register('context_offload',
            ContextOffloadManager.from_container(Container.instance()))