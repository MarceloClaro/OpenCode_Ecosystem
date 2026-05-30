# Coleção de Templates LaTeX — Antiprojeto UFC

## Visão Geral

18 categorias de templates instalados em `templates/`. Total: ~130+ arquivos (~12 MB).

| # | Categoria | Diretório | Finalidade |
|---|-----------|-----------|------------|
| 1 | IEEE | `ieee/` | Transações, conferências |
| 2 | Elsevier | `elsevier/` | Journals Qualis A1 |
| 3 | Elsevier CAS | `elsevier-cas/` | Complex Article Service |
| 4 | ACM | `acm/` | Conferências SIG, journals |
| 5 | Springer Nature | `springer/` | Springer, Nature, BMC |
| 6 | ABNT | `abntex2/` | Teses, dissertações, TCCs |
| 7 | APA 7 | `apa7/` | Manuscritos APA 7 |
| 8 | KOMA-Script | `koma-script/` | Alternativa alemã (scrartcl, scrreprt, scrbook) |
| 9 | MDPI | `mdpi/` | Journals MDPI (open access) |
| 10 | SBC | `sbc/` | Conferências SBC |
| 11 | Taylor & Francis | `tandf/` | T&F journals (Interact) |
| 12 | PRISMA 2020 | `prisma/` | Revisões sistemáticas |
| 13 | CAPES/CNPq | `capes/` | Propostas de fomento |
| 14 | **Artigo Qualis A1** | `artigo/` | Modelo de artigo científico |
| 15 | **Dissertação/Tese** | `dissertacao/` | Modelo ABNT completo |
| 16 | **Ensaios/Fichamentos** | `ensaio_fichamento/` | Gêneros acadêmicos complementares |
| 17 | **Diretrizes Editoriais** | `regulamentos/` | Referencial regulatório |
| 18 | **Anteprojeto** | (raiz) | Anteprojeto PPGTE/UFC |

---

## 1. IEEE (`ieee/`)

| Arquivo | Descrição |
|---------|-----------|
| `IEEEtran.cls` | Classe oficial IEEE V1.8b (2015) |
| `bare_conf.tex` | Template para conferências |
| `bare_jrnl.tex` | Template para periódicos/journals |
| `IEEEtran_HOWTO.pdf` | Documentação (~90 pág.) |

**Uso:** `\documentclass[conference]{IEEEtran}` ou `\documentclass[journal]{IEEEtran}`
**Destino:** Transações IEEE, conferências (Engenharia, Computação)

---

## 2. Elsevier (`elsevier/`)

| Arquivo | Descrição |
|---------|-----------|
| `elsarticle.cls` | Classe oficial Elsevier v3.5 (Jan/2026) |
| `elsarticle-template-num.tex` | Template referências numeradas |
| `elsarticle-template-harv.tex` | Template Harvard (autor-ano) |
| `elsarticle-template-num-names.tex` | Template numerado com natbib |
| `elsarticle-num.bst`, `elsarticle-harv.bst`, `elsarticle-num-names.bst` | Estilos bibliográficos |
| `doc/elsdoc.pdf` | Documentação completa |

**Uso:** `\documentclass[preprint,12pt,review]{elsarticle}`
**Destino:** Elsevier journals Qualis A1 (JSS, CORA, etc.)

---

## 3. ACM (`acm/`)

| Arquivo | Descrição |
|---------|-----------|
| `acmart.cls` | Classe oficial ACM v2.16 (Ago/2025) |
| `acmart-tagged.cls` | Versão com acessibilidade PDF |
| `ACM-Reference-Format.bst` | Estilo bibliográfico |
| `sample-sigconf.tex` | Modelo conferência SIG |
| `sample-acmsmall.tex` | Modelo journal ACM |
| +8 outros samples (biblatex, lualatex, xelatex, authordraft, etc.) | Variações |
| `acmart.pdf` | Documentação do pacote |

**Uso:** `\documentclass[sigconf]{acmart}`
**Destino:** ACM conferences, SIGs, Computing journals

---

## 4. Springer Nature (`springer/` e `nature/`)

| Arquivo | Descrição |
|---------|-----------|
| `sn-jnl.cls` | Classe oficial Springer Nature v0.1 (2019) |
| `sn-article.tex` | Template de artigo v3.1 (Dez/2024) |
| `bst/sn-nature.bst` | Estilo Nature Portfolio |
| `bst/sn-mathphys-num.bst`, `bst/sn-mathphys-ay.bst` | Estilos Matemática/Física |
| `bst/sn-basic.bst`, `bst/sn-vancouver-*.bst`, `bst/sn-chicago.bst`, `bst/sn-apacite.bst` | Outros estilos |
| `user-manual.pdf` | Manual do usuário |
| (legado) `ctan-nature.cls` | Nature.cls não oficial (2004) — apenas referência |

**Uso:** `\documentclass[sn-nature]{sn-jnl}` (Nature) ou `\documentclass[sn-mathphys]{sn-jnl}`
**Destino:** Springer Nature journals, Nature Portfolio, BMC

---

## 5. ABNT / Brasileiro (`abntex2/`)

| Arquivo | Descrição |
|---------|-----------|
| `abntex2.cls` | Classe ABNT v1.9.7 (NBR 14724, 6024, etc.) |
| `abntex2-alf.bst` | Estilo bibliográfico alfabético (autor-data) |
| `abntex2-num.bst` | Estilo bibliográfico numérico |
| `abntex2cite.sty` | Pacote de citações ABNT NBR 10520 |
| `abntex2abrev.sty` | Macros de abreviação |
| `abntex2-modelo-trabalho-academico.tex` | Modelo de tese/dissertação |
| `abntex2-modelo-artigo.tex` | Modelo de artigo científico (NBR 6022) |

**Uso:** `\documentclass[12pt,openright,twoside,a4paper]{abntex2}`
**Destino:** Teses, dissertações, TCCs, artigos ABNT

---

## 6. PRISMA 2020 (`prisma/`)

| Arquivo | Descrição |
|---------|-----------|
| `prisma2020-flow.tex` | Diagrama de fluxo PRISMA 2020 (TikZ) |
| `prisma2020-checklist.tex` | Checklist PRISMA 2020 de 27 itens |

**Uso:** Compilar com `pdflatex`. Números editáveis via `\newcommand`.
**Destino:** Revisões sistemáticas e meta-análises

---

## 7. Fomento CAPES/CNPq (`capes/`)

| Arquivo | Descrição |
|---------|-----------|
| `proposta_fomento.tex` | Template de proposta de projeto de pesquisa |

**Seções:** Capa, Identificação, Resumo, Introdução, Objetivos, Metodologia, Resultados, Plano de Trabalho, Orçamento, Equipe, Referências
**Destino:** Editais CNPq Universal, CAPES, FAPESP, FAPs estaduais

---

## 8. APA 7 (`apa7/`)

| Arquivo | Descrição |
|---------|-----------|
| `apa7.dtx`, `apa7.ins` | Fonte da classe APA 7 (gerar com `latex apa7.ins`) |
| `apa7.pdf` | Documentação |
| `longsample.pdf`, `shortsample.pdf` | Exemplos compilados (PSYCH, etc.) |

**Uso:** `\documentclass[man]{apa7}` (manuscrito) | `\documentclass[jou]{apa7}` (publicado) | `\documentclass[doc]{apa7}` (tese)
**Destino:** Manuscritos APA 7 (Psicologia, Educação, Ciências Sociais)

---

## 9. Elsevier CAS (`elsevier-cas/`)

| Arquivo | Descrição |
|---------|-----------|
| `cas-dc.cls` | Classe CAS duas colunas |
| `cas-sc.cls` | Classe CAS coluna única |
| `cas-common.sty` | Estilos compartilhados CAS |
| `cas-dc-sample.tex` | Template duas colunas |
| `cas-sc-sample.tex` | Template coluna única |
| `cas-model2-names.bst` | Estilo bibliográfico |
| `cas-refs.bib` | Referências de exemplo |

**Uso:** `\documentclass{ cas-dc }` ou `\documentclass{ cas-sc }`
**Destino:** Elsevier journals com Complex Article Service

---

## 10. KOMA-Script (`koma-script/`)

| Arquivo | Descrição |
|---------|-----------|
| Fonte `.dtx` | CTAN snapshot (referência) |
| Classes instaladas no MiKTeX | `scrartcl`, `scrreprt`, `scrbook` |

**Uso:** `\documentclass{scrartcl}` | `\documentclass{scrreprt}` | `\documentclass{scrbook}`
**Destino:** Alternativa tipográfica europeia a `article`/`report`/`book`

---

## 11. MDPI (`mdpi/`)

| Arquivo | Descrição |
|---------|-----------|
| `Definitions/mdpi.cls` | Classe oficial MDPI |
| `template.tex` | Template de artigo |
| `bibliography.bib` | Referências de exemplo |

**Uso:** `\documentclass[journal,article,submit]{Definitions/mdpi}`
**Destino:** Journals MDPI open access (Sensors, Energies, etc.)

---

## 12. SBC (`sbc/`)

| Arquivo | Descrição |
|---------|-----------|
| `sbc-template.sty` | Pacote de estilo SBC |
| `sbc-template.tex` | Template de artigo |
| `sbc.bst` | Estilo bibliográfico |
| `sbc-template.bib` | Referências de exemplo |

**Uso:** `\documentclass[12pt]{article}` + `\usepackage{sbc-template}`
**Destino:** Congressos e revistas SBC (Computação)

---

## 13. Taylor & Francis (`tandf/`)

| Arquivo | Descrição |
|---------|-----------|
| `interact.cls` | Classe Interact (T\&F) |
| `interactnlmsample.tex` | Template NLM (biomédicas) |

**Observação:** Arquivos complementares (`interact.bst`, `interactapasample.*`) não localizados. Usar template Overleaf oficial: jqhskrsqqzfz (APA) ou bngwgqnxcxrp (NLM).
**Destino:** Taylor & Francis journals

---

## 14. Artigo Qualis A1 (`artigo/`)

| Arquivo | Descrição |
|---------|-----------|
| `artigo_modelo_qualis_a1.tex` | Modelo completo de artigo científico |
| `artigo_modelo_qualis_a1.bib` | Base bibliográfica (12 tipos de entrada) |

**Classes suportadas:** Elsevier (`elsarticle`), ACM (`acmart`), Springer Nature (`sn-jnl`), MDPI (`mdpi`)
**Seções:** Título, Autores, Resumo, Keywords, Introdução, Referencial Teórico, Metodologia, Resultados, Discussão, Conclusão, Financiamento, Agradecimentos, Declarações
**Destino:** Submissão a periódicos Qualis A1

---

## 15. Dissertação/Tese ABNT (`dissertacao/`)

| Arquivo | Descrição |
|---------|-----------|
| `dissertacao_modelo_abnt.tex` | Modelo completo de dissertação/tese (abnTeX2) |
| `dissertacao_modelo_abnt.bib` | Base bibliográfica |

**Elementos:** Capa, Folha de rosto, Dedicatória, Agradecimentos, Epígrafe, Resumo/Abstract, Listas, Siglas, Símbolos, Sumário, 6 capítulos, Referências, Apêndices
**Destino:** Dissertações de mestrado e teses de doutorado (formato ABNT)

---

## 16. Ensaios e Fichamentos (`ensaio_fichamento/`)

| Arquivo | Descrição |
|---------|-----------|
| `ensaio_academico.tex` | Modelo de ensaio acadêmico |
| `resenha_critica.tex` | Modelo de resenha crítica |
| `fichamento.tex` | Modelo de fichamento estruturado |
| `ensaio_modelo.bib`, `resenha_modelo.bib`, `fichamento_bib.bib` | Bases bibliográficas |

**Características:**
- **Ensaio:** Tom autoral, reflexão teórica, estrutura livre, 5-15 referências
- **Resenha:** Identificação da obra (1/3), análise crítica (2/3)
- **Fichamento:** Tabela Longtable (obra, citações, paráfrases, comentários, conexões)

**Destino:** Trabalhos acadêmicos de gêneros complementares

---

## 17. Diretrizes Editoriais (`regulamentos/`)

| Arquivo | Descrição |
|---------|-----------|
| `REFERENCIAL_REGULATORIO.md` | Compilação das diretrizes editoriais de 10 entidades |

**Entidades cobertas:** IEEE, Elsevier, ACM, Springer Nature, ABNT/CAPES, APA 7, MDPI, SBC, T&F, Comparativo Rápido
**Conteúdo:** Classes, opções, formatação, citações, elementos obrigatórios, submissão, documentação oficial

---

## Como Usar

### Opção A — Copiar para o diretório do projeto
```bash
cp templates/ieee/IEEEtran.cls meu-artigo/
```

### Opção B — Instalar no MiKTeX (Windows)
Abra o MiKTeX Console e instale os pacotes:
- `ieeetran`, `elsarticle`, `acmart`, `abntex2`, `sn-jnl`

### Opção C — Manter no diretório de templates e referenciar
```latex
\documentclass{../templates/ieee/IEEEtran}
```

---

## Histórico

| Data | Ação |
|------|------|
| 30/05/2026 | Criação da coleção com 8 categorias |
| 30/05/2026 | Expansão para 18 categorias: adicionados ELSEVIER-CAS, APA7, KOMA-SCRIPT, MDPI, SBC, T\&F, Artigo Qualis A1, Dissertação ABNT, Ensaios/Fichamentos, Regulamentos |
