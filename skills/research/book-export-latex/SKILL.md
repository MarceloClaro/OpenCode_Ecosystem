---
name: book-export-latex
description: "Skill do ecossistema OpenCode - book-export-latex"
---

name: book-export-latex
description: "Exportação e estruturação de livros acadêmicos e literários em LaTeX, com suporte a templates clássicos, portfólios e minimalistas."
user-invocable: true
license: MIT
compatibility: OpenCode, Claude Code
metadata:
  author: OpenCode Ecosystem v5.1
  version: "1.0.0"
  ecossistema: opencode
  categoria: escrita-livros
allowed-tools: Read Edit Write Bash Python Code-Runner
---

# Book Export LaTeX v1.0

Esta skill gerencia a estruturação de capítulos, compilação de sumário, bibliografia e exportação de livros acadêmicos longos para PDF usando o repositório de templates `lathex-template`.

## Regra Mandatória de Execução

> [!IMPORTANT]
> **SELEÇÃO DE TEMPLATE ANTES DA ESCRITA**:
> Antes de iniciar qualquer trabalho de redação, geração de capítulos ou estruturação do livro, os agentes do ecossistema **devem obrigatoriamente fazer uma pergunta de múltipla escolha ao usuário** para decidir o template desejado:
> - **book**: Design clássico estruturado com capa, sumário e divisões tradicionais.
> - **forta**: Design moderno/portfólio com cabeçalhos arrojados.
> - **apehex**: Design minimalista e direto ao ponto.

## Diretórios de Trabalho

- Repositório de Modelos: `templates/livro/`
- Estrutura de Trabalho: `livro-opencode/`
  - `capitulos/` - Arquivos `.tex` de capítulos individuais.
  - `ilustracoes/` - Arquivos de imagens e figuras TikZ.
  - `referencias/` - Arquivo de bibliografia.
