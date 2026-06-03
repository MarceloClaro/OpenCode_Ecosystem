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

"""PDB (Protein Data Bank) database client for OpenCode Ecosystem.

Provides API access to the RCSB PDB REST API for 3D macromolecular
structure search and metadata retrieval.
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

BASE_URL = "https://data.rcsb.org/rest/v1"
SEARCH_URL = "https://search.rcsb.org/rcsbsearch/v2"
_CLIENT = http_client.HttpClient(BASE_URL, qps=2.0)
_SEARCH_CLIENT = http_client.HttpClient(SEARCH_URL, qps=2.0)


class PDBClient:
    """Client for the RCSB PDB REST and Search APIs.

    Search 3D macromolecular structures by PDB ID, molecule name,
    organism, experimental method, or structural features.
    """

    def __init__(self):
        self._available = True

    @property
    def available(self) -> bool:
        return self._available

    def search(
        self, query: str, limit: int = 10
    ) -> dict[str, Any]:
        """Search PDB structures by free-text query.

        Uses the RCSB Search API for full-text search across
        structure titles, keywords, and descriptions.

        Args:
            query: Search term (molecule name, organism, keyword).
            limit: Maximum number of results.

        Returns:
            Parsed JSON response with matching structure summaries.
        """
        search_payload = {
            "query": {
                "type": "terminal",
                "service": "full_text",
                "parameters": {"value": query},
            },
            "return_type": "entry",
            "request_options": {
                "paginate": {"start": 0, "rows": limit},
                "results_content_type": ["experimental"],
                "sort": [{"sort_by": "score", "direction": "desc"}],
            },
        }
        try:
            return _SEARCH_CLIENT.fetch_json(
                "/query", method="POST", json_body=search_payload
            )
        except http_client.HttpError as e:
            return {"status": "error", "http_code": e.status_code, "message": str(e)}

    def get_structure(self, pdb_id: str) -> dict[str, Any]:
        """Retrieve full metadata for a PDB entry.

        Args:
            pdb_id: 4-character PDB identifier (e.g. '4HHB' for hemoglobin).

        Returns:
            Parsed JSON with complete structure metadata including
            citation, experimental details, polymer entities, and ligands.
        """
        try:
            return _CLIENT.fetch_json(f"/core/entry/{pdb_id.upper()}")
        except http_client.HttpError as e:
            return {"status": "error", "http_code": e.status_code, "message": str(e)}

    def search_by_molecule(
        self, molecule_name: str, limit: int = 10
    ) -> dict[str, Any]:
        """Search PDB by molecule or ligand name.

        Args:
            molecule_name: Name of the molecule (e.g. 'hemoglobin',
                'ATP', 'ribosome').
            limit: Maximum number of results.

        Returns:
            Parsed JSON with matching structures.
        """
        return self.search(molecule_name, limit=limit)

    def search_by_organism(
        self, organism: str, limit: int = 10
    ) -> dict[str, Any]:
        """Search PDB structures by source organism.

        Args:
            organism: Organism scientific name (e.g. 'Homo sapiens',
                'Escherichia coli').
            limit: Maximum number of results.

        Returns:
            Parsed JSON with matching structures.
        """
        search_payload = {
            "query": {
                "type": "group",
                "logical_operator": "and",
                "nodes": [
                    {
                        "type": "terminal",
                        "service": "text",
                        "parameters": {
                            "attribute": "rcsb_entity_source_organism.taxonomy_lineage.name",
                            "operator": "exact_match",
                            "value": organism,
                        },
                    }
                ],
            },
            "return_type": "entry",
            "request_options": {
                "paginate": {"start": 0, "rows": limit},
                "results_content_type": ["experimental"],
            },
        }
        try:
            return _SEARCH_CLIENT.fetch_json(
                "/query", method="POST", json_body=search_payload
            )
        except http_client.HttpError as e:
            return {"status": "error", "http_code": e.status_code, "message": str(e)}

    def search_by_method(
        self, method: str, limit: int = 10
    ) -> dict[str, Any]:
        """Search PDB by experimental method.

        Args:
            method: Experimental method ('X-RAY DIFFRACTION',
                'SOLUTION NMR', 'ELECTRON MICROSCOPY',
                'SOLID-STATE NMR', 'NEUTRON DIFFRACTION', etc.).
            limit: Maximum number of results.

        Returns:
            Parsed JSON with matching structures.
        """
        search_payload = {
            "query": {
                "type": "terminal",
                "service": "text",
                "parameters": {
                    "attribute": "exptl.method",
                    "operator": "exact_match",
                    "value": method.upper(),
                },
            },
            "return_type": "entry",
            "request_options": {
                "paginate": {"start": 0, "rows": limit},
                "results_content_type": ["experimental"],
            },
        }
        try:
            return _SEARCH_CLIENT.fetch_json(
                "/query", method="POST", json_body=search_payload
            )
        except http_client.HttpError as e:
            return {"status": "error", "http_code": e.status_code, "message": str(e)}

    def get_polymer_entities(self, pdb_id: str) -> dict[str, Any]:
        """Retrieve polymer entity (protein/nucleic acid) metadata.

        Args:
            pdb_id: 4-character PDB identifier.

        Returns:
            Parsed JSON with polymer entity details.
        """
        try:
            return _CLIENT.fetch_json(
                f"/core/polymer_entity/{pdb_id.upper()}/1"
            )
        except http_client.HttpError as e:
            return {"status": "error", "http_code": e.status_code, "message": str(e)}

    def get_assembly(self, pdb_id: str, assembly_id: int = 1) -> dict[str, Any]:
        """Retrieve biological assembly metadata.

        Args:
            pdb_id: 4-character PDB identifier.
            assembly_id: Assembly number (default: 1).

        Returns:
            Parsed JSON with assembly details.
        """
        try:
            return _CLIENT.fetch_json(
                f"/core/assembly/{pdb_id.upper()}/{assembly_id}"
            )
        except http_client.HttpError as e:
            return {"status": "error", "http_code": e.status_code, "message": str(e)}

    def search_by_resolution(
        self, max_resolution: float, limit: int = 10
    ) -> dict[str, Any]:
        """Search PDB by maximum resolution (in Angstroms).

        Args:
            max_resolution: Maximum resolution in Angstroms
                (e.g. 2.0 for <= 2.0 A).
            limit: Maximum number of results.

        Returns:
            Parsed JSON with matching high-resolution structures.
        """
        search_payload = {
            "query": {
                "type": "terminal",
                "service": "text",
                "parameters": {
                    "attribute": "rcsb_entry_info.resolution_combined",
                    "operator": "less_or_equal",
                    "value": max_resolution,
                },
            },
            "return_type": "entry",
            "request_options": {
                "paginate": {"start": 0, "rows": limit},
                "results_content_type": ["experimental"],
                "sort": [{"sort_by": "rcsb_entry_info.resolution_combined", "direction": "asc"}],
            },
        }
        try:
            return _SEARCH_CLIENT.fetch_json(
                "/query", method="POST", json_body=search_payload
            )
        except http_client.HttpError as e:
            return {"status": "error", "http_code": e.status_code, "message": str(e)}


def write_output(data: Any, output_path: str) -> None:
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
        f.write("\n")
    print(f"Output written to: {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="RCSB PDB REST API client")
    subparsers = parser.add_subparsers(dest="command")

    sp_search = subparsers.add_parser("search", help="Full-text search for structures")
    sp_search.add_argument("--query", required=True, help="Search query")
    sp_search.add_argument("--limit", type=int, default=10)
    sp_search.add_argument("--output", required=True, help="Output JSON file path")

    sp_get = subparsers.add_parser("get", help="Get structure metadata by PDB ID")
    sp_get.add_argument("--pdb_id", required=True, help="4-character PDB ID")
    sp_get.add_argument("--output", required=True, help="Output JSON file path")

    sp_molecule = subparsers.add_parser("molecule", help="Search by molecule name")
    sp_molecule.add_argument("--name", required=True, help="Molecule name")
    sp_molecule.add_argument("--limit", type=int, default=10)
    sp_molecule.add_argument("--output", required=True, help="Output JSON file path")

    sp_organism = subparsers.add_parser("organism", help="Search by source organism")
    sp_organism.add_argument("--organism", required=True, help="Organism name")
    sp_organism.add_argument("--limit", type=int, default=10)
    sp_organism.add_argument("--output", required=True, help="Output JSON file path")

    sp_method = subparsers.add_parser("method", help="Search by experimental method")
    sp_method.add_argument(
        "--method",
        required=True,
        help="Method (e.g. 'X-RAY DIFFRACTION', 'ELECTRON MICROSCOPY')",
    )
    sp_method.add_argument("--limit", type=int, default=10)
    sp_method.add_argument("--output", required=True, help="Output JSON file path")

    sp_entity = subparsers.add_parser(
        "polymer", help="Get polymer entity metadata"
    )
    sp_entity.add_argument("--pdb_id", required=True, help="4-character PDB ID")
    sp_entity.add_argument("--output", required=True, help="Output JSON file path")

    sp_assembly = subparsers.add_parser("assembly", help="Get assembly metadata")
    sp_assembly.add_argument("--pdb_id", required=True, help="4-character PDB ID")
    sp_assembly.add_argument("--assembly_id", type=int, default=1)
    sp_assembly.add_argument("--output", required=True, help="Output JSON file path")

    sp_resolution = subparsers.add_parser(
        "resolution", help="Search by maximum resolution"
    )
    sp_resolution.add_argument(
        "--max_resolution", type=float, required=True, help="Max resolution in Angstroms"
    )
    sp_resolution.add_argument("--limit", type=int, default=10)
    sp_resolution.add_argument("--output", required=True, help="Output JSON file path")

    args = parser.parse_args()
    client = PDBClient()

    if args.command == "search":
        result = client.search(args.query, limit=args.limit)
    elif args.command == "get":
        result = client.get_structure(args.pdb_id)
    elif args.command == "molecule":
        result = client.search_by_molecule(args.name, limit=args.limit)
    elif args.command == "organism":
        result = client.search_by_organism(args.organism, limit=args.limit)
    elif args.command == "method":
        result = client.search_by_method(args.method, limit=args.limit)
    elif args.command == "polymer":
        result = client.get_polymer_entities(args.pdb_id)
    elif args.command == "assembly":
        result = client.get_assembly(args.pdb_id, args.assembly_id)
    elif args.command == "resolution":
        result = client.search_by_resolution(args.max_resolution, limit=args.limit)
    else:
        parser.print_help()
        sys.exit(1)

    write_output(result, args.output)
