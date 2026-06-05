"""Discovery — busca web e classificação inteligente de editais.

SearchEngine: busca editais em mecanismos de busca (DuckDuckGo, SerpAPI).
EditalClassifier: usa IA para classificar páginas como edital, portal ou outro.
"""

import json
import logging
import re
import httpx

logger = logging.getLogger(__name__)

DUCKDUCKGO_URL = "https://html.duckduckgo.com/html/"


class SearchEngine:
    """Busca editais de fomento usando mecanismos de busca na web.

    Suporta múltiplos backends: duckduckgo (gratuito) e serpapi (pago).
    """

    def __init__(self, backend: str = "duckduckgo", api_key: str = "", google_api_key: str = "", serper_key: str = ""):
        self.backend = backend
        self.api_key = api_key
        self.google_api_key = google_api_key
        self.serper_key = serper_key

    def search(self, query: str, max_results: int = 20) -> list[dict]:
        """Busca editais na web.

        Args:
            query: Termo de busca (ex: "editais fomento tecnologia 2026").
            max_results: Número máximo de resultados.

        Returns:
            Lista de dicts com 'url' e 'title'.
        """
        if self.backend == "duckduckgo":
            return self._search_duckduckgo(query, max_results)
        elif self.backend == "serpapi":
            return self._search_serpapi(query, max_results)
        elif self.backend == "serper":
            return self._search_serper(query, max_results)
        elif self.backend == "gemini":
            return self._search_gemini(query, max_results)
        else:
            raise ValueError(f"Backend desconhecido: {self.backend}")

    def _search_duckduckgo(self, query: str, max_results: int) -> list[dict]:
        """Busca via DuckDuckGo HTML (gratuito, sem API key)."""
        results = []
        try:
            with httpx.Client(timeout=15, headers={"User-Agent": "Mozilla/5.0"}) as client:
                response = client.get(
                    DUCKDUCKGO_URL,
                    params={"q": query},
                )
                response.raise_for_status()
                results = self._parse_duckduckgo_html(response.text)
        except Exception as e:
            logger.error(f"Erro na busca DuckDuckGo: {e}")

        return results[:max_results]

    def _parse_duckduckgo_html(self, html: str) -> list[dict]:
        """Extrai resultados do HTML do DuckDuckGo."""
        from urllib.parse import unquote

        results = []
        # DuckDuckGo usa links redirect: //duckduckgo.com/l/?uddg=URL_ENCODED
        for match in re.finditer(
            r'class="result__a"[^>]*href="([^"]*)"[^>]*>(.*?)</a>',
            html,
            re.DOTALL,
        ):
            raw_url, title_raw = match.groups()
            title = re.sub(r"<[^>]+>", "", title_raw).strip()

            # Decodifica URL do redirect DuckDuckGo
            url = raw_url
            uddg_match = re.search(r'uddg=([^&"]+)', raw_url)
            if uddg_match:
                url = unquote(uddg_match.group(1))

            if url and title and url.startswith("http"):
                results.append({"url": url, "title": title})

        return results

    def _search_serpapi(self, query: str, max_results: int) -> list[dict]:
        """Busca via SerpAPI (requer API key)."""
        if not self.api_key:
            logger.warning("SerpAPI requer api_key")
            return []

        results = []
        try:
            with httpx.Client(timeout=15) as client:
                response = client.get(
                    "https://serpapi.com/search",
                    params={
                        "q": query,
                        "api_key": self.api_key,
                        "engine": "google",
                        "gl": "br",
                        "hl": "pt",
                        "num": min(max_results, 20),
                    },
                )
                response.raise_for_status()
                data = response.json()
                for item in data.get("organic_results", []):
                    results.append({"url": item.get("link", ""), "title": item.get("title", "")})
        except Exception as e:
            logger.error(f"Erro na busca SerpAPI: {e}")

        return results[:max_results]

    def _search_serper(self, query: str, max_results: int) -> list[dict]:
        """Busca via Serper.dev (Google Search API gratuita)."""
        results = []
        try:
            with httpx.Client(timeout=15) as client:
                response = client.post(
                    "https://google.serper.dev/search",
                    json={"q": query, "gl": "br", "hl": "pt", "num": min(max_results, 25)},
                    headers={"X-API-KEY": self.serper_key},
                )
                response.raise_for_status()
                data = response.json()
                for item in data.get("organic", []):
                    results.append({
                        "url": item.get("link", ""),
                        "title": item.get("title", ""),
                        "snippet": item.get("snippet", ""),
                        "date": item.get("date", ""),
                    })
            logger.info(f"Serper retornou {len(results)} resultados para '{query[:40]}'")
        except Exception as e:
            logger.warning(f"Serper falhou: {e}, usando DuckDuckGo fallback")
            return self._search_duckduckgo(query, max_results)

        return results[:max_results]

    def _search_gemini(self, query: str, max_results: int) -> list[dict]:
        """Usa Google Gemini para buscar editais via web."""
        results = []
        try:
            import google.generativeai as genai

            genai.configure(api_key=self.google_api_key)
            model = genai.GenerativeModel(
                "gemini-2.0-flash",
                tools=[{"google_search": {}}],
            )

            prompt = f"""Busque por editais de fomento reais e abertos no Brasil com a query: "{query}".
Retorne APENAS um JSON array com objetos contendo "url" e "title" dos editais encontrados.
Máximo {max_results} resultados. Exemplo:
[{{"url": "https://...", "title": "Edital..."}}]"""

            response = model.generate_content(prompt)
            content = response.text or "[]"

            # Extrai JSON da resposta
            import re as _re
            json_match = _re.search(r"\[[^\]]*\]", content, _re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                for item in data:
                    if isinstance(item, dict) and "url" in item:
                        results.append({"url": item["url"], "title": item.get("title", "")})

            logger.info(f"Gemini search retornou {len(results)} resultados para '{query[:40]}'")

        except Exception as e:
            logger.warning(f"Gemini search falhou: {e}, usando DuckDuckGo fallback")
            return self._search_duckduckgo(query, max_results)

        return results[:max_results]


class EditalClassifier:
    """Classifica páginas web como edital, portal de editais, ou outro conteúdo.

    Usa IA (DeepSeek) para analisar o conteúdo e decidir o tipo.
    """

    def __init__(self, api_key: str = "", google_api_key: str = ""):
        self.api_key = api_key
        self.google_api_key = google_api_key

    def classify(self, html: str) -> dict:
        """Classifica uma página web.

        Args:
            html: Conteúdo HTML da página.

        Returns:
            Dict com 'tipo' (edital/portal_list/outro) e 'confidence' (0-1).
        """
        text = self._extract_text(html)
        if not text.strip():
            return {"tipo": "outro", "confidence": 0.0}

        # Se tiver API key, usa IA (DeepSeek ou Gemini); senão, heurísticas
        if self.google_api_key:
            return self._call_gemini(text)
        if self.api_key:
            return self._call_ai(text)
        return self._classify_heuristic(text)

    def _extract_text(self, html: str) -> str:
        """Extrai texto visível do HTML (versão simplificada)."""
        text = re.sub(r"<script[^>]*>.*?</script>", "", html, flags=re.DOTALL)
        text = re.sub(r"<style[^>]*>.*?</style>", "", text, flags=re.DOTALL)
        text = re.sub(r"<[^>]+>", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text[:3000]  # limita para não gastar tokens

    def _classify_heuristic(self, text: str) -> dict:
        """Classificação por heurísticas (sem IA)."""
        text_lower = text.lower()

        # Palavras-chave de edital
        edital_keywords = [
            "edital", "chamada pública", "chamamento público", "seleção pública",
            "concurso", "fomento", "financiamento", "bolsa", "auxílio",
            "inscrições até", "prazo de inscrição", "edital nº",
        ]
        portal_keywords = [
            "editais abertos", "lista de editais", "central de editais",
            "chamadas públicas", "oportunidades", "calendário de editais",
        ]

        edital_score = sum(1 for kw in edital_keywords if kw in text_lower)
        portal_score = sum(1 for kw in portal_keywords if kw in text_lower)

        if edital_score >= 3:
            confidence = min(0.5 + edital_score * 0.1, 0.95)
            return {"tipo": "edital", "confidence": confidence}
        elif portal_score >= 2:
            confidence = min(0.5 + portal_score * 0.1, 0.95)
            return {"tipo": "portal_list", "confidence": confidence}
        else:
            return {"tipo": "outro", "confidence": 0.3}

    def _call_ai(self, text: str) -> dict:
        """Classifica usando IA (DeepSeek)."""
        from openai import OpenAI

        prompt = f"""Classifique o texto abaixo como um dos tipos:
- edital: página de um edital específico com detalhes (valor, datas, requisitos)
- portal_list: listagem de múltiplos editais
- outro: nenhum dos anteriores

Retorne APENAS um JSON: {{"tipo": "...", "confidence": 0.0}}

Texto:
{text}

JSON:"""

        try:
            client = OpenAI(api_key=self.api_key, base_url="https://api.deepseek.com")
            response = client.chat.completions.create(
                model="deepseek-v4-flash",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=200,
            )
            content = response.choices[0].message.content or "{}"
            json_match = re.search(r"\{[^}]+\}", content)
            if json_match:
                return json.loads(json_match.group())
        except Exception as e:
            logger.warning(f"Erro na classificação IA: {e}")

        return self._classify_heuristic(text)

    def _call_gemini(self, text: str) -> dict:
        """Classifica usando Google Gemini (AI Studio)."""
        try:
            import google.generativeai as genai

            prompt = f"""Classifique o texto como: edital, portal_list, ou outro.
- edital: página de UM edital com detalhes (valor, datas, requisitos)
- portal_list: listagem de MÚLTIPLOS editais
- outro: nenhum dos anteriores

Retorne APENAS: {{"tipo": "...", "confidence": 0.0}}

Texto: {text}"""

            genai.configure(api_key=self.google_api_key)
            model = genai.GenerativeModel("gemini-2.0-flash")
            response = model.generate_content(prompt)
            content = response.text or "{}"
            json_match = re.search(r"\{[^}]+\}", content)
            if json_match:
                return json.loads(json_match.group())
        except Exception as e:
            logger.warning(f"Erro na classificação Gemini: {e}")

        return self._classify_heuristic(text)
