import markdown
import weasyprint
import os
import re

DIR = r"C:\Users\marce\OneDrive\Documentos\Antiprojeto UFC\Documentos\transicao_conselho_escolar"

CSS_ABNT = """
@page {
  size: A4;
  margin: 3cm 2cm 2cm 3cm;
  @top-right {
    content: counter(page);
    font-family: 'Times New Roman', serif;
    font-size: 10pt;
  }
}
body {
  font-family: 'Times New Roman', Times, serif;
  font-size: 12pt;
  line-height: 1.5;
  text-align: justify;
  color: #000;
}
h1, h2, h3, h4 {
  font-family: 'Times New Roman', Times, serif;
  color: #000;
}
h1 { font-size: 14pt; text-align: center; margin-top: 2cm; margin-bottom: 1cm; font-weight: bold; }
h2 { font-size: 13pt; margin-top: 1cm; margin-bottom: 0.5cm; font-weight: bold; }
h3 { font-size: 12pt; margin-top: 0.7cm; font-weight: bold; }
hr { border: none; border-top: 1px solid #000; margin: 0.5cm 0; }
strong { font-weight: bold; }
em { font-style: italic; }
p { margin: 0.3cm 0; text-indent: 0; }
ul, ol { margin: 0.3cm 0; padding-left: 1.5cm; }
li { margin: 0.15cm 0; }
table { width: 100%; border-collapse: collapse; margin: 0.5cm 0; }
td, th { border: 1px solid #000; padding: 4pt 8pt; font-size: 11pt; text-align: left; }
th { font-weight: bold; background: #f0f0f0; }
blockquote { margin: 0.5cm 1cm; font-style: italic; }
.meta-block {
  margin-bottom: 1.5cm;
  line-height: 2.0;
}
.data-local {
  text-align: right;
  margin-top: 1cm;
}
.assinatura {
  margin-top: 2.5cm;
  text-align: center;
}
.assinatura p { text-align: center; margin: 0.1cm 0; }
.recibo {
  margin-top: 2cm;
  border-top: 2px solid #000;
  padding-top: 0.5cm;
}
"""

def md_to_pdf(md_text, output_path, title=""):
    html_body = markdown.markdown(md_text, extensions=['extra'])
    full_html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<title>{title}</title>
<style>{CSS_ABNT}</style>
</head>
<body>
{html_body}
</body>
</html>"""
    weasyprint.HTML(string=full_html).write_pdf(output_path)
    return output_path


def gerar_relacao_documental():
    return """# RELAÇÃO DOCUMENTAL — TRANSIÇÃO DE GESTÃO

## Documentos Recebidos

| Item | Documento | Status |
|------|-----------|--------|
| 1 | Termo de Transição assinado | ✓ Recebido |
| 2 | Ata de Posse da nova gestão | ✓ Recebido |
| 3 | Relação de bens patrimoniais (parcial) | ✓ Recebido |
| 4 | Boletim de Ocorrência nº 931-21050/2026 (furto notebook Dell) | ✓ Recebido |

## Documentos Faltantes (não entregues pela gestão anterior)

| Item | Documento | Fundamento Legal |
|------|-----------|------------------|
| 1 | Extratos bancários completos das contas vinculadas ao PDDE (2024-2025) | Res. CD/FNDE 15/2021, art. 26 |
| 2 | Certidões Negativas de Débitos (CND) das empresas fornecedoras | Res. CD/FNDE 15/2021, art. 27 |
| 3 | Pesquisas de preço e cotações das aquisições realizadas | Lei 14.133/2021, art. 23 |
| 4 | Notas fiscais originais ou cópias autenticadas | Res. CD/FNDE 15/2021, art. 28 |
| 5 | Relatório consolidado de prestação de contas final do período | Res. CD/FNDE 15/2021, art. 29 |
| 6 | Comprovante de prestação de contas ao FNDE dos exercícios 2024-2025 | Res. CD/FNDE 15/2021, art. 30 |

## Observações

1. O Conselho Fiscal da gestão anterior recusou-se formalmente a aprovar as contas.
2. A ex-gestora reconheceu a entrega limitada de documentos no Termo de Transição.
3. Há indícios de potencial desvio de finalidade na aplicação de recursos do PDDE.
4. O furto do notebook Dell (tombo 54595) foi registrado no BO nº 931-21050/2026.

---

*Documento elaborado em 28 de maio de 2026 pela nova diretoria da UEx ESCOLA DE CIDADANIA AIRAM VERAS.*"""


def processar():
    arquivos = [
        ("NOTIFICACAO_EXTRAJUDICIAL.md", "Notificação Extrajudicial - Valdisa Bezerra de Meneses Torres"),
        ("OFICIO_FNDE.md", "Ofício ao FNDE - Comunicação de Transição de Gestão"),
        ("OFICIO_SEDUC.md", "Ofício à SEDUC/CE - Comunicação de Transição de Gestão"),
    ]

    resultados = []

    for md_file, titulo in arquivos:
        md_path = os.path.join(DIR, md_file)
        pdf_name = md_file.replace(".md", ".pdf")
        pdf_path = os.path.join(DIR, pdf_name)

        with open(md_path, "r", encoding="utf-8") as f:
            conteudo = f.read()

        md_to_pdf(conteudo, pdf_path, titulo)
        resultados.append((md_file, pdf_name))
        print(f"✓ {md_file} → {pdf_name}")

    # Relação Documental
    relacao = gerar_relacao_documental()
    relacao_path = os.path.join(DIR, "RELACAO_DOCUMENTAL.pdf")
    md_to_pdf(relacao, relacao_path, "Relação Documental - Transição de Gestão")
    resultados.append(("(gerado)", "RELACAO_DOCUMENTAL.pdf"))
    print("✓ Relação Documental → RELACAO_DOCUMENTAL.pdf")

    print("\n---\nDocumentos gerados com sucesso!")
    for origem, destino in resultados:
        print(f"  {destino}")

if __name__ == "__main__":
    processar()
