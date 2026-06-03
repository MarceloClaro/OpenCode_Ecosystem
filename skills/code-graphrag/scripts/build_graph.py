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

# ─── Mapeamento Tools OpenCode → MCPs ────────────────────────────────────
# Tools são permissões declaradas nos agent files (ex: tools: [bash, read, write]).
# MCPs são servidores externos registrados em opencode.json.
# Este mapa liga tools aos MCPs que provêem funcionalidade correspondente.

TOOL_MCP_MAP = {
    "bash":             [],                           # shell nativo, sem MCP
    "read":              ["filesystem"],
    "write":             ["filesystem"],
    "edit":              ["filesystem"],
    "grep":              ["gh_grep"],
    "glob":              ["filesystem"],
    "diff":              ["diff"],
    "search":            ["websearch", "gh_grep"],
    "fetch":             ["fetch", "webfetch"],
    "webfetch":          ["fetch", "webfetch"],
    "websearch":         ["websearch"],
    "browser_snapshot":  ["playwright"],
    "browser_navigate":  ["playwright"],
    "browser_click":     ["playwright"],
    "browser_type":      ["playwright"],
    "code-runner":       ["code-runner"],
    "sql":               ["sqlite"],
    "sqlite":            ["sqlite"],
    "task":              [],                           # meta-orquestração, sem MCP
    "sequential-thinking": ["sequential-thinking"],
    "memory":            ["memory"],
    "github":            ["github"],
    "pdf":               ["pdf"],
    "time":              ["time"],
    "playwright":        ["playwright"],
    "filesystem":        ["filesystem"],
    "glob":              ["filesystem"],
    "evaluate":          ["code-runner"],
}

# ─── Tipos de Raciocínio Científico ──────────────────────────────────────
# Nós do tipo 'razão' representam categorias de raciocínio implementadas
# pelos agents/skills do ecossistema.

REASONING_TYPES = {
    "razão:deductive":        "Raciocínio dedutivo — deriva conclusões necessárias a partir de premissas",
    "razão:inductive":        "Raciocínio indutivo — generaliza padrões a partir de observações específicas",
    "razão:abductive":        "Raciocínio abdutivo — infere a melhor explicação para observações",
    "razão:causal":           "Raciocínio causal — modela relações de causa e efeito",
    "razão:counterfactual":   "Raciocínio contrafactual — avalia cenários alternativos ('e se...')",
    "razão:analogical":       "Raciocínio analógico — transfere conhecimento entre domínios análogos",
    "razão:systems-thinking": "Pensamento sistêmico — analisa interações emergentes em sistemas complexos",
    "razão:first-principles": "Primeiros princípios — decompõe problemas até fundamentos irredutíveis",
    "razão:dialectical":      "Raciocínio dialético — sintetiza tese e antítese em síntese superior",
    "razão:strategic":        "Raciocínio estratégico — planeja sequências de ações sob incerteza",
    "razão:game-theoretic":   "Raciocínio de teoria dos jogos — modela interações estratégicas entre agentes",
    "razão:probabilistic":    "Raciocínio probabilístico — quantifica e propaga incerteza",
    "razão:bayesian":         "Raciocínio bayesiano — atualiza crenças probabilisticamente com novas evidências",
    "razão:moral":            "Raciocínio ético — avalia cursos de ação sob princípios morais",
    "razão:creative":         "Raciocínio criativo — gera soluções originais além do espaço conhecido",
    "razão:mathematical":     "Raciocínio matemático formal — prova teoremas, verifica conjecturas",
    "razão:statistical":      "Raciocínio estatístico — infere propriedades de populações a partir de amostras",
    "razão:experimental":     "Raciocínio experimental — desenha e analisa experimentos controlados",
    "razão:temporal":         "Raciocínio temporal — raciocina sobre sequências, estados e mudanças no tempo",
    "razão:spatial":          "Raciocínio espacial — manipula representações geométricas e topológicas",
}

# Mapeamento de agents/skills para tipos de raciocínio que implementam
# (matches por keywords na description + nome do nó)
REASONING_KEYWORDS = {
    "deductive":       ["dedutivo", "deductive", "proof", "prova", "verifica", "theorem", "teorema", "lógico", "logical"],
    "inductive":       ["indutivo", "inductive", "generaliza", "generalization", "pattern"],
    "abductive":       ["abdutivo", "abductive", "abdução", "best explanation", "diagnosis"],
    "causal":          ["causal", "causa", "causality", "counterfactual", "contrafactual", "do-calculus"],
    "counterfactual":  ["counterfactual", "contrafactual", "e se", "what if", "pre-mortem", "premortem"],
    "analogical":      ["analógico", "analogical", "analogy", "metaphor", "transfer"],
    "systems-thinking":["sistêmico", "systems", "systemic", "emergente", "complexo", "holistic"],
    "first-principles":["primeiros princípios", "first principles", "decompos", "fundamental"],
    "dialectical":     ["dialético", "dialectical", "dialectic", "debate", "thesis", "antithesis", "forum", "argument"],
    "strategic":       ["estratégico", "strategic", "strategy", "planejamento", "planning", "longo prazo"],
    "game-theoretic":  ["game theory", "teoria dos jogos", "game theoretic", "nash", "equilibrium"],
    "probabilistic":   ["probabilístico", "probabilistic", "probabilidade", "uncertainty", "incerteza"],
    "bayesian":        ["bayesiano", "bayesian", "bayes", "prior", "posterior", "belief update"],
    "moral":           ["ético", "ethical", "moral", "ethics", "decolonial", "justiça"],
    "creative":        ["criativo", "creative", "novel", "original", "idea generation", "innovation"],
    "mathematical":    ["matemático", "mathematical", "math", "matematica", "algebra", "geometria", "number theory", "proof"],
    "statistical":     ["estatístico", "statistical", "statistics", "estatistica", "regression", "bootstrap", "pca"],
    "experimental":    ["experimental", "experiment", "desenho experimental", "methodology", "metodologia"],
    "temporal":        ["temporal", "sequential", "sequência", "long horizon", "longo horizonte", "dag"],
    "spatial":         ["espacial", "spatial", "geometric", "geométrico", "topological", "grafo", "graph"],
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


def get_body_text(text):
    """Extrai o corpo do markdown (remove frontmatter)."""
    match = re.match(r'^---\s*\n.*?\n---\s*\n(.*)', text, re.DOTALL)
    if match:
        return match.group(1)
    return text


# ─── Diretórios de Skills Externas ────────────────────────────────────────

AGENTS_SKILLS_DIR = Path.home() / ".agents" / "skills"


def discover_external_collections():
    """Descobre coleções de skills externas em ~/.agents/skills/.

    Cada subdiretório é uma coleção (ex: broomva-skills, cc-skills, open-design).
    Retorna lista de Paths absolutos.
    """
    collections = []
    if AGENTS_SKILLS_DIR.exists():
        for item in sorted(AGENTS_SKILLS_DIR.iterdir()):
            if item.is_dir():
                collections.append(item.resolve())
    return collections


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
        body = get_body_text(text)
        
        nodes.append({
            "id": agent_id,
            "type": "agent",
            "name": name,
            "description": desc[:300],
            "path": str(path.relative_to(base_dir)),
            "metadata": json.dumps({
                "mode": fm.get("mode", ""),
                "tools": extract_yaml_list(text, "tools"),
            }),
            "checksum": file_checksum(path),
        })
        
        # Tags da descrição + body
        for word in re.findall(r'\b(security|performance|architecture|review|analysis|generation|synthesis|planning|graph|knowledge|research|debate|audit|code|test|documentation)\b', desc.lower() + " " + body.lower()[:500]):
            tags.append((agent_id, word))
        
        # Afinidades (affinity → edges multi-tipo)
        affinity = extract_yaml_list(text, "affinity")
        for item in affinity:
            parts = item.rsplit(':', 1)
            affinity_name = parts[0].strip()
            weight = float(parts[1].strip()) if len(parts) > 1 and parts[1].strip().replace('.','',1).isdigit() else 0.5
            for prefix in ["agent", "mcp", "skill"]:
                target_id = f"{prefix}:{affinity_name}"
                if target_id != agent_id:
                    edges.append((agent_id, target_id, "affinity", weight, "{}"))

        # NOTA: Tools→MCP mapping é feito em pós-processamento (build_graph)
    
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
        body = get_body_text(text)
        
        # Fallback description: se vazia, extrai primeira linha significativa do corpo
        if not desc and body.strip():
            first_line = body.strip().split('\n')[0].strip()
            desc = first_line[:200] if first_line else "(skill sem descrição)"
        
        nodes.append({
            "id": skill_id,
            "type": "skill",
            "name": name,
            "description": desc[:300],
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


def get_reversa_agent_names(base_dir):
    """Retorna conjunto de nomes de agentes reversa-* encontrados no diretório agents/."""
    names = set()
    agents_dir = base_dir / "agents"
    if agents_dir.exists():
        for path in agents_dir.glob("reversa-*.md"):
            names.add(f"agent:{path.stem}")
    return names


def scan_external_skills(collection_dir):
    """Escaneia uma coleção externa de skills usando **/SKILL.md (qualquer profundidade).

    Diferente de scan_skills() que usa skills/*/SKILL.md, esta função
    cobre os 3 padrões encontrados em ~/.agents/skills/:
      - collection/skills/<skill>/SKILL.md
      - collection/<skill>/SKILL.md  (skills-showcase, blog-post, etc.)
      - collection/agent-smith/agent-smith/SKILL.md  (subdir aninhado)

    Usa path absoluto no banco para que cross_reference_scan e
    connect_reasoning_to_agents possam ler o corpo dos arquivos.
    """
    nodes = []
    edges = []
    tags = []

    for path in sorted(collection_dir.rglob("SKILL.md")):
        try:
            text = path.read_text(encoding="utf-8")
        except Exception:
            continue  # ignora arquivos corrompidos

        fm = parse_frontmatter(text)

        skill_dir = path.parent.name
        skill_id = f"skill:{skill_dir}"
        name = fm.get("name", skill_dir)
        desc = fm.get("description", "")
        body = get_body_text(text)

        # Fallback description
        if not desc and body.strip():
            first_line = body.strip().split('\n')[0].strip()
            desc = first_line[:200] if first_line else "(skill sem descrição)"

        # Path relativo à coleção para legibilidade, mas também guarda o absoluto
        try:
            rel_path = str(path.relative_to(AGENTS_SKILLS_DIR))
        except ValueError:
            rel_path = str(path)

        nodes.append({
            "id": skill_id,
            "type": "skill",
            "name": name,
            "description": desc[:300],
            "path": str(path),           # absoluto → cross_reference lê direto
            "metadata": json.dumps({
                "domain": fm.get("metadata.domain", ""),
                "triggers": extract_yaml_list(text, "triggers"),
                "collection": collection_dir.name,
                "rel_path": rel_path,
            }),
            "checksum": file_checksum(path),
        })

        # related-skills
        related = extract_yaml_list(text, "related-skills")
        for rskill in related:
            edges.append((skill_id, f"skill:{rskill}", "related_to", 0.5, "{}"))

        # Tags do domínio e triggers
        domain = fm.get("metadata.domain", "")
        if domain:
            tags.append((skill_id, domain))
        for t in extract_yaml_list(text, "triggers"):
            tags.append((skill_id, t.strip()))

    return nodes, edges, tags


def scan_commands(base_dir):
    """Escaneia command/ para nós do tipo command.
    
    Inclui comandos built-in do OpenCode (/devcontainer, /workspaces, /worktree)
    mesmo sem arquivo .md correspondente, para evitar falsos órfãos.
    """
    nodes = []
    edges = []
    
    # ── Comandos built-in do OpenCode (sem arquivo .md) ──────────────
    BUILTIN_COMMANDS = {
        "devcontainer": "Comando built-in do OpenCode para gerenciar contêineres de desenvolvimento",
        "workspaces":   "Comando built-in do OpenCode para gerenciar múltiplos workspaces",
        "worktree":     "Comando built-in do OpenCode para gerenciar worktrees Git",
    }
    for cmd_name, cmd_desc in BUILTIN_COMMANDS.items():
        cmd_id = f"command:{cmd_name}"
        nodes.append({
            "id": cmd_id,
            "type": "command",
            "name": f"/{cmd_name}",
            "description": cmd_desc,
            "path": "(built-in)",
            "metadata": json.dumps({"builtin": True}),
            "checksum": "",
        })
    
    # ── Comandos customizados (arquivos .md em command/) ─────────────
    cmd_dir = base_dir / "command"
    if not cmd_dir.exists():
        return nodes, edges
    
    # Carrega agentes reversa conhecidos para referência cruzada
    reversa_agents = get_reversa_agent_names(base_dir)
    
    for path in sorted(cmd_dir.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        fm = parse_frontmatter(text)
        
        cmd_id = f"command:{path.stem}"
        name = path.stem
        desc = fm.get("description", "")
        body = get_body_text(text)
        
        nodes.append({
            "id": cmd_id,
            "type": "command",
            "name": f"/{name}",
            "description": desc[:300],
            "path": str(path.relative_to(base_dir)),
            "metadata": json.dumps({}),
            "checksum": file_checksum(path),
        })
        
        # Varre o texto completo do arquivo em busca de agentes reversa-*
        for agent_match in re.finditer(r'\breversa-[\w-]+', text.lower()):
            agent_ref = f"agent:{agent_match.group(0)}"
            if agent_ref in reversa_agents:
                edges.append((cmd_id, agent_ref, "depends_on", 0.7, "{}"))
    
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
        
        # Checksum do JSON de configuração do MCP (para detectar mudanças)
        config_json = json.dumps(mcp_config, sort_keys=True)
        mcp_checksum = hashlib.md5(config_json.encode()).hexdigest()
        
        # Descrição enriquecida com tipo e comando
        mcp_type = mcp_config.get("type", "unknown")
        enriched_desc = f"MCP: {name} ({'enabled' if enabled else 'disabled'}) | type={mcp_type}"
        if cmd_str:
            enriched_desc += f" | cmd={cmd_str[:100]}"
        
        nodes.append({
            "id": mcp_id,
            "type": "mcp",
            "name": name,
            "description": enriched_desc[:300],
            "path": str(config_path.relative_to(base_dir)),
            "metadata": json.dumps({
                "enabled": enabled,
                "type": mcp_type,
                "command": cmd_str[:200],
            }),
            "checksum": mcp_checksum,
        })
        
        # Tag de status
        if enabled:
            tags.append((mcp_id, "status:enabled"))
        else:
            tags.append((mcp_id, "status:disabled"))
        
        for t in tags_list:
            tags.append((mcp_id, t))
    
    return nodes, edges, tags


# ─── Reasoning Nodes ──────────────────────────────────────────────────────

def generate_reasoning_nodes():
    """Gera nós do tipo 'razão' para tipos de raciocínio científico."""
    nodes = []
    tags = []
    for rid, desc in REASONING_TYPES.items():
        short_name = rid.split(':')[1]
        nodes.append({
            "id": rid,
            "type": "razão",
            "name": short_name,
            "description": desc[:300],
            "path": "",
            "metadata": json.dumps({"category": "reasoning"}),
            "checksum": "",
        })
        tags.append((rid, short_name))
        tags.append((rid, "reasoning"))
    return nodes, tags


def connect_reasoning_to_agents(conn, base_dir):
    """Varre descrições E corpo completo dos agents/skills e cria arestas implements.
    
    Antes: só descriptions do DB (perdia matches no corpo dos arquivos).
    Agora: description + corpo do SKILL.md / agent.md para matching mais completo.
    """
    edges = []
    base = Path(base_dir)
    
    # Carrega todos os agents e skills
    entities = conn.execute("""
        SELECT id, name, description, path FROM graph_nodes
        WHERE type IN ('agent', 'skill')
    """).fetchall()
    
    if not entities:
        return edges
    
    for eid, ename, edesc, efile in entities:
        # Texto base: nome + descrição
        text_to_scan = (ename + " " + (edesc or "")).lower()
        
        # Tenta ler corpo do arquivo se existir
        body_text = ""
        if efile and efile != "(built-in)":
            # Path pode ser absoluto (skills externas) ou relativo (internas)
            fpath = Path(efile)
            if not fpath.is_absolute():
                fpath = base / efile
            if fpath.exists():
                raw = fpath.read_text(encoding="utf-8", errors="replace")
                # Se for SKILL.md, usa body inteiro; se for .md simples, também
                body_text = get_body_text(raw)
        
        full_text = text_to_scan + " " + body_text.lower()
        
        for rtype, keywords in REASONING_KEYWORDS.items():
            target_id = f"razão:{rtype}"
            for kw in keywords:
                if kw in full_text:
                    edges.append((eid, target_id, "implements", 0.5, "{}"))
                    break
    
    return edges


# ─── Tools → MCP Mapping ─────────────────────────────────────────────────

def generate_tool_mcp_edges(conn):
    """Varre tools declaradas nos agent files e cria arestas tool → mcp.
    
    As tools são extraídas do metadata de cada nó agent (campo 'tools').
    Para cada tool, consulta TOOL_MCP_MAP e cria arestas provided_by
    para os MCPs correspondentes (se existirem no banco).
    """
    edges = []
    
    # Carrega MCPs conhecidos do banco
    known_mcps = set()
    for row in conn.execute("SELECT id FROM graph_nodes WHERE type = 'mcp'"):
        known_mcps.add(row[0])
    
    if not known_mcps:
        return edges
    
    # Carrega agents com suas tools
    agents = conn.execute("""
        SELECT id, metadata FROM graph_nodes WHERE type = 'agent'
    """).fetchall()
    
    for aid, meta_json in agents:
        if not meta_json:
            continue
        try:
            meta = json.loads(meta_json)
        except json.JSONDecodeError:
            continue
        
        tools = meta.get("tools", [])
        if not tools:
            continue
        
        for tool_name in tools:
            if tool_name in TOOL_MCP_MAP:
                for mcp_name in TOOL_MCP_MAP[tool_name]:
                    mcp_id = f"mcp:{mcp_name}"
                    if mcp_id in known_mcps:
                        edges.append((aid, mcp_id, "depends_on", 0.8, json.dumps({"tool": tool_name})))
    
    return edges


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


# ─── Cross-Reference Scan (Expanded) ──────────────────────────────────────

def build_name_map(conn):
    """Constrói mapa nome→id de todas as entidades conhecidas no banco.
    
    Inclui agents, skills, MCPs, commands e razão.
    Mapeia também stems (parte após prefixo) para matching flexível.
    """
    name_map = {}
    
    entities = conn.execute("""
        SELECT id, name, type FROM graph_nodes
    """).fetchall()
    
    for nid, name, ntype in entities:
        # Mapeia nome completo
        name_map[name.lower()] = nid
        
        # Para agent:reversa-scout, mapeia 'reversa-scout'
        if ':' in nid:
            name_map[nid] = nid
        
        # Stem (parte após 'agent:', 'skill:', 'mcp:', 'command:', 'razão:')
        if ':' in nid:
            stem = nid.split(':', 1)[1]
            if len(stem) > 2:
                name_map[stem.lower()] = nid
        
        # Para nomes com hífen, mapeia a parte após o primeiro hífen
        if '-' in name:
            stem = name.split('-', 1)[1]
            if len(stem) > 2:
                name_map[stem.lower()] = nid
    
    return name_map


def scan_text_for_references(text, name_map, source_id, min_word_len=4):
    """Varre um texto em busca de menções a entidades conhecidas.
    
    Retorna lista de arestas (source_id, ref_id, 'references', 0.6, '{}').
    """
    edges = []
    text_lower = text.lower()
    
    for name_text, ref_id in name_map.items():
        if ref_id == source_id:
            continue
        if len(name_text) < min_word_len:
            continue
        if name_text in text_lower:
            edge_tuple = (source_id, ref_id, "references", 0.6, "{}")
            if edge_tuple not in edges:
                edges.append(edge_tuple)
    
    return edges


def cross_reference_scan(base_dir, conn):
    """Pós-processamento expandido: varre descrições E corpo de TODOS os tipos de nó.
    
    Antes: skills + commands apenas.
    Agora: agents, skills, commands, MCPs — usa description + full text.
    """
    edges = []
    name_map = build_name_map(conn)
    
    if not name_map:
        return edges
    
    # Varre agents
    for row in conn.execute("SELECT id, description FROM graph_nodes WHERE type = 'agent'"):
        nid, desc = row
        if desc:
            edges.extend(scan_text_for_references(desc, name_map, nid))
    
    # Varre skills
    for row in conn.execute("SELECT id, description FROM graph_nodes WHERE type = 'skill'"):
        nid, desc = row
        if desc:
            edges.extend(scan_text_for_references(desc, name_map, nid))
    
    # Varre commands
    for row in conn.execute("SELECT id, description FROM graph_nodes WHERE type = 'command'"):
        nid, desc = row
        if desc:
            edges.extend(scan_text_for_references(desc, name_map, nid))
    
    # Varre MCPs
    for row in conn.execute("SELECT id, description FROM graph_nodes WHERE type = 'mcp'"):
        nid, desc = row
        if desc:
            edges.extend(scan_text_for_references(desc, name_map, nid))
    
    # --- Full-text scanning: varre corpo dos agent files ---
    base = Path(base_dir)
    agents_dir = base / "agents"
    if agents_dir.exists():
        for path in sorted(agents_dir.glob("*.md")):
            text = path.read_text(encoding="utf-8", errors="replace")
            body = get_body_text(text)
            sid = f"agent:{path.stem}"
            edges.extend(scan_text_for_references(body, name_map, sid))
    
    # Full-text: corpo dos command files
    cmd_dir = base / "command"
    if cmd_dir.exists():
        for path in sorted(cmd_dir.glob("*.md")):
            text = path.read_text(encoding="utf-8", errors="replace")
            body = get_body_text(text)
            sid = f"command:{path.stem}"
            edges.extend(scan_text_for_references(body, name_map, sid))
    
    # Full-text: corpo dos SKILL.md (skills podem chamar outras entidades)
    for row in conn.execute("SELECT id, path FROM graph_nodes WHERE type = 'skill'"):
        sid, sfile = row
        if sfile and sfile != "(built-in)":
            fpath = Path(sfile)
            if not fpath.is_absolute():
                fpath = base / sfile
            if fpath.exists():
                text = fpath.read_text(encoding="utf-8", errors="replace")
                body = get_body_text(text)
                edges.extend(scan_text_for_references(body, name_map, sid))
    
    return edges


# ─── Verify ───────────────────────────────────────────────────────────────

def verify_integrity(conn):
    """Verifica integridade do grafo."""
    issues = []
    
    # Nós órfãos (sem arestas)
    orphans = conn.execute("""
        SELECT n.id, n.name, n.type
        FROM graph_nodes n
        LEFT JOIN graph_edges e ON n.id = e.source_id OR n.id = e.target_id
        WHERE e.id IS NULL
    """).fetchall()
    
    if orphans:
        issues.append(f"🔴 {len(orphans)} nós órfãos (sem arestas):")
        # Agrupa por tipo
        by_type = {}
        for oid, name, otype in orphans:
            by_type.setdefault(otype, []).append(oid)
        for t, ids in sorted(by_type.items()):
            issues.append(f"   - {t}: {len(ids)}")
        # Top 5
        for oid, name, otype in orphans[:5]:
            issues.append(f"     {oid} ({name})")
        if len(orphans) > 5:
            issues.append(f"     ... e mais {len(orphans)-5}")
    
    # Arestas quebradas (remove automaticamente)
    broken = conn.execute("""
        SELECT e.id, e.source_id, e.target_id
        FROM graph_edges e
        LEFT JOIN graph_nodes s ON e.source_id = s.id
        LEFT JOIN graph_nodes t ON e.target_id = t.id
        WHERE s.id IS NULL OR t.id IS NULL
    """).fetchall()
    
    if broken:
        conn.executemany("DELETE FROM graph_edges WHERE id = ?", [(b[0],) for b in broken])
        conn.commit()
        issues.append(f"🔴 {len(broken)} arestas quebradas removidas")
    
    # Ciclos (detecção simples: self-loops)
    self_loops = conn.execute("""
        SELECT id, source_id FROM graph_edges
        WHERE source_id = target_id
    """).fetchall()
    
    if self_loops:
        issues.append(f"🟡 {len(self_loops)} self-loops encontrados")
    
    # Checksums faltantes
    missing_cs = conn.execute("""
        SELECT id, type FROM graph_nodes
        WHERE checksum IS NULL OR checksum = ''
    """).fetchall()
    if missing_cs:
        issues.append(f"🟡 {len(missing_cs)} nós sem checksum:")
        for nid, ntype in missing_cs[:5]:
            issues.append(f"     {nid} ({ntype})")
        if len(missing_cs) > 5:
            issues.append(f"     ... e mais {len(missing_cs)-5}")
    
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
    
    # ── Fase 1: Scanners ──────────────────────────────────────────────
    
    # Scan agents
    print("  📦 Agents...")
    agent_nodes, agent_edges, agent_tags = scan_agents(base)
    insert_nodes(conn, agent_nodes)
    insert_edges(conn, agent_edges)
    insert_tags(conn, agent_tags)
    print(f"     {len(agent_nodes)} nós, {len(agent_edges)} arestas")
    
    # Scan skills (internas: ~/.config/opencode/skills/)
    print("  📦 Skills (internas)...")
    skill_nodes, skill_edges, skill_tags = scan_skills(base)
    insert_nodes(conn, skill_nodes)
    insert_edges(conn, skill_edges)
    insert_tags(conn, skill_tags)
    print(f"     {len(skill_nodes)} nós, {len(skill_edges)} arestas")

    # Scan skills externas (~/.agents/skills/*/)
    print("  📦 Skills (externas)...")
    collections = discover_external_collections()
    ext_total_nodes = 0
    ext_total_edges = 0
    for col in collections:
        ext_nodes, ext_edges, ext_tags = scan_external_skills(col)
        insert_nodes(conn, ext_nodes)
        insert_edges(conn, ext_edges)
        insert_tags(conn, ext_tags)
        ext_total_nodes += len(ext_nodes)
        ext_total_edges += len(ext_edges)
        print(f"     {col.name}: {len(ext_nodes)} nós, {len(ext_edges)} arestas")
    print(f"     Total externas: {ext_total_nodes} nós, {ext_total_edges} arestas")
    
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
    
    # ── Fase 2: Reasoning Nodes ───────────────────────────────────────
    print("  🧠 Reasoning types...")
    raz_nodes, raz_tags = generate_reasoning_nodes()
    insert_nodes(conn, raz_nodes)
    insert_tags(conn, raz_tags)
    print(f"     {len(raz_nodes)} nós de raciocínio")
    
    # ── Fase 3: Tools → MCP mapping ──────────────────────────────────
    print("  🔧 Tools → MCP mapping...")
    tool_edges = generate_tool_mcp_edges(conn)
    insert_edges(conn, tool_edges)
    print(f"     {len(tool_edges)} arestas tool→mcp")
    
    # ── Fase 4: Reasoning → Agents ───────────────────────────────────
    print("  🔗 Reasoning → Agents (com corpo completo dos arquivos)...")
    raz_edges = connect_reasoning_to_agents(conn, base)
    insert_edges(conn, raz_edges)
    print(f"     {len(raz_edges)} arestas implements")
    
    # ── Fase 5: Cross-reference scan (expandido) ─────────────────────
    print("  🔗 Cross-reference scan (full)...")
    xref_edges = cross_reference_scan(base, conn)
    insert_edges(conn, xref_edges)
    print(f"     {len(xref_edges)} arestas cruzadas")
    
    # ── Verify ────────────────────────────────────────────────────────
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
