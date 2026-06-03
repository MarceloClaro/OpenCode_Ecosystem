"""TDD tests for domain-shift-camada1b system skill (has scripts)."""

import pathlib
import sys

SKILL_DIR = pathlib.Path(__file__).parent.parent
SKILL_MD = SKILL_DIR / "SKILL.md"
SCRIPTS_DIR = SKILL_DIR / "scripts"


def test_skill_md_exists():
    assert SKILL_MD.exists(), f"SKILL.md not found at {SKILL_MD}"


def test_has_category():
    content = SKILL_MD.read_text(encoding="utf-8")
    assert "category:" in content, "SKILL.md must declare a category in frontmatter"


def test_has_version():
    content = SKILL_MD.read_text(encoding="utf-8")
    assert "version:" in content, "SKILL.md must declare a version in frontmatter"


def test_module_imports():
    """Validates that domain_shift_audit.py imports cleanly."""
    sys.path.insert(0, str(SCRIPTS_DIR))
    try:
        import domain_shift_audit  # type: ignore
        assert domain_shift_audit is not None
    finally:
        sys.path.remove(str(SCRIPTS_DIR))


def test_key_functions_exist():
    """Validates key functions are importable from domain_shift_audit."""
    sys.path.insert(0, str(SCRIPTS_DIR))
    try:
        import domain_shift_audit as dsa  # type: ignore

        assert hasattr(dsa, "jaccard"), "jaccard function missing"
        assert hasattr(dsa, "decompor_variancia"), "decompor_variancia missing"
        assert hasattr(dsa, "bootstrap_limiar_jaccard"), "bootstrap_limiar_jaccard missing"
        assert hasattr(dsa, "aplicar_regra_decisao"), "aplicar_regra_decisao missing"
        assert hasattr(dsa, "gerar_relatorio_completo"), "gerar_relatorio_completo missing"
        assert hasattr(dsa, "Documento"), "Documento dataclass missing"
        assert hasattr(dsa, "PadraoInstituicao"), "PadraoInstituicao dataclass missing"
    finally:
        sys.path.remove(str(SCRIPTS_DIR))


def test_documento_dataclass():
    """Validates Documento dataclass creation and fields."""
    sys.path.insert(0, str(SCRIPTS_DIR))
    try:
        from domain_shift_audit import Documento  # type: ignore

        doc = Documento(
            id="DOC-001",
            texto="art. 5º, CF. RE 001. ADI 0001.",
            instituicao="STF",
            ano=2023,
            templates_extraidos={"art. 5º, CF", "RE 001", "ADI 0001"},
        )
        assert doc.instituicao == "STF"
        assert doc.ano == 2023
        assert doc.id == "DOC-001"
        assert "art. 5º, CF" in doc.templates_extraidos
    finally:
        sys.path.remove(str(SCRIPTS_DIR))
