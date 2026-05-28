# Specs: MCPs — Model Context Protocol Servers

**Total:** 41 (25 ativos + 16 inativos) | **Revisao:** 2026-05-27

---

## MCPs Ativos (25)

### Core / Infraestrutura (5)
| MCP | Funcao | Comando |
|-----|--------|---------|
| **filesystem** | Acesso a filesystem local | `npx @modelcontextprotocol/server-filesystem` |
| **code-runner** | Execucao de codigo em sandbox | `mcp-server-code-runner` |
| **mcp-python-interpreter** | Interpretador Python com sessoes REPL | `mcp-python-interpreter` |
| **sqlite** | Banco SQLite para queries estruturadas | `mcp-server-sqlite` |
| **sequential-thinking** | Raciocinio multi-etapa com revisao | `node .../server-sequential-thinking` |

### Busca / Web (3)
| MCP | Funcao |
|-----|--------|
| **websearch** | DuckDuckGo search integrado | 
| **fetch** | Fetch HTTP generico (HTML, JSON, Markdown) |
| **context7** | Documentacao de bibliotecas (Context7 API) — REMOTO |

### Codigo / Qualidade (4)
| MCP | Funcao |
|-----|--------|
| **gh_grep** | Busca em codigo GitHub (grep.app) — REMOTO |
| **eslint** | Linting JavaScript/TypeScript |
| **diff** | Diff entre textos (unified diff) |
| **node-sandbox** | Sandbox Node.js isolado (Docker) |

### Browser / UI (1)
| MCP | Funcao |
|-----|--------|
| **playwright** | Automacao de browser (headless) |

### Sistema / Tempo (2)
| MCP | Funcao |
|-----|--------|
| **memory** | Knowledge graph persistente |
| **time** | Conversao de timezone, timestamps |

### Colaboracao (1)
| MCP | Funcao |
|-----|--------|
| **github** | GitHub API: repos, PRs, issues, commits |

### Documentos (1)
| MCP | Funcao |
|-----|--------|
| **pdf** | Manipulacao de PDF: texto, watermark, header/footer |

### Ecossistema / Custom (5)
| MCP | Funcao |
|-----|--------|
| **decisionnode** | Memoria de decisoes entre ferramentas IA |
| **maswos-mcp** | Orquestracao MASWOS (agentes) |
| **maswos-juridico** | Servicos juridicos MASWOS |
| **maswos-rag** | RAG pipeline MASWOS |
| **antigravity-mcp** | Bridge Antigravity (Google DeepMind) |

### Verificacao / Diagramas (2)
| MCP | Funcao |
|-----|--------|
| **cora-verifier** | Verificacao simbolica CoRA |
| **flowzap-mcp** | Diagramas de arquitetura |

### Self-Healing (1)
| MCP | Funcao |
|-----|--------|
| **self-healer** | Auto-cura do ecossistema via Python |

---

## MCPs Inativos (16)

| MCP | Funcao | Motivo da Inatividade |
|-----|--------|----------------------|
| wikipedia | Enciclopedia | Sobreposicao com websearch |
| puppeteer | Browser automation | Sobreposicao com playwright |
| chrome-devtools | DevTools Chrome | Sobreposicao com playwright |
| desktop-commander | Automacao desktop | Escopo limitado |
| shell-server | Shell remoto | Seguranca |
| run-python | Python isolado | Sobreposicao com mcp-python-interpreter |
| mcp-server-commands | Comandos sistema | Sobreposicao com shell |
| biomcp | Bioinformatica | Dominio especifico |
| biothings | Dados biologicos | Dominio especifico |
| gget | Genomica | Dominio especifico |
| opengenes | Genomica | Dominio especifico |
| scihub | Artigos cientificos | Manutencao instavel |
| youtube-transcript | Transcricao YouTube | Manutencao instavel |
| mermaid | Diagramas Mermaid | Sobreposicao com flowzap-mcp |
| mem0-mcp | Memoria alternativa | Sobreposicao com memory |
| hacker-news | Noticias tech | Baixa prioridade |
| astronomy-oracle | Astronomia | Dominio muito especifico |

---

## Criterios de Qualidade MCP

Todos os MCPs ativos devem satisfazer:
- [ ] Health check responde em < 5s
- [ ] Timeout configurado por operacao
- [ ] Erros retornam mensagem descritiva (nao crasham)
- [ ] Logging estruturado (JSON ou key=value)
- [ ] Documentacao de ferramentas expostas
