"""
Ontology Generator — Geração Automática de Ontologias para Grafos.

Inspirado pelo OntologyGenerator do MiroFish-Offline (ontology_generator.py).
Modos: generate, validate, schema.

Uso:
    python generate_ontology.py generate --text <file> --requirement "<req>"
    python generate_ontology.py validate --input ontology.json
    python generate_ontology.py schema --input ontology.json --output schema.sql
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# ─── Configurações ────────────────────────────────────────────────
MAX_TEXT_LENGTH = 50000
MAX_ENTITY_TYPES = 10
MAX_EDGE_TYPES = 10
PERSON_FALLBACK = {
    "name": "Person",
    "description": "Any individual person not fitting other specific person types.",
    "attributes": [
        {"name": "full_name", "type": "text", "description": "Full name of the person"},
        {"name": "role", "type": "text", "description": "Role or occupation"},
    ],
    "examples": ["ordinary citizen", "anonymous netizen"],
}
ORGANIZATION_FALLBACK = {
    "name": "Organization",
    "description": "Any organization not fitting other specific organization types.",
    "attributes": [
        {"name": "org_name", "type": "text", "description": "Name of the organization"},
        {"name": "org_type", "type": "text", "description": "Type of organization"},
    ],
    "examples": ["small business", "community group"],
}


# ─── System Prompt ────────────────────────────────────────────────
ONTOLOGY_SYSTEM_PROMPT = """You are a professional knowledge graph ontology design expert. Your task is to analyze given text content and simulation requirements, and design entity types and relationship types suitable for **social media opinion simulation**.

**Important: You must output valid JSON format data, do not output anything else.**

## Core Task Background

We are building a **social media opinion simulation system**. In this system:
- Each entity is an "account" or "subject" that can voice, interact, and spread information on social media
- Entities influence each other, retweet, comment, and respond
- We need to simulate the reactions of various parties in opinion events and information dissemination paths

Therefore, **entities must be real-world entities that can voice and interact on social media**:

**Can be**:
- Specific individuals (public figures, stakeholders, opinion leaders, experts, ordinary people)
- Companies and enterprises (including their official accounts)
- Organizations (universities, associations, NGOs, unions, etc.)
- Government departments and regulatory agencies
- Media institutions (newspapers, TV stations, self-media, websites)
- Social media platforms themselves
- Specific group representatives (such as alumni associations, fan groups, rights protection groups, etc.)

**Cannot be**:
- Abstract concepts (such as "public opinion", "emotion", "trend")
- Topics/subjects (such as "academic integrity", "education reform")
- Views/attitudes (such as "supporters", "opponents")

## Output Format

```json
{
    "entity_types": [
        {
            "name": "Entity type name (English, PascalCase)",
            "description": "Brief description (English, no more than 100 characters)",
            "attributes": [{"name": "attribute_name", "type": "text", "description": "Description"}],
            "examples": ["Example 1", "Example 2"]
        }
    ],
    "edge_types": [
        {
            "name": "UPPER_SNAKE_CASE",
            "description": "Brief description",
            "source_targets": [{"source": "SourceType", "target": "TargetType"}],
            "attributes": []
        }
    ],
    "analysis_summary": "Brief analysis of text content"
}
```

## Design Guidelines

### Entity Types — Exactly 10 required
### Relationship Types — 6-10 required
### Fallback Types — Last 2 must be Person and Organization
"""


# ─── OntologyGenerator ────────────────────────────────────────────
class OntologyGenerator:
    """Geração de ontologias a partir de textos"""

    def __init__(self, use_mock: bool = True):
        self.use_mock = use_mock

    def generate(
        self,
        document_texts: List[str],
        simulation_requirement: str,
        additional_context: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Gera ontologia (mock — sem LLM real)"""
        if self.use_mock:
            return self._mock_generate(document_texts, simulation_requirement)
        raise NotImplementedError("Modo LLM requer LLMClient configurado")

    def _mock_generate(self, texts: List[str], requirement: str) -> Dict[str, Any]:
        """Gera ontologia de demonstração baseada em palavras-chave"""
        combined = "\n".join(texts)[:500].lower()
        topics = {"academic": ["student", "professor", "university", "education", "research"],
                  "regulation": ["regulation", "government", "law", "policy", "agency"],
                  "tech": ["technology", "ai", "software", "startup", "innovation"],
                  "health": ["doctor", "hospital", "patient", "health", "medical"]}

        detected = [t for t, kw in topics.items() if any(k in combined for k in kw)]
        domain = detected[0] if detected else "general"

        ontology_templates = {
            "academic": {
                "entity_types": [
                    {"name": "Student", "description": "A student enrolled in an educational institution",
                     "attributes": [{"name": "full_name", "type": "text", "description": "Full name"}],
                     "examples": ["Alice Chen"]},
                    {"name": "Professor", "description": "A professor or academic researcher",
                     "attributes": [{"name": "full_name", "type": "text"}, {"name": "department", "type": "text"}],
                     "examples": ["Dr. Smith"]},
                    {"name": "University", "description": "An educational institution",
                     "attributes": [{"name": "org_name", "type": "text"}, {"name": "location", "type": "text"}],
                     "examples": ["State University"]},
                    {"name": "Researcher", "description": "A research professional",
                     "attributes": [{"name": "full_name", "type": "text"}, {"name": "field", "type": "text"}],
                     "examples": ["Dr. Johnson"]},
                    {"name": "Department", "description": "An academic department",
                     "attributes": [{"name": "dept_name", "type": "text"}],
                     "examples": ["Computer Science Dept"]},
                    {"name": "ResearchGroup", "description": "A research group or lab",
                     "attributes": [{"name": "group_name", "type": "text"}, {"name": "focus_area", "type": "text"}],
                     "examples": ["AI Lab"]},
                    {"name": "FundingAgency", "description": "A research funding organization",
                     "attributes": [{"name": "agency_name", "type": "text"}],
                     "examples": ["CNPq"]},
                    {"name": "Journalist", "description": "A media professional covering academia",
                     "attributes": [{"name": "full_name", "type": "text"}, {"name": "outlet", "type": "text"}],
                     "examples": ["Maria Santos"]},
                    PERSON_FALLBACK,
                    ORGANIZATION_FALLBACK,
                ],
                "edge_types": [
                    {"name": "STUDIES_AT", "description": "Student enrolled at institution",
                     "source_targets": [{"source": "Student", "target": "University"}], "attributes": []},
                    {"name": "WORKS_FOR", "description": "Employment relationship",
                     "source_targets": [{"source": "Professor", "target": "University"},
                                        {"source": "Researcher", "target": "ResearchGroup"}],
                     "attributes": []},
                    {"name": "AFFILIATED_WITH", "description": "Affiliation relationship",
                     "source_targets": [{"source": "Researcher", "target": "University"},
                                        {"source": "ResearchGroup", "target": "Department"}],
                     "attributes": []},
                    {"name": "COLLABORATES_WITH", "description": "Research collaboration",
                     "source_targets": [{"source": "Professor", "target": "Researcher"}],
                     "attributes": []},
                    {"name": "FUNDED_BY", "description": "Funding relationship",
                     "source_targets": [{"source": "ResearchGroup", "target": "FundingAgency"},
                                        {"source": "University", "target": "FundingAgency"}],
                     "attributes": []},
                    {"name": "REPORTS_ON", "description": "Media coverage",
                     "source_targets": [{"source": "Journalist", "target": "University"},
                                        {"source": "Journalist", "target": "ResearchGroup"}],
                     "attributes": []},
                    {"name": "COMMENTS_ON", "description": "Public commentary",
                     "source_targets": [{"source": "Professor", "target": "ResearchGroup"},
                                        {"source": "Student", "target": "University"}],
                     "attributes": []},
                ],
                "analysis_summary": f"Academic domain ontology for: {requirement}",
            },
            "regulation": {
                "entity_types": [
                    {"name": "GovernmentAgency", "description": "A government regulatory body",
                     "attributes": [{"name": "agency_name", "type": "text"}, {"name": "jurisdiction", "type": "text"}],
                     "examples": ["Ministry of Science"]},
                    {"name": "Company", "description": "A business enterprise",
                     "attributes": [{"name": "org_name", "type": "text"}, {"name": "sector", "type": "text"}],
                     "examples": ["TechCorp"]},
                    {"name": "Executive", "description": "A corporate executive",
                     "attributes": [{"name": "full_name", "type": "text"}, {"name": "title", "type": "text"}],
                     "examples": ["CEO João"]},
                    {"name": "Lawyer", "description": "A legal professional",
                     "attributes": [{"name": "full_name", "type": "text"}, {"name": "specialization", "type": "text"}],
                     "examples": ["Dr. Legal"]},
                    {"name": "MediaOutlet", "description": "A news organization",
                     "attributes": [{"name": "org_name", "type": "text"}, {"name": "reach", "type": "text"}],
                     "examples": ["Major News"]},
                    {"name": "Expert", "description": "A domain expert or consultant",
                     "attributes": [{"name": "full_name", "type": "text"}, {"name": "expertise", "type": "text"}],
                     "examples": ["Dr. Specialist"]},
                    {"name": "NGO", "description": "A non-governmental organization",
                     "attributes": [{"name": "org_name", "type": "text"}, {"name": "cause", "type": "text"}],
                     "examples": ["Transparency Org"]},
                    {"name": "Citizen", "description": "An ordinary citizen or consumer",
                     "attributes": [{"name": "full_name", "type": "text"}, {"name": "occupation", "type": "text"}],
                     "examples": ["Ordinary Citizen"]},
                    PERSON_FALLBACK, ORGANIZATION_FALLBACK,
                ],
                "edge_types": [
                    {"name": "REGULATES", "description": "Regulatory authority over",
                     "source_targets": [{"source": "GovernmentAgency", "target": "Company"}],
                     "attributes": []},
                    {"name": "REPRESENTS", "description": "Legal representation",
                     "source_targets": [{"source": "Lawyer", "target": "Company"},
                                        {"source": "Lawyer", "target": "Citizen"}],
                     "attributes": []},
                    {"name": "REPORTS_ON", "description": "Media coverage",
                     "source_targets": [{"source": "MediaOutlet", "target": "Company"},
                                        {"source": "MediaOutlet", "target": "GovernmentAgency"}],
                     "attributes": []},
                    {"name": "EMPLOYS", "description": "Employment relationship",
                     "source_targets": [{"source": "Company", "target": "Executive"}],
                     "attributes": []},
                    {"name": "ADVISES", "description": "Expert advisory role",
                     "source_targets": [{"source": "Expert", "target": "GovernmentAgency"},
                                        {"source": "Expert", "target": "Company"}],
                     "attributes": []},
                    {"name": "ADVOCATES_FOR", "description": "Advocacy relationship",
                     "source_targets": [{"source": "NGO", "target": "Citizen"}],
                     "attributes": []},
                    {"name": "COMMENTS_ON", "description": "Public commentary",
                     "source_targets": [{"source": "Citizen", "target": "Company"},
                                        {"source": "Expert", "target": "Regulation"}],
                     "attributes": []},
                ],
                "analysis_summary": f"Regulatory domain ontology for: {requirement}",
            },
        }

        return ontology_templates.get(domain, ontology_templates["academic"])

    def validate(self, ontology: Dict[str, Any]) -> Dict[str, Any]:
        """Valida e pós-processa ontologia"""
        if "entity_types" not in ontology:
            ontology["entity_types"] = []
        if "edge_types" not in ontology:
            ontology["edge_types"] = []
        if "analysis_summary" not in ontology:
            ontology["analysis_summary"] = ""

        # Validar entity types
        for entity in ontology["entity_types"]:
            if "attributes" not in entity:
                entity["attributes"] = []
            if "examples" not in entity:
                entity["examples"] = []
            if len(entity.get("description", "")) > 100:
                entity["description"] = entity["description"][:97] + "..."

        # Validar edge types
        for edge in ontology["edge_types"]:
            if "source_targets" not in edge:
                edge["source_targets"] = []
            if "attributes" not in edge:
                edge["attributes"] = []

        # Garantir fallbacks
        entity_names = {e["name"] for e in ontology["entity_types"]}
        fallbacks = []
        if "Person" not in entity_names:
            fallbacks.append(PERSON_FALLBACK)
        if "Organization" not in entity_names:
            fallbacks.append(ORGANIZATION_FALLBACK)

        if fallbacks:
            current = len(ontology["entity_types"])
            needed = len(fallbacks)
            if current + needed > MAX_ENTITY_TYPES:
                to_remove = current + needed - MAX_ENTITY_TYPES
                ontology["entity_types"] = ontology["entity_types"][:-to_remove]
            ontology["entity_types"].extend(fallbacks)

        # Limitar quantidades
        ontology["entity_types"] = ontology["entity_types"][:MAX_ENTITY_TYPES]
        ontology["edge_types"] = ontology["edge_types"][:MAX_EDGE_TYPES]

        return ontology

    def generate_schema_sql(self, ontology: Dict[str, Any]) -> str:
        """Gera SQL de schema a partir da ontologia"""
        lines = [
            "-- Ontology Schema",
            f"-- Generated: {__import__('datetime').datetime.now().isoformat()}",
            "",
            "-- Entity Types Table",
            "CREATE TABLE IF NOT EXISTS ontology_entity_types (",
            "    name TEXT PRIMARY KEY,",
            "    description TEXT,",
            "    attributes TEXT,  -- JSON array",
            "    examples TEXT,    -- JSON array",
            "    is_fallback INTEGER DEFAULT 0",
            ");",
            "",
            "-- Edge Types Table",
            "CREATE TABLE IF NOT EXISTS ontology_edge_types (",
            "    name TEXT PRIMARY KEY,",
            "    description TEXT,",
            "    source_targets TEXT,  -- JSON array",
            "    attributes TEXT       -- JSON array",
            ");",
            "",
            "-- Insert Entity Types",
        ]
        for e in ontology.get("entity_types", []):
            is_fb = 1 if e["name"] in ("Person", "Organization") else 0
            lines.append(
                f"INSERT OR IGNORE INTO ontology_entity_types "
                f"VALUES ('{e['name']}', '{e.get('description', '')}', "
                f"'{json.dumps(e.get('attributes', []))}', "
                f"'{json.dumps(e.get('examples', []))}', {is_fb});"
            )

        lines.extend(["", "-- Insert Edge Types"])
        for e in ontology.get("edge_types", []):
            lines.append(
                f"INSERT OR IGNORE INTO ontology_edge_types "
                f"VALUES ('{e['name']}', '{e.get('description', '')}', "
                f"'{json.dumps(e.get('source_targets', []))}', "
                f"'{json.dumps(e.get('attributes', []))}');"
            )

        return "\n".join(lines)


# ─── CLI ──────────────────────────────────────────────────────────
def cmd_generate(args):
    text = Path(args.text).read_text(encoding="utf-8")
    if len(text) > MAX_TEXT_LENGTH:
        text = text[:MAX_TEXT_LENGTH] + f"\n\n...(truncated from {len(text)} chars)"

    gen = OntologyGenerator(use_mock=True)
    ontology = gen.generate([text], args.requirement)
    ontology = gen.validate(ontology)

    out_path = args.output or "ontology.json"
    Path(out_path).write_text(json.dumps(ontology, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n✅ Ontologia gerada: {out_path}")
    print(f"   Entity types: {len(ontology['entity_types'])}")
    print(f"   Edge types: {len(ontology['edge_types'])}")
    print(f"   Analysis: {ontology['analysis_summary'][:100]}")
    return ontology


def cmd_validate(args):
    ontology = json.loads(Path(args.input).read_text(encoding="utf-8"))
    gen = OntologyGenerator()
    result = gen.validate(ontology)

    issues = []
    if len(result["entity_types"]) != 10:
        issues.append(f"Entity types deve ser 10, tem {len(result['entity_types'])}")
    
    names = [e["name"] for e in result["entity_types"]]
    if "Person" not in names:
        issues.append("Fallback 'Person' ausente")
    if "Organization" not in names:
        issues.append("Fallback 'Organization' ausente")
    
    reserved = {"name", "uuid", "group_id", "created_at", "summary"}
    for e in result["entity_types"]:
        for a in e.get("attributes", []):
            if a["name"] in reserved:
                issues.append(f"Attributo reservado '{a['name']}' em {e['name']}")

    print(f"\n{'✅' if not issues else '❌'} Validação da ontologia: {args.input}")
    if issues:
        for i in issues:
            print(f"   ⚠️  {i}")
    else:
        print("   Ontologia válida ✅")
    print(f"   Entity types: {len(result['entity_types'])}")
    names_str = ", ".join(names)
    print(f"   Tipos: {names_str}")
    print(f"   Edge types: {len(result['edge_types'])}")
    return {"valid": len(issues) == 0, "issues": issues}


def cmd_schema(args):
    ontology = json.loads(Path(args.input).read_text(encoding="utf-8"))
    gen = OntologyGenerator()
    sql = gen.generate_schema_sql(ontology)
    out_path = args.output or "schema.sql"
    Path(out_path).write_text(sql, encoding="utf-8")
    print(f"\n✅ Schema SQL gerado: {out_path}")
    print(sql)
    return sql


def main():
    parser = argparse.ArgumentParser(description="Ontology Generator")
    sub = parser.add_subparsers(dest="mode", required=True)

    p_gen = sub.add_parser("generate")
    p_gen.add_argument("--text", required=True, help="Text file to analyze")
    p_gen.add_argument("--requirement", default="Generic simulation", help="Simulation requirement")
    p_gen.add_argument("--output", default="ontology.json", help="Output JSON path")
    p_gen.set_defaults(func=cmd_generate)

    p_val = sub.add_parser("validate")
    p_val.add_argument("--input", required=True, help="Ontology JSON file")
    p_val.set_defaults(func=cmd_validate)

    p_sch = sub.add_parser("schema")
    p_sch.add_argument("--input", required=True, help="Ontology JSON file")
    p_sch.add_argument("--output", default="schema.sql", help="Output SQL path")
    p_sch.set_defaults(func=cmd_schema)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    main()
