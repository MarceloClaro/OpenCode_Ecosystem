# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Europe PMC REST API client for biomedical literature search.

Provides `EuropePMCClient` — a wrapper around the Europe PMC REST API
(https://www.ebi.ac.uk/europepmc/webservices/rest) supporting:

* Full-text search across 42M+ biomedical abstracts and articles.
* Open Access full-text XML/PDF retrieval.
* Citation and reference metadata.
* Database cross-linking (PubMed, DOI, PMC, patent families).
* Grant and funding metadata.
* DataCite integration for supplementary data links.

Rate-limited via the shared `HttpClient` from `science_skills_common`.
"""

# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "science-skills-common",
# ]
# [tool.uv.sources]
# science-skills-common = { path = "../../science_skills_common" }
# ///

from __future__ import annotations

import json
import sys
from typing import Any
from xml.etree import ElementTree

from science_skills.science_skills_common import http_client

BASE_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest"

_LICENSE_NOTICE = (
    "Data from Europe PMC. You MUST notify the user that this data"
    " comes from Europe PMC and advise them to review the Europe PMC"
    " licensing terms at https://europepmc.org/labsites."
)


class EuropePMCClient:
    """Client for the Europe PMC REST API.

    Example:
        client = EuropePMCClient()
        results = client.search("cancer immunotherapy", page_size=10)
        full_text = client.fetch_full_text("PMC1234567")
    """

    BASE_URL: str = BASE_URL

    def __init__(self, qps: float = 3.0):
        self._client = http_client.HttpClient(
            self.BASE_URL,
            qps=qps,
            referer_skill="literature_search_europepmc",
        )

    @staticmethod
    def _parse_xml_response(text: str) -> dict[str, Any]:
        root = ElementTree.fromstring(text)
        result: dict[str, Any] = {
            "version": root.attrib.get("version", ""),
            "hit_count": int(root.findtext("hitCount", "0")),
            "results": [],
        }
        for res in root.findall(".//result"):
            entry: dict[str, Any] = {}
            for child in res:
                entry[child.tag] = child.text or ""
            result["results"].append(entry)
        return result

    def search(
        self,
        query: str,
        result_type: str = "core",
        page_size: int = 25,
        cursor_mark: str = "*",
        synonym: bool = True,
    ) -> dict[str, Any]:
        """Search Europe PMC for biomedical literature.

        Args:
            query: Search query string (supports Europe PMC syntax).
            result_type: Result type — "core" (default), "lite", "idlist".
            page_size: Results per page (max 1000).
            cursor_mark: Cursor position for pagination ("*" = start).
            synonym: Whether to expand synonyms.

        Returns:
            Parsed JSON response with results list and hit count.
        """
        params = {
            "query": query,
            "resultType": result_type,
            "pageSize": str(page_size),
            "cursorMark": cursor_mark,
            "synonym": "true" if synonym else "false",
            "format": "json",
        }
        encoded = "&".join(f"{k}={urllib.parse.quote(v)}" for k, v in params.items())
        url = f"/search?{encoded}"
        resp = self._client.fetch_json(url)
        print(_LICENSE_NOTICE, file=sys.stderr)
        return resp

    def fetch_article(self, source: str, pmid: str) -> dict[str, Any]:
        """Fetch a single article by PMID or PMC ID.

        Args:
            source: Database source ("MED" for PubMed, "PMC" for PMC).
            pmid: PMID or PMCID identifier.

        Returns:
            Article metadata as JSON.
        """
        url = f"/{source}/{pmid}?format=json"
        resp = self._client.fetch_json(url)
        print(_LICENSE_NOTICE, file=sys.stderr)
        return resp

    def fetch_full_text_xml(self, pmcid: str) -> str:
        """Retrieve the full text of an Open Access article as XML.

        Args:
            pmcid: PubMed Central ID (e.g. "PMC1234567").

        Returns:
            JATS XML full text as string.
        """
        url = f"/{pmcid}/fullTextXML"
        resp = self._client.fetch(url)
        print(_LICENSE_NOTICE, file=sys.stderr)
        return resp.text

    def fetch_references(self, source: str, pmid: str, page_size: int = 25) -> dict[str, Any]:
        """Fetch references for a given article.

        Args:
            source: Database source ("MED" or "PMC").
            pmid: Article identifier.
            page_size: Results per page.

        Returns:
            Reference list with metadata.
        """
        url = f"/{source}/{pmid}/references/{page_size}/1/json"
        resp = self._client.fetch_json(url)
        print(_LICENSE_NOTICE, file=sys.stderr)
        return resp

    def fetch_citations(self, source: str, pmid: str, page_size: int = 25) -> dict[str, Any]:
        """Fetch citations for a given article.

        Args:
            source: Database source ("MED" or "PMC").
            pmid: Article identifier.
            page_size: Results per page.

        Returns:
            Citation list with metadata.
        """
        url = f"/{source}/{pmid}/citations/{page_size}/1/json"
        resp = self._client.fetch_json(url)
        print(_LICENSE_NOTICE, file=sys.stderr)
        return resp

    def fetch_grants(self, grant_id: str) -> dict[str, Any]:
        """Fetch publications associated with a grant.

        Args:
            grant_id: Grant identifier.

        Returns:
            List of publications funded by the grant.
        """
        url = f"/search?query=GRANT_ID:{grant_id}&format=json"
        resp = self._client.fetch_json(url)
        print(_LICENSE_NOTICE, file=sys.stderr)
        return resp

    def fetch_datalinks(self, source: str, pmid: str) -> dict[str, Any]:
        """Fetch supplementary data links (DataCite) for an article.

        Args:
            source: Database source ("MED" or "PMC").
            pmid: Article identifier.

        Returns:
            DataCite links and supplementary data metadata.
        """
        url = f"/{source}/{pmid}/datalinks?format=json"
        resp = self._client.fetch_json(url)
        print(_LICENSE_NOTICE, file=sys.stderr)
        return resp


import urllib.parse

if __name__ == "__main__":
    client = EuropePMCClient()
    results = client.search("CRISPR", page_size=3)
    print(f"Found {results.get('hitCount', 0)} results")
