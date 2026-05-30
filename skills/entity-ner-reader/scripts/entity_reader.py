"""
Entity NER Reader — Leitura e Filtragem de Entidades em Grafos.

Inspirado pelo EntityReader do MiroFish-Offline (entity_reader.py).
Modos: list, filter, context, stats.

Uso:
    python entity_reader.py list --graph <graph_id>
    python entity_reader.py filter --graph <graph_id> --type Person
    python entity_reader.py context --graph <graph_id> --uuid <uuid>
    python entity_reader.py stats --graph <graph_id>
"""

import argparse
import json
import sqlite3
import sys
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

# ─── Caminho do DB ───────────────────────────────────────────────
DB_PATH = Path(__file__).resolve().parents[3] / ".reversa" / "code-graph.db"


# ─── Data Classes ─────────────────────────────────────────────────
@dataclass
class EntityNode:
    """Entity node data structure"""
    uuid: str
    name: str
    labels: List[str]
    summary: str
    attributes: Dict[str, Any]
    related_edges: List[Dict[str, Any]] = field(default_factory=list)
    related_nodes: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "uuid": self.uuid,
            "name": self.name,
            "labels": self.labels,
            "summary": self.summary,
            "attributes": self.attributes,
            "related_edges": self.related_edges,
            "related_nodes": self.related_nodes,
        }

    def get_entity_type(self) -> Optional[str]:
        for label in self.labels:
            if label not in ("Entity", "Node"):
                return label
        return None


@dataclass
class FilteredEntities:
    """Filtered entity set"""
    entities: List[EntityNode]
    entity_types: Set[str]
    total_count: int
    filtered_count: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "entities": [e.to_dict() for e in self.entities],
            "entity_types": list(self.entity_types),
            "total_count": self.total_count,
            "filtered_count": self.filtered_count,
        }


# ─── Mock Storage (para demonstração sem Neo4j) ──────────────────
class MockGraphStorage:
    """Storage simulado para testes"""

    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path

    def _ensure_db(self):
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(self.db_path))
        conn.execute("""
            CREATE TABLE IF NOT EXISTS entities (
                uuid TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                labels TEXT,
                summary TEXT,
                attributes TEXT,
                entity_type TEXT,
                created_at TEXT DEFAULT (datetime('now'))
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS entity_edges (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entity_uuid TEXT NOT NULL,
                direction TEXT NOT NULL,
                edge_name TEXT NOT NULL,
                fact TEXT,
                target_uuid TEXT,
                source_uuid TEXT,
                FOREIGN KEY (entity_uuid) REFERENCES entities(uuid)
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS entity_types (
                type TEXT PRIMARY KEY,
                count INTEGER DEFAULT 0,
                description TEXT
            )
        """)
        conn.commit()
        return conn

    def get_all_nodes(self, graph_id: str) -> List[Dict[str, Any]]:
        conn = self._ensure_db()
        rows = conn.execute(
            "SELECT uuid, name, labels, summary, attributes, entity_type FROM entities"
        ).fetchall()
        conn.close()
        return [
            {
                "uuid": r[0], "name": r[1],
                "labels": json.loads(r[2]) if r[2] else ["Entity"],
                "summary": r[3] or "",
                "attributes": json.loads(r[4]) if r[4] else {},
                "entity_type": r[5] or "",
            }
            for r in rows
        ] or self._seed_demo_data()

    def get_all_edges(self, graph_id: str) -> List[Dict[str, Any]]:
        conn = self._ensure_db()
        rows = conn.execute(
            "SELECT entity_uuid, direction, edge_name, fact, target_uuid, source_uuid "
            "FROM entity_edges"
        ).fetchall()
        conn.close()
        return [
            {
                "source_node_uuid": r[5] or r[0],
                "target_node_uuid": r[4] or r[0],
                "name": r[2],
                "fact": r[3] or "",
            }
            for r in rows
        ]

    def get_node(self, uuid: str) -> Optional[Dict[str, Any]]:
        nodes = self.get_all_nodes("demo")
        for n in nodes:
            if n["uuid"] == uuid:
                return n
        return None

    def get_node_edges(self, uuid: str) -> List[Dict[str, Any]]:
        all_edges = self.get_all_edges("demo")
        return [
            e for e in all_edges
            if e.get("source_node_uuid") == uuid or e.get("target_node_uuid") == uuid
        ]

    def _seed_demo_data(self) -> List[Dict[str, Any]]:
        """Cria dados de demonstração"""
        from datetime import datetime
        demo_nodes = [
            {"uuid": "ent-001", "name": "Carlos Silva", "labels": ["Person", "Student"],
             "summary": "Estudante de ciência da computação", "attributes": {"full_name": "Carlos Silva", "course": "Ciência da Computação"}},
            {"uuid": "ent-002", "name": "Universidade Federal", "labels": ["Organization", "University"],
             "summary": "Universidade pública federal", "attributes": {"org_name": "Universidade Federal", "location": "São Paulo"}},
            {"uuid": "ent-003", "name": "Prof. Dra. Ana Oliveira", "labels": ["Person", "Professor"],
             "summary": "Professora de IA e ética", "attributes": {"full_name": "Ana Oliveira", "department": "Inteligência Artificial"}},
            {"uuid": "ent-004", "name": "Regulação de IA no Brasil", "labels": ["Entity"],
             "summary": "Projeto de lei sobre regulação de inteligência artificial", "attributes": {}},
            {"uuid": "ent-005", "name": "TechNews Brasil", "labels": ["Organization", "MediaOutlet"],
             "summary": "Portal de notícias de tecnologia", "attributes": {"org_name": "TechNews Brasil"}},
            {"uuid": "ent-006", "name": "João Pereira", "labels": ["Person", "Journalist"],
             "summary": "Jornalista especializado em tecnologia", "attributes": {"full_name": "João Pereira", "role": "Jornalista"}},
            {"uuid": "ent-007", "name": "Ministério da Ciência", "labels": ["Organization", "GovernmentAgency"],
             "summary": "Órgão governamental de ciência e tecnologia", "attributes": {"org_name": "Ministério da Ciência"}},
        ]
        demo_edges = [
            {"entity_uuid": "ent-001", "direction": "outgoing", "edge_name": "STUDIES_AT",
             "fact": "Carlos estuda na Universidade Federal", "target_uuid": "ent-002", "source_uuid": "ent-001"},
            {"entity_uuid": "ent-003", "direction": "outgoing", "edge_name": "WORKS_FOR",
             "fact": "Profa. Ana trabalha na Universidade Federal", "target_uuid": "ent-002", "source_uuid": "ent-003"},
            {"entity_uuid": "ent-006", "direction": "outgoing", "edge_name": "WORKS_FOR",
             "fact": "João trabalha na TechNews Brasil", "target_uuid": "ent-005", "source_uuid": "ent-006"},
            {"entity_uuid": "ent-006", "direction": "outgoing", "edge_name": "REPORTS_ON",
             "fact": "João cobre regulação de IA", "target_uuid": "ent-004", "source_uuid": "ent-006"},
            {"entity_uuid": "ent-007", "direction": "outgoing", "edge_name": "REGULATES",
             "fact": "Ministério regula o setor", "target_uuid": "ent-004", "source_uuid": "ent-007"},
        ]

        conn = self._ensure_db()
        for n in demo_nodes:
            conn.execute(
                "INSERT OR IGNORE INTO entities (uuid, name, labels, summary, attributes, entity_type) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (n["uuid"], n["name"], json.dumps(n["labels"]), n["summary"],
                 json.dumps(n["attributes"]), n["labels"][-1]),
            )
        for e in demo_edges:
            conn.execute(
                "INSERT OR IGNORE INTO entity_edges (entity_uuid, direction, edge_name, fact, target_uuid, source_uuid) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (e["entity_uuid"], e["direction"], e["edge_name"], e["fact"],
                 e.get("target_uuid"), e.get("source_uuid")),
            )
        conn.commit()
        conn.close()
        return demo_nodes


# ─── EntityReader ─────────────────────────────────────────────────
class EntityReader:
    """Leitura e filtragem de entidades em grafos de conhecimento"""

    def __init__(self, storage):
        self.storage = storage

    def filter_defined_entities(
        self,
        graph_id: str,
        defined_entity_types: Optional[List[str]] = None,
        enrich_with_edges: bool = True,
    ) -> FilteredEntities:
        """Filtra nós com tipos significativos"""
        all_nodes = self.storage.get_all_nodes(graph_id)
        total_count = len(all_nodes)
        all_edges = self.storage.get_all_edges(graph_id) if enrich_with_edges else []
        node_map = {n["uuid"]: n for n in all_nodes}

        filtered = []
        types_found: Set[str] = set()

        for node in all_nodes:
            labels = node.get("labels", [])
            custom_labels = [la for la in labels if la not in ("Entity", "Node")]

            if not custom_labels:
                continue

            if defined_entity_types:
                matching = [la for la in custom_labels if la in defined_entity_types]
                if not matching:
                    continue
                entity_type = matching[0]
            else:
                entity_type = custom_labels[0]

            types_found.add(entity_type)

            entity = EntityNode(
                uuid=node["uuid"],
                name=node["name"],
                labels=labels,
                summary=node.get("summary", ""),
                attributes=node.get("attributes", {}),
            )

            if enrich_with_edges:
                related_edges = []
                related_uuids: Set[str] = set()
                for edge in all_edges:
                    if edge.get("source_node_uuid") == node["uuid"]:
                        related_edges.append({
                            "direction": "outgoing",
                            "edge_name": edge["name"],
                            "fact": edge.get("fact", ""),
                            "target_node_uuid": edge["target_node_uuid"],
                        })
                        related_uuids.add(edge["target_node_uuid"])
                    elif edge.get("target_node_uuid") == node["uuid"]:
                        related_edges.append({
                            "direction": "incoming",
                            "edge_name": edge["name"],
                            "fact": edge.get("fact", ""),
                            "source_node_uuid": edge["source_node_uuid"],
                        })
                        related_uuids.add(edge["source_node_uuid"])

                entity.related_edges = related_edges
                entity.related_nodes = [
                    {
                        "uuid": node_map[ru]["uuid"],
                        "name": node_map[ru]["name"],
                        "labels": node_map[ru].get("labels", []),
                        "summary": node_map[ru].get("summary", ""),
                    }
                    for ru in related_uuids if ru in node_map
                ]

            filtered.append(entity)

        return FilteredEntities(
            entities=filtered,
            entity_types=types_found,
            total_count=total_count,
            filtered_count=len(filtered),
        )

    def get_entity_with_context(self, graph_id: str, entity_uuid: str) -> Optional[EntityNode]:
        """Entidade única com contexto completo"""
        node = self.storage.get_node(entity_uuid)
        if not node:
            return None

        edges = self.storage.get_node_edges(entity_uuid)
        related_edges = []
        related_uuids: Set[str] = set()

        for edge in edges:
            if edge.get("source_node_uuid") == entity_uuid:
                related_edges.append({
                    "direction": "outgoing",
                    "edge_name": edge["name"],
                    "fact": edge.get("fact", ""),
                    "target_node_uuid": edge["target_node_uuid"],
                })
                related_uuids.add(edge["target_node_uuid"])
            else:
                related_edges.append({
                    "direction": "incoming",
                    "edge_name": edge["name"],
                    "fact": edge.get("fact", ""),
                    "source_node_uuid": edge["source_node_uuid"],
                })
                related_uuids.add(edge["source_node_uuid"])

        related_nodes = []
        for ru in related_uuids:
            rn = self.storage.get_node(ru)
            if rn:
                related_nodes.append({
                    "uuid": rn["uuid"],
                    "name": rn["name"],
                    "labels": rn.get("labels", []),
                    "summary": rn.get("summary", ""),
                })

        return EntityNode(
            uuid=node["uuid"],
            name=node["name"],
            labels=node.get("labels", []),
            summary=node.get("summary", ""),
            attributes=node.get("attributes", {}),
            related_edges=related_edges,
            related_nodes=related_nodes,
        )

    def get_entities_by_type(
        self, graph_id: str, entity_type: str, enrich_with_edges: bool = True
    ) -> List[EntityNode]:
        """Todas as entidades de um tipo específico"""
        result = self.filter_defined_entities(
            graph_id=graph_id,
            defined_entity_types=[entity_type],
            enrich_with_edges=enrich_with_edges,
        )
        return result.entities


# ─── CLI ──────────────────────────────────────────────────────────
def cmd_list(args):
    reader = EntityReader(MockGraphStorage())
    result = reader.filter_defined_entities(args.graph, enrich_with_edges=True)
    data = result.to_dict()
    print(f"\n📋 Entidades encontradas: {data['filtered_count']}/{data['total_count']}")
    print(f"   Tipos: {', '.join(sorted(data['entity_types']))}\n")
    for e in data["entities"]:
        print(f"  [{e['labels'][-1]}] {e['name']} ({e['uuid']})")
        print(f"       Summary: {e['summary'][:80]}")
        if e["related_edges"]:
            for edge in e["related_edges"][:3]:
                print(f"       → {edge['direction']} {edge['edge_name']}")
        print()
    return data


def cmd_filter(args):
    reader = EntityReader(MockGraphStorage())
    entities = reader.get_entities_by_type(args.graph, args.type)
    print(f"\n📋 Entidades do tipo '{args.type}': {len(entities)}\n")
    for e in entities:
        print(f"  {e.name} ({e.uuid})")
        print(f"    Summary: {e.summary[:100]}")
        if e.related_edges:
            print(f"    Arestas: {len(e.related_edges)}")
        print()
    return [e.to_dict() for e in entities]


def cmd_context(args):
    reader = EntityReader(MockGraphStorage())
    entity = reader.get_entity_with_context(args.graph, args.uuid)
    if not entity:
        print(f"\n❌ Entidade {args.uuid} não encontrada")
        return None

    data = entity.to_dict()
    print(f"\n📋 Entidade: {data['name']}")
    print(f"   Tipo: {data['labels'][-1]}")
    print(f"   Summary: {data['summary'][:200]}")
    print(f"   Arestas ({len(data['related_edges'])}):")
    for edge in data["related_edges"]:
        print(f"     [{edge['direction']}] {edge['edge_name']}: {edge.get('fact', '')[:80]}")
    print(f"   Nós relacionados ({len(data['related_nodes'])}):")
    for rn in data["related_nodes"]:
        print(f"     → {rn['name']} ({rn['labels'][-1]})")
    return data


def cmd_stats(args):
    reader = EntityReader(MockGraphStorage())
    result = reader.filter_defined_entities(args.graph)
    data = result.to_dict()
    print(f"\n📊 Estatísticas do Grafo '{args.graph}'")
    print(f"   Total de nós: {data['total_count']}")
    print(f"   Entidades filtradas: {data['filtered_count']}")
    print(f"   Tipos de entidade: {len(data['entity_types'])}")
    for t in sorted(data['entity_types']):
        print(f"     - {t}")
    return data


def main():
    parser = argparse.ArgumentParser(description="Entity NER Reader")
    parser.add_argument("--graph", default="demo", help="Graph ID")
    sub = parser.add_subparsers(dest="mode", required=True)

    sub.add_parser("list").set_defaults(func=cmd_list)
    p_filter = sub.add_parser("filter")
    p_filter.add_argument("--type", required=True)
    p_filter.set_defaults(func=cmd_filter)
    p_ctx = sub.add_parser("context")
    p_ctx.add_argument("--uuid", required=True)
    p_ctx.set_defaults(func=cmd_context)
    p_stats = sub.add_parser("stats")
    p_stats.set_defaults(func=cmd_stats)

    args = parser.parse_args()
    result = args.func(args)
    return result


if __name__ == "__main__":
    main()
