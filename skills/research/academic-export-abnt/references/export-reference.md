# Guia de Exportação ABNT — Referência Completa

## 1. Exportação para PDF (LaTeX)

### Pré-requisitos
- MiKTeX (Windows) ou TeX Live (Linux/macOS)
- Pandoc 3.1+
- Pacotes LaTeX: geometry, setspace, fontspec, titling, fancyhdr, hyperref

### Comandos

```bash
# Passo 1: Markdown → LaTeX
pandoc ARTIGO.md -o artigo.tex `
  --pdf-engine=pdflatex `
  -V fontsize=12pt `
  -V geometry:margin=3cm `
  -V geometry:left=3cm `
  -V geometry:right=2cm `
  -V geometry:top=3cm `
  -V geometry:bottom=2cm `
  -V linestretch=1.5 `
  -V toc=true `
  -V lang=pt-BR

# Passo 2: LaTeX → PDF (primeira passagem)
pdflatex -interaction=nonstopmode artigo.tex

# Passo 3: LaTeX → PDF (segunda passagem - referências)
pdflatex -interaction=nonstopmode artigo.tex
```

### Solução de Problemas PDF

| Erro | Causa | Solução |
|------|-------|---------|
| `! LaTeX Error: File 'geometry.sty' not found` | Pacote faltando | `miktex packages install geometry` |
| `! Undefined control sequence` | Comando LaTeX inválido | Verificar escape de underscores |
| `! Package inputenc Error` | Caractere Unicode não suportado | Usar `--pdf-engine=xelatex` |
| Figuras não aparecem | Path errado | Usar paths relativos ou `--shell-escape` |
| Tabela ultrapassa margem | Tabela larga | Usar `longtable` ou `adjustbox` |

## 2. Exportação para DOCX

### Template ABNT via python-docx

```python
from docx import Document
from docx.shared import Pt, Cm

doc = Document()
# Configurar margens
for section in doc.sections:
    section.top_margin = Cm(3)
    section.bottom_margin = Cm(2)
    section.left_margin = Cm(3)
    section.right_margin = Cm(2)

# Configurar estilo Normal
style = doc.styles['Normal']
style.font.name = 'Times New Roman'
style.font.size = Pt(12)
style.paragraph_format.line_spacing = 1.5
```

### Pandoc com referência

```bash
pandoc artigo.md -o artigo.docx --reference-doc=template-abnt.docx
```

## 3. Exportação para HTML

```bash
pandoc artigo.md -o artigo.html --standalone --self-contained --embed-resources
```

## 4. Validação de Encoding

```bash
# Verificar encoding
python -c "
with open('artigo.md','rb') as f:
    raw = f.read()
print('UTF-8 OK' if raw.startswith(b'\\xef\\xbb\\xbf') else 'Sem BOM')
print(f'Tamanho: {len(raw)} bytes')
"

# Corrigir caracteres problemáticos
python -c "
with open('artigo.md','r',encoding='utf-8') as f:
    t = f.read()
t = t.replace('\u2013','--').replace('\u2014','---')
t = t.replace('\u2018',\"'\").replace('\u2019',\"'\")
t = t.replace('\u201c','\"').replace('\u201d','\"')
with open('artigo_fixed.md','w',encoding='utf-8') as f:
    f.write(t)
print('OK - caracteres corrigidos')
"
```

## Checklist Pré-Exportação

- [ ] Markdown válido (sem sintaxe quebrada)
- [ ] Figuras existem nos paths referenciados
- [ ] Tabelas sem colspan/rowspan complexos
- [ ] Encoding UTF-8 (com ou sem BOM)
- [ ] Citações ABNT formatadas
- [ ] Numeração sequencial de figuras e tabelas
- [ ] Alt text descritivo em imagens
- [ ] Zero caracteres CJK no conteúdo
