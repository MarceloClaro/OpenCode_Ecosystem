#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dissertation Compiler v1.0 — SPEC-052: Autonomous Academic Production
=====================================================================
Pipeline completo de compilação acadêmica:
  LaTeX → PDF → Áudio MP3 → DOCX

Uso:
  python dissertation_compiler.py --input ./dissertacao-latex/ --formats pdf,audio,docx
  python dissertation_compiler.py --input ./dissertacao.tex --formats pdf
  python dissertation_compiler.py --input ./dissertacao.pdf --formats audio,docx

Autor: OpenCode Ecosystem (2026) — R27: Dissertation Automation
Integração: SPEC-052 + marceloclaro + metacognitive_loop
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# Try imports with fallbacks
try:
    import pdfplumber
    HAS_PDFPLUMBER = True
except ImportError:
    HAS_PDFPLUMBER = False

try:
    import edge_tts
    HAS_EDGE_TTS = True
except ImportError:
    HAS_EDGE_TTS = False

try:
    from docx import Document
    HAS_PYTHON_DOCX = True
except ImportError:
    HAS_PYTHON_DOCX = False


BRAZIL_TZ = timezone.utc
SCRIPT_DIR = Path(__file__).parent


# ═══════════════════════════════════════════════════════════════════════════
# DATA CLASSES
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class CompileResult:
    """Resultado de uma etapa de compilação."""
    stage: str
    success: bool
    output_path: Optional[Path] = None
    error_message: str = ""
    duration_seconds: float = 0.0
    metadata: dict = field(default_factory=dict)


@dataclass
class DissertationStats:
    """Estatísticas da dissertação."""
    total_pages: int = 0
    total_chars: int = 0
    total_words: int = 0
    total_chapters: int = 0
    total_sections: int = 0
    total_tables: int = 0
    total_figures: int = 0
    total_references: int = 0
    estimated_audio_minutes: float = 0.0


# ═══════════════════════════════════════════════════════════════════════════
# LATEX COMPILER
# ═══════════════════════════════════════════════════════════════════════════

class LaTeXCompiler:
    """Compila arquivos LaTeX para PDF."""

    def __init__(self, pdflatex: str = "pdflatex", biber: str = "biber",
                 pdflatex_path: str = None, biber_path: str = None):
        self.pdflatex = pdflatex_path or pdflatex
        self.biber = biber_path or biber

    def _find_executable(self, name: str) -> str:
        """Encontra executável no PATH ou em locais conhecidos."""
        # Check PATH
        result = shutil.which(name)
        if result:
            return result

        # Check common Windows locations
        common_paths = [
            r"C:\Program Files\MiKTeX\miktex\bin\x64\{}.exe",
            r"C:\Program Files\MiKTeX\miktex\bin\{}.exe",
            r"C:\Program Files\texlive\2024\bin\win32\{}.exe",
            r"C:\texlive\2024\bin\win32\{}.exe",
        ]
        for pattern in common_paths:
            path = pattern.format(name)
            if os.path.exists(path):
                return path

        return name  # Fallback to name (will fail if not found)

    def _find_bibliography_tool(self) -> str:
        """Auto-detecta ferramenta de bibliografia disponivel: biber > bibtex."""
        biber_path = self._find_executable("biber")
        # Verifica se biber realmente funciona (pode estar presente mas sem deps Perl)
        if biber_path and biber_path != "biber":
            try:
                subprocess.run([biber_path, "--version"],
                               capture_output=True, text=True, timeout=10)
                return biber_path
            except (subprocess.SubprocessError, OSError):
                pass
        # Fallback para bibtex
        bibtex_path = self._find_executable("bibtex")
        if bibtex_path and bibtex_path != "bibtex":
            return bibtex_path
        return "bibtex"  # tentativa final (pode falhar)

    def compile(self, tex_file: Path, timeout: int = 300) -> CompileResult:
        """Executa pipeline completo: pdflatex → biber/bibtex → pdflatex → pdflatex."""
        start = datetime.now(BRAZIL_TZ)
        work_dir = tex_file.parent
        base_name = tex_file.stem

        pdflatex = self._find_executable("pdflatex")
        bib_tool = self._find_bibliography_tool()
        use_biber = "biber" in bib_tool

        # Step 1: pdflatex
        result = subprocess.run(
            [pdflatex, "-interaction=nonstopmode", "-halt-on-error", tex_file.name],
            cwd=work_dir, capture_output=True, text=True, timeout=timeout
        )
        if result.returncode != 0 and "Fatal error" in result.stdout:
            return CompileResult(
                stage="latex", success=False,
                error_message=f"pdflatex failed: {result.stdout[-500:]}",
                duration_seconds=(datetime.now(BRAZIL_TZ) - start).total_seconds()
            )

        # Step 2: biber/bibtex (if bibliography exists)
        bbl_file = work_dir / f"{base_name}.bbl"
        if not bbl_file.exists():
            subprocess.run(
                [bib_tool, base_name],
                cwd=work_dir, capture_output=True, text=True, timeout=timeout
            )

        # Step 3: pdflatex (resolve references)
        subprocess.run(
            [pdflatex, "-interaction=nonstopmode", "-halt-on-error", tex_file.name],
            cwd=work_dir, capture_output=True, text=True, timeout=timeout
        )

        # Step 4: pdfinal pdflatex (finalize)
        result = subprocess.run(
            [pdflatex, "-interaction=nonstopmode", "-halt-on-error", tex_file.name],
            cwd=work_dir, capture_output=True, text=True, timeout=timeout
        )

        pdf_file = work_dir / f"{base_name}.pdf"
        duration = (datetime.now(BRAZIL_TZ) - start).total_seconds()

        if pdf_file.exists():
            return CompileResult(
                stage="latex", success=True, output_path=pdf_file,
                duration_seconds=duration,
                metadata={"pages": self._count_pages(pdf_file)}
            )
        else:
            return CompileResult(
                stage="latex", success=False,
                error_message="PDF not generated",
                duration_seconds=duration
            )

    def _count_pages(self, pdf_path: Path) -> int:
        """Conta páginas do PDF."""
        try:
            import subprocess
            result = subprocess.run(
                ["pdfinfo", str(pdf_path)], capture_output=True, text=True
            )
            for line in result.stdout.split("\n"):
                if "Pages:" in line:
                    return int(line.split(":")[1].strip())
        except Exception:
            pass
        return 0


# ═══════════════════════════════════════════════════════════════════════════
# AUDIO GENERATOR
# ═══════════════════════════════════════════════════════════════════════════

class AudioGenerator:
    """Gera áudio MP3 a partir de PDF usando edge-tts."""

    def __init__(self, voice: str = "pt-BR-FranciscaNeural", rate: str = "-5%"):
        self.voice = voice
        self.rate = rate
        self.chunk_size = 3500

    async def generate(self, pdf_path: Path, output_dir: Path) -> CompileResult:
        """Pipeline completo: PDF → Texto → Áudio MP3."""
        start = datetime.now(BRAZIL_TZ)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Step 1: Extract text
        text = self._extract_text(pdf_path)
        if not text:
            return CompileResult(
                stage="audio-extract", success=False,
                error_message="No text extracted from PDF"
            )

        # Step 2: Clean text
        clean_text = self._clean_text(text)
        text_file = output_dir / "dissertacao_texto_limpo.txt"
        text_file.write_text(clean_text, encoding="utf-8")

        # Step 3: Split into chunks
        chunks = self._split_chunks(clean_text)

        # Step 4: Generate audio chunks
        chunks_dir = output_dir / "chunks"
        chunks_dir.mkdir(exist_ok=True)

        audio_files = []
        for i, chunk in enumerate(chunks):
            chunk_file = chunks_dir / f"chunk_{i:04d}.mp3"
            if not chunk_file.exists():
                try:
                    communicate = edge_tts.Communicate(chunk, self.voice, rate=self.rate)
                    await communicate.save(str(chunk_file))
                except Exception as e:
                    print(f"  Warning: chunk {i} failed: {e}")
                    continue
            audio_files.append(chunk_file)

        if not audio_files:
            return CompileResult(
                stage="audio-generate", success=False,
                error_message="No audio chunks generated"
            )

        # Step 5: Concatenate
        output_file = output_dir / "dissertacao_completa.mp3"
        with open(output_file, 'wb') as outfile:
            for af in audio_files:
                with open(af, 'rb') as infile:
                    outfile.write(infile.read())

        duration = (datetime.now(BRAZIL_TZ) - start).total_seconds()
        size_mb = output_file.stat().st_size / (1024 * 1024)

        return CompileResult(
            stage="audio", success=True, output_path=output_file,
            duration_seconds=duration,
            metadata={
                "chunks": len(audio_files),
                "size_mb": round(size_mb, 1),
                "estimated_minutes": round(len(clean_text) / 15, 0)
            }
        )

    def _extract_text(self, pdf_path: Path) -> str:
        """Extrai texto do PDF."""
        if not HAS_PDFPLUMBER:
            return ""
        with pdfplumber.open(pdf_path) as pdf:
            texts = []
            for page in pdf.pages:
                text = page.extract_text() or ""
                texts.append(text)
            return "\n\n".join(texts)

    def _clean_text(self, text: str) -> str:
        """Limpa texto para TTS."""
        text = re.sub(r'\n\d{1,3}\n', '\n', text)
        text = re.sub(r'https?://\S+', '', text)
        text = re.sub(r'\S+@\S+\.\S+', '', text)
        text = re.sub(r' {2,}', ' ', text)
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text.strip()

    def _split_chunks(self, text: str) -> list:
        """Divide texto em blocos para TTS."""
        paragraphs = text.split('\n\n')
        chunks = []
        current = ""
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            if len(para) > self.chunk_size:
                # Try splitting by sentences first
                sentences = re.split(r'(?<=[.!?])\s+', para)
                if len(sentences) > 1:
                    for sent in sentences:
                        if len(current) + len(sent) + 1 > self.chunk_size:
                            if current:
                                chunks.append(current.strip())
                            current = sent
                        else:
                            current += " " + sent if current else sent
                else:
                    # No sentence boundaries — split by character count
                    while len(para) > self.chunk_size:
                        chunks.append(para[:self.chunk_size].strip())
                        para = para[self.chunk_size:]
                    if para:
                        current = para
            else:
                if len(current) + len(para) + 2 > self.chunk_size:
                    if current:
                        chunks.append(current.strip())
                    current = para
                else:
                    current += "\n\n" + para if current else para
        if current.strip():
            chunks.append(current.strip())
        return chunks


# ═══════════════════════════════════════════════════════════════════════════
# DOCX CONVERTER
# ═══════════════════════════════════════════════════════════════════════════

class DOCXConverter:
    """Converte LaTeX/PDF para DOCX usando pandoc."""

    def __init__(self):
        self.pandoc = self._find_pandoc()

    def _find_pandoc(self) -> str:
        """Encontra pandoc."""
        result = shutil.which("pandoc")
        if result:
            return result
        # Check common locations
        common = [
            r"C:\Program Files\Pandoc\pandoc.exe",
            r"C:\Users\{os.getlogin()}\AppData\Local\Pandoc\pandoc.exe",
        ]
        for path in common:
            if os.path.exists(path):
                return path
        return "pandoc"

    def convert(self, tex_file: Path, bib_file: Optional[Path] = None) -> CompileResult:
        """Converte .tex para .docx."""
        start = datetime.now(BRAZIL_TZ)
        output_file = tex_file.parent / f"{tex_file.stem}.docx"

        cmd = [self.pandoc, str(tex_file), "-o", str(output_file)]

        if bib_file and bib_file.exists():
            cmd.extend(["--bibliography", str(bib_file)])
            cmd.extend(["--citeproc"])

            # Find APA CSL
            csl_file = SCRIPT_DIR / "apa.csl"
            if not csl_file.exists():
                # Download APA CSL
                import urllib.request
                url = "https://raw.githubusercontent.com/citation-style-language/styles/master/apa.csl"
                try:
                    urllib.request.urlretrieve(url, str(csl_file))
                except Exception:
                    pass
            if csl_file.exists():
                cmd.extend(["--csl", str(csl_file)])

        cmd.extend(["--toc", "--toc-depth=3", "--number-sections"])

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        duration = (datetime.now(BRAZIL_TZ) - start).total_seconds()

        if output_file.exists():
            return CompileResult(
                stage="docx", success=True, output_path=output_file,
                duration_seconds=duration,
                metadata={"size_kb": round(output_file.stat().st_size / 1024, 1)}
            )
        else:
            return CompileResult(
                stage="docx", success=False,
                error_message=f"pandoc failed: {result.stderr[:500]}",
                duration_seconds=duration
            )


# ═══════════════════════════════════════════════════════════════════════════
# MAIN COMPILER
# ═══════════════════════════════════════════════════════════════════════════

class DissertationCompiler:
    """Orquestrador principal do pipeline de compilação."""

    def __init__(self, input_path: Path, formats: list[str] = None):
        self.input_path = input_path
        self.formats = formats or ["pdf", "audio", "docx"]
        self.results: list[CompileResult] = []
        self.stats = DissertationStats()

    def run(self) -> list[CompileResult]:
        """Executa pipeline completo."""
        print("=" * 60)
        print("  DISSERTATION COMPILER v1.0")
        print("  SPEC-052: Autonomous Academic Production")
        print("=" * 60)
        print()

        # Determine input type
        if self.input_path.suffix == ".tex":
            self._compile_latex()
        elif self.input_path.suffix == ".pdf":
            self._process_pdf()
        elif self.input_path.is_dir():
            self._compile_directory()
        else:
            print(f"Unsupported input: {self.input_path}")
            return []

        # Generate requested formats
        pdf_path = self._find_pdf()

        if "audio" in self.formats and pdf_path:
            self._generate_audio(pdf_path)

        if "docx" in self.formats:
            tex_path = self._find_tex()
            if tex_path:
                self._generate_docx(tex_path)

        # Print summary
        self._print_summary()

        return self.results

    def _compile_latex(self):
        """Compila arquivo .tex para PDF."""
        if "pdf" in self.formats:
            print("[1/3] Compilando LaTeX → PDF...")
            compiler = LaTeXCompiler()
            result = compiler.compile(self.input_path)
            self.results.append(result)
            if result.success:
                print(f"  ✓ PDF gerado: {result.output_path}")
            else:
                print(f"  ✗ Erro: {result.error_message}")

    def _process_pdf(self):
        """Processa PDF existente."""
        print(f"[1/3] PDF encontrado: {self.input_path}")
        self.stats.total_pages = self._count_pages(self.input_path)

    def _compile_directory(self):
        """Compila todos os .tex em um diretório."""
        tex_files = list(self.input_path.glob("*.tex"))
        if not tex_files:
            print("  Nenhum arquivo .tex encontrado")
            return

        # Find main.tex or dissertacao.tex
        main_tex = None
        for tf in tex_files:
            if tf.name in ["main.tex", "dissertacao.tex", "thesis.tex"]:
                main_tex = tf
                break
        if not main_tex:
            main_tex = tex_files[0]

        self.input_path = main_tex
        if "pdf" in self.formats:
            self._compile_latex()

    def _generate_audio(self, pdf_path: Path):
        """Gera áudio a partir do PDF."""
        print(f"[2/3] Gerando áudio MP3...")
        output_dir = pdf_path.parent / "audio"
        generator = AudioGenerator()
        result = asyncio.run(generator.generate(pdf_path, output_dir))
        self.results.append(result)
        if result.success:
            print(f"  ✓ Áudio gerado: {result.output_path}")
            print(f"    Tamanho: {result.metadata.get('size_mb', 0)} MB")
        else:
            print(f"  ✗ Erro: {result.error_message}")

    def _generate_docx(self, tex_path: Path):
        """Gera DOCX a partir do .tex."""
        print(f"[3/3] Convertendo LaTeX → DOCX...")
        bib_file = tex_path.parent / "referencias.bib"
        converter = DOCXConverter()
        result = converter.convert(tex_path, bib_file)
        self.results.append(result)
        if result.success:
            print(f"  ✓ DOCX gerado: {result.output_path}")
        else:
            print(f"  ✗ Erro: {result.error_message}")

    def _find_pdf(self) -> Optional[Path]:
        """Encontra PDF correspondente."""
        if self.input_path.suffix == ".pdf":
            return self.input_path
        pdf_path = self.input_path.parent / f"{self.input_path.stem}.pdf"
        return pdf_path if pdf_path.exists() else None

    def _find_tex(self) -> Optional[Path]:
        """Encontra .tex correspondente."""
        if self.input_path.suffix == ".tex":
            return self.input_path
        tex_path = self.input_path.parent / f"{self.input_path.stem}.tex"
        return tex_path if tex_path.exists() else None

    def _count_pages(self, pdf_path: Path) -> int:
        """Conta páginas do PDF."""
        try:
            if HAS_PDFPLUMBER:
                with pdfplumber.open(pdf_path) as pdf:
                    return len(pdf.pages)
        except Exception:
            pass
        return 0

    def _print_summary(self):
        """Imprime resumo da compilação."""
        print()
        print("=" * 60)
        print("  RESUMO DA COMPILAÇÃO")
        print("=" * 60)

        successful = sum(1 for r in self.results if r.success)
        total = len(self.results)

        for r in self.results:
            status = "✓" if r.success else "✗"
            print(f"  {status} {r.stage}: {r.output_path or r.error_message}")

        print()
        print(f"  Sucesso: {successful}/{total}")
        print(f"  Tempo total: {sum(r.duration_seconds for r in self.results):.1f}s")
        print("=" * 60)


# ═══════════════════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="Dissertation Compiler — SPEC-052"
    )
    parser.add_argument(
        "--input", "-i", required=True,
        help="Input path (.tex, .pdf, or directory)"
    )
    parser.add_argument(
        "--formats", "-f", default="pdf,audio,docx",
        help="Output formats (comma-separated: pdf,audio,docx)"
    )

    args = parser.parse_args()
    input_path = Path(args.input)
    formats = args.formats.split(",")

    compiler = DissertationCompiler(input_path, formats)
    compiler.run()


if __name__ == "__main__":
    main()
