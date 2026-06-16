"""DecisionNode MCP Server — Gerencia ADRs (Architecture Decision Records)"""
import json, os, sys
from pathlib import Path
from datetime import datetime, timezone
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("decide-mcp")
DATA_DIR = Path(os.environ.get("DECIDE_DATA_DIR", ".decisionnode"))
DATA_DIR.mkdir(exist_ok=True)
DECISIONS_FILE = DATA_DIR / "decisions.json"
HISTORY_FILE = DATA_DIR / "history.json"

def _load_json(path):
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return []

def _save_json(path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

def _now():
    return datetime.now(timezone.utc).isoformat()

def _load_decisions():
    return {d["id"]: d for d in _load_json(DECISIONS_FILE)}

def _save_decisions(decisions):
    _save_json(DECISIONS_FILE, list(decisions.values()))

def _add_history(action, decision_id, detail=""):
    history = _load_json(HISTORY_FILE)
    history.append({"action": action, "decisionId": decision_id, "detail": detail, "timestamp": _now()})
    _save_json(HISTORY_FILE, history[-100:])

@mcp.tool()
def search_decisions(query: str, top_k: int = 5, scope: str = "") -> str:
    decisions = _load_decisions()
    results = []
    query_lower = query.lower()
    for d in decisions.values():
        if scope and d.get("scope", "") != scope:
            continue
        if query_lower in d.get("decision", "").lower() or query_lower in d.get("rationale", "").lower():
            results.append(d)
    results = sorted(results, key=lambda x: x.get("timestamp", ""), reverse=True)[:top_k]
    if not results:
        return json.dumps({"results": [], "total": 0})
    return json.dumps({"results": results, "total": len(results)})

@mcp.tool()
def add_decision(decisions: list) -> str:
    existing = _load_decisions()
    added = []
    for d in decisions:
        did = d.get("id", f"adr-{_now()}")
        entry = {
            "id": did, "scope": d.get("scope", "general"),
            "decision": d.get("decision", ""), "rationale": d.get("rationale", ""),
            "constraints": d.get("constraints", []), "status": d.get("status", "active"),
            "timestamp": _now()
        }
        existing[did] = entry
        _add_history("add", did, d.get("decision", ""))
        added.append(did)
    _save_decisions(existing)
    return json.dumps({"added": added, "total": len(existing)})

@mcp.tool()
def update_decision(id: str, updates: dict) -> str:
    decisions = _load_decisions()
    if id not in decisions:
        return json.dumps({"error": f"Decision {id} not found"})
    decisions[id].update(updates)
    decisions[id]["timestamp"] = _now()
    _save_decisions(decisions)
    _add_history("update", id, json.dumps(updates))
    return json.dumps({"success": True, "id": id})

@mcp.tool()
def delete_decision(id: str) -> str:
    decisions = _load_decisions()
    if id not in decisions:
        return json.dumps({"error": f"Decision {id} not found"})
    del decisions[id]
    _save_decisions(decisions)
    _add_history("delete", id)
    return json.dumps({"success": True, "id": id})

@mcp.tool()
def list_decisions(scope: str = "", status: str = "all") -> str:
    decisions = _load_decisions()
    results = []
    for d in decisions.values():
        if scope and d.get("scope", "") != scope:
            continue
        if status != "all" and d.get("status", "active") != status:
            continue
        results.append(d)
    results.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    return json.dumps({"results": results, "total": len(results)})

@mcp.tool()
def get_history(limit: int = 10) -> str:
    history = _load_json(HISTORY_FILE)
    return json.dumps({"history": history[-limit:], "total": len(history)})

@mcp.tool()
def deprecate_decision(id: str) -> str:
    return update_decision(id, {"status": "deprecated"})

@mcp.tool()
def activate_decision(id: str) -> str:
    return update_decision(id, {"status": "active"})

@mcp.tool()
def get_project_info() -> str:
    return json.dumps({
        "name": "OpenCode Ecosystem",
        "version": "5.4.0",
        "description": "OpenCode Ecosystem — v5.4.0 (R23: Trust Engine + N3.5 Completo)",
        "decisions_count": len(_load_decisions())
    })

if __name__ == "__main__":
    mcp.run()
