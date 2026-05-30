import subprocess
import os

DIR = r"C:\Users\marce\OneDrive\Documentos\Antiprojeto UFC\Documentos\transicao_conselho_escolar"
PANDOC = r"C:\Users\marce\AppData\Local\Microsoft\WinGet\Packages\JohnMacFarlane.Pandoc_Microsoft.Winget.Source_8wekyb3d8bbwe\pandoc-3.9.0.2\pandoc.exe"

ABNT_OPTS = [
    "--pdf-engine=pdflatex",
    "-V", "fontsize=12pt",
    "-V", "geometry:left=3cm",
    "-V", "geometry:right=2cm",
    "-V", "geometry:top=3cm",
    "-V", "geometry:bottom=2cm",
    "-V", "linestretch=1.5",
    "-V", "lang=pt-BR",
    "-V", "mainfont=Times New Roman",
    "--metadata", "title=",
]

def md_to_pdf(md_path, pdf_path, title="", extra_opts=None):
    opts = [PANDOC, md_path, "-o", pdf_path] + ABNT_OPTS
    if title:
        opts += ["--metadata", f"title={title}"]
    if extra_opts:
        opts += extra_opts
    result = subprocess.run(opts, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  ERRO: {result.stderr[:500]}")
        return False
    return True


def gerar_relacao_documental():
    path = os.path.join(DIR, "RELACAO_DOCUMENTAL.md")
    content = """---
title: Relação Documental — Transição de Gestão
---

# RELAÇÃO DOCUMENTAL — TRANSIÇÃO DE GESTÃO

## Documentos Recebidos

1. **Termo de Transição** — assinado pela gestão anterior
2. **Ata de Posse** — nova gestão Biênio 2026-2028
3. **Relação de bens patrimoniais** — parcial
4. **Boletim de Ocorrência nº 931-21050/2026** — furto de notebook Dell (tombo 54595)

## Documentos Faltantes (não entregues pela gestão anterior)

1. **Extratos bancários completos** — contas vinculadas ao PDDE, exercícios 2024-2025
   - Fundamento: Res. CD/FNDE nº 15/2021, art. 26
2. **Certidões Negativas de Débitos (CND)** — empresas fornecedoras contratadas
   - Fundamento: Res. CD/FNDE nº 15/2021, art. 27
3. **Pesquisas de preço e cotações** — aquisições realizadas no período
   - Fundamento: Lei 14.133/2021, art. 23
4. **Notas fiscais** — originais ou cópias autenticadas
   - Fundamento: Res. CD/FNDE nº 15/2021, art. 28
5. **Relatório consolidado de prestação de contas** — exercícios 2024-2025
   - Fundamento: Res. CD/FNDE nº 15/2021, art. 29
6. **Comprovante de prestação de contas ao FNDE** — exercícios 2024-2025
   - Fundamento: Res. CD/FNDE nº 15/2021, art. 30

## Observações

- O Conselho Fiscal da gestão anterior recusou-se formalmente a aprovar as contas.
- A ex-gestora (Valdisa Bezerra de Meneses Torres) reconheceu a entrega limitada de documentos no Termo de Transição.
- Há indícios de potencial desvio de finalidade na aplicação de recursos do PDDE.
- O furto do notebook Dell (tombo 54595) foi registrado no BO nº 931-21050/2026.

---

*Documento elaborado em 28 de maio de 2026 pela nova diretoria da UEx ESCOLA DE CIDADANIA AIRAM VERAS.*
"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return path


def main():
    os.makedirs(DIR, exist_ok=True)

    # Relação Documental primeiro
    relacao_md = gerar_relacao_documental()
    print("[OK] Relacao Documental criada")

    # Processar cada documento
    docs = [
        ("NOTIFICACAO_EXTRAJUDICIAL.md", "Notificação Extrajudicial"),
        ("OFICIO_FNDE.md", "Ofício ao FNDE"),
        ("OFICIO_SEDUC.md", "Ofício à SEDUC/CE"),
        ("RELACAO_DOCUMENTAL.md", "Relação Documental"),
    ]

    for md_file, titulo in docs:
        md_path = os.path.join(DIR, md_file)
        pdf_name = md_file.replace(".md", ".pdf")
        pdf_path = os.path.join(DIR, pdf_name)

        if not os.path.exists(md_path):
            print(f"  ! {md_file} não encontrado, pulando")
            continue

        ok = md_to_pdf(md_path, pdf_path, titulo)
        status = "[OK]" if ok else "[ERR]"
        print(f"{status} {md_file} -> {pdf_name}")

    print("\n---\nConcluido! PDFs gerados no diretorio de documentos.")

if __name__ == "__main__":
    main()
