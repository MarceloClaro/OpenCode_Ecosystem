#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SciHubBridge v1.0 — Download e Verificacao de Artigos Cientificos
==================================================================
Integra multiplas fontes para download e verificacao de artigos:
  1. Sci-Hub (via scihub MCP + seeker_scihub_enhanced.py)
  2. arXiv API (via arxiv package)
  3. Semantic Scholar API (via semanticscholar package)
  4. Google Scholar (via scholarly package)
  5. Crossref API (via crossrefapi package)
  6. PubMed/NCBI (via pymed + biopython)
  7. Sci-Hub CN (via scihub-cn, opcional)

Integra-se com AcademicAuditTrail para verificacao de DOIs.

Uso:
  from scihub_bridge import SciHubBridge
  bridge = SciHubBridge()
  paper = bridge.download_by_doi("10.1038/s41524-017-0032-0")
  verified = bridge.verify_doi("10.1038/s41524-017-0032-0")
"""

from __future__ import annotations

import json
import hashlib
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

BRAZIL_TZ = timezone.utc


@dataclass
class PaperMetadata:
    """Metadados de um artigo cientifico."""
    doi: str = ""
    title: str = ""
    authors: list[str] = field(default_factory=list)
    year: int | None = None
    journal: str = ""
    abstract: str = ""
    citations: int = 0
    source: str = ""  # "scihub", "arxiv", "semanticscholar", "crossref", "pubmed"
    pdf_path: str = ""
    verified: bool = False
    verification_method: str = ""
    hash_sha256: str = ""


class SciHubBridge:
    """Ponte unificada para download e verificacao de artigos.

    Integra Sci-Hub, arXiv, Semantic Scholar, Google Scholar,
    Crossref e PubMed em uma unica interface.
    """

    # Domains Sci-Hub ativos (atualizado 2026)
    SCIHUB_DOMAINS = [
        "https://sci-hub.se",
        "https://sci-hub.st",
        "https://sci-hub.ru",
    ]

    def __init__(self, download_dir: str | Path = ".papers"):
        self.download_dir = Path(download_dir)
        self.download_dir.mkdir(parents=True, exist_ok=True)
        self.available_sources: list[str] = []
        self._discover_sources()

    def _discover_sources(self):
        """Descobre quais fontes estao disponiveis no ambiente."""
        sources = {
            "arxiv": "arxiv",
            "semanticscholar": "semanticscholar",
            "scholarly": "scholarly",
            "crossref": "crossrefapi",
            "pymed": "pymed",
            "biopython": "Bio",
        }
        for name, module in sources.items():
            try:
                __import__(module)
                self.available_sources.append(name)
            except ImportError:
                pass

        # Sci-Hub sempre via MCP (nao requer pacote Python)
        self.available_sources.append("scihub")

    # ═══════════════════════════════════════════════════════════════════
    # DOWNLOAD DE ARTIGOS
    # ═══════════════════════════════════════════════════════════════════

    def download_by_doi(self, doi: str) -> PaperMetadata | None:
        """Baixa artigo por DOI usando Sci-Hub como fonte primaria.

        Args:
            doi: DOI do artigo (ex: "10.1038/s41524-017-0032-0")

        Returns:
            PaperMetadata com caminho do PDF, ou None se falhar
        """
        # 1. Tentar Sci-Hub
        pdf_path = self._download_scihub(doi)
        if pdf_path:
            metadata = self._get_metadata(doi)
            metadata.pdf_path = str(pdf_path)
            metadata.hash_sha256 = self._hash_file(pdf_path)
            return metadata

        # 2. Tentar arXiv (se o DOI for de la)
        if "arxiv" in doi.lower():
            arxiv_id = doi.split("/")[-1]
            return self._download_arxiv(arxiv_id)

        # 3. Tentar Semantic Scholar (sem PDF, apenas metadados)
        if "semanticscholar" in self.available_sources:
            return self._get_metadata_semanticscholar(doi)

        return None

    def _download_scihub(self, doi: str) -> Path | None:
        """Download via Sci-Hub usando o seeker_scihub_enhanced."""
        try:
            import sys
            sys.path.insert(0, str(Path(__file__).parent.parent.parent / "basis-research" / "core"))
            from seeker_scihub_enhanced import SciHubEnhanced

            downloader = SciHubEnhanced()
            result = downloader.download(doi, str(self.download_dir))
            if result and Path(result).exists():
                return Path(result)
        except ImportError:
            pass
        except Exception:
            pass

        # Fallback: tentar download direto via scihub package
        try:
            from scihub import SciHub
            sh = SciHub()
            result = sh.fetch(doi)
            if result and "pdf" in result:
                pdf_path = self.download_dir / f"{doi.replace('/', '_')}.pdf"
                pdf_path.write_bytes(result["pdf"])
                return pdf_path
        except ImportError:
            pass
        except Exception:
            pass

        return None

    def _download_arxiv(self, arxiv_id: str) -> PaperMetadata | None:
        """Download via arXiv API."""
        try:
            import arxiv
            client = arxiv.Client()
            search = arxiv.Search(id_list=[arxiv_id])
            paper = next(client.results(search))

            # Download PDF
            pdf_path = self.download_dir / f"arxiv_{arxiv_id}.pdf"
            paper.download_pdf(dirpath=str(self.download_dir), filename=f"arxiv_{arxiv_id}.pdf")

            return PaperMetadata(
                doi=paper.doi or f"arxiv:{arxiv_id}",
                title=paper.title,
                authors=[str(a) for a in paper.authors],
                year=paper.published.year if paper.published else None,
                abstract=paper.summary,
                source="arxiv",
                pdf_path=str(pdf_path),
                hash_sha256=self._hash_file(pdf_path),
            )
        except ImportError:
            return None
        except Exception:
            return None

    # ═══════════════════════════════════════════════════════════════════
    # METADADOS E VERIFICACAO
    # ═══════════════════════════════════════════════════════════════════

    def _get_metadata(self, doi: str) -> PaperMetadata:
        """Obtem metadados de multiplas fontes."""
        meta = PaperMetadata(doi=doi)

        # Semantic Scholar
        if "semanticscholar" in self.available_sources:
            try:
                from semanticscholar import SemanticScholar
                sch = SemanticScholar(timeout=10)
                paper = sch.get_paper(doi)
                meta.title = paper.title or meta.title
                meta.year = paper.year or meta.year
                meta.citations = getattr(paper, "citationCount", 0)
                meta.abstract = getattr(paper, "abstract", "") or meta.abstract
                meta.source = "semanticscholar"
            except Exception:
                pass

        # Crossref (fallback)
        if not meta.title:
            try:
                meta2 = self._get_metadata_crossref(doi)
                if meta2:
                    meta.title = meta2.title or meta.title
                    meta.authors = meta2.authors or meta.authors
                    meta.journal = meta2.journal or meta.journal
                    meta.source = meta.source or "crossref"
            except Exception:
                pass

        return meta

    def _get_metadata_semanticscholar(self, doi: str) -> PaperMetadata | None:
        """Metadados via Semantic Scholar."""
        try:
            from semanticscholar import SemanticScholar
            sch = SemanticScholar(timeout=10)
            paper = sch.get_paper(doi)
            return PaperMetadata(
                doi=doi,
                title=paper.title or "",
                year=paper.year,
                citations=getattr(paper, "citationCount", 0),
                abstract=getattr(paper, "abstract", "") or "",
                source="semanticscholar",
            )
        except Exception:
            return None

    def _get_metadata_crossref(self, doi: str) -> PaperMetadata | None:
        """Metadados via Crossref API."""
        try:
            from crossref.restful import Works
            works = Works()
            paper = works.doi(doi)
            authors = [
                f"{a.get('given', '')} {a.get('family', '')}"
                for a in paper.get("author", [])
            ]
            return PaperMetadata(
                doi=doi,
                title=paper.get("title", [""])[0] if paper.get("title") else "",
                authors=authors,
                year=paper.get("created", {}).get("date-parts", [[None]])[0][0],
                journal=paper.get("container-title", [""])[0] if paper.get("container-title") else "",
                source="crossref",
            )
        except ImportError:
            return None
        except Exception:
            return None

    # ═══════════════════════════════════════════════════════════════════
    # VERIFICACAO DE DOIs
    # ═══════════════════════════════════════════════════════════════════

    def verify_doi(self, doi: str) -> dict[str, Any]:
        """Verifica se um DOI e valido e acessivel.

        Returns:
            Dict com status, metadados e fontes de verificacao
        """
        result = {
            "doi": doi,
            "valid": False,
            "accessible": False,
            "metadata_available": False,
            "sources_checked": [],
            "errors": [],
        }

        # 1. Crossref (fonte primaria de DOIs)
        try:
            from crossref.restful import Works
            works = Works()
            paper = works.doi(doi)
            if paper:
                result["valid"] = True
                result["metadata_available"] = True
                result["sources_checked"].append("crossref")
        except ImportError:
            result["errors"].append("crossrefapi not installed")
        except Exception as e:
            result["errors"].append(f"crossref error: {str(e)[:80]}")

        # 2. Semantic Scholar
        try:
            from semanticscholar import SemanticScholar
            sch = SemanticScholar(timeout=10)
            paper = sch.get_paper(doi)
            if paper and paper.title:
                result["accessible"] = True
                result["sources_checked"].append("semanticscholar")
        except ImportError:
            pass
        except Exception:
            pass

        # 3. Sci-Hub (verificar se o PDF esta disponivel)
        try:
            # Tenta apenas HEAD request para verificar disponibilidade
            import httpx
            for domain in self.SCIHUB_DOMAINS:
                try:
                    resp = httpx.head(f"{domain}/{doi}", timeout=5, follow_redirects=True)
                    if resp.status_code == 200:
                        result["accessible"] = True
                        result["sources_checked"].append("scihub")
                        break
                except Exception:
                    continue
        except ImportError:
            pass
        except Exception:
            pass

        return result

    def verify_references(self, doi_list: list[str]) -> list[dict[str, Any]]:
        """Verifica uma lista de DOIs em lote.

        Args:
            doi_list: Lista de DOIs para verificar

        Returns:
            Lista de resultados de verificacao
        """
        return [self.verify_doi(doi) for doi in doi_list]

    # ═══════════════════════════════════════════════════════════════════
    # BUSCA DE ARTIGOS
    # ═══════════════════════════════════════════════════════════════════

    def search(self, query: str, max_results: int = 5) -> list[PaperMetadata]:
        """Busca artigos em multiplas fontes.

        Args:
            query: Termo de busca
            max_results: Maximo de resultados por fonte

        Returns:
            Lista de PaperMetadata
        """
        results = []

        # arXiv
        if "arxiv" in self.available_sources:
            try:
                import arxiv
                client = arxiv.Client()
                search = arxiv.Search(query=query, max_results=max_results)
                for paper in client.results(search):
                    results.append(PaperMetadata(
                        doi=getattr(paper, "doi", "") or f"arxiv:{getattr(paper, 'entry_id', '')}",
                        title=paper.title,
                        authors=[str(a) for a in paper.authors],
                        year=paper.published.year if paper.published else None,
                        abstract=paper.summary,
                        source="arxiv",
                    ))
            except Exception:
                pass

        # Semantic Scholar
        if "semanticscholar" in self.available_sources:
            try:
                from semanticscholar import SemanticScholar
                sch = SemanticScholar(timeout=15)
                papers = sch.search_paper(query, limit=max_results)
                for paper in papers:
                    results.append(PaperMetadata(
                        doi=getattr(paper, "externalIds", {}).get("DOI", ""),
                        title=getattr(paper, "title", ""),
                        year=getattr(paper, "year", None),
                        citations=getattr(paper, "citationCount", 0),
                        source="semanticscholar",
                    ))
            except Exception:
                pass

        # Google Scholar
        if "scholarly" in self.available_sources:
            try:
                from scholarly import scholarly
                search = scholarly.search_pubs(query)
                for i, paper in enumerate(search):
                    if i >= max_results:
                        break
                    bib = paper.get("bib", {})
                    results.append(PaperMetadata(
                        title=bib.get("title", ""),
                        year=int(bib.get("pub_year", 0)) if bib.get("pub_year") else None,
                        citations=paper.get("num_citations", 0),
                        source="scholarly",
                    ))
            except Exception:
                pass

        return results

    # ═══════════════════════════════════════════════════════════════════
    # UTILITARIOS
    # ═══════════════════════════════════════════════════════════════════

    def _hash_file(self, filepath: Path) -> str:
        """Calcula hash SHA-256 de um arquivo."""
        if not filepath.exists():
            return ""
        sha = hashlib.sha256()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha.update(chunk)
        return sha.hexdigest()[:16]

    def get_status(self) -> dict[str, Any]:
        """Retorna status das fontes disponiveis."""
        return {
            "available_sources": self.available_sources,
            "total_sources": len(self.available_sources),
            "scihub_domains": self.SCIHUB_DOMAINS,
            "download_dir": str(self.download_dir),
        }


# ── Teste rapido ──
if __name__ == "__main__":
    bridge = SciHubBridge()
    print(f"Fontes disponiveis: {bridge.available_sources}")
    print(f"Total: {len(bridge.available_sources)}")

    # Teste de verificacao
    doi = "10.1038/s41524-017-0032-0"
    print(f"\nVerificando DOI: {doi}")
    result = bridge.verify_doi(doi)
    print(json.dumps(result, indent=2, ensure_ascii=False))
