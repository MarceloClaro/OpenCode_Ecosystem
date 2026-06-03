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

"""gnomAD database client for OpenCode Ecosystem.

Provides API access to the gnomAD (Genome Aggregation Database) via its
public GraphQL API for population-scale variant frequency data.
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

BASE_URL = "https://gnomad.broadinstitute.org/api"
_CLIENT = http_client.HttpClient(BASE_URL, qps=1.0)

GENE_QUERY = """
query GeneVariants($geneSymbol: String!, $datasetId: DatasetId!) {
  gene(gene_symbol: $geneSymbol, reference_genome: GRCh38) {
    gene_id
    symbol
    chrom
    start
    stop
    variants(dataset: $datasetId, first: {limit}) {
      variant_id
      pos
      ref
      alt
      exome { ac an af }
      genome { ac an af }
    }
  }
}
"""

REGION_QUERY = """
query RegionVariants($chrom: String!, $start: Int!, $stop: Int!, $datasetId: DatasetId!) {
  region(chrom: $chrom, start: $start, stop: $stop, reference_genome: GRCh38) {
    variants(dataset: $datasetId, first: {limit}) {
      variant_id
      pos
      ref
      alt
      rsid
      exome { ac an af }
      genome { ac an af }
    }
  }
}

"""


class GnomADClient:
    """Client for the gnomAD GraphQL API.

    Query variant population frequencies by gene, rs ID, or genomic position.
    Supports both exome and genome aggregate datasets.
    """

    def __init__(self):
        self._available = True

    @property
    def available(self) -> bool:
        return self._available

    def search(self, query: str, limit: int = 10) -> dict[str, Any]:
        """Search gnomAD for variants matching a query.

        Attempts to resolve the query as a gene symbol first, then falls
        back to rs ID lookup.

        Args:
            query: Gene symbol or rs ID.
            limit: Maximum number of variants to return.

        Returns:
            Parsed JSON response with variant frequency data.
        """
        if query.lower().startswith("rs"):
            return self.search_by_rsid(query, limit=limit)
        return self.search_by_gene(query, limit=limit)

    def search_by_gene(
        self, gene_symbol: str, limit: int = 10
    ) -> dict[str, Any]:
        """Search variants within a gene by symbol.

        Args:
            gene_symbol: HUGO gene symbol (e.g. 'BRCA2', 'TP53').
            limit: Maximum number of variants.

        Returns:
            Parsed JSON with gene metadata and variant frequency list.
        """
        query_str = GENE_QUERY.replace("{limit}", str(limit))
        payload = {
            "query": query_str,
            "variables": {
                "geneSymbol": gene_symbol.upper(),
                "datasetId": "gnomad_r4",
            },
        }
        try:
            return _CLIENT.fetch_json("/", method="POST", json_body=payload)
        except http_client.HttpError as e:
            return {"status": "error", "http_code": e.status_code, "message": str(e)}

    def search_by_rsid(self, rs_id: str, limit: int = 1) -> dict[str, Any]:
        """Search for a variant by dbSNP rs ID.

        Uses the region query with rsID filter via the variant lookup.

        Args:
            rs_id: dbSNP rs identifier (e.g. 'rs334').
            limit: Maximum number of variants.

        Returns:
            Parsed JSON with variant frequency data.
        """
        query_str = """
        query RsIdLookup($rsId: String!, $datasetId: DatasetId!) {
          variant(dataset: $datasetId, variantId: $rsId, reference_genome: GRCh38) {
            variant_id
            chrom
            pos
            ref
            alt
            rsid
            exome { ac an af }
            genome { ac an af }
            transcript_consequences {
              gene_id
              gene_symbol
              major_consequence
            }
          }
        }
        """
        payload = {
            "query": query_str,
            "variables": {
                "rsId": rs_id,
                "datasetId": "gnomad_r4",
            },
        }
        try:
            return _CLIENT.fetch_json("/", method="POST", json_body=payload)
        except http_client.HttpError as e:
            return {"status": "error", "http_code": e.status_code, "message": str(e)}

    def search_by_position(
        self,
        chromosome: str,
        start: int,
        end: int | None = None,
        limit: int = 10,
    ) -> dict[str, Any]:
        """Search variants in a genomic region.

        Args:
            chromosome: Chromosome (e.g. '2', 'X').
            start: Start position (1-based).
            end: End position (defaults to start).
            limit: Maximum number of variants.

        Returns:
            Parsed JSON with variant frequency data for the region.
        """
        region_end = end if end is not None else start
        query_str = REGION_QUERY.replace("{limit}", str(limit))
        payload = {
            "query": query_str,
            "variables": {
                "chrom": chromosome,
                "start": start,
                "stop": region_end,
                "datasetId": "gnomad_r4",
            },
        }
        try:
            return _CLIENT.fetch_json("/", method="POST", json_body=payload)
        except http_client.HttpError as e:
            return {"status": "error", "http_code": e.status_code, "message": str(e)}


def write_output(data: Any, output_path: str) -> None:
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
        f.write("\n")
    print(f"Output written to: {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="gnomAD GraphQL API client")
    subparsers = parser.add_subparsers(dest="command")

    sp_search = subparsers.add_parser("search", help="Search by gene or rs ID")
    sp_search.add_argument("--query", required=True, help="Gene symbol or rs ID")
    sp_search.add_argument("--limit", type=int, default=10)
    sp_search.add_argument("--output", required=True, help="Output JSON file path")

    sp_gene = subparsers.add_parser("gene", help="Search variants by gene symbol")
    sp_gene.add_argument("--gene", required=True, help="Gene symbol")
    sp_gene.add_argument("--limit", type=int, default=10)
    sp_gene.add_argument("--output", required=True, help="Output JSON file path")

    sp_rsid = subparsers.add_parser("rsid", help="Search variant by rs ID")
    sp_rsid.add_argument("--rs_id", required=True, help="dbSNP rs identifier")
    sp_rsid.add_argument("--output", required=True, help="Output JSON file path")

    sp_pos = subparsers.add_parser("position", help="Search by genomic position")
    sp_pos.add_argument("--chromosome", required=True, help="Chromosome")
    sp_pos.add_argument("--start", type=int, required=True, help="Start position")
    sp_pos.add_argument("--end", type=int, default=None, help="End position")
    sp_pos.add_argument("--limit", type=int, default=10)
    sp_pos.add_argument("--output", required=True, help="Output JSON file path")

    args = parser.parse_args()
    client = GnomADClient()

    if args.command == "search":
        result = client.search(args.query, limit=args.limit)
    elif args.command == "gene":
        result = client.search_by_gene(args.gene, limit=args.limit)
    elif args.command == "rsid":
        result = client.search_by_rsid(args.rs_id)
    elif args.command == "position":
        result = client.search_by_position(
            args.chromosome, args.start, args.end, limit=args.limit
        )
    else:
        parser.print_help()
        sys.exit(1)

    write_output(result, args.output)
