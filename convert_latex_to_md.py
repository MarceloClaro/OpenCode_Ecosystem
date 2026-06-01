#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Conversor LaTeX -> Markdown para monografia academica.
Converte todos os capitulos + anexo + preambulo em um unico arquivo .md.
"""

import re
import json
from pathlib import Path

# Carrega dados de enriquecimento de fichamentos
from enrichment_data import get_reference, format_citation, get_passages, REFERENCES

# ============================================================
# CONFIGURACAO
# ============================================================
BASE = Path(r"C:\Users\marce\OneDrive\Documentos\Antiprojeto UFC\A Proteção da Personalidade Humana na Era da Inteligência Artificial - Contribuições da Encíclica Magnifica Humanitas para o Direito Contemporâneo\manuscrito")
OUTPUT = Path(r"C:\Users\marce\OneDrive\Documentos\Antiprojeto UFC\monografia-completa.md")

# ============================================================
# LEITURA DOS ARQUIVOS
# ============================================================
def read_file(filename):
    path = BASE / filename
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

# ============================================================
# FUNCOES DE CONVERSAO
# ============================================================

def convert_text_basic(text):
    """Basic text-level conversions that can be applied anywhere."""
    # MH and MHn commands
    text = re.sub(r'\\MH\{\}', 'Magnifica Humanitas', text)
    text = re.sub(r'\\MHn\{([^}]*)\}', r'Magnifica Humanitas, §\1', text)
    text = re.sub(r'\\MH', 'Magnifica Humanitas', text)

    # citecaps
    text = re.sub(r'\\citecaps\{([^}]*)\}', r'\1', text)

    # Special LaTeX dashes
    text = text.replace('---', '\u2014')  # em-dash
    text = text.replace('--', '\u2013')   # en-dash

    # Ellipsis
    text = text.replace(r'\dots', '\u2026')
    text = text.replace(r'\ldots', '\u2026')

    # Quotes (curly double)
    text = text.replace('\u201c', '"')
    text = text.replace('\u201d', '"')
    text = text.replace("``", '"')
    text = text.replace("''", '"')

    # French quotes
    text = re.sub(r'\\og\s*', '\u00ab', text)
    text = re.sub(r'\\fg\s*', '\u00bb', text)

    return text

def convert_inline(text):
    """Convert inline LaTeX formatting to Markdown."""
    # \\textbf{...} -> **...**
    text = re.sub(r'\\textbf\{([^}]*)\}', r'**\1**', text)
    # \\textit{...} -> *...*
    text = re.sub(r'\\textit\{([^}]*)\}', r'*\1*', text)
    # \\emph{...} -> *...*
    text = re.sub(r'\\emph\{([^}]*)\}', r'*\1*', text)
    # \\textsc{...} -> plain text
    text = re.sub(r'\\textsc\{([^}]*)\}', r'\1', text)
    # \\textsuperscript{...} -> ^(...)
    text = re.sub(r'\\textsuperscript\{([^}]*)\}', r'^\1', text)
    # \\textsubscript{...} -> _\1
    text = re.sub(r'\\textsubscript\{([^}]*)\}', r'_\1', text)
    # \\texttt{...} -> `...`
    text = re.sub(r'\\texttt\{([^}]*)\}', r'`\1`', text)
    # \\underline{...} -> <u>...</u>
    text = re.sub(r'\\underline\{([^}]*)\}', r'<u>\1</u>', text)
    return text

def convert_urls(text):
    r"""Convert \url{...} to Markdown links."""
    text = re.sub(r'\\url\{([^}]*)\}', r'\1', text)
    return text

def convert_footnotes(text):
    r"""Convert \footnote{...} to Markdown inline footnotes or endnotes."""
    def replace_fn(m):
        content = m.group(1)
        content = convert_inline(content)
        content = convert_urls(content)
        return f'[^{content}]'
    text = re.sub(r'\\footnote\{([^}]*)\}', replace_fn, text)
    return text

def convert_labels_refs(text):
    """Remove label and ref commands."""
    text = re.sub(r'\\label\{[^}]*\}', '', text)
    text = re.sub(r'\\ref\{[^}]*\}', r'[ref]', text)
    return text

def convert_citations(text):
    r"""Convert \cite{...} to bracketed citation keys."""
    text = re.sub(r'\\cite(?:\[[^\]]*\])?\{([^}]*)\}', r'[\1]', text)
    return text

def convert_siglas(text):
    r"""Convert siglas environment to a definition list."""
    def replace_siglas(m):
        content = m.group(1)
        items = re.findall(r'\\item\[([^\]]*)\]\s*(.*?)(?=\\item\[|$)', content, re.DOTALL)
        lines = ['| Sigla | Significado |', '|-------|-------------|']
        for abbr, meaning in items:
            meaning = meaning.strip()
            meaning = convert_inline(meaning)
            lines.append(f'| {abbr} | {meaning} |')
        return '\n'.join(lines)
    text = re.sub(r'\\begin\{siglas\}\s*\n?(.*?)\\end\{siglas\}', replace_siglas, text, flags=re.DOTALL)
    return text

def convert_enumerate(text):
    """Convert enumerate environment to numbered list."""
    def replace_env(m):
        content = m.group(1)
        items = re.findall(r'\\item\s+(.*?)(?=\\item|$)', content, re.DOTALL)
        lines = []
        for i, item in enumerate(items, 1):
            item = item.strip()
            item = convert_inline(item)
            item = convert_citations(item)
            lines.append(f'  {i}. {item}')
        return '\n'.join(lines)
    text = re.sub(r'\\begin\{enumerate\}(.*?)\\end\{enumerate\}', replace_env, text, flags=re.DOTALL)
    return text

def convert_itemize(text):
    """Convert itemize environment to bullet list."""
    def replace_env(m):
        content = m.group(1)
        items = re.findall(r'\\item\s+(.*?)(?=\\item|$)', content, re.DOTALL)
        lines = []
        for item in items:
            item = item.strip()
            item = convert_inline(item)
            item = convert_citations(item)
            # Handle line breaks within items
            item_lines = item.split('\n')
            item = ' '.join(l.strip() for l in item_lines)
            lines.append(f'  - {item}')
        return '\n'.join(lines)
    text = re.sub(r'\\begin\{itemize\}(.*?)\\end\{itemize\}', replace_env, text, flags=re.DOTALL)
    return text

def convert_fichamento(text):
    """Convert fichamento environment to styled block with enriched references."""
    def replace_env(m):
        raw_content = m.group(1)

        # --- EXTRAI CHAVE DE CITACAO ANTES DA CONVERSAO ---
        cite_match = re.search(r'\\cite\{([^}]+)\}', raw_content)
        cite_key = cite_match.group(1) if cite_match else None

        # Remove o cite_key duplicado para nao poluir a saida,
        # ja que vamos exibir a citacao formatada no enrichment.
        # Mas preservamos o \cite{} para a conversao padrao.

        # --- CONVERSAO PADRAO ---
        content = convert_inline(raw_content)
        content = convert_citations(content)
        content = convert_itemize(content)
        content = convert_enumerate(content)

        # Process lines
        lines = content.split('\n')
        md_lines = ['', '---']
        for line in lines:
            line = line.strip()
            if not line:
                continue
            # Already processed itemize/enumerate
            if line.startswith('  -') or re.match(r'^\s+\d+\.', line):
                md_lines.append(line)
            else:
                md_lines.append(line)

        # --- ENRIQUECIMENTO ---
        if cite_key and cite_key in REFERENCES:
            md_lines.append('')
            md_lines.append('### Dados da Referência')
            md_lines.append(f'- **Citação completa:** {format_citation(cite_key)}')

            # Tipo
            ref_type = REFERENCES[cite_key].get("type", "")
            type_labels = {
                "magisterio": "Magistério Pontifício",
                "livro": "Livro",
                "artigo": "Artigo Acadêmico",
                "legislacao": "Legislação",
            }
            md_lines.append(f'- **Tipo:** {type_labels.get(ref_type, ref_type)}')

            # URL
            url = REFERENCES[cite_key].get("url", "")
            if url:
                md_lines.append(f'- **Disponível em:** {url}')

            # Passagens citadas
            passages = get_passages(cite_key)
            if passages:
                md_lines.append('')
                md_lines.append('### Passagens Citadas')
                for p in passages:
                    ref = p.get("ref", "")
                    orig = p.get("orig", "")
                    traducao = p.get("traducao", "")
                    paginas = p.get("paginas", "")

                    parts = [f'- **{ref}:**']
                    if orig:
                        parts.append(f'\n  - Original: {orig}')
                    if traducao:
                        parts.append(f'\n  - Tradução: {traducao}')
                    if paginas:
                        parts.append(f'\n  - Páginas: {paginas}')
                    if not orig and not traducao:
                        parts.append(' *(excerto original a localizar)*')

                    md_lines.append(''.join(parts))
        elif cite_key:
            # Citacao nao encontrada no dicionario
            md_lines.append('')
            md_lines.append(f'*[Referência {cite_key} não encontrada na base de dados]*')

        md_lines.append('---')
        return '\n'.join(md_lines)
    text = re.sub(r'\\begin\{fichamento\}(.*?)\\end\{fichamento\}', replace_env, text, flags=re.DOTALL)
    return text

def convert_abstract(text):
    """Convert abstract/resumo environment."""
    def replace_resumo(m):
        content = m.group(1)
        content = convert_inline(content)
        content = convert_citations(content)
        content = convert_text_basic(content)
        return f'\n> **Resumo:** {content.strip()}\n'

    def replace_abstract(m):
        content = m.group(1)
        content = convert_inline(content)
        content = convert_citations(content)
        content = convert_text_basic(content)
        return f'\n> **Abstract:** {content.strip()}\n'

    text = re.sub(r'\\begin\{resumo\}(.*?)\\end\{resumo\}', replace_resumo, text, flags=re.DOTALL)
    text = re.sub(r'\\begin\{abstract\}(.*?)\\end\{abstract\}', replace_abstract, text, flags=re.DOTALL)
    return text

def convert_otherlanguage(text):
    """Remove otherlanguage environment, keep content."""
    text = re.sub(r'\\begin\{otherlanguage\*\}\{[^}]*\}', '', text)
    text = re.sub(r'\\end\{otherlanguage\*\}', '', text)
    return text

def convert_flushright(text):
    """Convert flushright to blockquote."""
    text = re.sub(r'\\begin\{flushright\}(.*?)\\end\{flushright\}', r'\n> \1\n', text, flags=re.DOTALL)
    return text

def convert_center(text):
    """Convert center to centered text (no special md)."""
    text = re.sub(r'\\begin\{center\}(.*?)\\end\{center\}', r'\1', text, flags=re.DOTALL)
    return text

def convert_minipage(text):
    """Remove minipage environment."""
    text = re.sub(r'\\begin\{minipage\}\{[^}]*\}', '', text)
    text = re.sub(r'\\end\{minipage\}', '', text)
    return text

def convert_sectioning(text):
    r"""Convert chapter, section, etc. to Markdown headings."""
    text = re.sub(r'\\chapter\*\{([^}]*)\}', r'# \1', text)
    text = re.sub(r'\\chapter\{([^}]*)\}', r'# \1', text)
    text = re.sub(r'\\section\*\{([^}]*)\}', r'## \1', text)
    text = re.sub(r'\\section\{([^}]*)\}', r'## \1', text)
    text = re.sub(r'\\subsection\*\{([^}]*)\}', r'### \1', text)
    text = re.sub(r'\\subsection\{([^}]*)\}', r'### \1', text)
    text = re.sub(r'\\subsubsection\*\{([^}]*)\}', r'#### \1', text)
    text = re.sub(r'\\subsubsection\{([^}]*)\}', r'#### \1', text)
    return text

def convert_paragraphs(text):
    r"""Convert \par to newline."""
    text = re.sub(r'\\par\s*', '\n\n', text)
    return text

def convert_newlines(text):
    """Convert double backslash to newline."""
    text = text.replace('\\\\', '\n')
    return text

def convert_vspace(text):
    r"""Remove vspace commands."""
    text = re.sub(r'\\vspace\*?\{[^}]*\}', '', text)
    text = re.sub(r'\\vfill', '', text)
    return text

def convert_noindent(text):
    r"""Remove noindent."""
    text = re.sub(r'\\noindent\s*', '', text)
    return text

def convert_hspace(text):
    r"""Remove hspace."""
    text = re.sub(r'\\hspace\*?\{[^}]*\}', '', text)
    return text

def convert_clearpage(text):
    r"""Convert clearpage to horizontal rule."""
    text = re.sub(r'\\clearpage\s*', '\n\n---\n\n', text)
    return text

def convert_pdfbookmark(text):
    r"""Remove pdfbookmark."""
    text = re.sub(r'\\pdfbookmark\[[^\]]*\]\{[^}]*\}\{[^}]*\}', '', text)
    return text

def convert_includegraphics(text):
    r"""Convert includegraphics to simple image reference."""
    text = re.sub(r'\\includegraphics(?:\[[^\]]*\])?\{([^}]*)\}', r'[Imagem: \1]', text)
    return text

def convert_table_of_contents(text):
    r"""Remove tableofcontents."""
    text = re.sub(r'\\tableofcontents', '', text)
    return text

def convert_list_of(text):
    r"""Remove listoffigures, listoftables."""
    text = re.sub(r'\\listoffigures', '', text)
    text = re.sub(r'\\listoftables', '', text)
    return text

def convert_anexos(text):
    """Convert anexosenv environment."""
    text = re.sub(r'\\begin\{anexosenv\}', '', text)
    text = re.sub(r'\\end\{anexosenv\}', '', text)
    text = re.sub(r'\\partanexos', '', text)
    return text

def convert_epigrafe(text):
    """Convert epigrafe environment."""
    def replace_env(m):
        content = m.group(1)
        content = convert_text_basic(content)
        content = convert_inline(content)
        content = convert_citations(content)
        content = convert_flushright(content)
        return f'\n> **Epigrafe**\n{content}\n'
    text = re.sub(r'\\begin\{epigrafe\}(.*?)\\end\{epigrafe\}', replace_env, text, flags=re.DOTALL)
    return text

def convert_dedicatoria(text):
    """Convert dedicatoria environment."""
    def replace_env(m):
        content = m.group(1)
        content = convert_text_basic(content)
        content = convert_inline(content)
        return f'\n> **Dedicat\u00f3ria:** {content.strip()}\n'
    text = re.sub(r'\\begin\{dedicatoria\}(.*?)\\end\{dedicatoria\}', replace_env, text, flags=re.DOTALL)
    return text

def convert_agradecimentos(text):
    """Convert agradecimentos environment."""
    def replace_env(m):
        content = m.group(1)
        return f'\n## Agradecimentos\n\n{content.strip()}\n'
    text = re.sub(r'\\begin\{agradecimentos\}(.*?)\\end\{agradecimentos\}', replace_env, text, flags=re.DOTALL)
    return text

def clean_empty_lines(text):
    """Remove excessive empty lines."""
    text = re.sub(r'\n{4,}', '\n\n\n', text)
    return text.strip()

def convert_chapter_file(text):
    """Full conversion of a chapter file."""
    # Remove comments
    lines = text.split('\n')
    cleaned = []
    for line in lines:
        if re.match(r'^\s*%', line):
            continue
        cleaned.append(line)
    text = '\n'.join(cleaned)

    # Structural conversions (order matters!)
    text = convert_anexos(text)
    text = convert_epigrafe(text)
    text = convert_dedicatoria(text)
    text = convert_agradecimentos(text)
    text = convert_abstract(text)
    text = convert_otherlanguage(text)

    # List environments first (before inline)
    text = convert_fichamento(text)
    text = convert_enumerate(text)
    text = convert_itemize(text)
    text = convert_siglas(text)

    # Layout
    text = convert_flushright(text)
    text = convert_center(text)
    text = convert_minipage(text)

    # Sectioning
    text = convert_sectioning(text)

    # Inline
    text = convert_text_basic(text)
    text = convert_inline(text)
    text = convert_citations(text)
    text = convert_footnotes(text)
    text = convert_urls(text)
    text = convert_labels_refs(text)

    # Spacing and misc
    text = convert_paragraphs(text)
    text = convert_newlines(text)
    text = convert_vspace(text)
    text = convert_noindent(text)
    text = convert_hspace(text)
    text = convert_clearpage(text)
    text = convert_pdfbookmark(text)
    text = convert_includegraphics(text)
    text = convert_table_of_contents(text)
    text = convert_list_of(text)

    # Clean up remaining LaTeX commands
    text = re.sub(r'\\begin\{[^}]*\}', '', text)
    text = re.sub(r'\\end\{[^}]*\}', '', text)
    text = re.sub(r'\\newcommand\{[^}]*\}[^}]*', '', text)
    text = re.sub(r'\\newenvironment\{[^}]*\}[^}]*\{[^}]*\}', '', text)
    text = re.sub(r'\\setlength\{[^}]*\}\{[^}]*\}', '', text)

    # Cleanup empty lines
    text = clean_empty_lines(text)

    return text

def convert_preamble(text):
    """Extract metadata from preamble."""
    title_match = re.search(r'\\titulo\{([^}]*)\}', text)
    author_match = re.search(r'\\autor\{([^}]*)\}', text)
    date_match = re.search(r'\\data\{([^}]*)\}', text)
    local_match = re.search(r'\\local\{([^}]*)\}', text)
    advisor_match = re.search(r'\\orientador\{([^}]*)\}', text)
    institution_match = re.search(r'\\instituicao\{([^}]*)\}', text)
    preamble_match = re.search(r'\\preambulo\{([^}]*)\}', text)

    meta = {}
    if title_match:
        meta['title'] = title_match.group(1)
    if author_match:
        meta['author'] = author_match.group(1)
    if date_match:
        meta['date'] = date_match.group(1)
    if local_match:
        meta['local'] = local_match.group(1)
    if advisor_match:
        meta['advisor'] = advisor_match.group(1)
    if institution_match:
        meta['institution'] = institution_match.group(1)
    if preamble_match:
        meta['preamble'] = preamble_match.group(1)

    return meta

def generate_frontmatter(meta):
    """Generate YAML front matter."""
    lines = ['---']
    title_clean = meta.get("title", "").replace("\\textit{", "").replace("}", "")
    lines.append(f'title: "{title_clean}"')
    lines.append(f'author: "{meta.get("author", "")}"')
    lines.append(f'date: "{meta.get("date", "")}"')
    lines.append(f'local: "{meta.get("local", "")}"')
    lines.append(f'advisor: "{meta.get("advisor", "")}"')
    lines.append(f'institution: "{meta.get("institution", "")}"')
    lines.append(f'description: "{meta.get("preamble", "")}"')
    lines.append('---\n')
    return '\n'.join(lines)

# ============================================================
# MAIN
# ============================================================
def main():
    # Read main.tex for metadata and preamble content
    main_tex = read_file('main.tex')
    meta = convert_preamble(main_tex)

    # Generate front matter
    output = generate_frontmatter(meta)

    # Title
    title = meta.get('title', 'Monografia')
    title_clean = title.replace('\\textit{', '').replace('}', '')
    output += f'# {title_clean}\n\n'

    # Epigrafe (from main.tex)
    epigrafe_match = re.search(r'\\begin\{epigrafe\}(.*?)\\end\{epigrafe\}', main_tex, re.DOTALL)
    if epigrafe_match:
        epig_text = epigrafe_match.group(1)
        epig_text = re.sub(r'\\vspace\*?\{[^}]*\}', '', epig_text)
        epig_text = re.sub(r'\\vfill', '', epig_text)
        epig_text = epig_text.replace('\\\\', '\n')
        epig_text = re.sub(r'\\noindent\s*', '', epig_text)
        epig_text = convert_text_basic(epig_text)
        epig_text = convert_inline(epig_text)
        epig_text = convert_flushright(epig_text)
        output += f'\n{epig_text}\n\n---\n\n'

    # Dedicatoria
    ded_match = re.search(r'\\begin\{dedicatoria\}(.*?)\\end\{dedicatoria\}', main_tex, re.DOTALL)
    if ded_match:
        ded_text = ded_match.group(1)
        ded_text = re.sub(r'\\vspace\*?\{[^}]*\}', '', ded_text)
        ded_text = re.sub(r'\\vfill', '', ded_text)
        ded_text = re.sub(r'\\noindent\s*', '', ded_text)
        ded_text = convert_text_basic(ded_text)
        ded_text = convert_inline(ded_text)
        output += f'> **Dedicat\u00f3ria:** {ded_text.strip()}\n\n---\n\n'

    # Abstract/Resumo
    resumo_match = re.search(r'\\begin\{resumo\}(.*?)\\end\{resumo\}', main_tex, re.DOTALL)
    if resumo_match:
        # Split into resumo and abstract (if present)
        res_parts = re.split(r'\\begin\{resumo\}\[Abstract\]', main_tex)
        if len(res_parts) > 1:
            # Has both resumo and abstract
            resumo_part = res_parts[0]
            resumo_match2 = re.search(r'\\begin\{resumo\}(.*?)\\end\{resumo\}', resumo_part, re.DOTALL)
            if resumo_match2:
                resumo_text = resumo_match2.group(1)
                # Remove the keywords part
                resumo_body = re.sub(r'\\vspace\{[^}]*\}.*?\\noindent\s*\\textbf\{Palavras-chave\}.*$', '', resumo_text, flags=re.DOTALL)
                resumo_body = convert_text_basic(resumo_body)
                resumo_body = convert_inline(resumo_body)
                resumo_body = convert_citations(resumo_body)
                output += f'> **Resumo:** {resumo_body.strip()}\n\n'

                # Keywords
                kw_match = re.search(r'\\textbf\{Palavras-chave\}:\s*(.*?)\\end\{resumo\}', resumo_match2.group(0), re.DOTALL)
                if kw_match:
                    kws = kw_match.group(1).strip()
                    kws = convert_text_basic(kws)
                    output += f'> **Palavras-chave:** {kws}\n\n'

    # Abstract in English
    abs_match2 = re.search(r'\\begin\{otherlanguage\*\}\{english\}(.*?)\\end\{otherlanguage\*\}', main_tex, re.DOTALL)
    if abs_match2:
        abs_text = abs_match2.group(1)
        abs_body = re.sub(r'\\vspace\{[^}]*\}.*?\\noindent\s*\\textbf\{Keywords\}.*$', '', abs_text, flags=re.DOTALL)
        abs_body = convert_text_basic(abs_body)
        abs_body = convert_inline(abs_body)
        abs_body = convert_citations(abs_body)
        output += f'> **Abstract:** {abs_body.strip()}\n\n'

        # Keywords EN
        kw_en = re.search(r'\\textbf\{Keywords\}:\s*(.*)', abs_text)
        if kw_en:
            kws = kw_en.group(1).strip()
            kws = convert_text_basic(kws)
            output += f'> **Keywords:** {kws}\n\n'

    output += '---\n\n'

    # Siglas table (from main.tex)
    siglas_match = re.search(r'\\begin\{siglas\}(.*?)\\end\{siglas\}', main_tex, re.DOTALL)
    if siglas_match:
        siglas_text = siglas_match.group(1)
        items = re.findall(r'\\item\[([^\]]*)\]\s*(.*?)(?=\\item\[|$)', siglas_text, re.DOTALL)
        output += '## Lista de Abreviaturas e Siglas\n\n'
        output += '| Sigla | Significado |\n|-------|-------------|\n'
        for abbr, meaning in items:
            meaning = meaning.strip()
            meaning = convert_inline(meaning)
            output += f'| {abbr} | {meaning} |\n'
        output += '\n---\n\n'

    # Process each chapter file
    chapters = [
        ('cap1-introducao.tex', 'Introdu\u00e7\u00e3o'),
        ('cap2-fundamentos-antropologicos.tex', 'Fundamentos Antropol\u00f3gicos e \u00c9ticos'),
        ('cap3-ia-desafios.tex', 'Intelig\u00eancia Artificial e os Desafios \u00e0 Personalidade Humana'),
        ('cap4-protecao-juridica.tex', 'Prote\u00e7\u00e3o Jur\u00eddica da Personalidade no Direito Brasileiro'),
        ('cap5-contribuicoes-magnifica.tex', 'Contribui\u00e7\u00f5es da Magnifica Humanitas para a Regula\u00e7\u00e3o da IA'),
        ('cap6-conclusao.tex', 'Conclus\u00e3o'),
    ]

    for filename, _ in chapters:
        chapter_text = read_file(filename)
        md = convert_chapter_file(chapter_text)
        output += f'\n\n{md}\n\n'

    # References placeholder
    output += '\n---\n\n## Refer\u00eancias\n\n> As refer\u00eancias completas encontram-se no arquivo `refs.bib` (formato BibTeX). Esta se\u00e7\u00e3o deve ser gerada automaticamente pelo sistema de cita\u00e7\u00e3o.\n\n'

    # Appendix
    output += '\n---\n\n'
    anexo_text = read_file('anexo-fichamentos.tex')
    md_anexo = convert_chapter_file(anexo_text)
    output += md_anexo

    # Final cleanup
    output = clean_empty_lines(output)

    # Write output
    with open(OUTPUT, 'w', encoding='utf-8') as f:
        f.write(output)

    print(f"Conversao concluida! Arquivo salvo em: {OUTPUT}")
    print(f"   Tamanho: {len(output):,} caracteres")
    print(f"   Linhas: {output.count(chr(10)):,}")

if __name__ == '__main__':
    main()
