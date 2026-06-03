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

"""Ensembl REST API client for OpenCode Ecosystem.

Provides API access to the Ensembl genome browser REST service.
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

BASE_URL = "https://rest.ensembl.org"
_CLIENT = http_client.HttpClient(BASE_URL, qps=3.0)


class EnsemblClient:
    """Client for the Ensembl REST API.

    Search genes, transcripts, variants, and homologous sequences by ID,
    symbol, or genomic region.
    """

    def __init__(self):
        self._available = True

    @property
    def available(self) -> bool:
        return self._available

    def search(
        self, query: str, limit: int = 10
    ) -> dict[str, Any]:
        """Search Ensembl by free-text query.

        The query can be a gene symbol, Ensembl ID, or keyword.

        Args:
            query: Search query string.
            limit: Maximum number of results.

        Returns:
            Parsed JSON response with matching entities.
        """
        try:
            return _CLIENT.fetch_json(
                f"/lookup/symbol/homo_sapiens/{query}?expand=1"
            )
        except http_client.HttpError:
            # Fallback: try generic lookup
            try:
                return _CLIENT.fetch_json(f"/lookup/id/{query}?expand=1")
            except http_client.HttpError as e:
                return {
                    "status": "error",
                    "http_code": e.status_code,
                    "message": str(e),
                }

    def get_gene(self, gene_id: str) -> dict[str, Any]:
        """Retrieve gene information by Ensembl gene ID.

        Args:
            gene_id: Ensembl gene ID (e.g. 'ENSG00000139618' for BRCA2).

        Returns:
            Parsed JSON with gene details including name, location, and biotype.
        """
        try:
            return _CLIENT.fetch_json(f"/lookup/id/{gene_id}?expand=1")
        except http_client.HttpError as e:
            return {"status": "error", "http_code": e.status_code, "message": str(e)}

    def get_transcript(self, transcript_id: str) -> dict[str, Any]:
        """Retrieve transcript information by Ensembl transcript ID.

        Args:
            transcript_id: Ensembl transcript ID (e.g. 'ENST00000380152').

        Returns:
            Parsed JSON with transcript details including exons and CDS.
        """
        try:
            return _CLIENT.fetch_json(f"/lookup/id/{transcript_id}?expand=1")
        except http_client.HttpError as e:
            return {"status": "error", "http_code": e.status_code, "message": str(e)}

    def get_variant(self, variant_id: str) -> dict[str, Any]:
        """Retrieve variant consequences by rs ID.

        Uses the VEP (Variant Effect Predictor) endpoint.

        Args:
            variant_id: dbSNP rs identifier (e.g. 'rs699').

        Returns:
            Parsed JSON with predicted variant consequences.
        """
        try:
            return _CLIENT.fetch_json(
                f"/vep/human/id/{variant_id}",
                headers={"Content-Type": "application/json"},
            )
        except http_client.HttpError as e:
            return {"status": "error", "http_code": e.status_code, "message": str(e)}

    def get_sequence(self, region_id: str) -> dict[str, Any]:
        """Retrieve genomic sequence for a region.

        Args:
            region_id: Region identifier in format 'chromosome:start-end'
                (e.g. 'X:1000000-1000100').

        Returns:
            Parsed JSON with sequence data.
        """
        try:
            return _CLIENT.fetch_json(
                f"/sequence/region/human/{region_id}",
                headers={"Content-Type": "text/plain"},
            )
        except http_client.HttpError as e:
            return {"status": "error", "http_code": e.status_code, "message": str(e)}

    def get_homology(self, gene_id: str) -> dict[str, Any]:
        """Retrieve homology data for a gene across species.

        Args:
            gene_id: Ensembl gene ID.

        Returns:
            Parsed JSON with ortholog and paralog information.
        """
        try:
            return _CLIENT.fetch_json(
                f"/homology/id/{gene_id}",
                headers={"Content-Type": "application/json"},
            )
        except http_client.HttpError as e:
            return {"status": "error", "http_code": e.status_code, "message": str(e)}


def write_output(data: Any, output_path: str) -> None:
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
        f.write("\n")
    print(f"Output written to: {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ensembl REST API client")
    subparsers = parser.add_subparsers(dest="command")

    sp_search = subparsers.add_parser("search", help="Search by gene symbol or ID")
    sp_search.add_argument("--query", required=True, help="Gene symbol or Ensembl ID")
    sp_search.add_argument("--output", required=True, help="Output JSON file path")

    sp_gene = subparsers.add_parser("gene", help="Get gene by Ensembl ID")
    sp_gene.add_argument("--gene_id", required=True, help="Ensembl gene ID")
    sp_gene.add_argument("--output", required=True, help="Output JSON file path")

    sp_transcript = subparsers.add_parser("transcript", help="Get transcript by ID")
    sp_transcript.add_argument(
        "--transcript_id", required=True, help="Ensembl transcript ID"
    )
    sp_transcript.add_argument("--output", required=True, help="Output JSON file path")

    sp_variant = subparsers.add_parser("variant", help="Get variant consequences")
    sp_variant.add_argument("--variant_id", required=True, help="dbSNP rs ID")
    sp_variant.add_argument("--output", required=True, help="Output JSON file path")

    sp_seq = subparsers.add_parser("sequence", help="Get genomic sequence")
    sp_seq.add_argument(
        "--region", required=True, help="Region (e.g. X:1000000-1000100)"
    )
    sp_seq.add_argument("--output", required=True, help="Output JSON file path")

    sp_homology = subparsers.add_parser("homology", help="Get gene homology data")
    sp_homology.add_argument("--gene_id", required=True, help="Ensembl gene ID")
    sp_homology.add_argument("--output", required=True, help="Output JSON file path")

    args = parser.parse_args()
    client = EnsemblClient()

    if args.command == "search":
        result = client.search(args.query)
    elif args.command == "gene":
        result = client.get_gene(args.gene_id)
    elif args.command == "transcript":
        result = client.get_transcript(args.transcript_id)
    elif args.command == "variant":
        result = client.get_variant(args.variant_id)
    elif args.command == "sequence":
        result = client.get_sequence(args.region)
    elif args.command == "homology":
        result = client.get_homology(args.gene_id)
    else:
        parser.print_help()
        sys.exit(1)

    write_output(result, args.output)
