"""
Code GraphRAG — Builder do Grafo de Conhecimento do OpenCode.

Inspirado pelo graph_builder.py e zep_tools.py do MiroFish.
Escaneia o ecossistema OpenCode e constrói um grafo em SQLite.

Uso:
    python build_graph.py --rebuild    # Reconstrói do zero
    python build_graph.py --update     # Atualização incremental
    python build_graph.py --verify     # Verifica integridade
    python build_graph.py --query "termo"  # Busca semântica rápida
"""

import os
import re
import json
import sqlite3
import hashlib
import argparse
from pathlib import Path
from datetime import datetime

# ─── Config ───────────────────────────────────────────────────────────────

OPENCODE_DIR = Path.home() / ".config" / "opencode"
DB_PATH = OPENCODE_DIR / ".reversa" / "code-graph.db"

KNOWN_TYPES = {
    "agents": "agent",
    "skills": "skill",
    "command": "command",
}

# ─── Schema ───────────────────────────────────────────────────────────────

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS graph_nodes (
    id          TEXT PRIMARY KEY,
    type        TEXT NOT NULL,
    name        TEXT NOT NULL,
    description TEXT,
    path        TEXT,
    metadata    TEXT DEFAULT '{}',
    checksum    TEXT,
    created_at  TEXT DEFAULT (datetime('now')),
    updated_at  TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS graph_edges (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id   TEXT NOT NULL,
    target_id   TEXT NOT NULL,
    type        TEXT NOT NULL,
    weight      REAL DEFAULT 1.0,
    metadata    TEXT DEFAULT '{}',
    created_at  TEXT DEFAULT (datetime('now')),
    UNIQUE(source_id, target_id, type)
);

CREATE TABLE IF NOT EXISTS graph_tags (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    node_id TEXT NOT NULL,
    tag     TEXT NOT NULL,
    UNIQUE(node_id, tag)
);

CREATE INDEX IF NOT EXISTS idx_nodes_type ON graph_nodes(type);
CREATE INDEX IF NOT EXISTS idx_nodes_name ON graph_nodes(name);
CREATE INDEX IF NOT EXISTS idx_edges_source ON graph_edges(source_id);
CREATE INDEX IF NOT EXISTS idx_edges_target ON graph_edges(target_id);
CREATE INDEX IF NOT EXISTS idx_edges_type ON graph_edges(type);
CREATE INDEX IF NOT EXISTS idx_tags_tag ON graph_tags(tag);
"""

# ─── Helpers ──────────────────────────────────────────────────────────────

def parse_frontmatter(text):
    """Extrai frontmatter YAML de arquivos .md."""
    match = re.match(r'^---\s*\n(.*?)\n---', text, re.DOTALL)
    if not match:
        return {}
    fm = {}
    for line in match.group(1).split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            fm[key.strip()] = value.strip().strip('"').strip("'")
    return fm


def file_checksum(path):
    """MD5 checksum de arquivo."""
    return hashlib.md5(Path(path).read_bytes()).hexdigest()


def extract_yaml_list(text, key):
    """Extrai lista de valores de frontmatter YAML."""
    pattern = rf'{key}:\s*\[(.*?)\]'
    match = re.search(pattern, text)
    if match:
        return [s.strip().strip('"').strip("'") for s in match.group(1).split(',')]
    
    # Tenta formato de lista multilinha
    lines = text.split('\n')
    in_list = False
    values = []
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith(f'{key}:'):
            in_list = True
            rest = stripped[len(key)+1:].strip()
            if rest.startswith('- '):
                values.append(rest[2:])
            continue
        if in_list:
            if stripped.startswith('- '):
                values.append(stripped[2:])
            elif not stripped or stripped.startswith('---'):
                in_list = False
    
    return values


# ─── Scanners ─────────────────────────────────────────────────────────────

def scan_agents(base_dir):
    """Escaneia agents/ para nós do tipo agent."""
    nodes = []
    edges = []
    tags = []
    
    agents_dir = base_dir / "agents"
    if not agents_dir.exists():
        return nodes, edges, tags
    
    for path in sorted(agents_dir.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        fm = parse_frontmatter(text)
        
        agent_id = f"agent:{path.stem}"
        name = fm.get("name", path.stem)
        desc = fm.get("description", "")
        
        nodes.append({
            "id": agent_id,
            "type": "agent",
            "name": name,
            "description": desc[:200],
            "path": str(path.relative_to(base_dir)),
            "metadata": json.dumps({
                "mode": fm.get("mode", ""),
                "tools": extract_yaml_list(text, "tools"),
            }),
            "checksum": file_checksum(path),
        })
        
        # Tags da descrição
        for word in re.findall(r'\b(security|performance|architecture|review|analysis|generation|synthesis|planning|graph|knowledge)\b', desc.lower()):
            tags.append((agent_id, word))
        
        # Dependências (tools → MCPs)
        tools = extract_yaml_list(text, "tools")
        for tool in tools:
            edges.append((agent_id, f"mcp:{tool}", "depends_on", 0.9, "{}"))
    
    return nodes, edges, tags


def scan_skills(base_dir):
    """Escaneia skills/ para nós do tipo skill."""
    nodes = []
    edges = []
    tags = []
    
    skills_dir = base_dir / "skills"
    if not skills_dir.exists():
        return nodes, edges, tags
    
    for path in sorted(skills_dir.glob("*/SKILL.md")):
        text = path.read_text(encoding="utf-8")
        fm = parse_frontmatter(text)
        
        skill_dir = path.parent.name
        skill_id = f"skill:{skill_dir}"
        name = fm.get("name", skill_dir)
        desc = fm.get("description", "")
        
        nodes.append({
            "id": skill_id,
            "type": "skill",
            "name": name,
            "description": desc[:200],
            "path": str(path.relative_to(base_dir)),
            "metadata": json.dumps({
                "domain": fm.get("metadata.domain", ""),
                "triggers": extract_yaml_list(text, "triggers"),
            }),
            "checksum": file_checksum(path),
        })
        
        # related-skills
        related = extract_yaml_list(text, "related-skills")
        for rskill in related:
            edges.append((skill_id, f"skill:{rskill}", "related_to", 0.5, "{}"))
        
        # Tags
        domain = fm.get("metadata.domain", "")
        if domain:
            tags.append((skill_id, domain))
        for t in extract_yaml_list(text, "triggers"):
            tags.append((skill_id, t.strip()))
    
    return nodes, edges, tags


def scan_commands(base_dir):
    """Escaneia command/ para nós do tipo command."""
    nodes = []
    edges = []
    
    cmd_dir = base_dir / "command"
    if not cmd_dir.exists():
        return nodes, edges
    
    for path in sorted(cmd_dir.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        fm = parse_frontmatter(text)
        
        cmd_id = f"command:{path.stem}"
        name = path.stem
        desc = fm.get("description", "")
        
        nodes.append({
            "id": cmd_id,
            "type": "command",
            "name": f"/{name}",
            "description": desc[:200],
            "path": str(path.relative_to(base_dir)),
            "metadata": json.dumps({}),
            "checksum": file_checksum(path),
        })
        
        # Tenta encontrar agentes mencionados na descrição
        for agent_match in re.finditer(r'reversa-(\w+)', desc.lower()):
            agent_name = agent_match.group(0)
            edges.append((cmd_id, f"agent:{agent_name}", "depends_on", 0.7, "{}"))
    
    return nodes, edges


def scan_mcps(base_dir):
    """Extrai MCPs do opencode.json."""
    nodes = []
    edges = []
    tags = []
    
    config_path = base_dir / "opencode.json"
    if not config_path.exists():
        return nodes, edges, tags
    
    config = json.loads(config_path.read_text(encoding="utf-8"))
    mcps = config.get("mcp", {})
    
    for name, mcp_config in mcps.items():
        mcp_id = f"mcp:{name}"
        enabled = mcp_config.get("enabled", False)
        tags_list = mcp_config.get("tags", [])
        
        cmd = mcp_config.get("command", [])
        cmd_str = " ".join(cmd) if isinstance(cmd, list) else str(cmd)
        
        nodes.append({
            "id": mcp_id,
            "type": "mcp",
            "name": name,
            "description": f"MCP: {name} ({'enabled' if enabled else 'disabled'})",
            "path": str(config_path.relative_to(base_dir)),
            "metadata": json.dumps({
                "enabled": enabled,
                "type": mcp_config.get("type", ""),
            }),
            "checksum": "",
        })
        
        for t in tags_list:
            tags.append((mcp_id, t))
    
    return nodes, edges, tags


# ─── Database ─────────────────────────────────────────────────────────────

def init_db(db_path):
    """Inicializa o banco SQLite."""
    conn = sqlite3.connect(str(db_path))
    conn.executescript(SCHEMA_SQL)
    conn.commit()
    return conn


def clear_db(conn):
    """Limpa todas as tabelas."""
    conn.executescript("""
        DELETE FROM graph_tags;
        DELETE FROM graph_edges;
        DELETE FROM graph_nodes;
    """)
    conn.commit()


def insert_nodes(conn, nodes):
    """Insere nós em lote."""
    cursor = conn.cursor()
    for n in nodes:
        try:
            cursor.execute("""
                INSERT OR REPLACE INTO graph_nodes
                (id, type, name, description, path, metadata, checksum)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (n["id"], n["type"], n["name"], n["description"],
                  n["path"], n["metadata"], n["checksum"]))
        except sqlite3.IntegrityError as e:
            print(f"  ⚠ Erro inserindo nó {n['id']}: {e}")
    conn.commit()


def insert_edges(conn, edges):
    """Insere arestas em lote."""
    cursor = conn.cursor()
    for source, target, etype, weight, meta in edges:
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO graph_edges
                (source_id, target_id, type, weight, metadata)
                VALUES (?, ?, ?, ?, ?)
            """, (source, target, etype, weight, meta))
        except sqlite3.IntegrityError:
            pass
    conn.commit()


def insert_tags(conn, tag_list):
    """Insere tags em lote."""
    cursor = conn.cursor()
    for node_id, tag in tag_list:
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO graph_tags (node_id, tag)
                VALUES (?, ?)
            """, (node_id, tag))
        except sqlite3.IntegrityError:
            pass
    conn.commit()


# ─── Verify ───────────────────────────────────────────────────────────────

def verify_integrity(conn):
    """Verifica integridade do grafo."""
    issues = []
    
    # Nós órfãos
    orphans = conn.execute("""
        SELECT n.id, n.name, n.type
        FROM graph_nodes n
        LEFT JOIN graph_edges e ON n.id = e.source_id OR n.id = e.target_id
        WHERE e.id IS NULL
    """).fetchall()
    
    if orphans:
        issues.append(f"🔴 {len(orphans)} nós órfãos (sem arestas):")
        for oid, name, otype in orphans[:5]:
            issues.append(f"   - {oid} ({name}, {otype})")
        if len(orphans) > 5:
            issues.append(f"   ... e mais {len(orphans)-5}")
    
    # Arestas quebradas
    broken = conn.execute("""
        SELECT e.id, e.source_id, e.target_id
        FROM graph_edges e
        LEFT JOIN graph_nodes s ON e.source_id = s.id
        LEFT JOIN graph_nodes t ON e.target_id = t.id
        WHERE s.id IS NULL OR t.id IS NULL
    """).fetchall()
    
    if broken:
        issues.append(f"🔴 {len(broken)} arestas quebradas (nó inexistente)")
    
    # Ciclos (detecção simples: self-loops)
    self_loops = conn.execute("""
        SELECT id, source_id FROM graph_edges
        WHERE source_id = target_id
    """).fetchall()
    
    if self_loops:
        issues.append(f"🟡 {len(self_loops)} self-loops encontrados")
    
    # Estatísticas
    stats = {
        "total_nodes": conn.execute("SELECT COUNT(*) FROM graph_nodes").fetchone()[0],
        "total_edges": conn.execute("SELECT COUNT(*) FROM graph_edges").fetchone()[0],
        "total_tags": conn.execute("SELECT COUNT(*) FROM graph_tags").fetchone()[0],
    }
    nodes_by_type = conn.execute(
        "SELECT type, COUNT(*) FROM graph_nodes GROUP BY type ORDER BY COUNT(*) DESC"
    ).fetchall()
    
    return issues, stats, nodes_by_type


# ─── Query ────────────────────────────────────────────────────────────────

def semantic_query(conn, query_term):
    """Busca semântica por tags + descrições."""
    term = f"%{query_term.lower()}%"
    
    results = conn.execute("""
        SELECT DISTINCT n.id, n.type, n.name, n.description
        FROM graph_nodes n
        LEFT JOIN graph_tags t ON n.id = t.node_id
        WHERE LOWER(n.name) LIKE ?
           OR LOWER(n.description) LIKE ?
           OR LOWER(t.tag) LIKE ?
        ORDER BY n.type, n.name
        LIMIT 30
    """, (term, term, term)).fetchall()
    
    return results


# ─── Build ────────────────────────────────────────────────────────────────

def build_graph(base_dir, db_path, rebuild=False):
    """Constrói o grafo completo."""
    if rebuild and db_path.exists():
        db_path.unlink()
    
    conn = init_db(db_path)
    
    if rebuild:
        clear_db(conn)
    
    base = Path(base_dir)
    print(f"🔍 Escaneando: {base}")
    
    # Scan agents
    print("  📦 Agents...")
    agent_nodes, agent_edges, agent_tags = scan_agents(base)
    insert_nodes(conn, agent_nodes)
    insert_edges(conn, agent_edges)
    insert_tags(conn, agent_tags)
    print(f"     {len(agent_nodes)} nós, {len(agent_edges)} arestas")
    
    # Scan skills
    print("  📦 Skills...")
    skill_nodes, skill_edges, skill_tags = scan_skills(base)
    insert_nodes(conn, skill_nodes)
    insert_edges(conn, skill_edges)
    insert_tags(conn, skill_tags)
    print(f"     {len(skill_nodes)} nós, {len(skill_edges)} arestas")
    
    # Scan commands
    print("  📦 Commands...")
    cmd_nodes, cmd_edges = scan_commands(base)
    insert_nodes(conn, cmd_nodes)
    insert_edges(conn, cmd_edges)
    print(f"     {len(cmd_nodes)} nós, {len(cmd_edges)} arestas")
    
    # Scan MCPs
    print("  📦 MCPs...")
    mcp_nodes, mcp_edges, mcp_tags = scan_mcps(base)
    insert_nodes(conn, mcp_nodes)
    insert_edges(conn, mcp_edges)
    insert_tags(conn, mcp_tags)
    print(f"     {len(mcp_nodes)} nós, {len(mcp_edges)} arestas")
    
    # Verify
    print("\n🔍 Verificando integridade...")
    issues, stats, by_type = verify_integrity(conn)
    
    print(f"\n📊 Estatísticas:")
    print(f"   Total: {stats['total_nodes']} nós, {stats['total_edges']} arestas, {stats['total_tags']} tags")
    for t, c in by_type:
        print(f"   {t}: {c}")
    
    if issues:
        print(f"\n⚠ Issues encontradas:")
        for issue in issues:
            print(f"   {issue}")
    else:
        print("\n✅ Grafo íntegro — sem issues!")
    
    conn.close()
    print(f"\n📁 Banco: {db_path}")


# ─── CLI ──────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Code GraphRAG Builder")
    parser.add_argument("--rebuild", action="store_true", help="Reconstruir do zero")
    parser.add_argument("--update", action="store_true", help="Atualização incremental")
    parser.add_argument("--verify", action="store_true", help="Verificar integridade")
    parser.add_argument("--query", type=str, help="Busca semântica")
    parser.add_argument("--dir", type=str, default=str(OPENCODE_DIR),
                       help="Diretório OpenCode")
    
    args = parser.parse_args()
    base = Path(args.dir)
    
    if args.query:
        conn = init_db(DB_PATH)
        results = semantic_query(conn, args.query)
        print(f"🔍 Query: '{args.query}' — {len(results)} resultados\n")
        for rid, rtype, rname, rdesc in results:
            print(f"  [{rtype:8}] {rid:30} {rname:25} {rdesc[:60]}")
        conn.close()
        return
    
    if args.verify:
        if not DB_PATH.exists():
            print("❌ Banco não encontrado. Execute --rebuild primeiro.")
            return
        conn = init_db(DB_PATH)
        issues, stats, by_type = verify_integrity(conn)
        print(f"📊 Estatísticas:")
        print(f"   Total: {stats['total_nodes']} nós, {stats['total_edges']} arestas, {stats['total_tags']} tags")
        for t, c in by_type:
            print(f"   {t}: {c}")
        if issues:
            print(f"\n⚠ Issues:")
            for iss in issues:
                print(f"   {iss}")
        else:
            print("\n✅ Grafo íntegro!")
        conn.close()
        return
    
    build_graph(base, DB_PATH, rebuild=args.rebuild or args.update)


if __name__ == "__main__":
    main()
