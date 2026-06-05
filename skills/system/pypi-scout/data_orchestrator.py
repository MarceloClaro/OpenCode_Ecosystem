#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DataOrchestrator v1.0 — Camada Universal de Acesso a Dados
===========================================================
Roteamento inteligente: o pesquisador solicita QUALQUER dado
e o orquestrador descobre a fonte, roteia e entrega.

Arquitetura:
  Query em linguagem natural
       │
       ▼
  QueryIntent (parse keywords → domínio + entidade + métrica)
       │
       ▼
  DataSourceRegistry (auto-discovery do que está instalado)
       │
       ▼
  FallbackChain (tenta fonte primária → secundária → terciária)
       │
       ▼
  DataResult (formato unificado: source, data, metadata, confidence)

Uso:
  orchestrator = DataOrchestrator()
  resultado = orchestrator.query("qual o PIB do Brasil em 2023?")
  resultado = orchestrator.query("preço da ação da Apple")
  resultado = orchestrator.query("artigos sobre machine learning no arXiv")
  resultado = orchestrator.query("top 5 criptomoedas por volume")
  resultado = orchestrator.query("coordenadas de São Paulo")
"""

from __future__ import annotations

import importlib
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

logger = logging.getLogger("DataOrchestrator")

BRAZIL_TZ = timezone.utc

# ─────────────────────────────────────────────────────────────────────
# Protocolo Unificado de Dados
# ─────────────────────────────────────────────────────────────────────


@dataclass
class DataResult:
    """Resultado unificado de qualquer fonte de dados."""

    source: str  # nome do hook/fonte
    domain: str  # geo, finance, crypto, biomed, academic, economic, health
    data: Any  # o dado em si (dict, list, DataFrame, etc.)
    metadata: dict[str, Any] = field(default_factory=dict)
    confidence: float = 1.0  # 0.0-1.0
    alternatives: list[dict[str, Any]] = field(default_factory=list)
    error: str | None = None
    timestamp: str = field(default_factory=lambda: datetime.now(BRAZIL_TZ).isoformat())

    def is_success(self) -> bool:
        return self.error is None and self.data is not None

    def to_dict(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "domain": self.domain,
            "data": self.data if isinstance(self.data, (dict, list, str, int, float, bool, type(None))) else str(self.data)[:500],
            "metadata": self.metadata,
            "confidence": self.confidence,
            "error": self.error,
            "timestamp": self.timestamp,
        }


@dataclass
class QueryIntent:
    """Intenção estruturada extraída da query em linguagem natural."""

    raw_query: str
    domain: str  # geo, finance, crypto, biomed, academic, economic, health, unknown
    entity: str  # país, empresa, ticker, moeda, DOI, cidade, etc.
    metric: str  # PIB, preço, volume, citações, coordenadas, etc.
    timeframe: str = ""  # "2023", "last_5_years", "1mo"
    extra_params: dict[str, Any] = field(default_factory=dict)
    confidence: float = 1.0


# ─────────────────────────────────────────────────────────────────────
# Auto-Discovery de Fontes
# ─────────────────────────────────────────────────────────────────────


class DataSourceRegistry:
    """Registro auto-descobridor de fontes de dados disponíveis."""

    # Mapeamento de domínios → bibliotecas requeridas
    DOMAIN_DEPENDENCIES: dict[str, list[str]] = {
        "finance": ["yfinance", "fredapi", "pandas_market_calendars"],
        "crypto": ["ccxt"],
        "geo": ["geopy", "geopandas", "folium"],
        "biomed": ["Bio", "covid"],
        "health": ["pysus"],
        "academic": ["arxiv", "scholarly", "semanticscholar", "Bio"],
        "economic": ["wbgapi", "fredapi"],
        "pdf": ["pypdf"],
    }

    # Palavras-chave → domínio (para parsing de intenção)
    KEYWORD_MAP: dict[str, str] = {
        # Geo
        "coordenada": "geo", "latitude": "geo", "longitude": "geo",
        "mapa": "geo", "geocode": "geo", "endereço": "geo", "endereco": "geo",
        "cidade": "geo", "estado": "geo", "país": "geo", "pais": "geo",
        "geográfico": "geo", "geografico": "geo",
        # Finance
        "ação": "finance", "acao": "finance", "stock": "finance",
        "ações": "finance", "acoes": "finance", "bolsa": "finance",
        "ibovespa": "finance", "bovespa": "finance", "nyse": "finance",
        "nasdaq": "finance", "preço": "finance", "preco": "finance",
        "dividendo": "finance", "market cap": "finance",
        "ticker": "finance", "yahoo": "finance",
        # Crypto
        "cripto": "crypto", "bitcoin": "crypto", "ethereum": "crypto",
        "btc": "crypto", "eth": "crypto", "exchange": "crypto",
        "binance": "crypto", "criptomoeda": "crypto",
        # Econômico
        "pib": "economic", "gdp": "economic", "inflação": "economic",
        "inflacao": "economic", "desemprego": "economic",
        "banco mundial": "economic", "world bank": "economic",
        "fred": "economic", "wdi": "economic", "indicador": "economic",
        # Acadêmico
        "artigo": "academic", "paper": "academic", "arxiv": "academic",
        "pubmed": "academic", "scholar": "academic", "doi": "academic",
        "citação": "academic", "citacao": "academic", "publicação": "academic",
        "publicacao": "academic", "pesquisa": "academic",
        # Saúde
        "saúde": "health", "saude": "health", "datasus": "health",
        "covid": "health", "hospital": "health", "sus": "health",
        "epidemiológico": "health", "epidemiologico": "health",
        # PDF
        "pdf": "pdf", "extrair texto": "pdf",
    }

    @classmethod
    def check_available(cls) -> dict[str, bool]:
        """Verifica quais domínios têm bibliotecas instaladas."""
        available: dict[str, bool] = {}
        for domain, libs in cls.DOMAIN_DEPENDENCIES.items():
            available[domain] = False
            for lib in libs:
                try:
                    importlib.import_module(lib)
                    available[domain] = True
                    break
                except ImportError:
                    continue
        return available

    @classmethod
    def get_available_domains(cls) -> list[str]:
        """Lista domínios com dados disponíveis."""
        return [d for d, ok in cls.check_available().items() if ok]

    @classmethod
    def parse_intent(cls, query: str) -> QueryIntent:
        """Extrai intenção de uma query em linguagem natural."""
        qlower = query.lower().strip()
        matched_domains: dict[str, int] = {}

        for keyword, domain in cls.KEYWORD_MAP.items():
            if keyword in qlower:
                matched_domains[domain] = matched_domains.get(domain, 0) + 1

        if not matched_domains:
            # Fallback: tenta detectar entidades conhecidas
            if any(t in qlower for t in ["r$", "us$", "eur", "brl", ".sa"]):
                matched_domains["finance"] = 1
            elif any(c in qlower for c in ["bitcoin", "btc", "eth", "usdt", "crypto"]):
                matched_domains["crypto"] = 1
            else:
                return QueryIntent(
                    raw_query=query, domain="unknown", entity=query[:50], metric="",
                    confidence=0.3,
                )

        # Domínio com mais matches
        domain = max(matched_domains, key=lambda k: matched_domains[k])
        confidence = min(matched_domains[domain] / 3, 1.0)

        # Extrair entidade (palavras após preposições ou artigos)
        entity = cls._extract_entity(query)

        # Extrair métrica
        metric = cls._extract_metric(query, domain)

        return QueryIntent(
            raw_query=query, domain=domain, entity=entity, metric=metric,
            confidence=confidence,
        )

    @staticmethod
    def _extract_entity(query: str) -> str:
        """Extrai entidade principal da query."""
        # Remove palavras comuns de query
        stopwords = ["qual", "o", "a", "os", "as", "do", "da", "de", "no", "na",
                     "para", "me", "mostre", "quero", "buscar", "obter", "dados",
                     "informação", "informacao", "sobre", "?", "!", ".", ","]
        words = query.lower().split()
        filtered = [w for w in words if w not in stopwords]
        # Junta palavras restantes como entidade
        if filtered:
            # Pega até 5 palavras após keywords de domínio
            domain_keywords = ["pib", "gdp", "ação", "acao", "stock", "artigo",
                              "paper", "covid", "bitcoin", "ethereum"]
            for i, w in enumerate(filtered):
                if w in domain_keywords:
                    return " ".join(filtered[i+1:i+5]) or " ".join(filtered[:4])
            return " ".join(filtered[:5])
        return query[:80]


    @staticmethod
    def _extract_metric(query: str, domain: str) -> str:
        """Extrai métrica baseada no domínio."""
        metric_map = {
            "finance": "price",
            "crypto": "ticker",
            "geo": "coordinates",
            "academic": "search",
            "economic": "indicator",
            "health": "statistics",
            "biomed": "search",
            "pdf": "extract",
        }
        qlower = query.lower()
        # Override por palavras específicas
        if any(w in qlower for w in ["pib", "gdp"]): return "GDP"
        if any(w in qlower for w in ["inflação", "inflacao"]): return "inflation"
        if any(w in qlower for w in ["preço", "preco", "cotação", "cotacao"]): return "price"
        if any(w in qlower for w in ["volume"]): return "volume"
        if any(w in qlower for w in ["citação", "citacao"]): return "citations"
        if any(w in qlower for w in ["coordenada", "latitude"]): return "coordinates"
        return metric_map.get(domain, "")


# ─────────────────────────────────────────────────────────────────────
# DataOrchestrator
# ─────────────────────────────────────────────────────────────────────


class DataOrchestrator:
    """Orquestrador universal de dados.
    
    Recebe queries em linguagem natural e roteia para a fonte correta,
    com fallback automático e merge de múltiplas fontes.
    
    Uso:
        orch = DataOrchestrator()
        result = orch.query("PIB do Brasil 2023")
        result = orch.query("preço da ação AAPL")
        result = orch.query("top criptomoedas")
        result = orch.query("artigos sobre IA no arXiv")
    """

    def __init__(self) -> None:
        self.registry = DataSourceRegistry()
        self.available = self.registry.check_available()
        self._init_hooks()

    def _init_hooks(self) -> None:
        """Inicializa hooks disponíveis."""
        self.hooks: dict[str, Any] = {}

        # Tenta importar hooks do ecossistema
        try:
            from ecosystem_hooks import (
                GeoAnalyzer, FinanceAnalyzer, MarketSpeculator,
                BioMedAnalyzer, WorldBankAnalyzer, SeekerMultiSource,
                QualisDatasetHub, PDFProcessor,
            )
            if self.available.get("geo"):
                self.hooks["geo"] = GeoAnalyzer()
            if self.available.get("finance"):
                self.hooks["finance"] = FinanceAnalyzer()
            if self.available.get("crypto"):
                self.hooks["crypto"] = MarketSpeculator()
            if self.available.get("biomed"):
                self.hooks["biomed"] = BioMedAnalyzer()
            if self.available.get("economic"):
                self.hooks["economic"] = WorldBankAnalyzer()
            if self.available.get("academic"):
                self.hooks["academic"] = SeekerMultiSource()
            self.hooks["qualis"] = QualisDatasetHub()
            if self.available.get("pdf"):
                self.hooks["pdf"] = PDFProcessor()
        except ImportError:
            logger.warning("ecosystem_hooks not available")

    def query(self, prompt: str, **kwargs: Any) -> DataResult:
        """Roteia query em linguagem natural para a fonte correta.
        
        Args:
            prompt: Query em linguagem natural
            **kwargs: Parâmetros extras (timeframe, limit, etc.)
        
        Returns:
            DataResult com dados, metadados e confiança
        """
        intent = self.registry.parse_intent(prompt)

        # Roteamento por domínio
        router: dict[str, Callable[..., DataResult]] = {
            "geo": self._handle_geo,
            "finance": self._handle_finance,
            "crypto": self._handle_crypto,
            "economic": self._handle_economic,
            "academic": self._handle_academic,
            "biomed": self._handle_biomed,
            "health": self._handle_health,
            "pdf": self._handle_pdf,
        }

        handler = router.get(intent.domain, self._handle_unknown)
        result = handler(intent, **kwargs)

        # Se falhou, tenta fallback para outro domínio
        if not result.is_success() and intent.domain != "unknown":
            logger.info(f"Fallback para domínio alternativo (was: {intent.domain})")
            result = self._handle_unknown(intent, **kwargs)

        return result

    def list_sources(self) -> dict[str, Any]:
        """Lista todas as fontes de dados disponíveis."""
        return {
            "available_domains": self.registry.get_available_domains(),
            "all_domains": list(self.registry.DOMAIN_DEPENDENCIES.keys()),
            "hooks_loaded": list(self.hooks.keys()),
            "total_sources": len(self.hooks),
        }

    def search_all(self, query: str, **kwargs: Any) -> list[DataResult]:
        """Busca em TODAS as fontes disponíveis simultaneamente."""
        results: list[DataResult] = []
        intent = self.registry.parse_intent(query)
        primary_domain = intent.domain

        for domain in self.registry.get_available_domains():
            # Pula finanças para queries claramente não financeiras
            if domain == "finance" and primary_domain not in ("finance", "unknown"):
                continue
            if domain == "crypto" and primary_domain not in ("crypto", "unknown"):
                continue
            try:
                intent2 = QueryIntent(
                    raw_query=query, domain=domain,
                    entity=intent.entity, metric=intent.metric,
                )
                handler = {
                    "geo": self._handle_geo, "finance": self._handle_finance,
                    "crypto": self._handle_crypto, "economic": self._handle_economic,
                    "academic": self._handle_academic, "biomed": self._handle_biomed,
                    "health": self._handle_health, "pdf": self._handle_pdf,
                }.get(domain)
                if handler:
                    result = handler(intent2, **kwargs)
                    if result.is_success():
                        results.append(result)
            except Exception as e:
                logger.warning(f"search_all [{domain}]: {e}")
        return results

    # ── Handlers por domínio ──────────────────────────────────────────

    def _handle_geo(self, intent: QueryIntent, **kw: Any) -> DataResult:
        hook = self.hooks.get("geo")
        if not hook:
            return DataResult(source="geo", domain="geo", data=None, error="GeoAnalyzer not loaded")
        try:
            loc = hook.geocode(intent.entity)
            if loc:
                return DataResult(
                    source="GeoAnalyzer", domain="geo", data=loc,
                    metadata={"entity": intent.entity, "method": "geocode"},
                )
            return DataResult(source="GeoAnalyzer", domain="geo", data=None,
                            error=f"Não encontrado: {intent.entity}")
        except Exception as e:
            return DataResult(source="GeoAnalyzer", domain="geo", data=None, error=str(e)[:200])

    def _handle_finance(self, intent: QueryIntent, **kw: Any) -> DataResult:
        hook = self.hooks.get("finance")
        if not hook:
            return DataResult(source="finance", domain="finance", data=None, error="FinanceAnalyzer not loaded")
        try:
            ticker = intent.entity.upper().replace(" ", "")
            if ".SA" not in ticker and any(w in intent.entity.lower() for w in ["petrobras", "brasil", "vale"]):
                # Mapeamento de nomes brasileiros comuns
                br_map = {"PETROBRAS": "PETR4.SA", "VALE": "VALE3.SA", "ITAU": "ITUB4.SA",
                         "BRADESCO": "BBDC4.SA", "AMBEV": "ABEV3.SA", "WEG": "WEGE3.SA"}
                ticker = br_map.get(ticker, ticker)
            data = hook.get_stock_data(ticker, period=kw.get("period", "1mo"))
            if "error" in data:
                return DataResult(source="FinanceAnalyzer", domain="finance", data=None, error=data["error"])
            return DataResult(
                source="FinanceAnalyzer", domain="finance", data=data,
                metadata={"ticker": ticker, "period": kw.get("period", "1mo")},
            )
        except Exception as e:
            return DataResult(source="FinanceAnalyzer", domain="finance", data=None, error=str(e)[:200])

    def _handle_crypto(self, intent: QueryIntent, **kw: Any) -> DataResult:
        hook = self.hooks.get("crypto")
        if not hook:
            return DataResult(source="crypto", domain="crypto", data=None, error="MarketSpeculator not loaded")
        try:
            if "top" in intent.raw_query.lower() or not intent.entity:
                data = hook.get_top_crypto(kw.get("n", 5))
            else:
                symbol = intent.entity.upper()
                if "/" not in symbol:
                    symbol = f"{symbol}/USDT"
                data = hook.get_ticker("binance", symbol)
            return DataResult(source="MarketSpeculator", domain="crypto", data=data)
        except Exception as e:
            return DataResult(source="MarketSpeculator", domain="crypto", data=None, error=str(e)[:200])

    def _handle_economic(self, intent: QueryIntent, **kw: Any) -> DataResult:
        hook = self.hooks.get("economic")
        if not hook:
            return DataResult(source="economic", domain="economic", data=None, error="WorldBankAnalyzer not loaded")
        try:
            # Tenta detectar indicador
            indicator_map = {
                "pib": "NY.GDP.PCAP.CD", "gdp": "NY.GDP.PCAP.CD",
                "inflação": "FP.CPI.TOTL.ZG", "inflacao": "FP.CPI.TOTL.ZG",
                "desemprego": "SL.UEM.TOTL.ZS", "população": "SP.POP.TOTL",
                "populacao": "SP.POP.TOTL",
            }
            code: str = "NY.GDP.PCAP.CD"  # default
            for kw, ind in indicator_map.items():
                if kw in intent.raw_query.lower():
                    code = ind
                    break
            data_raw: Any = hook.get_indicator_data(code, "BRA")
            return DataResult(source="WorldBankAnalyzer", domain="economic", data=data_raw,
                            metadata={"indicator": code})
        except Exception as e:
            return DataResult(source="WorldBankAnalyzer", domain="economic", data=None, error=str(e)[:200])

    def _handle_academic(self, intent: QueryIntent, **kw: Any) -> DataResult:
        hook = self.hooks.get("academic")
        if not hook:
            return DataResult(source="academic", domain="academic", data=None, error="SeekerMultiSource not loaded")
        try:
            papers = hook.search_arxiv(intent.entity, max_results=kw.get("limit", 5))
            if not papers:
                papers = hook.search_scholarly(intent.entity, max_results=kw.get("limit", 3))
            data = [{"title": p.title, "year": p.year, "citations": p.citations} for p in papers]
            return DataResult(source="SeekerMultiSource", domain="academic", data=data,
                            metadata={"query": intent.entity, "count": len(data)})
        except Exception as e:
            return DataResult(source="SeekerMultiSource", domain="academic", data=None, error=str(e)[:200])

    def _handle_biomed(self, intent: QueryIntent, **kw: Any) -> DataResult:
        hook = self.hooks.get("biomed")
        if not hook:
            return DataResult(source="biomed", domain="biomed", data=None, error="BioMedAnalyzer not loaded")
        try:
            papers = hook.search_pubmed(intent.entity, max_results=kw.get("limit", 3))
            return DataResult(source="BioMedAnalyzer", domain="biomed", data=papers,
                            metadata={"query": intent.entity, "count": len(papers)})
        except Exception as e:
            return DataResult(source="BioMedAnalyzer", domain="biomed", data=None, error=str(e)[:200])

    def _handle_health(self, intent: QueryIntent, **kw: Any) -> DataResult:
        hook = self.hooks.get("biomed")
        if not hook:
            return DataResult(source="health", domain="health", data=None, error="BioMedAnalyzer not loaded")
        try:
            if "covid" in intent.raw_query.lower():
                data = hook.get_covid_stats()
            else:
                data = hook.get_datasus_data(kw.get("dataset", "sinan"))
            return DataResult(source="BioMedAnalyzer", domain="health", data=data)
        except Exception as e:
            return DataResult(source="BioMedAnalyzer", domain="health", data=None, error=str(e)[:200])

    def _handle_pdf(self, intent: QueryIntent, **kw: Any) -> DataResult:
        hook = self.hooks.get("pdf")
        if not hook:
            return DataResult(source="pdf", domain="pdf", data=None, error="PDFProcessor not loaded")
        try:
            path = Path(intent.entity)
            if path.exists():
                text = hook.extract_text(path)
                meta = hook.get_metadata(path)
                return DataResult(source="PDFProcessor", domain="pdf",
                                data={"text_preview": text[:500], "metadata": meta})
            return DataResult(source="PDFProcessor", domain="pdf", data=None, error=f"File not found: {path}")
        except Exception as e:
            return DataResult(source="PDFProcessor", domain="pdf", data=None, error=str(e)[:200])

    def _handle_unknown(self, intent: QueryIntent, **kw: Any) -> DataResult:
        """Fallback: tenta todas as fontes disponíveis."""
        results = self.search_all(intent.raw_query, **kw)
        if results:
            return DataResult(
                source="multi", domain="unknown",
                data=[r.to_dict() for r in results],
                metadata={"sources_used": len(results)},
            )
        return DataResult(
            source="unknown", domain="unknown", data=None,
            error=f"Nenhuma fonte disponível para: {intent.raw_query}",
            alternatives=[{"available_domains": self.registry.get_available_domains()}],
        )


# ── CLI ────────────────────────────────────────────────────────────────


def main() -> None:
    """CLI interativa para consultas de dados."""
    import sys

    orch = DataOrchestrator()
    sources = orch.list_sources()
    print("=" * 60)
    print("DataOrchestrator — Acesso Universal a Dados")
    print("=" * 60)
    print(f"Dominios disponiveis: {sources['available_domains']}")
    print(f"Hooks carregados: {sources['hooks_loaded']}")
    print(f"Total fontes: {sources['total_sources']}")
    print()

    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        print(f"Query: {query}")
        result = orch.query(query)
        print(f"Dominio: {result.domain} | Fonte: {result.source} | Confianca: {result.confidence:.0%}")
        if result.is_success():
            print(f"Dados: {json.dumps(result.to_dict()['data'], indent=2, ensure_ascii=False)[:500]}")
        else:
            print(f"Erro: {result.error}")
    else:
        print("Modo interativo. Digite 'sources' para listar fontes, 'exit' para sair.")
        print("Exemplos:")
        print("  > PIB do Brasil 2023")
        print("  > preco da acao AAPL")
        print("  > top criptomoedas")
        print("  > artigos sobre machine learning")
        print("  > coordenadas de Sao Paulo")
        print()

        while True:
            try:
                q = input("> ").strip()
                if not q:
                    continue
                if q.lower() in ("exit", "quit", "sair"):
                    break
                if q.lower() == "sources":
                    print(json.dumps(sources, indent=2, ensure_ascii=False))
                    continue

                result = orch.query(q)
                print(f"  [{result.domain}] {result.source} (confianca: {result.confidence:.0%})")
                if result.is_success():
                    data = result.to_dict()["data"]
                    if isinstance(data, list):
                        for i, item in enumerate(data[:5]):
                            if isinstance(item, dict):
                                print(f"    {i+1}. {item.get('title', item.get('symbol', str(item)[:60]))}")
                            else:
                                print(f"    {i+1}. {str(item)[:80]}")
                    elif isinstance(data, dict):
                        for k, v in list(data.items())[:5]:
                            print(f"    {k}: {str(v)[:60]}")
                    else:
                        print(f"    {str(data)[:200]}")
                else:
                    print(f"  Erro: {result.error}")
                print()
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"  Erro: {e}")


if __name__ == "__main__":
    main()
