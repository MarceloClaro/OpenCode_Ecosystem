"""docling_skill.py — Wrapper da skill docling-pdf-extraction.

Ponte entre a skill e o adapter em nexus/scripts/docling_adapter.py.
Uso: python docling_skill.py <caminho_do_pdf> [--output FORMATO]

Referencia a implementacao real em nexus/scripts/docling_adapter.py
que utiliza Docling (IBM Research, LF AI and Data).
"""

import sys, json
from pathlib import Path


def extrair_pdf(pdf_path: str, formato: str = "markdown") -> dict:
    """Extrai conhecimento de um PDF usando Docling via adapter."""
    adapter_path = Path(__file__).parent.parent.parent.parent / "nexus" / "scripts"
    sys.path.insert(0, str(adapter_path.resolve()))
    try:
        from docling_adapter import DoclingAdapter
        adapter = DoclingAdapter(enable_ocr=True, enable_tables=True)
        resultado = adapter.extract_knowledge(pdf_path)
        return {"status": "ok", "dados": str(resultado)[:500], "fonte": "docling_adapter"}
    except ImportError:
        return {
            "status": "fallback",
            "mensagem": "Adapter nao encontrado. Instale Docling: pip install docling",
            "formato": formato, "arquivo": pdf_path,
        }


def main():
    if len(sys.argv) < 2:
        print("Uso: python docling_skill.py <arquivo.pdf|arquivo.docx> [--output markdown|json|html]")
        sys.exit(1)
    pdf_path = sys.argv[1]
    formato = "markdown"
    if "--output" in sys.argv:
        idx = sys.argv.index("--output")
        if idx + 1 < len(sys.argv):
            formato = sys.argv[idx + 1]
    resultado = extrair_pdf(pdf_path, formato)
    print(json.dumps(resultado, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
