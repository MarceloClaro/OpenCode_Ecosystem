# -*- coding: utf-8 -*-
"""
ROUTER v1.0 — Roteador Inteligente de Queries para Coleções

Dado uma query do usuário, decide em qual(is) coleção(ões) buscar
ANTES de executar a busca FTS5. Isso evita buscar em 3000+ PDFs.

Estratégias de roteamento:
  1. Keyword matching — rápido, baseado em palavras-chave das coleções
  2. Description matching — compara query com descrição das coleções
  3. Historical — prioriza coleções que retornaram bons resultados antes

Uso:
  from pdf_rag.router import QueryRouter
  router = QueryRouter("banco.db")
  results = router.query("prescrição tributária intercorrente", top_k=10)
"""

import re
import time
import logging
from dataclasses import dataclass, field
from typing import Optional

from collections import CollectionManager, SearchResult, Collection

logger = logging.getLogger(__name__)


@dataclass
class RouteDecision:
    """Decisão de roteamento com explicação."""
    collection: str
    confidence: float
    reason: str
    keywords_matched: list = field(default_factory=list)


@dataclass
class QueryResult:
    """Resultado completo de uma query roteada."""
    query: str
    routes: list[RouteDecision]
    results: list[SearchResult]
    total_results: int
    search_time_ms: float
    collections_searched: int


# Mapeamento padrão: coleção → palavras-chave para roteamento
ROUTE_KEYWORDS = {
    "tributario": [
        "tributo", "imposto", "icms", "iss", "irpf", "irpj", "ctn",
        "tributário", "tributária", "fiscal", "fisco", "contribuinte",
        "alíquota", "base de cálculo", "fato gerador", "obrigação tributária",
        "crédito tributário", "lançamento", "prescrição", "decadência",
        "isenção", "imunidade", "taxa", "contribuição", "cofins", "pis",
        "simples nacional", "lucro real", "lucro presumido",
    ],
    "constitucional": [
        "constituição", "constitucional", "stf", "supremo", "emenda",
        "direito fundamental", "mandado de segurança", "habeas corpus",
        "ação direta", "adi", "adpf", "controle de constitucionalidade",
        "cláusula pétrea", "federalismo", "separação de poderes",
    ],
    "civil": [
        "código civil", "contrato", "obrigação", "responsabilidade civil",
        "posse", "propriedade", "família", "sucessão", "herança", "dano moral",
        "indenização", "prescrição civil", "usucapião", "casamento", "divórcio",
    ],
    "penal": [
        "código penal", "crime", "pena", "dosimetria", "tipicidade",
        "antijuridicidade", "culpabilidade", "prisão", "homicídio", "furto",
        "roubo", "estelionato", "tráfico", "lavagem de dinheiro",
    ],
    "processual": [
        "cpc", "processo civil", "recurso", "sentença", "tutela",
        "citação", "intimação", "agravo", "apelação", "embargos",
        "execução", "cumprimento de sentença", "contestação",
    ],
    "trabalhista": [
        "clt", "trabalhista", "empregado", "empregador", "rescisão",
        "férias", "fgts", "justa causa", "aviso prévio", "dissídio",
        "convenção coletiva", "insalubridade", "periculosidade",
    ],
    "administrativo": [
        "administrativo", "licitação", "contrato administrativo",
        "servidor público", "concurso", "improbidade", "ato administrativo",
        "poder de polícia", "serviço público", "concessão",
    ],
    "ambiental": [
        "ambiental", "meio ambiente", "licenciamento", "ibama",
        "desmatamento", "poluição", "sustentabilidade", "eia", "rima",
    ],
    "tecnologia": [
        "software", "lgpd", "dados pessoais", "inteligência artificial",
        "marco civil", "internet", "tecnologia", "digital", "startup",
        "propriedade intelectual", "patente", "direito autoral",
    ],
    "medicina": [
        "médico", "saúde", "diagnóstico", "tratamento", "paciente",
        "farmacêutico", "epidemiologia", "clínico", "sus", "anvisa",
    ],
    "engenharia": [
        "engenharia", "estrutural", "concreto", "cálculo", "nbr",
        "resistência", "materiais", "construção", "projeto",
    ],
}


class QueryRouter:
    """Roteia queries para as coleções mais relevantes antes da busca."""

    def __init__(self, db_path: str = "pdf_collections.db",
                 route_keywords: dict = None):
        self.mgr = CollectionManager(db_path)
        self.route_keywords = route_keywords or ROUTE_KEYWORDS
        self._history: list[dict] = []

    def route(self, query: str, max_collections: int = 3) -> list[RouteDecision]:
        """
        Decide em quais coleções buscar para uma query.

        Retorna lista ordenada por confiança (máximo max_collections).
        """
        query_lower = query.lower()
        query_words = set(re.findall(r'\w+', query_lower))

        # Buscar coleções existentes no banco
        existing = {c.name for c in self.mgr.list_collections()}

        decisions = []
        for collection, keywords in self.route_keywords.items():
            if collection not in existing:
                continue

            matched = []
            for kw in keywords:
                kw_words = set(kw.lower().split())
                # Match exato de frase ou de palavras individuais
                if kw.lower() in query_lower:
                    matched.append(kw)
                elif kw_words & query_words:
                    matched.append(kw)

            if matched:
                confidence = min(len(matched) / max(len(keywords) * 0.3, 1), 1.0)
                decisions.append(RouteDecision(
                    collection=collection,
                    confidence=confidence,
                    reason=f"{len(matched)} keywords matched",
                    keywords_matched=matched[:5]
                ))

        # Se nenhum match, buscar em "geral" ou na maior coleção
        if not decisions:
            cols = self.mgr.list_collections()
            if cols:
                biggest = max(cols, key=lambda c: c.chunk_count)
                decisions.append(RouteDecision(
                    collection=biggest.name,
                    confidence=0.3,
                    reason=f"Fallback para maior coleção ({biggest.chunk_count} chunks)",
                ))

        # Ordenar por confiança e limitar
        decisions.sort(key=lambda d: d.confidence, reverse=True)
        return decisions[:max_collections]

    def query(self, query: str, top_k: int = 10,
              max_collections: int = 2,
              collection: str = None) -> QueryResult:
        """
        Executa query completa: roteamento → busca FTS5 → resultados.

        Args:
            query: Texto da busca
            top_k: Máximo de resultados totais
            max_collections: Máximo de coleções a buscar
            collection: Se especificado, busca só nessa coleção (bypass do router)
        """
        start = time.time()

        # Roteamento
        if collection:
            routes = [RouteDecision(collection=collection, confidence=1.0,
                                    reason="Coleção especificada pelo usuário")]
        else:
            routes = self.route(query, max_collections)

        if not routes:
            return QueryResult(
                query=query, routes=[], results=[],
                total_results=0, search_time_ms=0,
                collections_searched=0
            )

        # Busca FTS5 em cada coleção roteada
        all_results = []
        per_collection = max(top_k // len(routes), 5)

        for route in routes:
            hits = self.mgr.search(route.collection, query, limit=per_collection)
            all_results.extend(hits)

        # Ordenar por relevância (score FTS5)
        all_results.sort(key=lambda r: r.score, reverse=True)
        all_results = all_results[:top_k]

        elapsed = (time.time() - start) * 1000

        # Registrar no histórico
        self._history.append({
            "query": query,
            "routes": [r.collection for r in routes],
            "results_count": len(all_results),
            "time_ms": elapsed,
        })

        return QueryResult(
            query=query,
            routes=routes,
            results=all_results,
            total_results=len(all_results),
            search_time_ms=elapsed,
            collections_searched=len(routes)
        )

    def interactive(self):
        """Modo interativo: digita queries e vê resultados."""
        print("\n" + "="*60)
        print("  PDF RAG — Busca por Coleções")
        print("  Digite sua pergunta (ou 'sair' para encerrar)")
        print("="*60)

        stats = self.mgr.stats()
        print(f"  {stats['collections']} coleções | "
              f"{stats['total_documents']} documentos | "
              f"{stats['total_chunks']} chunks")
        print("="*60 + "\n")

        while True:
            try:
                q = input("Query> ").strip()
            except (EOFError, KeyboardInterrupt):
                break

            if not q or q.lower() in ("sair", "exit", "quit"):
                break

            result = self.query(q)

            # Mostrar roteamento
            print(f"\n  Roteamento ({result.search_time_ms:.0f}ms):")
            for r in result.routes:
                print(f"    → {r.collection} (confiança: {r.confidence:.0%}, "
                      f"{r.reason})")

            # Mostrar resultados
            if result.results:
                print(f"\n  {result.total_results} resultados:\n")
                for i, hit in enumerate(result.results, 1):
                    print(f"  [{i}] {hit.doc_title} (p.{hit.page}) "
                          f"— {hit.collection}")
                    # Mostrar preview do conteúdo
                    preview = hit.content[:200].replace("\n", " ")
                    print(f"      {preview}...")
                    print()
            else:
                print("\n  Nenhum resultado encontrado.\n")

    def stats(self) -> dict:
        """Retorna estatísticas do banco e do roteador."""
        s = self.mgr.stats()
        s["router_queries"] = len(self._history)
        s["available_routes"] = list(self.route_keywords.keys())
        return s

    def close(self):
        self.mgr.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
