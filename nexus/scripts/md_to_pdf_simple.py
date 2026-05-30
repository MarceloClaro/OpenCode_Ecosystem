"""
Conversor MD→PDF usando apenas stdlib Python + webbrowser.
Gera HTML estilizado e abre no navegador para impressao via Ctrl+P.

Uso: python md_to_pdf_simple.py
"""
import os, webbrowser

DESKTOP = os.path.join(os.path.expanduser("~"), "OneDrive", "Área de Trabalho")
HTML_SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "dashboard", "opencode_framework_analysis.html")
HTML_DEST = os.path.join(DESKTOP, "opencode_framework_analysis.html")

# Copiar HTML para Desktop
with open(HTML_SRC, "r", encoding="utf-8") as f:
    content = f.read()

with open(HTML_DEST, "w", encoding="utf-8") as f:
    f.write(content)

print(f"HTML copiado para: {HTML_DEST}")
print("Abrindo no navegador... Use Ctrl+P para salvar como PDF.")
webbrowser.open(f"file:///{HTML_DEST.replace(os.sep, '/')}")
