#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SEEKER Hook Bridge — Integração ecosystem_hooks.py ↔ SEEKER Pipeline
=====================================================================
Conecta os hooks do PyPI Scout ao pipeline SEEKER existente.
Permite que o Grounder e o Social usem busca multi-fonte real
(arXiv + Semantic Scholar + Google Scholar) como fonte primária.

Uso:
  from seeker_hook_bridge import enrich_seeker_search
  papers = enrich_seeker_search("machine learning Brazil", max_results=10)
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import Any

# ── Localizar hooks ────────────────────────────────────────────────────
HOOKS_DIR = Path(__file__).resolve().parent.parent / "skills" / "system" / "pypi-scout"
sys.path.insert(0, str(HOOKS_DIR))

from ecosystem_hooks import (
    SeekerMultiSource,
    WorldBankAnalyzer,
    PDFProcessor,
    PaperResult,
)

# ── Constantes de integração ───────────────────────────────────────────
SEEKER_DIR = HOOKS_DIR.parent.parent.parent / "basis-research"
OUTPUT_DIR = HOOKS_DIR.parent.parent.parent / ".evolve" / "seeker-hooks"
BRAZIL_TZ = timezone.utc  # UTC-3 na prática


# ─────────────────────────────────────────────────────────────────────
# Bridge 1: Enriquecer busca do SEEKER com multi-fonte
# ─────────────────────────────────────────────────────────────────────


def enrich_seeker_search(
    query: str,
    max_per_source: int = 5,
    save_artifacts: bool = True,
) -> dict[str, Any]:
    """Busca multi-fonte e salva artefatos para o SEEKER.
    
    Substitui a busca manual do Grounder por resultado consolidado
    de arXiv + Semantic Scholar + Google Scholar.
    
    Args:
        query: Termo de busca acadêmica
        max_per_source: Máximo de resultados por fonte
        save_artifacts: Se True, salva JSON para consumo pelo SEEKER
    
    Returns:
        Dict com resultados consolidados e metadados de busca
    """
    results = SeekerMultiSource.search_all(query, max_per_source)

    # Consolidar todos os resultados em lista única, removendo duplicatas por título
    seen_titles: set[str] = set()
    all_papers: list[dict[str, Any]] = []

    for source, papers in results.items():
        for p in papers:
            title_key = p.title.lower().strip()[:100]
            if title_key not in seen_titles:
                seen_titles.add(title_key)
                all_papers.append({
                    "title": p.title,
                    "authors": p.authors,
                    "year": p.year,
                    "doi": p.doi,
                    "citations": p.citations,
                    "source": p.source,
                    "abstract": p.abstract[:500] if p.abstract else "",
                    "url": p.url,
                    "pdf_url": p.pdf_url,
                })

    output = {
        "query": query,
        "timestamp": datetime.now(BRAZIL_TZ).isoformat(),
        "total_sources": len([s for s, p in results.items() if p]),
        "total_papers": len(all_papers),
        "sources_breakdown": {
            s: len(papers) for s, papers in results.items()
        },
        "papers": all_papers,
    }

    if save_artifacts:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        fname = OUTPUT_DIR / f"seeker_search_{ts}.json"
        fname.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8")

        # Também salva em formato compatível com SEEKER (Markdown)
        md_content = _format_as_seeker_markdown(output)
        md_fname = OUTPUT_DIR / f"seeker_search_{ts}.md"
        md_fname.write_text(md_content, encoding="utf-8")

    return output


def _format_as_seeker_markdown(data: dict[str, Any]) -> str:
    """Formata resultados como Markdown compatível com artefatos SEEKER."""
    lines = [
        f"# SEEKER Multi-Source Search: {data['query']}",
        f"",
        f"**Timestamp**: {data['timestamp']}",
        f"**Fontes**: {data['total_sources']} | **Artigos**: {data['total_papers']}",
        f"",
        f"## Fontes Consultadas",
    ]
    for source, count in data["sources_breakdown"].items():
        lines.append(f"- **{source}**: {count} resultados")

    lines.append("")
    lines.append("## Artigos Encontrados")
    lines.append("")

    for i, paper in enumerate(data["papers"], 1):
        lines.append(f"### {i}. {paper['title']}")
        if paper["authors"]:
            authors = ", ".join(paper["authors"][:3])
            if len(paper["authors"]) > 3:
                authors += f" et al."
            lines.append(f"**Autores**: {authors}")
        if paper["year"]:
            lines.append(f"**Ano**: {paper['year']}")
        if paper["doi"]:
            lines.append(f"**DOI**: [{paper['doi']}](https://doi.org/{paper['doi']})")
        if paper["citations"]:
            lines.append(f"**Citações**: {paper['citations']}")
        lines.append(f"**Fonte**: {paper['source']}")
        if paper["abstract"]:
            lines.append(f"")
            lines.append(f"> {paper['abstract'][:300]}...")
        lines.append("")

    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────────
# Bridge 2: Dados do Banco Mundial → PhD Auditor
# ─────────────────────────────────────────────────────────────────────


def get_brazil_indicators_for_audit() -> dict[str, Any]:
    """Obtém indicadores-chave do Brasil para auditoria PhD.
    
    Retorna dados prontos para inclusão em artigos MASWOS
    com contexto estatístico e fontes rastreáveis.
    """
    indicators = {
        "NY.GDP.PCAP.CD": "PIB per capita (US$ corrente)",
        "NY.GDP.MKTP.KD.ZG": "Crescimento do PIB (% anual)",
        "SE.XPD.TOTL.GD.ZS": "Gasto público em educação (% PIB)",
        "GB.XPD.RSDV.GD.ZS": "Gasto em P&D (% PIB)",
        "IT.NET.USER.ZS": "Indivíduos usando Internet (% população)",
        "SP.POP.TOTL": "População total",
    }

    results = {}
    for code, name in indicators.items():
        data = WorldBankAnalyzer.get_indicator_data(code, "BRA")
        results[code] = {
            "name": name,
            "data": data,
        }

    output = {
        "country": "Brazil (BRA)",
        "timestamp": datetime.now(BRAZIL_TZ).isoformat(),
        "indicators": results,
    }

    return output


# ─────────────────────────────────────────────────────────────────────
# Bridge 3: Extração de PDF → MASWOS
# ─────────────────────────────────────────────────────────────────────


def extract_pdf_for_maswos(pdf_path: str | Path) -> dict[str, Any]:
    """Extrai texto e metadados de PDF para o pipeline MASWOS.
    
    Útil para o estágio de compilação de manuscrito,
    onde artigos fonte precisam ser analisados.
    """
    path = Path(pdf_path)
    if not path.exists():
        return {"error": f"PDF não encontrado: {path}"}

    text = PDFProcessor.extract_text(path)
    meta = PDFProcessor.get_metadata(path)

    return {
        "file": str(path),
        "size_bytes": path.stat().st_size,
        "pages": meta.get("pages", 0),
        "metadata": meta.get("metadata", {}),
        "text_length": len(text),
        "text_preview": text[:1000] if text else "",
    }


# ─────────────────────────────────────────────────────────────────────
# Testes e demonstração
# ─────────────────────────────────────────────────────────────────────


if __name__ == "__main__":
    print("=" * 60)
    print("SEEKER Hook Bridge — Teste de Integração")
    print("=" * 60)

    # Teste 1: Busca multi-fonte
    print("\n🔍 Teste 1: Busca multi-fonte SEEKER")
    result = enrich_seeker_search("artificial intelligence ethics Brazil", max_per_source=2)
    print(f"   Fontes: {result['total_sources']}")
    print(f"   Artigos: {result['total_papers']}")
    for p in result["papers"][:5]:
        print(f"   • {p['title'][:70]}... [{p['source']}]")

    # Teste 2: Indicadores Brasil
    print("\n📊 Teste 2: Indicadores Brasil para PhD Auditor")
    br = get_brazil_indicators_for_audit()
    for code, info in br["indicators"].items():
        print(f"   {code}: {info['name']}")

    print("\n✅ Bridge testado com sucesso!")
