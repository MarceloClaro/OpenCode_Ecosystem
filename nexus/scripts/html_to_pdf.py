"""Converte HTML para PDF usando Playwright (headless Chromium)."""
import subprocess, sys, os

HTML_PATH = os.path.join(os.path.dirname(__file__), "..", "dashboard", "opencode_framework_analysis.html")
PDF_PATH = os.path.join(os.path.expanduser("~"), "OneDrive", "Área de Trabalho", "opencode_framework_analysis.pdf")

# Garante que playwright está instalado
try:
    from playwright.sync_api import sync_playwright
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "playwright", "-q"])
    subprocess.check_call([sys.executable, "-m", "playwright", "install", "chromium"])
    from playwright.sync_api import sync_playwright

def main():
    html_abs = os.path.abspath(HTML_PATH)
    pdf_abs = os.path.abspath(PDF_PATH)
    
    print(f"HTML: {html_abs}")
    print(f"PDF:  {pdf_abs}")
    
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(f"file:///{html_abs.replace(os.sep, '/')}", wait_until="networkidle")
        page.wait_for_timeout(2000)  # espera fontes carregarem
        page.pdf(
            path=pdf_abs,
            format="A4",
            margin={"top": "20mm", "bottom": "20mm", "left": "15mm", "right": "15mm"},
            print_background=True,
        )
        browser.close()
    
    size_kb = os.path.getsize(pdf_abs) / 1024
    print(f"PDF gerado com sucesso: {pdf_abs} ({size_kb:.0f} KB)")

if __name__ == "__main__":
    main()
