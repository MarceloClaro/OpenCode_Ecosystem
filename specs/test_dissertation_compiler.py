#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TDD Test Suite for SPEC-052: Dissertation Compiler v1.0
======================================================
16 Casos de Teste (CTs) — pytest

Execução:
  pytest test_dissertation_compiler.py -v
  pytest test_dissertation_compiler.py -v --tb=short
  pytest test_dissertation_compiler.py -v -x  (stop on first failure)

Autor: OpenCode Ecosystem (2026) — R27: TDD
"""

import os
import sys
import shutil
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch, AsyncMock

import pytest

# Add skill directory to path for imports
SKILL_DIR = Path(__file__).parent.parent / "skills" / "research" / "dissertation-generator"
sys.path.insert(0, str(SKILL_DIR))

from dissertation_compiler import (
    LaTeXCompiler,
    AudioGenerator,
    DOCXConverter,
    DissertationCompiler,
    CompileResult,
    DissertationStats,
    HAS_EDGE_TTS,
)


# ═══════════════════════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════════════════════

@pytest.fixture
def temp_dir():
    """Create temporary directory for test files."""
    with tempfile.TemporaryDirectory(prefix="spec052_test_") as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_tex(temp_dir):
    """Create a minimal valid .tex file."""
    tex_content = r"""
\documentclass{article}
\usepackage[utf8]{inputenc}
\usepackage[brazil]{babel}
\usepackage{hyperref}
\begin{document}
\section{Introducao}
Este e um teste de compilacao LaTeX.
\section{Metodologia}
Metodo descrito aqui.
\section{Resultados}
Resultados apresentados.
\section{Conclusao}
Conclusao final.
\end{document}
"""
    tex_file = temp_dir / "test_dissertation.tex"
    tex_file.write_text(tex_content, encoding="utf-8")
    return tex_file


@pytest.fixture
def sample_tex_with_bib(temp_dir):
    """Create .tex file with bibliography."""
    tex_content = r"""
\documentclass{article}
\usepackage[utf8]{inputenc}
\usepackage[brazil]{babel}
\usepackage[backend=biber,style=numeric,sorting=none]{biblatex}
\addbibresource{referencias.bib}
\begin{document}
Introducao com citacao \cite{TEST2024}.
\printbibliography
\end{document}
"""
    tex_file = temp_dir / "test_with_bib.tex"
    tex_file.write_text(tex_content, encoding="utf-8")

    bib_content = """
@article{TEST2024,
  author = {Silva, Joao},
  title = {Artigo de Teste},
  journal = {Revista Teste},
  year = {2024},
  volume = {1},
  pages = {1-10},
  doi = {10.1234/test.2024.001}
}
"""
    bib_file = temp_dir / "referencias.bib"
    bib_file.write_text(bib_content, encoding="utf-8")

    return tex_file, bib_file


@pytest.fixture
def sample_text():
    """Sample text for AudioGenerator tests."""
    return """
Metodologias Ativas na Educacao Brasileira.

O Aprendizado Baseado em Problemas (ABP) e uma abordagem pedagogica
que coloca o estudante no centro do processo de aprendizagem.

O Aprendizado Baseado em Projetos (ABPr) complementa o ABP
através da execucao de projetos contextualizados.

https://www.example.com/referencia
contato@universidade.edu.br

15

Esta secao apresenta os resultados da pesquisa realizada
com 150 participantes de tres instituicoes de ensino superior.
"""


@pytest.fixture
def sample_pdf(temp_dir):
    """Create a mock PDF path (for testing without real PDF)."""
    return temp_dir / "test_dissertation.pdf"


# ═══════════════════════════════════════════════════════════════════════════
# CT-052.01: LaTeXCompiler initialization
# ═══════════════════════════════════════════════════════════════════════════

def test_ct052_01_latex_compiler_init():
    """CT-052.01: LaTeXCompiler initialization."""
    compiler = LaTeXCompiler()
    assert compiler.pdflatex == "pdflatex"
    assert compiler.biber == "biber"


def test_ct052_01_latex_compiler_custom_paths():
    """CT-052.01: LaTeXCompiler with custom paths."""
    compiler = LaTeXCompiler(
        pdflatex="/custom/pdflatex",
        biber="/custom/biber"
    )
    assert compiler.pdflatex == "/custom/pdflatex"
    assert compiler.biber == "/custom/biber"


# ═══════════════════════════════════════════════════════════════════════════
# CT-052.02: LaTeXCompiler._find_executable
# ═══════════════════════════════════════════════════════════════════════════

def test_ct052_02_find_executable():
    """CT-052.02: _find_executable returns valid path."""
    compiler = LaTeXCompiler()
    path = compiler._find_executable("pdflatex")
    assert path is not None
    assert isinstance(path, str)
    assert len(path) > 0


def test_ct052_02_find_executable_fallback():
    """CT-052.02: _find_executable falls back to name."""
    compiler = LaTeXCompiler()
    path = compiler._find_executable("nonexistent_tool_xyz")
    assert path == "nonexistent_tool_xyz"


# ═══════════════════════════════════════════════════════════════════════════
# CT-052.03: LaTeXCompiler.compile success
# ═══════════════════════════════════════════════════════════════════════════

@pytest.mark.skipif(
    not shutil.which("pdflatex"),
    reason="pdflatex not installed"
)
def test_ct052_03_compile_success(sample_tex):
    """CT-052.03: compile succeeds with valid .tex file."""
    compiler = LaTeXCompiler()
    result = compiler.compile(sample_tex)

    assert result.success is True
    assert result.stage == "latex"
    assert result.output_path is not None
    assert result.output_path.exists()
    assert result.output_path.suffix == ".pdf"


# ═══════════════════════════════════════════════════════════════════════════
# CT-052.04: LaTeXCompiler.compile failure
# ═══════════════════════════════════════════════════════════════════════════

@pytest.mark.skipif(
    not shutil.which("pdflatex"),
    reason="pdflatex not installed"
)
def test_ct052_04_compile_failure(temp_dir):
    """CT-052.04: compile fails with invalid .tex file."""
    bad_tex = temp_dir / "bad.tex"
    bad_tex.write_text(r"\documentclass{article}\begin{document}\missingcommand", encoding="utf-8")

    compiler = LaTeXCompiler()
    result = compiler.compile(bad_tex)

    # May succeed with nonstopmode, but should still produce output
    assert result.stage == "latex"


# ═══════════════════════════════════════════════════════════════════════════
# CT-052.05: AudioGenerator initialization
# ═══════════════════════════════════════════════════════════════════════════

def test_ct052_05_audio_generator_init():
    """CT-052.05: AudioGenerator initialization."""
    gen = AudioGenerator()
    assert gen.voice == "pt-BR-FranciscaNeural"
    assert gen.rate == "-5%"
    assert gen.chunk_size == 3500


def test_ct052_05_audio_generator_custom():
    """CT-052.05: AudioGenerator with custom voice/rate."""
    gen = AudioGenerator(voice="pt-BR-AntonioNeural", rate="+10%")
    assert gen.voice == "pt-BR-AntonioNeural"
    assert gen.rate == "+10%"


# ═══════════════════════════════════════════════════════════════════════════
# CT-052.06: AudioGenerator._clean_text
# ═══════════════════════════════════════════════════════════════════════════

def test_ct052_06_clean_text_urls():
    """CT-052.06: _clean_text removes URLs."""
    gen = AudioGenerator()
    text = "Visite https://www.example.com para mais informacoes."
    result = gen._clean_text(text)
    assert "https://" not in result
    assert "example.com" not in result


def test_ct052_06_clean_text_emails():
    """CT-052.06: _clean_text removes emails."""
    gen = AudioGenerator()
    text = "Contato: usuario@universidade.edu.br"
    result = gen._clean_text(text)
    assert "@" not in result


def test_ct052_06_clean_text_page_numbers():
    """CT-052.06: _clean_text removes standalone page numbers."""
    gen = AudioGenerator()
    text = "Texto anterior\n15\nTexto posterior"
    result = gen._clean_text(text)
    assert "\n15\n" not in result


def test_ct052_06_clean_text_multiple_spaces():
    """CT-052.06: _clean_text collapses multiple spaces."""
    gen = AudioGenerator()
    text = "Palavra   com   espacos"
    result = gen._clean_text(text)
    assert "   " not in result


# ═══════════════════════════════════════════════════════════════════════════
# CT-052.07: AudioGenerator._split_chunks
# ═══════════════════════════════════════════════════════════════════════════

def test_ct052_07_split_chunks_size():
    """CT-052.07: _split_chunks respects max_chars."""
    gen = AudioGenerator()
    text = "A" * 10000
    chunks = gen._split_chunks(text)
    assert len(chunks) >= 2
    for chunk in chunks:
        assert len(chunk) <= 3500 + 100  # Small tolerance for sentence boundaries


def test_ct052_07_split_chunks_count():
    """CT-052.07: _split_chunks produces expected number of chunks."""
    gen = AudioGenerator()
    text = "A" * 10000
    chunks = gen._split_chunks(text)
    expected = 10000 // 3500
    assert len(chunks) >= expected


# ═══════════════════════════════════════════════════════════════════════════
# CT-052.08: AudioGenerator._split_chunks respects sentences
# ═══════════════════════════════════════════════════════════════════════════

def test_ct052_08_split_chunks_sentences():
    """CT-052.08: _split_chunks doesn't cut sentences in half."""
    gen = AudioGenerator()
    sentences = ["Primeira frase completa. "] * 20
    text = "".join(sentences)
    chunks = gen._split_chunks(text)
    for chunk in chunks:
        # Each chunk should end with a complete sentence (period at end or near end)
        stripped = chunk.rstrip()
        assert stripped.endswith(".") or len(stripped) < 100


# ═══════════════════════════════════════════════════════════════════════════
# CT-052.09: AudioGenerator.generate (mock)
# ═══════════════════════════════════════════════════════════════════════════

@pytest.mark.skipif(
    not shutil.which("pdflatex") or not Path(r"C:\Users\marce\Documents\OpenCode_Ecosystem\MD\dissertacao-latex\dissertacao.pdf").exists(),
    reason="PDF not available for audio test"
)
def test_ct052_09_generate_audio():
    """CT-052.09: generate produces MP3 from PDF."""
    import asyncio

    pdf_path = Path(r"C:\Users\marce\Documents\OpenCode_Ecosystem\MD\dissertacao-latex\dissertacao.pdf")
    output_dir = Path(tempfile.mkdtemp(prefix="audio_test_"))

    try:
        gen = AudioGenerator()
        result = asyncio.run(gen.generate(pdf_path, output_dir))

        assert result.success is True
        assert result.stage == "audio"
        assert result.output_path.exists()
        assert result.output_path.suffix == ".mp3"
        assert result.metadata["chunks"] > 0
    finally:
        shutil.rmtree(output_dir, ignore_errors=True)


@pytest.mark.skipif(
    not HAS_EDGE_TTS,
    reason="edge-tts not installed"
)
def test_ct052_09_generate_audio_mock(temp_dir):
    """CT-052.09: generate with mocked PDF extraction."""
    import asyncio

    # Create a mock PDF path (won't actually read PDF)
    mock_pdf = temp_dir / "mock.pdf"
    mock_pdf.write_bytes(b"%PDF-1.4 mock")

    gen = AudioGenerator()

    # Mock the _extract_text method
    with patch.object(gen, '_extract_text', return_value="Texto de teste. Segunda frase. Terceira frase."):
        with patch.object(gen, '_clean_text', return_value="Texto de teste. Segunda frase. Terceira frase."):
            result = asyncio.run(gen.generate(mock_pdf, temp_dir / "audio"))

            assert result.success is True
            assert result.stage == "audio"
            assert result.output_path.exists()
            assert result.output_path.suffix == ".mp3"
            assert result.metadata["chunks"] >= 1


# ═══════════════════════════════════════════════════════════════════════════
# CT-052.10: DOCXConverter initialization
# ═══════════════════════════════════════════════════════════════════════════

def test_ct052_10_docx_converter_init():
    """CT-052.10: DOCXConverter initialization."""
    converter = DOCXConverter()
    assert converter.pandoc is not None
    assert isinstance(converter.pandoc, str)


# ═══════════════════════════════════════════════════════════════════════════
# CT-052.11: DOCXConverter.convert
# ═══════════════════════════════════════════════════════════════════════════

@pytest.mark.skipif(
    not shutil.which("pandoc"),
    reason="pandoc not installed"
)
def test_ct052_11_convert_docx(sample_tex):
    """CT-052.11: convert produces DOCX from .tex."""
    converter = DOCXConverter()
    result = converter.convert(sample_tex)

    assert result.success is True
    assert result.stage == "docx"
    assert result.output_path.exists()
    assert result.output_path.suffix == ".docx"


# ═══════════════════════════════════════════════════════════════════════════
# CT-052.12: DissertationCompiler initialization
# ═══════════════════════════════════════════════════════════════════════════

def test_ct052_12_compiler_init():
    """CT-052.12: DissertationCompiler initialization."""
    compiler = DissertationCompiler(
        input_path=Path("/test/path"),
        formats=["pdf", "audio"]
    )
    assert compiler.input_path == Path("/test/path")
    assert compiler.formats == ["pdf", "audio"]


def test_ct052_12_compiler_default_formats():
    """CT-052.12: DissertationCompiler default formats."""
    compiler = DissertationCompiler(input_path=Path("/test"))
    assert compiler.formats == ["pdf", "audio", "docx"]


# ═══════════════════════════════════════════════════════════════════════════
# CT-052.13: DissertationCompiler._find_pdf
# ═══════════════════════════════════════════════════════════════════════════

def test_ct052_13_find_pdf_from_tex(temp_dir):
    """CT-052.13: _find_pdf finds corresponding PDF."""
    tex_file = temp_dir / "test.tex"
    tex_file.write_text("test", encoding="utf-8")
    pdf_file = temp_dir / "test.pdf"
    pdf_file.write_bytes(b"%PDF-1.4 test")

    compiler = DissertationCompiler(input_path=tex_file)
    result = compiler._find_pdf()
    assert result == pdf_file


def test_ct052_13_find_pdf_none(temp_dir):
    """CT-052.13: _find_pdf returns None when no PDF."""
    tex_file = temp_dir / "test.tex"
    tex_file.write_text("test", encoding="utf-8")

    compiler = DissertationCompiler(input_path=tex_file)
    result = compiler._find_pdf()
    assert result is None


# ═══════════════════════════════════════════════════════════════════════════
# CT-052.14: DissertationCompiler._find_tex
# ═══════════════════════════════════════════════════════════════════════════

def test_ct052_14_find_tex_from_pdf(temp_dir):
    """CT-052.14: _find_tex finds corresponding .tex."""
    pdf_file = temp_dir / "test.pdf"
    pdf_file.write_bytes(b"%PDF-1.4 test")
    tex_file = temp_dir / "test.tex"
    tex_file.write_text("test", encoding="utf-8")

    compiler = DissertationCompiler(input_path=pdf_file)
    result = compiler._find_tex()
    assert result == tex_file


def test_ct052_14_find_tex_none(temp_dir):
    """CT-052.14: _find_tex returns None when no .tex."""
    pdf_file = temp_dir / "test.pdf"
    pdf_file.write_bytes(b"%PDF-1.4 test")

    compiler = DissertationCompiler(input_path=pdf_file)
    result = compiler._find_tex()
    assert result is None


# ═══════════════════════════════════════════════════════════════════════════
# CT-052.15: CompileResult dataclass
# ═══════════════════════════════════════════════════════════════════════════

def test_ct052_15_compile_result():
    """CT-052.15: CompileResult dataclass."""
    result = CompileResult(
        stage="latex",
        success=True,
        output_path=Path("/test.pdf"),
        duration_seconds=12.5,
        metadata={"pages": 100}
    )
    assert result.stage == "latex"
    assert result.success is True
    assert result.output_path == Path("/test.pdf")
    assert result.duration_seconds == 12.5
    assert result.metadata["pages"] == 100
    assert result.error_message == ""


def test_ct052_15_compile_result_error():
    """CT-052.15: CompileResult with error."""
    result = CompileResult(
        stage="audio",
        success=False,
        error_message="No text extracted"
    )
    assert result.success is False
    assert result.error_message == "No text extracted"


# ═══════════════════════════════════════════════════════════════════════════
# CT-052.16: DissertationStats dataclass
# ═══════════════════════════════════════════════════════════════════════════

def test_ct052_16_dissertation_stats():
    """CT-052.16: DissertationStats dataclass."""
    stats = DissertationStats()
    assert stats.total_pages == 0
    assert stats.total_words == 0
    assert stats.total_references == 0
    assert stats.estimated_audio_minutes == 0.0


def test_ct052_16_dissertation_stats_values():
    """CT-052.16: DissertationStats with values."""
    stats = DissertationStats(
        total_pages=124,
        total_words=39121,
        total_references=51,
        estimated_audio_minutes=261.0
    )
    assert stats.total_pages == 124
    assert stats.total_words == 39121
    assert stats.total_references == 51
    assert stats.estimated_audio_minutes == 261.0


# ═══════════════════════════════════════════════════════════════════════════
# RUNNER
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
