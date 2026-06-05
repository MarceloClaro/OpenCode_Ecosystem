## Problemas Conhecidos e Soluções

| Problema | Solução |
|----------|---------|
| Encoding UTF-8 | Verificar BOM, usar `encoding='utf-8'` explícito |
| Figuras não aparecem no PDF | Converter PNG para PDF: `pdflatex --shell-escape` |
| Tabelas quebram no DOCX | Simplificar tabelas: evitar colspan/rowspan complexos |
| MiKTeX sem pacotes | `miktex packages install` ou instalar manualmente |
| Pandoc sem template ABNT | Usar `--reference-doc` com template python-docx |
