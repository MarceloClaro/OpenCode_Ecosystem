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

"""InterPro database client for OpenCode Ecosystem.

Provides API access to the EBI InterPro REST API for protein domain,
family, and functional site classification.
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

import argparse
import json
import sys
from typing import Any

from science_skills.science_skills_common import http_client

BASE_URL = "https://www.ebi.ac.uk/interpro/api"
_CLIENT = http_client.HttpClient(BASE_URL, qps=2.0)


class InterProClient:
    """Client for the EBI InterPro REST API.

    Search protein domains, families, homologous superfamilies, repeats,
    and functional sites by accession, keyword, or protein sequence.
    """

    def __init__(self):
        self._available = True

    @property
    def available(self) -> bool:
        return self._available

    def search(
        self, query: str, limit: int = 10
    ) -> dict[str, Any]:
        """Search InterPro entries by keyword or accession.

        Args:
            query: Search term (domain name, accession, keyword).
            limit: Maximum number of results per page.

        Returns:
            Parsed JSON response with matching InterPro entries.
        """
        params: dict[str, Any] = {
            "search": query,
            "page_size": limit,
        }
        try:
            return _CLIENT.fetch_json(
                f"/entry/interpro/?{_encode_params(params)}"
            )
        except http_client.HttpError as e:
            return {"status": "error", "http_code": e.status_code, "message": str(e)}

    def search_by_accession(
        self, accession: str
    ) -> dict[str, Any]:
        """Retrieve a specific InterPro entry by accession.

        Args:
            accession: InterPro accession (e.g. 'IPR020422')
                or member database accession (e.g. 'PF00001' for Pfam,
                'SSF52540' for CATH-Gene3D).

        Returns:
            Parsed JSON with full domain/family metadata.
        """
        try:
            return _CLIENT.fetch_json(f"/entry/interpro/{accession}/")
        except http_client.HttpError as e:
            return {"status": "error", "http_code": e.status_code, "message": str(e)}

    def search_by_protein(
        self, protein_accession: str
    ) -> dict[str, Any]:
        """Retrieve domain annotations for a specific protein.

        Args:
            protein_accession: UniProt accession (e.g. 'P04637' for TP53).

        Returns:
            Parsed JSON with domain matches on the protein sequence.
        """
        params: dict[str, Any] = {
            "protein_accession": protein_accession,
        }
        try:
            return _CLIENT.fetch_json(
                f"/entry/interpro/protein/reviewed/{protein_accession}/"
            )
        except http_client.HttpError as e:
            return {"status": "error", "http_code": e.status_code, "message": str(e)}

    def search_by_text(
        self, text: str, limit: int = 10
    ) -> dict[str, Any]:
        """Full-text search across InterPro entries.

        Searches entry names, short names, and descriptions.

        Args:
            text: Search text (e.g. 'kinase', 'immunoglobulin').
            limit: Maximum number of results.

        Returns:
            Parsed JSON with matching entries.
        """
        params: dict[str, Any] = {
            "search": text,
            "page_size": limit,
        }
        try:
            return _CLIENT.fetch_json(
                f"/entry/interpro/?{_encode_params(params)}"
            )
        except http_client.HttpError as e:
            return {"status": "error", "http_code": e.status_code, "message": str(e)}


def _encode_params(params: dict[str, Any]) -> str:
    import urllib.parse

    return urllib.parse.urlencode(params)


def write_output(data: Any, output_path: str) -> None:
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
        f.write("\n")
    print(f"Output written to: {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="InterPro REST API client")
    subparsers = parser.add_subparsers(dest="command")

    sp_search = subparsers.add_parser("search", help="Search InterPro entries")
    sp_search.add_argument("--query", required=True, help="Search keyword or accession")
    sp_search.add_argument("--limit", type=int, default=10)
    sp_search.add_argument("--output", required=True, help="Output JSON file path")

    sp_accession = subparsers.add_parser(
        "accession", help="Get entry by InterPro accession"
    )
    sp_accession.add_argument(
        "--accession", required=True, help="InterPro or member DB accession"
    )
    sp_accession.add_argument("--output", required=True, help="Output JSON file path")

    sp_protein = subparsers.add_parser(
        "protein", help="Get domain annotations for a protein"
    )
    sp_protein.add_argument(
        "--protein_accession", required=True, help="UniProt accession"
    )
    sp_protein.add_argument("--output", required=True, help="Output JSON file path")

    sp_text = subparsers.add_parser("text", help="Full-text search across entries")
    sp_text.add_argument("--text", required=True, help="Search text")
    sp_text.add_argument("--limit", type=int, default=10)
    sp_text.add_argument("--output", required=True, help="Output JSON file path")

    args = parser.parse_args()
    client = InterProClient()

    if args.command == "search":
        result = client.search(args.query, limit=args.limit)
    elif args.command == "accession":
        result = client.search_by_accession(args.accession)
    elif args.command == "protein":
        result = client.search_by_protein(args.protein_accession)
    elif args.command == "text":
        result = client.search_by_text(args.text, limit=args.limit)
    else:
        parser.print_help()
        sys.exit(1)

    write_output(result, args.output)
