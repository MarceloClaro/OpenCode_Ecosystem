"""
seeker/argument_tree.py (proposto) - Argument Tree refatorada para DI.

Mudanças em relação ao original (core/argument_tree.py):
  1. TreeBuilder aceita IDatabase opcional via construtor (em vez de SQLite direto)
  2. Métodos de query delegados à interface IDatabase
  3. Geração de ID injetável (não depende mais de core.utils.generate_id)
  4. EventBus opcional para notificações de mutações
  5. Compatibilidade retroativa via fallback para SQLite direto

Risco: MÉDIO — TreeBuilder tem acoplamento forte com SQLite.
       Extrair IDatabase daqui é complexo porque database.py também usa SQLite.
Complexidade: 6/10
"""

from __future__ import annotations

import json
import sqlite3
import logging
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, Callable

from core.interfaces import IStateManager, IEventBus

logger = logging.getLogger(__name__)


# ─── Geração de ID injetável ─────────────────────────────────────────────────

def default_id_generator(prefix: str) -> str:
    """Fallback: mesma lógica de core.utils.generate_id."""
    import uuid
    return f"{prefix}-{uuid.uuid4().hex[:8].upper()}"


# ─── Schema SQLite (fallback) ─────────────────────────────────────────────────

TREE_SCHEMA = """
CREATE TABLE IF NOT EXISTS argument_tree (
    node_id         TEXT PRIMARY KEY,
    run_id          TEXT NOT NULL,
    parent_node_id  TEXT,
    node_type       TEXT NOT NULL,
    depth           INTEGER DEFAULT 0,
    content         TEXT NOT NULL,
    status          TEXT DEFAULT 'unsupported',
    confidence      REAL DEFAULT 0.0,
    source_ids      TEXT DEFAULT '[]',
    agent_origin    TEXT DEFAULT '',
    created_at      TEXT NOT NULL,
    metadata        TEXT DEFAULT '{}',
    FOREIGN KEY (run_id) REFERENCES runs(run_id),
    FOREIGN KEY (parent_node_id) REFERENCES argument_tree(node_id)
);
CREATE INDEX IF NOT EXISTS idx_tree_run ON argument_tree(run_id);
CREATE INDEX IF NOT EXISTS idx_tree_parent ON argument_tree(parent_node_id);
CREATE INDEX IF NOT EXISTS idx_tree_type ON argument_tree(run_id, node_type);
"""

VALID_NODE_TYPES = {
    "root", "question", "claim", "evidence", "bridge",
    "counter", "historical", "external", "audit_note",
}

VALID_STATUSES = {
    "supported", "contested", "unsupported", "weak",
    "solid", "contradicted", "bridged",
}


# ─── TreeBuilder com DI ──────────────────────────────────────────────────

class TreeBuilder:
    """
    Constrói e mantém a árvore de argumentos para uma execução do pipeline.

    Aceita state_manager e event_bus opcionais.
    Usa SQLite direto como fallback (compatibilidade retroativa).
    """

    def __init__(
        self,
        run_id: str,
        state_manager: Optional[IStateManager] = None,
        event_bus: Optional[IEventBus] = None,
        db_path: Optional[Path] = None,
        id_generator: Optional[Callable[[str], str]] = None,
    ):
        self.run_id = run_id
        self.state_manager = state_manager
        self.event_bus = event_bus
        self._gen_id = id_generator or default_id_generator

        # Fallback: SQLite direto
        if db_path is None:
            db_path = Path(__file__).parent.parent / "db" / "pipeline.db"
        self._conn = sqlite3.connect(str(db_path))
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.executescript(TREE_SCHEMA)
        self._conn.commit()

    def close(self):
        self._conn.close()

    # ── Publish (EventBus) ──────────────────────────────────────────────

    def _publish(self, topic: str, data: dict):
        if self.event_bus:
            import asyncio
            try:
                asyncio.create_task(
                    self.event_bus.publish(topic, data, source="argument_tree")
                )
            except Exception:
                pass

    # ── Helpers ─────────────────────────────────────────────────────────

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _insert(self, node_id: str, parent_id: Optional[str], node_type: str,
                content: str, status: str = "unsupported", confidence: float = 0.0,
                source_ids: list = None, agent: str = "", metadata: dict = None) -> str:
        depth = 0
        if parent_id:
            row = self._conn.execute(
                "SELECT depth FROM argument_tree WHERE node_id = ?", (parent_id,)
            ).fetchone()
            if row:
                depth = row["depth"] + 1

        self._conn.execute(
            """INSERT OR REPLACE INTO argument_tree
               (node_id, run_id, parent_node_id, node_type, depth,
                content, status, confidence, source_ids,
                agent_origin, created_at, metadata)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (node_id, self.run_id, parent_id, node_type, depth,
             content, status, confidence, json.dumps(source_ids or []),
             agent, self._now(), json.dumps(metadata or {})),
        )
        self._conn.commit()
        self._publish("tree.node_created", {
            "node_id": node_id, "type": node_type, "agent": agent,
        })
        return node_id

    # ── Criação ─────────────────────────────────────────────────────────

    def create_root(self, problem: str) -> str:
        node_id = self._gen_id("ROOT")
        return self._insert(node_id, None, "root", problem,
                            status="unsupported", agent="system")

    def add_question(self, parent_id: str, question_text: str,
                     question_level: str = "foundational",
                     agent: str = "grounder") -> str:
        node_id = self._gen_id("Q")
        return self._insert(node_id, parent_id, "question", question_text,
                            agent=agent, metadata={"question_level": question_level})

    def add_claim(self, parent_question_id: str, claim_text: str,
                  confidence: float = 0.5, agent: str = "grounder",
                  source_ids: list = None) -> str:
        node_id = self._gen_id("CLM")
        return self._insert(node_id, parent_question_id, "claim", claim_text,
                            status="supported" if source_ids else "unsupported",
                            confidence=confidence, source_ids=source_ids, agent=agent)

    def add_evidence(self, parent_claim_id: str, source_id: str,
                     evidence_type: str = "paper", relationship: str = "supports",
                     snippet: str = "", agent: str = "grounder",
                     metadata: dict = None) -> str:
        node_id = self._gen_id("EV")
        meta = metadata or {}
        meta["evidence_type"] = evidence_type
        meta["relationship"] = relationship
        meta["snippet"] = snippet[:500]
        return self._insert(node_id, parent_claim_id, "evidence",
                            f"[{evidence_type}] {snippet[:200]}",
                            status="supported", confidence=0.8,
                            source_ids=[source_id], agent=agent, metadata=meta)

    def add_bridge(self, from_node_id: str, to_node_id: str,
                   source_id: str, bridge_type: str = "temporal",
                   description: str = "", agent: str = "social") -> str:
        node_id = self._gen_id("BRG")
        return self._insert(node_id, from_node_id, "bridge",
                            description or f"Bridge to {to_node_id}",
                            status="bridged", confidence=0.6,
                            source_ids=[source_id], agent=agent,
                            metadata={"bridge_type": bridge_type,
                                      "bridges_to": to_node_id})

    def add_counter(self, parent_claim_id: str, counter_text: str,
                    source_id: str, agent: str = "grounder") -> str:
        node_id = self._gen_id("CTR")
        self._insert(node_id, parent_claim_id, "counter", counter_text,
                     status="supported", confidence=0.7,
                     source_ids=[source_id], agent=agent)
        self._conn.execute(
            "UPDATE argument_tree SET status = 'contested' WHERE node_id = ?",
            (parent_claim_id,))
        self._conn.commit()
        self._publish("tree.status_changed",
                       {"node_id": parent_claim_id, "new_status": "contested"})
        return node_id

    def add_historical(self, parent_id: str, content: str,
                       year: int = None, source_id: str = "",
                       agent: str = "historian") -> str:
        node_id = self._gen_id("HIST")
        return self._insert(node_id, parent_id, "historical", content,
                            source_ids=[source_id] if source_id else [],
                            agent=agent, metadata={"year": year})

    def add_external(self, parent_id: str, content: str,
                     factor_type: str = "event", year: int = None,
                     source_id: str = "", agent: str = "historian") -> str:
        node_id = self._gen_id("EXT")
        return self._insert(node_id, parent_id, "external", content,
                            source_ids=[source_id] if source_id else [],
                            agent=agent,
                            metadata={"factor_type": factor_type, "year": year})

    def add_audit_note(self, target_node_id: str, assessment: str,
                       new_status: str = None, new_confidence: float = None,
                       agent: str = "historian") -> str:
        node_id = self._gen_id("AUD")
        self._insert(node_id, target_node_id, "audit_note", assessment,
                     agent=agent,
                     metadata={"audited_node": target_node_id,
                               "previous_status": self._get_field(target_node_id, "status"),
                               "previous_confidence": self._get_field(target_node_id, "confidence")})
        if new_status:
            self._conn.execute(
                "UPDATE argument_tree SET status = ? WHERE node_id = ?",
                (new_status, target_node_id))
        if new_confidence is not None:
            self._conn.execute(
                "UPDATE argument_tree SET confidence = ? WHERE node_id = ?",
                (new_confidence, target_node_id))
        self._conn.commit()
        return node_id

    # ── Atualização ─────────────────────────────────────────────────────

    def update_status(self, node_id: str, status: str):
        self._conn.execute(
            "UPDATE argument_tree SET status = ? WHERE node_id = ?",
            (status, node_id))
        self._conn.commit()
        self._publish("tree.status_changed", {"node_id": node_id, "new_status": status})

    def update_confidence(self, node_id: str, confidence: float):
        self._conn.execute(
            "UPDATE argument_tree SET confidence = ? WHERE node_id = ?",
            (confidence, node_id))
        self._conn.commit()

    # ── Consulta ────────────────────────────────────────────────────────

    def _get_field(self, node_id: str, field: str):
        row = self._conn.execute(
            f"SELECT {field} FROM argument_tree WHERE node_id = ?", (node_id,)
        ).fetchone()
        return row[0] if row else None

    def get_node(self, node_id: str) -> Optional[dict]:
        row = self._conn.execute(
            "SELECT * FROM argument_tree WHERE node_id = ?", (node_id,)
        ).fetchone()
        return dict(row) if row else None

    def get_children(self, node_id: str) -> list[dict]:
        rows = self._conn.execute(
            "SELECT * FROM argument_tree WHERE parent_node_id = ? ORDER BY created_at",
            (node_id,)
        ).fetchall()
        return [dict(r) for r in rows]

    def get_tree(self) -> dict:
        rows = self._conn.execute(
            "SELECT * FROM argument_tree WHERE run_id = ? ORDER BY depth, created_at",
            (self.run_id,)
        ).fetchall()
        nodes = {r["node_id"]: dict(r) for r in rows}
        for nid, node in nodes.items():
            node["children"] = []
            node["source_ids"] = json.loads(node.get("source_ids", "[]"))
            node["metadata"] = json.loads(node.get("metadata", "{}"))
        root = None
        for nid, node in nodes.items():
            parent = node.get("parent_node_id")
            if parent and parent in nodes:
                nodes[parent]["children"].append(node)
            elif node["node_type"] == "root":
                root = node
        return root or {}

    def get_branch(self, node_id: str) -> dict:
        node = self.get_node(node_id)
        if not node:
            return {}
        node["source_ids"] = json.loads(node.get("source_ids", "[]"))
        node["metadata"] = json.loads(node.get("metadata", "{}"))
        node["children"] = []
        for child in self.get_children(node_id):
            child_branch = self.get_branch(child["node_id"])
            if child_branch:
                node["children"].append(child_branch)
        return node

    def get_nodes_by_type(self, node_type: str) -> list[dict]:
        rows = self._conn.execute(
            "SELECT * FROM argument_tree WHERE run_id = ? AND node_type = ? ORDER BY created_at",
            (self.run_id, node_type)
        ).fetchall()
        return [dict(r) for r in rows]

    def get_all_source_ids(self) -> list[str]:
        rows = self._conn.execute(
            "SELECT source_ids FROM argument_tree WHERE run_id = ?",
            (self.run_id,)
        ).fetchall()
        all_ids = set()
        for row in rows:
            all_ids.update(json.loads(row["source_ids"]))
        return sorted(all_ids - {""})

    # ── Análise ─────────────────────────────────────────────────────────

    def get_stats(self) -> dict:
        rows = self._conn.execute(
            "SELECT node_type, COUNT(*) as cnt FROM argument_tree WHERE run_id = ? GROUP BY node_type",
            (self.run_id,)
        ).fetchall()
        type_counts = {r["node_type"]: r["cnt"] for r in rows}
        status_rows = self._conn.execute(
            "SELECT status, COUNT(*) as cnt FROM argument_tree WHERE run_id = ? AND node_type = 'claim' GROUP BY status",
            (self.run_id,)
        ).fetchall()
        claim_statuses = {r["status"]: r["cnt"] for r in status_rows}
        return {
            "total_nodes": sum(type_counts.values()),
            "by_type": type_counts,
            "claim_statuses": claim_statuses,
            "unique_sources": len(self.get_all_source_ids()),
        }

    def find_gaps(self) -> list[dict]:
        gaps = []
        for q in self.get_nodes_by_type("question"):
            children = self.get_children(q["node_id"])
            if not [c for c in children if c["node_type"] == "claim"]:
                gaps.append({"gap_type": "unanswered_question",
                             "node_id": q["node_id"], "content": q["content"]})
        for c in self.get_nodes_by_type("claim"):
            children = self.get_children(c["node_id"])
            if not [ch for ch in children if ch["node_type"] == "evidence"]:
                gaps.append({"gap_type": "unsupported_claim",
                             "node_id": c["node_id"], "content": c["content"]})
            if c["confidence"] and c["confidence"] < 0.3:
                gaps.append({"gap_type": "weak_claim",
                             "node_id": c["node_id"], "content": c["content"],
                             "confidence": c["confidence"]})
        return gaps

    def find_bridge_needs(self, min_gap_years: int = 15) -> list[dict]:
        needs = []
        for q in self.get_nodes_by_type("question"):
            evidence_years = []
            for claim in self.get_children(q["node_id"]):
                if claim["node_type"] != "claim":
                    continue
                for ev in self.get_children(claim["node_id"]):
                    meta = json.loads(ev.get("metadata", "{}"))
                    year = meta.get("year")
                    src_ids = json.loads(ev.get("source_ids", "[]"))
                    if year:
                        evidence_years.append((year, ev["node_id"], claim["node_id"]))
            if len(evidence_years) < 2:
                continue
            evidence_years.sort()
            for i in range(len(evidence_years) - 1):
                y1, ev1, cl1 = evidence_years[i]
                y2, ev2, cl2 = evidence_years[i + 1]
                if y2 - y1 >= min_gap_years:
                    needs.append({
                        "question_id": q["node_id"],
                        "question": q["content"][:100],
                        "earlier_node": ev1, "earlier_year": y1,
                        "later_node": ev2, "later_year": y2,
                        "gap_years": y2 - y1,
                    })
        return needs

    # ── Contexto para LLM ───────────────────────────────────────────────

    def to_context(self, max_depth: int = 4, include_evidence: bool = True) -> str:
        tree = self.get_tree()
        if not tree:
            return "(empty tree)"
        lines = [f"ARGUMENT TREE — {tree.get('content', '')}"]
        stats = self.get_stats()
        lines.append(f"Stats: {stats['total_nodes']} nodes, "
                     f"{stats['unique_sources']} sources, "
                     f"claims: {stats.get('claim_statuses', {})}")
        lines.append("")
        self._render_node(tree, lines, 0, max_depth, include_evidence)
        return "\n".join(lines)

    def _render_node(self, node: dict, lines: list, depth: int,
                     max_depth: int, include_evidence: bool):
        if depth > max_depth:
            return
        indent = "  " * depth
        ntype = node.get("node_type", "?")
        status = node.get("status", "?")
        conf = node.get("confidence", 0)
        content = node.get("content", "")[:200]
        if ntype == "root":
            lines.append(f"{indent}ROOT: {content}")
        elif ntype == "question":
            lines.append(f"{indent}Q: {content}")
        elif ntype == "claim":
            lines.append(f"{indent}CLAIM [{status}] (conf:{conf:.0%}): {content}")
        elif ntype == "evidence" and include_evidence:
            meta = node.get("metadata", {})
            lines.append(f"{indent}EVIDENCE [{meta.get('evidence_type','?')}] "
                         f"({meta.get('relationship','?')}): {content} "
                         f"| sources: {node.get('source_ids', [])}")
        elif ntype == "bridge":
            meta = node.get("metadata", {})
            lines.append(f"{indent}BRIDGE [{meta.get('bridge_type','')}] "
                         f"→ {meta.get('bridges_to','')}: {content}")
        elif ntype == "counter":
            lines.append(f"{indent}COUNTER: {content}")
        elif ntype == "historical":
            lines.append(f"{indent}HISTORICAL: {content}")
        elif ntype == "external":
            lines.append(f"{indent}EXTERNAL [{node.get('metadata',{}).get('factor_type','')}]: {content}")
        elif ntype == "audit_note":
            lines.append(f"{indent}AUDIT: {content}")
        for child in node.get("children", []):
            self._render_node(child, lines, depth + 1, max_depth, include_evidence)

    def to_reference_list(self) -> list[str]:
        source_ids = self.get_all_source_ids()
        if not source_ids:
            return []
        placeholders = ",".join("?" * len(source_ids))
        rows = self._conn.execute(
            f"SELECT * FROM sources WHERE source_id IN ({placeholders})", source_ids
        ).fetchall()
        refs = []
        for r in rows:
            authors = json.loads(r["authors"]) if r["authors"] else []
            author_str = ", ".join(authors[:3])
            if len(authors) > 3:
                author_str += " et al."
            year = r["year"] or "n.d."
            title = r["title"] or "Untitled"
            doi = r["doi"] or ""
            doi_str = f" doi:{doi}" if doi else ""
            refs.append(f"{author_str} ({year}). {title}.{doi_str}")
        return sorted(refs)
