#!/usr/bin/env python3
"""
Hybrid Graph Retrieval — 3 Estratégias de Busca em Grafo
Inspirado pelo GraphToolsService do MiroFish-Offline (graph_tools.py).

Estratégias:
  1. InsightForge  — Decomposição profunda de perguntas em sub-perguntas
  2. PanoramaSearch — Varredura ampla com contexto histórico/temporal
  3. QuickSearch    — Busca rápida por palavra-chave/semântica

Modo de uso (CLI):
  python hybrid_search.py insight --query "Sua pergunta"
  python hybrid_search.py panorama --query "Contexto"
  python hybrid_search.py quick --query "busca"

Autor: Reversa Engine (padrão MiroFish-Offline GraphTools)
Licença: MIT
"""

import argparse
import json
import sqlite3
import sys
import re
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional
from pathlib import Path


# ──────────────────────────────────────────────
# Estruturas de Dados (Dataclasses)
# ──────────────────────────────────────────────

@dataclass
class SearchResult:
    """Resultado de busca básico."""
    facts: List[str]
    edges: List[Dict[str, Any]]
    nodes: List[Dict[str, Any]]
    query: str
    total_count: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "facts": self.facts,
            "edges": self.edges,
            "nodes": self.nodes,
            "query": self.query,
            "total_count": self.total_count,
        }

    def to_text(self) -> str:
        lines = [f"## Search Results", f"Query: {self.query}", f"Total: {self.total_count}"]
        if self.facts:
            lines.append("\n### Facts")
            for i, f in enumerate(self.facts[:20], 1):
                lines.append(f"{i}. {f}")
        return "\n".join(lines)


@dataclass
class InsightForgeResult:
    """
    Resultado da análise profunda (InsightForge).
    Inclui sub-perguntas, fatos semânticos, entidades e cadeias de relação.
    """
    query: str
    sub_queries: List[str]
    semantic_facts: List[str] = field(default_factory=list)
    entity_insights: List[Dict[str, Any]] = field(default_factory=list)
    relationship_chains: List[str] = field(default_factory=list)
    total_facts: int = 0
    total_entities: int = 0
    total_relationships: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "query": self.query,
            "sub_queries": self.sub_queries,
            "semantic_facts": self.semantic_facts,
            "entity_insights": self.entity_insights,
            "relationship_chains": self.relationship_chains,
            "total_facts": self.total_facts,
            "total_entities": self.total_entities,
            "total_relationships": self.total_relationships,
        }

    def to_text(self) -> str:
        lines = [
            f"## InsightForge — Deep Analysis",
            f"Query: {self.query}",
            f"Facts: {self.total_facts} | Entities: {self.total_entities} | Relations: {self.total_relationships}",
        ]
        if self.sub_queries:
            lines.append("\n### Sub-Queries")
            for i, sq in enumerate(self.sub_queries, 1):
                lines.append(f"{i}. {sq}")
        if self.semantic_facts:
            lines.append(f"\n### Key Facts")
            for i, f in enumerate(self.semantic_facts[:15], 1):
                lines.append(f'{i}. "{f}"')
        if self.entity_insights:
            lines.append(f"\n### Core Entities")
            for e in self.entity_insights[:10]:
                lines.append(f"- {e.get('name','?')} ({e.get('type','Entity')})")
        if self.relationship_chains:
            lines.append(f"\n### Relationship Chains")
            for c in self.relationship_chains[:10]:
                lines.append(f"- {c}")
        return "\n".join(lines)


@dataclass
class PanoramaResult:
    """
    Resultado da varredura panorâmica (PanoramaSearch).
    Inclui nós, arestas, fatos ativos e históricos.
    """
    query: str
    all_nodes: List[Dict] = field(default_factory=list)
    all_edges: List[Dict] = field(default_factory=list)
    active_facts: List[str] = field(default_factory=list)
    historical_facts: List[str] = field(default_factory=list)
    total_nodes: int = 0
    total_edges: int = 0
    active_count: int = 0
    historical_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "query": self.query,
            "all_nodes": self.all_nodes,
            "all_edges": self.all_edges,
            "active_facts": self.active_facts,
            "historical_facts": self.historical_facts,
            "total_nodes": self.total_nodes,
            "total_edges": self.total_edges,
            "active_count": self.active_count,
            "historical_count": self.historical_count,
        }

    def to_text(self) -> str:
        lines = [
            f"## PanoramaSearch — Panoramic View",
            f"Query: {self.query}",
            f"Nodes: {self.total_nodes} | Edges: {self.total_edges}",
            f"Active Facts: {self.active_count} | Historical: {self.historical_count}",
        ]
        if self.active_facts:
            lines.append("\n### Active Facts")
            for i, f in enumerate(self.active_facts[:20], 1):
                lines.append(f'{i}. "{f}"')
        if self.historical_facts:
            lines.append("\n### Historical/Expired Facts")
            for i, f in enumerate(self.historical_facts[:10], 1):
                lines.append(f'{i}. "{f}"')
        return "\n".join(lines)


# ──────────────────────────────────────────────
# Motor de Busca Híbrida
# ──────────────────────────────────────────────

class HybridRetrievalEngine:
    """
    Motor de busca híbrida que opera sobre um banco SQLite (code-graph.db).
    Oferece 3 estratégias complementares de recuperação de informação.
    """

    def __init__(self, db_path: str = None):
        self.db_path = db_path or str(
            Path.home() / ".config" / "opencode" / "code-graph.db"
        )
        self.conn: Optional[sqlite3.Connection] = None

    # ── Conexão ─────────────────────────────

    def connect(self):
        if self.conn is None:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
        return self.conn

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, *args):
        self.close()

    # ── Helpers ──────────────────────────────

    def _get_graph_tables(self, graph_id: str) -> Optional[Dict[str, str]]:
        """
        Verifica as tabelas disponíveis para um grafo.
        Suporta dois formatos de nomenclatura:
          - <graph_id>_nodes / <graph_id>_edges
          - graph_nodes / graph_edges + filtro por graph_id
        """
        cursor = self.conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        )
        tables = [row["name"] for row in cursor.fetchall()]

        # Formato 1: <graph_id>_nodes, <graph_id>_edges
        node_table = f"{graph_id}_nodes"
        edge_table = f"{graph_id}_edges"
        if node_table in tables and edge_table in tables:
            return {"nodes": node_table, "edges": edge_table}

        # Formato 2: graph_nodes, graph_edges
        if "graph_nodes" in tables and "graph_edges" in tables:
            return {"nodes": "graph_nodes", "edges": "graph_edges"}

        return None

    def _keyword_match_score(self, text: str, query: str) -> int:
        """Score simples por correspondência de keywords."""
        if not text or not query:
            return 0
        text_lower = text.lower()
        query_lower = query.lower()
        score = 0

        if query_lower in text_lower:
            score += 100

        keywords = [
            w.strip() for w in re.split(r'[\s,，]+', query_lower) if len(w.strip()) > 2
        ]
        for kw in keywords:
            count = text_lower.count(kw)
            score += count * 10

        return score

    # ── Estratégia 1: InsightForge ───────────

    def insight_forge(
        self,
        graph_id: str,
        query: str,
        max_sub_queries: int = 5,
    ) -> InsightForgeResult:
        """
        [InsightForge] Análise profunda com decomposição de perguntas.

        Pipeline:
          1. Decompõe a pergunta original em sub-perguntas usando
             dimensões pré-definidas (quem, o que, por que, como, impacto)
          2. Busca cada sub-pergunta no grafo
          3. Extrai entidades e monta cadeias de relacionamento
          4. Integra tudo em um resultado consolidado
        """
        result = InsightForgeResult(query=query, sub_queries=[])

        # Step 1: Gerar sub-perguntas (dimensões fixas + LLM idealmente)
        sub_queries = self._generate_sub_queries(query, max_sub_queries)
        result.sub_queries = sub_queries

        # Step 2: Buscar cada sub-pergunta
        all_facts = set()
        all_edges_data = []
        all_node_uuids = set()

        for sq in sub_queries + [query]:
            sq_result = self._search_graph(graph_id, sq, scope="both", limit=15)
            for f in sq_result.facts:
                all_facts.add(f)
            all_edges_data.extend(sq_result.edges)
            for n in sq_result.nodes:
                uuid = n.get("uuid") or n.get("id", "")
                if uuid:
                    all_node_uuids.add(uuid)

        result.semantic_facts = list(all_facts)
        result.total_facts = len(all_facts)

        # Step 3: Extrair insights de entidades
        entity_insights = []
        for uuid in list(all_node_uuids)[:20]:
            entity_insights.append({
                "uuid": uuid,
                "related_facts": [
                    f for f in all_facts if uuid[:8] in f or any(
                        kw.lower() in f.lower()
                        for kw in re.split(r'\s+', query)
                        if len(kw) > 3
                    )
                ],
            })
        result.entity_insights = entity_insights
        result.total_entities = len(entity_insights)

        # Step 4: Montar cadeias de relacionamento
        chains = set()
        for e in all_edges_data:
            src = e.get("source_node_name", e.get("source_node_uuid", "?")[:8])
            tgt = e.get("target_node_name", e.get("target_node_uuid", "?")[:8])
            name = e.get("name", "related")
            chain = f"{src} --[{name}]--> {tgt}"
            chains.add(chain)
        result.relationship_chains = list(chains)
        result.total_relationships = len(chains)

        return result

    def _generate_sub_queries(self, query: str, max_q: int) -> List[str]:
        """Gera sub-perguntas usando dimensões pré-definidas."""
        # Dimensões analíticas fixas
        dimensions = [
            f"What is the core subject of {query}",
            f"Who are the main participants or stakeholders involved in {query}",
            f"What are the causes or drivers behind {query}",
            f"What are the impacts or consequences of {query}",
            f"How does {query} evolve over time",
        ]
        # Se o usuário tiver LLM, pode-se substituir por chamada real
        return dimensions[:max_q]

    # ── Estratégia 2: PanoramaSearch ─────────

    def panorama_search(
        self,
        graph_id: str,
        query: str,
        include_historical: bool = True,
        limit: int = 50,
    ) -> PanoramaResult:
        """
        [PanoramaSearch] Visão panorâmica completa do grafo.

        Retorna todos os nós e arestas, categorizando fatos como
        ativos (válidos atualmente) ou históricos (expirados/obsoletos).
        """
        result = PanoramaResult(query=query)

        tables = self._get_graph_tables(graph_id)
        if not tables:
            return result

        # Obter todos os nós
        try:
            cursor = self.conn.execute(f"SELECT * FROM {tables['nodes']}")
            rows = cursor.fetchall()
            for row in rows:
                d = dict(row)
                result.all_nodes.append(d)
            result.total_nodes = len(result.all_nodes)
        except Exception:
            pass

        # Obter todas as arestas
        try:
            cursor = self.conn.execute(f"SELECT * FROM {tables['edges']}")
            rows = cursor.fetchall()
            for row in rows:
                d = dict(row)
                result.all_edges.append(d)
                fact = d.get("fact") or d.get("description", "")
                if fact:
                    # Verificar temporal: se tem data de expiração
                    expired = d.get("expired_at") or d.get("invalid_at")
                    if expired:
                        result.historical_facts.append(
                            f"[{d.get('valid_at','?')} - {expired}] {fact}"
                        )
                    else:
                        result.active_facts.append(fact)
            result.total_edges = len(result.all_edges)
        except Exception:
            pass

        # Ordenar por relevância
        result.active_facts.sort(
            key=lambda f: self._keyword_match_score(f, query), reverse=True
        )
        result.historical_facts.sort(
            key=lambda f: self._keyword_match_score(f, query), reverse=True
        )

        result.active_count = len(result.active_facts)
        result.historical_count = len(result.historical_facts)
        result.active_facts = result.active_facts[:limit]
        result.historical_facts = (
            result.historical_facts[:limit] if include_historical else []
        )

        return result

    # ── Estratégia 3: QuickSearch ────────────

    def quick_search(
        self,
        graph_id: str,
        query: str,
        limit: int = 10,
    ) -> SearchResult:
        """
        [QuickSearch] Busca rápida e leve.

        Combina busca semântica (quando há LLM) com busca por
        correspondência de keywords. Limitada a top-K resultados.
        """
        return self._search_graph(graph_id, query, "edges", limit)

    # ── Busca Interna ────────────────────────

    def _search_graph(
        self,
        graph_id: str,
        query: str,
        scope: str = "edges",
        limit: int = 10,
    ) -> SearchResult:
        """
        Busca interna que opera sobre as tabelas SQLite.
        Usa correspondência de keywords (fallback quando não há vetores).
        """
        facts = []
        edges_data = []
        nodes_data = []

        tables = self._get_graph_tables(graph_id)
        if not tables:
            return SearchResult(facts=[], edges=[], nodes=[], query=query, total_count=0)

        # Busca em arestas
        if scope in ("edges", "both"):
            try:
                cursor = self.conn.execute(
                    f"SELECT * FROM {tables['edges']}"
                )
                scored = []
                for row in cursor.fetchall():
                    d = dict(row)
                    text = f"{d.get('fact','')} {d.get('name','')} {d.get('description','')}"
                    score = self._keyword_match_score(text, query)
                    if score > 0:
                        scored.append((score, d))

                scored.sort(key=lambda x: x[0], reverse=True)
                for score, edge in scored[:limit]:
                    fact = edge.get("fact") or edge.get("description", "")
                    if fact:
                        facts.append(fact)
                    edges_data.append(edge)
            except Exception:
                pass

        # Busca em nós
        if scope in ("nodes", "both"):
            try:
                cursor = self.conn.execute(
                    f"SELECT * FROM {tables['nodes']}"
                )
                scored = []
                for row in cursor.fetchall():
                    d = dict(row)
                    text = f"{d.get('name','')} {d.get('summary','')} {d.get('description','')}"
                    score = self._keyword_match_score(text, query)
                    if score > 0:
                        scored.append((score, d))

                scored.sort(key=lambda x: x[0], reverse=True)
                for score, node in scored[:limit]:
                    nodes_data.append(node)
                    summary = node.get("summary") or node.get("description", "")
                    if summary:
                        facts.append(f"[{node.get('name','?')}]: {summary}")
            except Exception:
                pass

        return SearchResult(
            facts=list(dict.fromkeys(facts)),  # dedup mantendo ordem
            edges=edges_data,
            nodes=nodes_data,
            query=query,
            total_count=len(facts),
        )

    # ── Estatísticas ─────────────────────────

    def get_graph_statistics(self, graph_id: str) -> Dict[str, Any]:
        """Retorna estatísticas do grafo."""
        tables = self._get_graph_tables(graph_id)
        if not tables:
            return {"error": f"Graph {graph_id} not found", "graph_id": graph_id}

        stats = {"graph_id": graph_id, "total_nodes": 0, "total_edges": 0}

        try:
            cursor = self.conn.execute(f"SELECT COUNT(*) as c FROM {tables['nodes']}")
            stats["total_nodes"] = cursor.fetchone()["c"]
        except Exception:
            pass

        try:
            cursor = self.conn.execute(f"SELECT COUNT(*) as c FROM {tables['edges']}")
            stats["total_edges"] = cursor.fetchone()["c"]
        except Exception:
            pass

        return stats


# ──────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Hybrid Graph Retrieval — 3 Estratégias de Busca em Grafo"
    )
    parser.add_argument(
        "strategy",
        choices=["insight", "panorama", "quick", "stats"],
        help="Estratégia de busca: insight (profundo), panorama (amplo), quick (rápido), stats",
    )
    parser.add_argument("--graph", default="mirofish_abc", help="Graph ID")
    parser.add_argument("--query", default="", help="Consulta/pesquisa")
    parser.add_argument("--db", default=None, help="Caminho do SQLite DB")
    parser.add_argument("--limit", type=int, default=15, help="Limite de resultados")
    parser.add_argument(
        "--include-historical",
        action="store_true",
        default=True,
        help="Incluir fatos históricos (PanoramaSearch)",
    )
    parser.add_argument("--json", action="store_true", help="Saída em JSON")

    args = parser.parse_args()

    engine = HybridRetrievalEngine(db_path=args.db)

    with engine:
        if args.strategy == "stats":
            result = engine.get_graph_statistics(args.graph)
            print(json.dumps(result, indent=2, ensure_ascii=False))
            return

        if not args.query:
            print("ERRO: --query é obrigatório para insight/panorama/quick")
            sys.exit(1)

        if args.strategy == "insight":
            result = engine.insight_forge(args.graph, args.query)
        elif args.strategy == "panorama":
            result = engine.panorama_search(
                args.graph, args.query, include_historical=args.include_historical, limit=args.limit
            )
        elif args.strategy == "quick":
            result = engine.quick_search(args.graph, args.query, limit=args.limit)
        else:
            print(f"Estratégia desconhecida: {args.strategy}")
            sys.exit(1)

        if args.json:
            print(json.dumps(result.to_dict(), indent=2, ensure_ascii=False))
        else:
            print(result.to_text())


if __name__ == "__main__":
    main()
