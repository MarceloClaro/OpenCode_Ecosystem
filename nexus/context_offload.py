# -*- coding: utf-8 -*-
"""
CONTEXT OFFLOAD v1.0 - Sem necessidade de DI (logica pura de filesystem).

Analise:
- ContextOffloadManager gerencia contexto via sistema de arquivos (json/txt)
- Nenhuma dependencia de core.state_manager ou core.event_bus
- Dependencias: json, os, time, hashlib, logging, pathlib, dataclasses, datetime
- E uma biblioteca de auxilio a contexto, nao um servico de infraestrutura

Decisao:
- NAO requer refatoracao DI
- Mantido como modulo de logica pura
- Copia documentada para referencia de arquitetura
"""

import json, os, time, hashlib, logging
from pathlib import Path
from typing import Any, Optional
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
                 summary_threshold: int = 10, compression_enabled: bool = True):
        self.base_dir = Path(base_dir or os.path.join(os.getcwd(), "nexus", "context_offload"))
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.max_context_size = max_context_size
        self.summary_threshold = summary_threshold
        self.compression_enabled = compression_enabled
        self.sessions: dict[str, SessionState] = {}
        self.active_session: Optional[str] = None
        self._entry_index: dict[str, ContextEntry] = {}

    def create_session(self, session_id: str = None, project_id: str = None) -> str:
        sid = session_id or f"session-{int(time.time())}"
        self.sessions[sid] = SessionState(session_id=sid, project_id=project_id)
        sd = self._session_dir(sid); sd.mkdir(parents=True, exist_ok=True)
        (sd / "intermediate").mkdir(exist_ok=True)
        (sd / "summaries").mkdir(exist_ok=True)
        (sd / "context").mkdir(exist_ok=True)
        self.active_session = sid
        return sid

    def add_entry(self, content: str, content_type: str = "text", priority: int = 5) -> str:
        if not self.active_session:
            raise ValueError("No active session. Call create_session() first.")
        sid = self.active_session
        eid = hashlib.md5(f"{sid}-{time.time()}-{content[:50]}".encode()).hexdigest()[:12]
        entry = ContextEntry(entry_id=eid, session_id=sid, content=content,
            content_type=content_type, timestamp=time.time(), priority=priority,
            original_size=len(content.encode()))
        self._entry_index[eid] = entry; self._save_entry(entry)
        s = self.sessions[sid]; s.entry_count += 1; s.total_size += entry.original_size
        s.last_active = time.time()
        if s.entry_count >= self.summary_threshold:
            self._summarize_session(sid)
        if s.total_size > self.max_context_size:
            self._compress_context(sid)
        return eid

    def add_intermediate_result(self, task_name: str, result: Any) -> str:
        data = json.dumps(result, default=str) if not isinstance(result, str) else result
        return self.add_entry(data, content_type="intermediate_result", priority=7)

    def get_session_context(self, session_id: str = None, max_entries: int = 20) -> list[str]:
        sid = session_id or self.active_session
        if not sid or sid not in self.sessions:
            return []
        cf = self._session_dir(sid) / "context" / "active.json"
        if cf.exists():
            return json.loads(cf.read_text(encoding="utf-8")).get("entries", [])
        entries = sorted(self._entry_index.values(), key=lambda e: e.timestamp, reverse=True)[:max_entries]
        return [e.content for e in entries]

    def get_session_summary(self, session_id: str = None) -> str:
        sid = session_id or self.active_session
        if not sid or sid not in self.sessions:
            return ""
        sf = self._session_dir(sid) / "summaries" / "latest.md"
        return sf.read_text(encoding="utf-8") if sf.exists() else self.sessions[sid].summary

    def create_behavioral_fingerprint(self, session_id: str = None) -> dict:
        sid = session_id or self.active_session
        if not sid or sid not in self.sessions: return {}
        entries = [e for e in self._entry_index.values() if e.session_id == sid]
        words = (" ".join(e.content for e in entries)).lower().split()
        tf = {}
        for w in words: tf[w] = tf.get(w, 0) + 1
        ck = ["must","should","cannot","do not","never","always","required","constraint"]
        fp = {"term_frequency": dict(sorted(tf.items(),key=lambda x:x[1],reverse=True)[:50]),
            "constraints":[kw for kw in ck if kw in " ".join(words)],
            "entry_count":len(entries),"total_tokens":len(words),
            "session_duration":time.time()-self.sessions[sid].created_at}
        self.sessions[sid].behavioral_fingerprint = fp
        self._save_fingerprint(sid, fp)
        return fp

    def check_resume_consistency(self, session_id: str, current_text: str) -> dict:
        sid = session_id or self.active_session
        if not sid or sid not in self.sessions:
            return {"drift_score":0,"ghost_terms":[],"status":"no_fingerprint"}
        fp = self.sessions[sid].behavioral_fingerprint
        if not fp or not fp.get("term_frequency"):
            return {"drift_score":0,"ghost_terms":[],"status":"no_fingerprint"}
        cw = set(current_text.lower().split())
        pt = set(fp["term_frequency"].keys())
        gt = [t for t in pt if t not in cw]
        ds = len(gt)/max(len(pt),1)
        return {"drift_score":round(ds,2),"ghost_terms":gt[:20],
            "status":"consistent" if ds<0.3 else "drift_detected",
            "prior_terms":len(pt),"current_terms":len(cw)}

    def _summarize_session(self, session_id: str) -> None:
        entries = sorted([e for e in self._entry_index.values() if e.session_id==session_id],key=lambda e:e.timestamp)
        parts = [f"[{e.content_type}] {(e.content[:200] if len(e.content)>200 else e.content)}" for e in entries[-self.summary_threshold:]]
        self.sessions[session_id].summary = f"Session Summary ({len(entries)} entries):\n"+"\n---\n".join(parts)
        (self._session_dir(session_id)/"summaries"/"latest.md").write_text(self.sessions[session_id].summary,encoding="utf-8")

    def _compress_context(self, session_id: str) -> None:
        for e in [e for e in self._entry_index.values() if e.session_id==session_id and e.priority<5 and not e.is_compressed]:
            e.content = e.content[:100]+"..." if len(e.content)>100 else e.content
            e.is_compressed = True; self._save_entry(e)

    def _save_entry(self, entry: ContextEntry) -> None:
        t = self._session_dir(entry.session_id)
        if entry.content_type=="intermediate_result":
            (t/"intermediate"/f"{entry.entry_id}.json").write_text(json.dumps(
                {"entry_id":entry.entry_id,"content":entry.content,"timestamp":entry.timestamp,"priority":entry.priority}))
        else:
            (t/"context"/f"{entry.entry_id}.txt").write_text(entry.content)

    def _save_fingerprint(self, sid: str, fp: dict) -> None:
        (self._session_dir(sid)/"fingerprint.json").write_text(json.dumps(fp,indent=2))

    def _session_dir(self, session_id: str) -> Path:
        return self.base_dir / session_id

    def get_session_state(self, session_id: str = None) -> Optional[dict]:
        sid = session_id or self.active_session
        if not sid or sid not in self.sessions: return None
        s = self.sessions[sid]
        return {"session_id":s.session_id,"project_id":s.project_id,
            "entry_count":s.entry_count,"total_size":s.total_size,
            "summary_length":len(s.summary),"has_fingerprint":bool(s.behavioral_fingerprint)}

    def list_sessions(self) -> list[dict]:
        return [self.get_session_state(sid) for sid in self.sessions if self.get_session_state(sid)]
