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

"""ClinicalTrials.gov API client for OpenCode Ecosystem.

Provides API access to the ClinicalTrials.gov study registry (v2 API).
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

BASE_URL = "https://clinicaltrials.gov/api/v2"
_CLIENT = http_client.HttpClient(BASE_URL, qps=1.0)


class ClinicalTrialsClient:
    """Client for the ClinicalTrials.gov REST API (v2).

    Search clinical studies by condition, drug, sponsor, or free-text query.
    """

    def __init__(self):
        self._available = True

    @property
    def available(self) -> bool:
        return self._available

    def search(
        self,
        query: str,
        page_size: int = 10,
        status: str | None = None,
        page_token: str | None = None,
    ) -> dict[str, Any]:
        """Search clinical trials by query term.

        Args:
            query: Free-text search query (condition, drug, sponsor, etc.).
            page_size: Number of results per page (max 100).
            status: Study status filter (e.g. 'RECRUITING', 'COMPLETED').
            page_token: Pagination token from a previous response.

        Returns:
            Parsed JSON response with studies and pagination info.
        """
        params: dict[str, Any] = {
            "query.term": query,
            "pageSize": min(page_size, 100),
            "format": "json",
        }
        if status:
            params["filter.overallStatus"] = status
        if page_token:
            params["pageToken"] = page_token

        try:
            return _CLIENT.fetch_json(f"/studies?{_encode_params(params)}")
        except http_client.HttpError as e:
            return {"status": "error", "http_code": e.status_code, "message": str(e)}

    def get_study(self, nct_id: str) -> dict[str, Any]:
        """Retrieve a single study by NCT identifier.

        Args:
            nct_id: NCT number (e.g. 'NCT04280705').

        Returns:
            Parsed JSON response with full study details.
        """
        params = {"format": "json"}
        try:
            return _CLIENT.fetch_json(
                f"/studies/{nct_id}?{_encode_params(params)}"
            )
        except http_client.HttpError as e:
            return {"status": "error", "http_code": e.status_code, "message": str(e)}

    def search_by_condition(
        self, condition: str, page_size: int = 10
    ) -> dict[str, Any]:
        """Search studies by medical condition.

        Args:
            condition: Medical condition name (e.g. 'breast cancer').
            page_size: Number of results per page.

        Returns:
            Parsed JSON response with matching studies.
        """
        return self.search(f"AREA[Condition]\"{condition}\"", page_size=page_size)

    def search_by_drug(self, drug: str, page_size: int = 10) -> dict[str, Any]:
        """Search studies by drug/intervention.

        Args:
            drug: Drug or intervention name (e.g. 'pembrolizumab').
            page_size: Number of results per page.

        Returns:
            Parsed JSON response with matching studies.
        """
        return self.search(f"AREA[Intervention]\"{drug}\"", page_size=page_size)

    def search_by_sponsor(self, sponsor: str, page_size: int = 10) -> dict[str, Any]:
        """Search studies by sponsor organization.

        Args:
            sponsor: Sponsor name (e.g. 'National Cancer Institute').
            page_size: Number of results per page.

        Returns:
            Parsed JSON response with matching studies.
        """
        return self.search(f"AREA[Sponsor]\"{sponsor}\"", page_size=page_size)


def _encode_params(params: dict[str, Any]) -> str:
    """Encode query params, joining multi-value params with '+'.

    The ClinicalTrials.gov v2 API expects '+' as the separator for
    repeated parameter keys (e.g. filter.overallStatus).
    """
    import urllib.parse

    pairs: list[str] = []
    for key, value in params.items():
        if isinstance(value, list):
            pairs.append(urllib.parse.urlencode({key: "+".join(value)}))
        else:
            pairs.append(f"{key}={urllib.parse.quote(str(value))}")
    return "&".join(pairs)


def write_output(data: Any, output_path: str) -> None:
    """Write JSON output to file."""
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
        f.write("\n")
    print(f"Output written to: {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ClinicalTrials.gov API client")
    subparsers = parser.add_subparsers(dest="command")

    sp_search = subparsers.add_parser("search", help="Search clinical trials")
    sp_search.add_argument("--query", required=True, help="Search query")
    sp_search.add_argument(
        "--page_size", type=int, default=10, help="Results per page (max 100)"
    )
    sp_search.add_argument("--status", help="Filter by status (e.g. RECRUITING)")
    sp_search.add_argument("--output", required=True, help="Output JSON file path")

    sp_get = subparsers.add_parser("get", help="Get study by NCT ID")
    sp_get.add_argument("--nct_id", required=True, help="NCT identifier")
    sp_get.add_argument("--output", required=True, help="Output JSON file path")

    sp_condition = subparsers.add_parser("condition", help="Search by condition")
    sp_condition.add_argument("--condition", required=True, help="Condition name")
    sp_condition.add_argument("--page_size", type=int, default=10)
    sp_condition.add_argument("--output", required=True, help="Output JSON file path")

    sp_drug = subparsers.add_parser("drug", help="Search by drug")
    sp_drug.add_argument("--drug", required=True, help="Drug name")
    sp_drug.add_argument("--page_size", type=int, default=10)
    sp_drug.add_argument("--output", required=True, help="Output JSON file path")

    sp_sponsor = subparsers.add_parser("sponsor", help="Search by sponsor")
    sp_sponsor.add_argument("--sponsor", required=True, help="Sponsor name")
    sp_sponsor.add_argument("--page_size", type=int, default=10)
    sp_sponsor.add_argument("--output", required=True, help="Output JSON file path")

    args = parser.parse_args()
    client = ClinicalTrialsClient()

    if args.command == "search":
        result = client.search(args.query, page_size=args.page_size, status=args.status)
    elif args.command == "get":
        result = client.get_study(args.nct_id)
    elif args.command == "condition":
        result = client.search_by_condition(args.condition, page_size=args.page_size)
    elif args.command == "drug":
        result = client.search_by_drug(args.drug, page_size=args.page_size)
    elif args.command == "sponsor":
        result = client.search_by_sponsor(args.sponsor, page_size=args.page_size)
    else:
        parser.print_help()
        sys.exit(1)

    write_output(result, args.output)
