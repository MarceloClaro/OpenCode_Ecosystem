# REFERENCIAL REGULATÓRIO — Diretrizes Editoriais para Publicação Científica

## Sumário

1. [IEEE](#1-ieee)
2. [Elsevier](#2-elsevier)
3. [ACM](#3-acm)
4. [Springer Nature](#4-springer-nature)
5. [ABNT/CAPES (Nacional)](#5-abntcapes-nacional)
6. [APA 7](#6-apa-7)
7. [MDPI](#7-mdpi)
8. [SBC](#8-sbc)
9. [Taylor & Francis](#9-taylor--francis)
10. [Comparativo Rápido](#10-comparativo-rapido)

---

## 1. IEEE

### Classe LaTeX
`IEEEtran.cls` v1.8b (2015)

### Opções de classe
| Opção | Uso |
|-------|-----|
| `\documentclass[conference]{IEEEtran}` | Conferências (padrão 10pt, duas colunas) |
| `\documentclass[journal]{IEEEtran}` | Transactions/journals (10pt, duas colunas) |
| `\documentclass[10pt,journal,compsoc]{IEEEtran}` | Computer Society journal |
| `\documentclass[conference,compsoc]{IEEEtran}` | Computer Society conference |
| `\documentclass[journal,comsoc]{IEEEtran}` | Communications Society |
| `\documentclass[9pt,technote]{IEEEtran}` | Briefs, correspondence |

### Formatação
- **Papel:** US Letter (8,5 × 11") ou A4 (conferências internacionais)
- **Colunas:** Duas colunas (exceto título/autores)
- **Fonte:** Times New Roman, corpo 10pt
- **Espaçamento:** Simples
- **Margens:** 0,67" (superior/inferior), 0,69" (laterais) — gerenciadas pela classe
- **Sem numeração de páginas** (adicionadas pelos organizadores)

### Citações
- Numeradas: `[1]`, `[2,3]`, `[4]-[7]`
- Estilo: `IEEEtran.bst` ou `IEEEtranSA.bst`
- Arquivo `.bst` incluso no pacote

### Elementos obrigatórios
- Title (sem símbolos especiais ou matemática)
- Author block (nome, afiliação, e-mail)
- Abstract (150-250 palavras)
- Index Terms (3-10 palavras-chave)
- Section numbering: I, II, III (romanos)
- References

### Submissão
- IEEE PDF eXpress obrigatório para validação do PDF
- Template atualizado em 2024 para Word; LaTeX permanece IEEEtran v1.8b
- Duplo-cego: remover autores na submissão inicial

### Documentação oficial
- `IEEEtran_HOWTO.pdf` (incluído no pacote)
- [IEEE Template Selector](https://template-selector.ieee.org/)
- [Manuscript Templates for Conference Proceedings](https://www.ieee.org/conferences/publishing/templates.html)

---

## 2. Elsevier

### Classe LaTeX
`elsarticle.cls` v3.5 (Jan/2026)

### Opções de classe
| Opção | Uso |
|-------|-----|
| `\documentclass[preprint,12pt,review]{elsarticle}` | Revisão (pré-publicação) |
| `\documentclass[3p,12pt]{elsarticle}` | Duas colunas (production) |
| `\documentclass[5p,12pt]{elsarticle}` | Duas colunas largas |
| `\documentclass[1p,12pt]{elsarticle}` | Coluna única |
| Classes CAS: `cas-dc.cls` (duas colunas), `cas-sc.cls` (coluna única) |

### Formatação
- **Papel:** A4
- **Fonte:** Times New Roman, 12pt (review), 10pt (production)
- **Espaçamento:** Duplo (review), simples (production) — controlado pela classe
- **Margens:** Gerenciadas pela classe

### Citações
| Estilo | `.bst` | Uso |
|--------|--------|-----|
| Numerado | `elsarticle-num.bst` | Padrão numérico |
| Harvard (autor-ano) | `elsarticle-harv.bst` | Ciências sociais |
| Numerado com nomes | `elsarticle-num-names.bst` | Híbrido |
| CAS Model 2 Names | `cas-model2-names.bst` | CAS workflow |

### Elementos obrigatórios
- Title (conciso, sem abreviações)
- Author names (given + family)
- Affiliations
- Abstract
- Keywords (4-8)
- Classification codes (opcional, por journal)

### Submissão
- PDF aceito na submissão inicial
- Fonte editável (.tex + .bib + figuras) na versão final
- Template CAS disponível para journals com Complex Article Service

### Documentação oficial
- `elsdoc.pdf` (incluído no pacote)
- [Elsevier LaTeX Instructions](https://www.elsevier.com/researcher/author/policies-and-guidelines/latex-instructions)
- [elsarticle no CTAN](https://ctan.org/pkg/elsarticle)
- Guide for Authors individual por journal

---

## 3. ACM

### Classe LaTeX
`acmart.cls` v2.16 (Ago/2025)

### Opções de classe (template styles)
| Template | Uso |
|----------|-----|
| `\documentclass[sigconf]{acmart}` | Conferências ACM (padrão) |
| `\documentclass[manuscript]{acmart}` | Submissão (coluna única, revisão) |
| `\documentclass[acmsmall]{acmart}` | Journals ACM small trim |
| `\documentclass[acmlarge]{acmart}` | Journals ACM large (IMWUT, PACMPL, etc.) |
| `\documentclass[acmtog]{acmart}` | TOG (ACM Transactions on Graphics) |
| `\documentclass[sigplan]{acmart}` | SIGPLAN conferences |

### Fluxo TAPS (desde 2020)
1. Submeter em **coluna única** (`manuscript`)
2. Se aceito, TAPS converte automaticamente para **coluna dupla** (publicação)
3. Revisar PDF e HTML gerados pelo TAPS antes da aprovação final

### Formatação
- **Papel:** US Letter (padrão)
- **Fonte:** Novos fontes ACM (Berkeley, Libertine, etc.) — gerenciados pela classe
- **Revisor:** coluna única, espaçamento 1.5
- **Publicação:** coluna dupla, espaçamento simples

### Citações
- Estilo: `ACM-Reference-Format.bst`
- Chicago-style (autor-ano ou numerado, controlado por opção)
- DOI obrigatório quando disponível

### Elementos obrigatórios
- Title
- Author (nome, ORCID obrigatório, afiliação, e-mail)
- Abstract (150-250 palavras)
- CCS Concepts (ACM Computing Classification System)
- Keywords
- Acknowledgments (incluindo divulgação de uso de IA)

### Políticas
- **Desde Jan/2026:** Anais de conferências ACM são open access
- Divulgação obrigatória de uso de IA generativa
- ORCID obrigatório para todos os autores

### Documentação oficial
- `acmart.pdf` (User's Guide)
- [ACM LaTeX Template](https://authors.acm.org/proceedings/production-information/preparing-your-article-with-latex)
- [ACM Primary Article Templates](https://www.acm.org/publications/proceedings-template)
- Chicago Manual of Style (copyediting)

---

## 4. Springer Nature

### Classe LaTeX
`sn-jnl.cls` v3.1 (Dez/2024)

### Opções de classe
| Opção | Uso |
|-------|-----|
| `\documentclass[sn-basic]{sn-jnl}` | Springer Basic Reference Style |
| `\documentclass[sn-nature]{sn-jnl}` | Nature Portfolio |
| `\documentclass[sn-mathphys-num]{sn-jnl}` | Matemática/Física (numerado) |
| `\documentclass[sn-mathphys-ay]{sn-jnl}` | Matemática/Física (autor-ano) |
| `\documentclass[sn-vancouver]{sn-jnl}` | Vancouver (biomédicas) |
| `\documentclass[sn-chicago]{sn-jnl}` | Chicago (humanidades) |
| `\documentclass[sn-apacite]{sn-jnl}` | APA |
| `\documentclass[referee]{sn-jnl}` | Revisão (espaçamento duplo) |
| `\documentclass[lineno]{sn-jnl}` | Linhas numeradas |

### Estilos bibliográficos disponíveis (9)
`sn-basic.bst`, `sn-nature.bst`, `sn-mathphys-num.bst`, `sn-mathphys-ay.bst`, `sn-vancouver-num.bst`, `sn-vancouver-ay.bst`, `sn-chicago.bst`, `sn-apacite.bst`, `sn-aps.bst`

### Formatação
- **Papel:** A4
- **Abordagem:** "content first" — formatação mínima, estilisticamente neutra
- **Fonte:** Padrão LaTeX (Computer Modern / Times)
- **Espaçamento:** Simples (padrão); duplo (opção referee)

### Regras importantes
- Não usar `\input{}` para incluir outros `.tex` — submeter como um único arquivo
- Todas as figuras como arquivos separados (não incorporadas no .tex)
- Não usar subdiretórios para arquivos
- Não usar fontes personalizadas
- Verificar instruções específicas do journal alvo (além do template)

### Submissão
- Template único para Springer, Nature Portfolio e BMC
- Overleaf: template oficial disponível
- Editorial Manager: selecionar "Manuscript" para todos os arquivos .tex/.cls/.bst

### Documentação oficial
- `user-manual.pdf` (incluído)
- [Springer Nature LaTeX Author Support](https://www.springernature.com/gp/authors/campaigns/latex-author-support)
- [Overleaf Template](https://www.overleaf.com/latex/templates/springer-nature-latex-template/gsvvftmrppwq)

---

## 5. ABNT/CAPES (Nacional)

### Classe LaTeX
`abntex2.cls` v1.9.7

### Normas ABNT vigentes (2023-2026)
| Norma | Objeto | Última atualização |
|-------|--------|-------------------|
| NBR 14724 | Trabalhos acadêmicos (estrutura) | 2011 (em revisão) |
| NBR 10520 | Citações | 2023 |
| NBR 6023 | Referências | 2018 |
| NBR 6022 | Artigos científicos | 2019 |
| NBR 6024 | Numeração progressiva | 2012 |
| NBR 6027 | Sumário | 2012 |
| NBR 6028 | Resumo | 2021 |
| NBR 15287 | Projeto de pesquisa | 2011 |

### Formatação ABNT (NBR 14724)
- **Papel:** A4 (210 × 297 mm)
- **Fonte:** Times New Roman ou Arial, tamanho 12 (corpo), 10 (citação longa/nota)
- **Espaçamento:** 1,5 entre linhas; simples em citações longas, notas, referências
- **Margens:** 3 cm (superior/esquerda), 2 cm (inferior/direita)
- **Alinhamento:** Justificado
- **Recuo:** 1,25 cm (primeira linha do parágrafo); 4 cm (citação direta longa)
- **Numeração:** A partir da primeira página textual (introdução), canto superior direito

### Elementos do trabalho acadêmico
**Pré-textuais:** Capa, folha de rosto, ficha catalográfica, errata (opcional), folha de aprovação, dedicatória (opcional), agradecimentos (opcional), epígrafe (opcional), resumo/abstract, listas (ilustrações/tabelas/abreviaturas), sumário

**Textuais:** Introdução, desenvolvimento, conclusão

**Pós-textuais:** Referências, glossário (opcional), apêndices, anexos, índice (opcional)

### Citações (NBR 10520:2023)
- **Direta curta** (< 3 linhas): no corpo do texto, entre aspas duplas
- **Direta longa** (≥ 3 linhas): bloco recuado 4 cm, fonte 10, sem aspas
- **Indireta:** paráfrase sem aspas, com autor e ano
- **Sistema autor-data:** (Sobrenome, ano) — padrão abntex2-alf
- **Sistema numérico:** [1], [2] — padrão abntex2-num

### Opções de classe abntex2
| Opção | Efeito |
|-------|--------|
| `12pt` | Corpo do texto |
| `openright` | Capítulos começam em página ímpar |
| `openany` | Capítulos em qualquer página |
| `twoside` | Verso e anverso |
| `oneside` | Apenas anverso |
| `a4paper` | Papel A4 |
| `brazilian` | Idioma português brasileiro |

### CAPES — Diretrizes gerais
- Dissertações e teses seguem NBR 14724
- Artigos: NBR 6022
- Ficha catalográfica obrigatória
- DOI recomendado para todos os trabalhos
- ORCID recomendado para autores
- Declaração de uso de IA generativa (exigência crescente desde 2025)

---

## 6. APA 7

### Classe LaTeX
`apa7.cls` (CTAN)

### Opções
| Opção | Uso |
|-------|-----|
| `\documentclass[man]{apa7}` | Manuscrito (submissão) |
| `\documentclass[jou]{apa7}` | Artigo publicado (formato journal) |
| `\documentclass[doc]{apa7}` | Documento acadêmico (tese/dissertação) |

### Formatação APA 7
- **Papel:** US Letter
- **Fonte:** Times New Roman 12pt
- **Espaçamento:** Duplo (todo o documento)
- **Margens:** 1" (2,54 cm) todos os lados
- **Recuo:** 0,5" (1,27 cm) primeira linha do parágrafo
- **Running head:** Título abreviado (≤ 50 caracteres) no topo

### Elementos do artigo
1. Title page (title, authors, affiliations, author note, word count)
2. Abstract (≤ 250 palavras)
3. Introduction
4. Method
5. Results
6. Discussion
7. References
8. Footnotes (se houver)
9. Tables
10. Figures
11. Appendices

### Citações APA 7
- Autor-data: (Sobrenome, ano)
- Citação narrativa: Sobrenome (ano)
- 3+ autores: (Sobrenome et al., ano)
- DOI obrigatório quando disponível
- Formato: `https://doi.org/xxxx`

---

## 7. MDPI

### Classe LaTeX
`mdpi.cls` (via GitHub `metaphori/Template-LaTeX-MDPI`)

### Opções de classe
| Opção | Uso |
|-------|-----|
| `\documentclass[journal,article,submit]{Definitions/mdpi}` | Submissão a journal |
| `\documentclass[preprints,article,submit]{Definitions/mdpi}` | Preprint |
| `submit` → `accept` | Remove line numbers (após aceite) |

### Formatação
- **Papel:** A4
- **Fonte:** Times New Roman
- **Coluna:** Duas colunas (padrão MDPI)
- **Espaçamento:** Simples
- **Abstract:** Máximo 200 palavras, sem citações

### Citações
- Numeradas: [1], [2]
- Estilos: `mdpi.bst` (padrão), `chicago2.bst` (Chicago para journals específicos)
- APA: `admsci, aieduc, behavsci, education`, etc.
- Chicago: `arts, genealogy, histories, humanities, laws, religions`, etc.

### Estrutura
1. Title
2. Abstract (≤ 200 palavras, sem citações)
3. Keywords
4. Introduction
5. Materials and Methods / Results / Discussion / Conclusions
6. Supplementary Materials (opcional)
7. Author Contributions
8. Funding
9. Acknowledgments
10. Conflicts of Interest
11. References

### Políticas
- Open access (todos os artigos)
- Template obrigatório (desk reject se não usar)
- English language editing disponível
- 120 MB max para arquivos

### Documentação oficial
- [MDPI LaTeX Template](https://www.mdpi.com/authors/latex)
- [Overleaf Template](https://www.overleaf.com/latex/templates/mdpi-article-template/fcpwsspfzsph)
- [MDPI Layout Style Guide](https://www.mdpi.com/authors/layout)

---

## 8. SBC

### Classe/Pacote LaTeX
`sbc-template.sty` (v2017)

### Uso
```latex
\documentclass[12pt]{article}
\usepackage{sbc-template}
```

### Formatação
- **Papel:** A4
- **Fonte:** Times, 12pt
- **Coluna:** Única
- **Margens:** 3,5 cm (superior), 2,5 cm (inferior), 3,0 cm (laterais)
- **Recuo:** 1,27 cm
- **Espaçamento:** 6pt entre parágrafos
- **Sem cabeçalhos/rodapés**
- **Sem numeração de páginas**

### Elementos
- Title
- Author(s) com instituições e e-mails
- Abstract (≤ 10 linhas, inglês)
- Resumo (≤ 10 linhas, português — obrigatório para artigos em PT-BR)
- Keywords / Palavras-chave
- Seções numeradas
- References (estilo `sbc.bst`)

### Regras
- Artigos completos: até 12 páginas
- Short papers: até 4 páginas
- Template SBC Reviews (2025): classe específica `sbcreviews-2025`

---

## 9. Taylor & Francis

### Classe LaTeX
`interact.cls`

### Opções
```latex
\documentclass[]{interact}
```

### Estilos de referência disponíveis
| Estilo | Arquivo | Uso |
|--------|---------|-----|
| NLM | `interactnlmsample.tex` | Ciências biomédicas |
| APA | `interactapasample.tex` | Ciências sociais |
| Chicago | `interactcadsample.tex` | Humanidades |

### Formatação
- **Papel:** US Letter ou A4
- **Fonte:** Times New Roman (submissão); Minion Pro/Myriad Pro (publicação)
- **Coluna:** Única (submissão/revisão); convertida para duas colunas pelo typesetter
- **Espaçamento:** Simples (padrão); duplo com pacote `setspace`

### Fluxo de publicação
1. Submeter em coluna única (template `interact`)
2. Se aceito, typesetter converte para formatação final do journal
3. Fontes Minion Pro/Myriad Pro usadas apenas na publicação final
4. Não tentar igualar a formatação final — usar fontes LaTeX padrão

### Elementos
- `\articletype{...}` — tipo de artigo
- Title
- Authors (nome, afiliação, e-mail, ORCID)
- Abstract
- Keywords (separadas por ponto e vírgula)
- Main text
- Acknowledgments
- Disclosure statement
- References
- Appendices

### Documentação oficial
- [Overleaf T&F Interact + APA](https://www.overleaf.com/latex/templates/taylor-and-francis-latex-template-for-authors-interact-layout-plus-apa-reference-style/jqhskrsqqzfz)
- [Overleaf T&F Interact + NLM](https://www.overleaf.com/latex/templates/taylor-and-francis-latex-template-for-authors-interact-layout-plus-nlm-reference-style/bngwgqnxcxrp)

---

## 10. Comparativo Rápido

| Característica | IEEE | Elsevier | ACM | Springer Nature | ABNT | MDPI | SBC | T&F | APA 7 |
|---------------|------|----------|-----|-----------------|------|------|-----|-----|-------|
| **Classe** | IEEEtran | elsarticle | acmart | sn-jnl | abntex2 | mdpi | sbc-template | interact | apa7 |
| **Colunas** | 2 | 1-2 | 1 (rev) / 2 (pub) | 1 | 1 | 2 | 1 | 1 | 1 |
| **Fonte** | Times 10pt | Times 12pt | ACM fonts | Content-first | Times 12pt | Times | Times 12pt | Times | Times 12pt |
| **Espaçamento** | Simples | Revisor duplo | 1.5 (rev) | Simples | 1.5 | Simples | 6pt | Simples | Duplo |
| **Citações** | Numérico | 3 estilos | Chicago | 9 estilos | Autor-data ou num | Numérico | sbc.bst | NLM/APA/Chicago | Autor-data |
| **Abstract** | 150-250 | 150-250 | 150-250 | Variável | 150-250 | ≤ 200 | ≤ 10 linhas | 150-250 | ≤ 250 |
| **Open Access** | Opcional | Opcional | Sim (conferências 2026) | Opcional | N/A | Sim | N/A | Opcional | Opcional |
| **Template obrigatório** | Recomendado | Recomendado | Sim | Recomendado | Sim | Sim | Sim | Recomendado | Sim |
| **Qualis A1 comum** | Trans. IEEE | Elsevier journals | ACM journals | Nature/Scientific Reports | N/A | MDPI journals | SBC Reviews | T&F journals | APA journals |
