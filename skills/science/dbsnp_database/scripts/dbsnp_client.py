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

"""dbSNP database client for OpenCode Ecosystem.

Provides API access to the NCBI dbSNP Variation Services API (v0).
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

BASE_URL = "https://api.ncbi.nlm.nih.gov/variation/v0"
_CLIENT = http_client.HttpClient(BASE_URL, qps=1.0)


class DbSNPClient:
    """Client for the NCBI dbSNP Variation Services API.

    Search variants by rs ID, gene symbol, chromosome position, or phenotype.
    """

    def __init__(self):
        self._available = True

    @property
    def available(self) -> bool:
        return self._available

    def search(
        self, query: str, limit: int = 10
    ) -> dict[str, Any]:
        """Search dbSNP variants by free-text query.

        Args:
            query: Search query (gene symbol, phenotype, rs ID, etc.).
            limit: Maximum number of results.

        Returns:
            Parsed JSON response with variant summaries.
        """
        params = {"q": query, "page_size": limit}
        try:
            return _CLIENT.fetch_json(f"/refsnp?{_encode_params(params)}")
        except http_client.HttpError as e:
            return {"status": "error", "http_code": e.status_code, "message": str(e)}

    def get_variant(self, rs_id: str) -> dict[str, Any]:
        """Retrieve a single variant by rs identifier.

        Args:
            rs_id: Reference SNP ID (e.g. 'rs334' for sickle cell).
                Accepts bare number ('334') or full form ('rs334').

        Returns:
            Parsed JSON response with full variant details.
        """
        clean_id = rs_id.replace("rs", "").strip()
        try:
            return _CLIENT.fetch_json(f"/refsnp/{clean_id}")
        except http_client.HttpError as e:
            return {"status": "error", "http_code": e.status_code, "message": str(e)}

    def search_by_gene(
        self, gene: str, limit: int = 10
    ) -> dict[str, Any]:
        """Search variants associated with a gene symbol.

        Args:
            gene: Gene symbol (e.g. 'BRCA1', 'TP53', 'HBB').
            limit: Maximum number of results.

        Returns:
            Parsed JSON response with variant summaries.
        """
        return self.search(f"gene:{gene}", limit=limit)

    def search_by_phenotype(
        self, phenotype: str, limit: int = 10
    ) -> dict[str, Any]:
        """Search variants by phenotype or clinical condition.

        Args:
            phenotype: Phenotype or condition name.
            limit: Maximum number of results.

        Returns:
            Parsed JSON response with variant summaries.
        """
        return self.search(f"clinical_significance:{phenotype}", limit=limit)

    def search_by_position(
        self,
        chromosome: str,
        start: int,
        end: int | None = None,
        limit: int = 10,
    ) -> dict[str, Any]:
        """Search variants in a genomic region.

        Args:
            chromosome: Chromosome (e.g. '11', 'X').
            start: Start position (1-based).
            end: End position (optional, defaults to start).
            limit: Maximum number of results.

        Returns:
            Parsed JSON response with variant summaries.
        """
        region_end = end if end is not None else start
        query = f"chr{chromosome}:{start}-{region_end}"
        return self.search(query, limit=limit)


def _encode_params(params: dict[str, Any]) -> str:
    import urllib.parse

    return urllib.parse.urlencode(params)


def write_output(data: Any, output_path: str) -> None:
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
        f.write("\n")
    print(f"Output written to: {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="dbSNP Variation Services client")
    subparsers = parser.add_subparsers(dest="command")

    sp_search = subparsers.add_parser("search", help="Search variants by query")
    sp_search.add_argument("--query", required=True, help="Search query")
    sp_search.add_argument("--limit", type=int, default=10, help="Max results")
    sp_search.add_argument("--output", required=True, help="Output JSON file path")

    sp_get = subparsers.add_parser("get", help="Get variant by rs ID")
    sp_get.add_argument("--rs_id", required=True, help="rs identifier")
    sp_get.add_argument("--output", required=True, help="Output JSON file path")

    sp_gene = subparsers.add_parser("gene", help="Search by gene symbol")
    sp_gene.add_argument("--gene", required=True, help="Gene symbol")
    sp_gene.add_argument("--limit", type=int, default=10)
    sp_gene.add_argument("--output", required=True, help="Output JSON file path")

    sp_pheno = subparsers.add_parser("phenotype", help="Search by phenotype")
    sp_pheno.add_argument("--phenotype", required=True, help="Phenotype name")
    sp_pheno.add_argument("--limit", type=int, default=10)
    sp_pheno.add_argument("--output", required=True, help="Output JSON file path")

    sp_pos = subparsers.add_parser("position", help="Search by genomic position")
    sp_pos.add_argument("--chromosome", required=True, help="Chromosome (e.g. 11, X)")
    sp_pos.add_argument("--start", type=int, required=True, help="Start position")
    sp_pos.add_argument("--end", type=int, default=None, help="End position")
    sp_pos.add_argument("--limit", type=int, default=10)
    sp_pos.add_argument("--output", required=True, help="Output JSON file path")

    args = parser.parse_args()
    client = DbSNPClient()

    if args.command == "search":
        result = client.search(args.query, limit=args.limit)
    elif args.command == "get":
        result = client.get_variant(args.rs_id)
    elif args.command == "gene":
        result = client.search_by_gene(args.gene, limit=args.limit)
    elif args.command == "phenotype":
        result = client.search_by_phenotype(args.phenotype, limit=args.limit)
    elif args.command == "position":
        result = client.search_by_position(
            args.chromosome, args.start, args.end, limit=args.limit
        )
    else:
        parser.print_help()
        sys.exit(1)

    write_output(result, args.output)
