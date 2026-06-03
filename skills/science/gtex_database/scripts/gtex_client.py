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

"""GTEx (Genotype-Tissue Expression) database client for OpenCode Ecosystem.

Provides API access to the GTEx Portal REST API for tissue-specific
gene expression data.
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

BASE_URL = "https://gtexportal.org/rest/v1"
_CLIENT = http_client.HttpClient(BASE_URL, qps=1.0)


class GTExClient:
    """Client for the GTEx Portal REST API.

    Query tissue-specific gene expression profiles by gene symbol,
    Ensembl ID, or tissue type. Supports median TPM, isoform expression,
    and eQTL data.
    """

    def __init__(self):
        self._available = True

    @property
    def available(self) -> bool:
        return self._available

    def search(self, query: str, limit: int = 10) -> dict[str, Any]:
        """Search GTEx for gene expression data by gene symbol.

        Args:
            query: Gene symbol or Ensembl gene ID.
            limit: Maximum number of results (informational).

        Returns:
            Parsed JSON with median tissue expression data.
        """
        return self.search_by_gene(query)

    def search_by_gene(self, gene_symbol: str) -> dict[str, Any]:
        """Retrieve median gene expression across all tissues for a gene.

        Args:
            gene_symbol: HUGO gene symbol (e.g. 'TP53', 'BRCA1') or
                Ensembl gene ID with version (e.g. 'ENSG00000141510.17').

        Returns:
            Parsed JSON with tissue-specific median TPM values.
        """
        query_both = (
            f"(symbol eq '{gene_symbol}' or gencodeId eq '{gene_symbol}')"
        )
        params = {
            "format": "json",
            "datasetId": "gtex_v10",
            "gencodeId": gene_symbol,
            "sortBy": "tissueSiteDetailId",
            "sortDirection": "asc",
        }
        try:
            return _CLIENT.fetch_json(
                f"/expression/geneExpression?{_encode_params(params)}"
            )
        except http_client.HttpError as e:
            return {"status": "error", "http_code": e.status_code, "message": str(e)}

    def get_median_expression(self, gencode_id: str) -> dict[str, Any]:
        """Retrieve median gene expression for a specific Ensembl gene.

        Args:
            gencode_id: GENCODE/Ensembl gene ID with version
                (e.g. 'ENSG00000141510.17').

        Returns:
            Parsed JSON with tissue expression values.
        """
        return self.search_by_gene(gencode_id)

    def get_isoform_expression(
        self, gencode_id: str
    ) -> dict[str, Any]:
        """Retrieve isoform-level expression data.

        Args:
            gencode_id: GENCODE/Ensembl gene ID.

        Returns:
            Parsed JSON with isoform expression across tissues.
        """
        params = {
            "format": "json",
            "datasetId": "gtex_v10",
            "gencodeId": gencode_id,
        }
        try:
            return _CLIENT.fetch_json(
                f"/expression/isoformExpression?{_encode_params(params)}"
            )
        except http_client.HttpError as e:
            return {"status": "error", "http_code": e.status_code, "message": str(e)}

    def get_top_eqtls(
        self, gencode_id: str, limit: int = 10
    ) -> dict[str, Any]:
        """Retrieve top eQTLs for a gene.

        Args:
            gencode_id: GENCODE/Ensembl gene ID.
            limit: Maximum number of eQTL associations.

        Returns:
            Parsed JSON with variant-gene expression associations.
        """
        params = {
            "format": "json",
            "datasetId": "gtex_v10",
            "gencodeId": gencode_id,
            "pageSize": limit,
            "sortBy": "pValue",
            "sortDirection": "asc",
        }
        try:
            return _CLIENT.fetch_json(
                f"/association/singleTissueEqtl?{_encode_params(params)}"
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
    parser = argparse.ArgumentParser(description="GTEx Portal REST API client")
    subparsers = parser.add_subparsers(dest="command")

    sp_search = subparsers.add_parser("search", help="Search by gene symbol")
    sp_search.add_argument("--query", required=True, help="Gene symbol or Ensembl ID")
    sp_search.add_argument("--output", required=True, help="Output JSON file path")

    sp_expression = subparsers.add_parser(
        "expression", help="Get median gene expression"
    )
    sp_expression.add_argument(
        "--gencode_id", required=True, help="GENCODE/Ensembl gene ID"
    )
    sp_expression.add_argument("--output", required=True, help="Output JSON file path")

    sp_isoform = subparsers.add_parser(
        "isoform", help="Get isoform expression data"
    )
    sp_isoform.add_argument(
        "--gencode_id", required=True, help="GENCODE/Ensembl gene ID"
    )
    sp_isoform.add_argument("--output", required=True, help="Output JSON file path")

    sp_eqtl = subparsers.add_parser("eqtl", help="Get top eQTLs for a gene")
    sp_eqtl.add_argument(
        "--gencode_id", required=True, help="GENCODE/Ensembl gene ID"
    )
    sp_eqtl.add_argument("--limit", type=int, default=10)
    sp_eqtl.add_argument("--output", required=True, help="Output JSON file path")

    args = parser.parse_args()
    client = GTExClient()

    if args.command == "search":
        result = client.search(args.query)
    elif args.command == "expression":
        result = client.get_median_expression(args.gencode_id)
    elif args.command == "isoform":
        result = client.get_isoform_expression(args.gencode_id)
    elif args.command == "eqtl":
        result = client.get_top_eqtls(args.gencode_id, limit=args.limit)
    else:
        parser.print_help()
        sys.exit(1)

    write_output(result, args.output)
