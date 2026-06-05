<!-- Conteudo extraido de academic-export-abnt/SKILL.md via progressive-disclosure -->

## Workflow de Exportação (3 Formatos)

### 1. Exportar para PDF (via LaTeX/pdflatex)

Pipeline: markdown → LaTeX → PDF

```bash
# Etapa 1: Markdown → LaTeX (com template ABNT)
pandoc artigo.md -o artigo.tex `
  --pdf-engine=pdflatex `
  --template=template-abnt.latex `
  -V lang=pt-BR `
  -V fontsize=12pt `
  -V geometry:margin=3cm `
  -V geometry:left=3cm `
  -V geometry:right=2cm `
  -V geometry:top=3cm `
  -V geometry:bottom=2cm `
  -V linestretch=1.5 `
  -V toc=true

# Etapa 2: LaTeX → PDF (2 passes para referências)
pdflatex artigo.tex
pdflatex artigo.tex
```

**Configurações ABNT para PDF:**
- Fonte: Times New Roman (12pt)
- Margens: superior 3cm, esquerda 3cm, direita 2cm, inferior 2cm
- Espaçamento: 1.5 linhas
- Numeração de seções: progressiva (1, 1.1, 1.1.1)
- Sumário automático (toc)
- Cabeçalho: título do capítulo
- Numeração de páginas: superior direita

### 2. Exportar para DOCX (via python-docx com template ABNT)

Pipeline: markdown → LaTeX intermediário → python-docx → DOCX formatado

```python
from docx import Document
from docx.shared import Pt, Cm, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn

def criar_template_abnt():
    """Cria documento ABNT formatado programaticamente."""
    doc = Document()
    
    # Margens ABNT
    for section in doc.sections:
        section.top_margin = Cm(3)
        section.bottom_margin = Cm(2)
        section.left_margin = Cm(3)
        section.right_margin = Cm(2)
    
    # Estilo Normal: Times 12pt, 1.5 espaçamento
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Times New Roman'
    font.size = Pt(12)
    pf = style.paragraph_format
    pf.line_spacing = 1.5
    pf.space_after = Pt(0)
    pf.space_before = Pt(0)
    
    # Estilo Heading 1: título de seção
    h1 = doc.styles['Heading 1']
    h1.font.name = 'Times New Roman'
    h1.font.size = Pt(14)
    h1.font.bold = True
    h1.paragraph_format.space_before = Pt(12)
    h1.paragraph_format.space_after = Pt(6)
    
    return doc

def markdown_para_docx_abnt(md_path, docx_path):
    """Converte markdown para DOCX ABNT formatado."""
    import subprocess, tempfile
    
    # 1. MD → DOCX bruto via pandoc
    subprocess.run([
        'pandoc', md_path, '-o', docx_path,
        '--reference-doc=template-abnt.docx',
        '-V', 'lang=pt-BR'
    ], check=True)
    
    # 2. Pós-processamento python-docx
    from docx import Document
    doc = Document(docx_path)
    
    # Ajustes finos de formatação
    for p in doc.paragraphs:
        if p.style.name.startswith('Heading'):
            for run in p.runs:
                run.font.name = 'Times New Roman'
    
    doc.save(docx_path)
```

### 3. Exportar para HTML Standalone

Pipeline: markdown → HTML com imagens embutidas (base64)

```bash
# HTML standalone com imagens embutidas
pandoc artigo.md -o artigo.html `
  --standalone `
  --self-contained `
  --embed-resources `
  -V lang=pt-BR `
  --metadata title="Título do Artigo" `
  --css=template-abnt.css
```


---

## Guia Rápido de Comandos

```bash
# PDF completo (recomendado: 2 passos)
pandoc ARTIGO.md -o artigo.tex --pdf-engine=pdflatex -V fontsize=12pt -V geometry:margin=3cm -V geometry:left=3cm -V geometry:right=2cm -V geometry:top=3cm -V geometry:bottom=2cm -V linestretch=1.5 -V toc=true
pdflatex artigo.tex && pdflatex artigo.tex

# DOCX com template
pandoc ARTIGO.md -o artigo.docx --reference-doc=template-abnt.docx

# HTML standalone
pandoc ARTIGO.md -o artigo.html --standalone --self-contained --embed-resources

# Correção de encoding (se necessário)
python -c "with open('artigo.md','r',encoding='utf-8') as f: t=f.read(); t=t.replace('\u2013','-').replace('\u2014','--'); open('artigo_fixed.md','w',encoding='utf-8') as o: o.write(t)"
```
