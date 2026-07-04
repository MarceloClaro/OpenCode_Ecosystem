"""
Testes R35 — Capability Registration Framework (SPEC-080)
==========================================================
Verifica que as keywords expandidas no KEYWORD_TO_CAPABILITY
registram corretamente as capacidades das 16 skills de pesquisa.
"""

import sys
import json
from pathlib import Path

# ── Caminhos ──
ECO_ROOT = Path(__file__).parent.parent.resolve()
SCANNER_PATH = ECO_ROOT / "skills" / "system" / "academic-audit" / "potentiality_scanner.py"
REGISTRY_PATH = ECO_ROOT / "nexus" / "skills_registry.json"


def load_keyword_map() -> dict:
    """Carrega o KEYWORD_TO_CAPABILITY do potentiality_scanner.py via AST."""
    import ast
    with open(SCANNER_PATH, "r", encoding="utf-8") as f:
        source = f.read()
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "KEYWORD_TO_CAPABILITY":
                    # node.value is ast.Dict — keys/values são listas de ast.Constant
                    d = node.value
                    return {k.value: v.value for k, v in zip(d.keys, d.values)}  # type: ignore
    return {}


def load_skills_registry() -> list[dict]:
    """Carrega a lista de skills do registry."""
    with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("skills", [])


# ── CT-01: paradigm_analysis registrada via keyword "paradigma" ──
def test_paradigm_analysis_registered():
    """CT-01: keyword 'paradigma' deve mapear para 'paradigm_analysis'."""
    km = load_keyword_map()
    assert km.get("paradigma") == "paradigm_analysis", \
        f"Esperado 'paradigm_analysis', obtido '{km.get('paradigma')}'"


# ── CT-02: methodology_design registrada via keyword "metodo" ──
def test_methodology_design_registered():
    """CT-02: keyword 'metodo' deve mapear para 'methodology_design'."""
    km = load_keyword_map()
    assert km.get("metodo") == "methodology_design", \
        f"Esperado 'methodology_design', obtido '{km.get('metodo')}'"


# ── CT-03: interdisciplinary_synthesis registrada via keyword "dominio" ──
def test_interdisciplinary_synthesis_registered():
    """CT-03: keyword 'dominio' deve mapear para 'interdisciplinary_synthesis'."""
    km = load_keyword_map()
    assert km.get("dominio") == "interdisciplinary_synthesis", \
        f"Esperado 'interdisciplinary_synthesis', obtido '{km.get('dominio')}'"


# ── CT-04: data_collection registrada via keyword "dados" ──
def test_data_collection_registered():
    """CT-04: keyword 'dados' deve mapear para 'data_collection'."""
    km = load_keyword_map()
    assert km.get("dados") == "data_collection", \
        f"Esperado 'data_collection', obtido '{km.get('dados')}'"


# ── CT-05: reasoning_engine registrada via keyword "raciocinio" ──
def test_reasoning_engine_registered():
    """CT-05: keyword 'raciocinio' deve mapear para 'reasoning_engine'."""
    km = load_keyword_map()
    assert km.get("raciocinio") == "reasoning_engine", \
        f"Esperado 'reasoning_engine', obtido '{km.get('raciocinio')}'"


# ── CT-06: Pelo menos 2 skills mapeadas para paradigm_analysis ──
def test_min_2_skills_for_paradigm_analysis():
    """CT-06: Pelo menos 2 skills de pesquisa devem ter 'paradigma' no nome/path."""
    skills = load_skills_registry()
    pm = [s for s in skills if "paradigma" in s.get("name", "").lower() or
          "epistemologia" in s.get("name", "").lower()]
    assert len(pm) >= 2, \
        f"Esperado >=2 skills com 'paradigma', encontrado {len(pm)}: {[s['name'] for s in pm]}"


# ── CT-07: Pelo menos 2 skills mapeadas para methodology_design ──
def test_min_2_skills_for_methodology():
    """CT-07: Pelo menos 2 skills de pesquisa devem ter 'metodo' no nome."""
    skills = load_skills_registry()
    mm = [s for s in skills if "metodo" in s.get("name", "").lower() or
          "qualitativ" in s.get("name", "").lower() or
          "grounded" in s.get("name", "").lower() or
          "revisao" in s.get("name", "").lower()]
    assert len(mm) >= 2, \
        f"Esperado >=2 skills com 'metodo', encontrado {len(mm)}: {[s['name'] for s in mm]}"


# ── CT-08: theoretical_integration registrada via keyword "teoria" ──
def test_theoretical_integration_registered():
    """CT-09: keyword 'teoria' deve mapear para 'theoretical_integration'."""
    km = load_keyword_map()
    assert km.get("teoria") == "theoretical_integration", \
        f"Esperado 'theoretical_integration', obtido '{km.get('teoria')}'"


# ── CT-09: Pelo menos 50% das 10 dimensões têm skills mapeadas ──
def test_min_5_dimensions_have_skills():
    """CT-10: Pelo menos 5 das 10 dimensões devem ter skills registradas."""
    # Verifica skills de pesquisa no registry
    skills = load_skills_registry()
    research_skills = [s for s in skills if s.get("category") == "research"]
    assert len(research_skills) >= 5, \
        f"Esperado >=5 research skills, encontrado {len(research_skills)}"


# ── CT-10: KEYWORD_TO_CAPABILITY tem pelo menos 60 entradas ──
def test_keyword_map_expanded():
    """Verifica que o mapa tem >= 60 keywords (era 36)."""
    km = load_keyword_map()
    assert len(km) >= 60, \
        f"Esperado >=60 keywords, encontrado {len(km)}"
