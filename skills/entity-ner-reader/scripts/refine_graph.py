"""
Refinement script: enrich graph edges + bridge to entity-reader schema
"""
import json
import sqlite3
import re
from pathlib import Path

DB_PATH = Path.home() / ".config" / "opencode" / ".reversa" / "code-graph.db"

def connect():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def ensure_entity_tables(conn):
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS entities (
        uuid TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        labels TEXT,
        summary TEXT,
        attributes TEXT,
        entity_type TEXT,
        created_at TEXT DEFAULT (datetime('now'))
    );
    CREATE TABLE IF NOT EXISTS entity_edges (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        entity_uuid TEXT NOT NULL REFERENCES entities(uuid),
        direction TEXT NOT NULL,
        edge_name TEXT NOT NULL,
        fact TEXT,
        target_uuid TEXT,
        source_uuid TEXT
    );
    CREATE TABLE IF NOT EXISTS entity_types (
        type TEXT PRIMARY KEY,
        count INTEGER DEFAULT 0,
        description TEXT
    );
    """)
    conn.commit()

def infer_edges_between_nodes(conn):
    """Add edges between related nodes based on naming conventions."""
    existing = set()
    for r in conn.execute("SELECT source_id, target_id, type FROM graph_edges").fetchall():
        existing.add((r["source_id"], r["target_id"], r["type"]))

    new_edges = 0

    # 1. Agent <-> Skill same name: agent:X supports skill:X
    agents = conn.execute("SELECT id, name, path FROM graph_nodes WHERE type='agent'").fetchall()
    skills = conn.execute("SELECT id, name, path FROM graph_nodes WHERE type='skill'").fetchall()
    mcps = conn.execute("SELECT id, name, path FROM graph_nodes WHERE type='mcp'").fetchall()
    cmds = conn.execute("SELECT id, name, path FROM graph_nodes WHERE type='command'").fetchall()

    agent_map = {a["name"]: a for a in agents}
    skill_map = {s["name"]: s for s in skills}
    mcp_map = {m["name"]: m for m in mcps}
    cmd_map = {c["name"]: c for c in cmds}

    # Agent -> Skill: same name or agent:X uses skill:X
    for a in agents:
        aname = a["name"].replace("reversa-", "", 1) if a["name"].startswith("reversa-") else a["name"]
        if aname in skill_map:
            key = (a["id"], skill_map[aname]["id"], "uses")
            if key not in existing:
                conn.execute(
                    "INSERT OR IGNORE INTO graph_edges (source_id, target_id, type, weight, metadata) VALUES (?, ?, ?, ?, ?)",
                    (a["id"], skill_map[aname]["id"], "uses", 0.9, '{}')
                )
                existing.add(key)
                new_edges += 1

    # Skill -> MCP: check skill description/path for MCP references
    for s in skills:
        desc = (s["path"] or "")
        for m in mcps:
            mname = m["name"].lower()
            if mname in desc.lower():
                key = (s["id"], m["id"], "references")
                if key not in existing:
                    conn.execute(
                        "INSERT OR IGNORE INTO graph_edges (source_id, target_id, type, weight, metadata) VALUES (?, ?, ?, ?, ?)",
                        (s["id"], m["id"], "references", 0.7, '{}')
                    )
                    existing.add(key)
                    new_edges += 1

    # Skill -> Command: same name
    for c in cmds:
        cname = c["name"].lstrip("/")
        if cname in skill_map:
            key = (c["id"], skill_map[cname]["id"], "triggered_by")
            if key not in existing:
                conn.execute(
                    "INSERT OR IGNORE INTO graph_edges (source_id, target_id, type, weight, metadata) VALUES (?, ?, ?, ?, ?)",
                    (c["id"], skill_map[cname]["id"], "triggered_by", 0.95, '{}')
                )
                existing.add(key)
                new_edges += 1

    # Agent -> Command: agent name matches command name
    for a in agents:
        aname = a["name"]
        for c in cmds:
            cname = c["name"].lstrip("/")
            if aname == cname:
                key = (a["id"], c["id"], "executes")
                if key not in existing:
                    conn.execute(
                        "INSERT OR IGNORE INTO graph_edges (source_id, target_id, type, weight, metadata) VALUES (?, ?, ?, ?, ?)",
                        (a["id"], c["id"], "executes", 0.85, '{}')
                    )
                    existing.add(key)
                    new_edges += 1

    conn.commit()
    return new_edges

def bridge_to_entity_tables(conn):
    """Copy data from graph_* to entity_* tables."""
    conn.execute("DELETE FROM entities")
    conn.execute("DELETE FROM entity_edges")
    conn.execute("DELETE FROM entity_types")

    # Copy nodes
    nodes = conn.execute("SELECT id, type, name, description, path, metadata FROM graph_nodes").fetchall()
    for n in nodes:
        labels = json.dumps(["Entity", n["type"].title() if n["type"] else "Node"])
        attrs = json.dumps({"path": n["path"], "metadata": n["metadata"] or "{}"})
        conn.execute(
            "INSERT OR IGNORE INTO entities (uuid, name, labels, summary, attributes, entity_type) VALUES (?, ?, ?, ?, ?, ?)",
            (n["id"], n["name"], labels, n["description"] or "", attrs, n["type"])
        )

    # Copy edges
    edges = conn.execute("SELECT source_id, target_id, type, weight FROM graph_edges").fetchall()
    for e in edges:
        fact = json.dumps({"type": e["type"], "weight": e["weight"]})
        # store as outgoing from source
        conn.execute(
            "INSERT INTO entity_edges (entity_uuid, direction, edge_name, fact, target_uuid, source_uuid) VALUES (?, ?, ?, ?, ?, ?)",
            (e["source_id"], "outgoing", e["type"], fact, e["target_id"], e["source_id"])
        )
        # store as incoming to target
        conn.execute(
            "INSERT INTO entity_edges (entity_uuid, direction, edge_name, fact, target_uuid, source_uuid) VALUES (?, ?, ?, ?, ?, ?)",
            (e["target_id"], "incoming", e["type"], fact, e["target_id"], e["source_id"])
        )

    # Update entity_types counts
    type_counts = conn.execute("SELECT entity_type, count(1) FROM entities GROUP BY entity_type").fetchall()
    for t, c in type_counts:
        conn.execute(
            "INSERT OR REPLACE INTO entity_types (type, count, description) VALUES (?, ?, ?)",
            (t, c, f"Entities of type {t}")
        )

    conn.commit()
    return len(nodes), len(edges)

def add_lgpd_tags(conn):
    """Tag nodes relevant to LGPD/conformity concepts."""
    keywords = {
        "lgpd": ["lgpd", "privacidade", "privac", "dados pessoais", "data protection",
                 "gdpr", "anonimização", "anonimiz", "pseudonimização"],
        "ethical_ai": ["ética", "etic", "integridade", "transparência", "transparenc",
                       "ia", "inteligência artificial", "ai", "artificial intelligence"],
        "research_compliance": ["pesquisa", "acadêmico", "científico", "universidade",
                                "ppg", "ufc", "regulação", "conformidade", "compliance"],
    }

    nodes = conn.execute("SELECT id, name, description, path FROM graph_nodes").fetchall()
    tagged = 0
    for n in nodes:
        text = f"{n['name']} {n['description'] or ''} {n['path'] or ''}".lower()
        for category, terms in keywords.items():
            if any(t in text for t in terms):
                conn.execute(
                    "INSERT OR IGNORE INTO graph_tags (node_id, tag) VALUES (?, ?)",
                    (n["id"], category)
                )
                tagged += 1
    conn.commit()
    return tagged

def main():
    conn = connect()
    ensure_entity_tables(conn)

    print("Adding inferred edges...")
    added = infer_edges_between_nodes(conn)
    print(f"  {added} new edges added")

    print("Tagging LGPD-relevant nodes...")
    tagged = add_lgpd_tags(conn)
    print(f"  {tagged} tags added")

    print("Bridging to entity-reader tables...")
    nn, ne = bridge_to_entity_tables(conn)
    print(f"  {nn} entities, {ne} entity_edges")

    # Stats
    ec = conn.execute("SELECT count(1) FROM graph_edges").fetchone()[0]
    print(f"\nFinal edge count in graph: {ec}")
    
    for r in conn.execute("SELECT tag, count(1) FROM graph_tags GROUP BY tag ORDER BY tag").fetchall():
        print(f"  Tag '{r['tag']}': {r['count']} nodes")

    conn.close()
    print("\nRefinement complete.")

if __name__ == "__main__":
    main()
