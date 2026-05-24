# LLM Wiki MVP

Implementação self-contained do padrão **LLM Wiki** como alternativa ao RAG tradicional. Roda 100% local com Ollama.

## O que faz

- **Upload** de PDFs, TXT e Markdown
- **Ingestão automática** com revisão humana (etapa "discutir antes de escrever" preservada)
- **Chat** para fazer perguntas sobre a wiki, com streaming
- **Browser** das páginas geradas, com edição inline
- **Graph view** interativo (pyvis)
- **Lint** para detectar páginas órfãs, links quebrados, estagnação
- **Editor de schema** para adaptar o comportamento ao seu domínio
- **100% local** — Ollama + sentence-transformers + SQLite + markdown no disco

## Arquitetura

| Camada | Implementação |
|---|---|
| 1. Ingestão | `pypdf` + extração de texto |
| 2. Síntese | Ollama orquestrado em 3 etapas (analyze → source page → entity pages) |
| 3. Armazenamento | SQLite (metadados, embeddings, log) + markdown em `data/wiki/` |
| 4. Interface | Streamlit single-page com 6 telas |

## Pré-requisitos

1. **Python 3.10+**
2. **Ollama** rodando local — instale em <https://ollama.com>
3. Pelo menos um modelo baixado:
   ```bash
   ollama pull llama3.1:8b
   ```
   Para hardware modesto, use `phi3:mini` ou `qwen2.5:3b`.
   Para hardware potente (Mac M-series, GPU), considere `qwen2.5:14b` ou `llama3.1:70b`.

## Instalação

```bash
git clone <este-repo>
cd llm-wiki-mvp
python -m venv .venv
source .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Como rodar

Em um terminal, garanta que o Ollama está rodando:
```bash
ollama serve
```

Em outro terminal, na pasta do projeto:
```bash
streamlit run app.py
```

A app abre em `http://localhost:8501`.

## Primeiro uso (5 minutos)

1. Em **Configurações → Modelo**, confirme que o Ollama está conectado e selecione o modelo desejado.
2. Em **Ingestão**, faça upload de um PDF ou TXT.
3. Clique em **🔍 Analisar** — o LLM apresenta resumo, pontos-chave e o que vai criar.
4. Clique em **✅ Confirmar ingestão** — a wiki é gerada (pode demorar com modelo grande).
5. Em **Wiki**, navegue pelas páginas geradas.
6. Em **Graph**, veja como as páginas se conectam.
7. Em **Chat**, faça perguntas sobre o conteúdo.
8. Repita com mais fontes — a wiki cresce e cruza referências.

## Estrutura de arquivos

```
llm-wiki-mvp/
├── app.py                    # entrypoint Streamlit
├── pyproject.toml
├── requirements.txt
├── config.yaml               # (criado automaticamente após primeira config)
├── src/
│   ├── config.py             # paths e modelo
│   ├── ingestion.py          # camada 1: PDF/TXT → texto
│   ├── synthesis.py          # camada 2: motor de wiki
│   ├── storage.py            # camada 3: SQLite + filesystem
│   ├── llm.py                # cliente Ollama + embeddings
│   └── ui/
│       ├── ingest_page.py
│       ├── chat_page.py
│       ├── browser_page.py
│       ├── graph_page.py
│       ├── lint_page.py
│       └── settings_page.py
├── prompts/                  # templates editáveis
│   ├── schema_default.md
│   ├── ingest_analyze.md
│   ├── create_source_page.md
│   ├── create_or_update_page.md
│   ├── query_answer.md
│   └── lint.md
└── data/                     # criado em runtime
    ├── wiki.db               # SQLite (metadados + embeddings)
    ├── schema.md             # schema editado pelo usuário
    ├── raw/                  # uploads originais
    └── wiki/                 # markdown gerado
        ├── topicos/
        ├── entidades/
        ├── conceitos/
        ├── sinteses/
        └── fontes/
```

## Limitações conhecidas (este é um MVP)

- **Modelos locais são mais limitados que Claude/GPT.** Esperar qualidade similar à demo da aula gravada com Claude Code é irrealista. Modelos abaixo de 7B costumam falhar em tarefas complexas; 14B+ é onde começa a funcionar bem.
- **Contexto curto.** Páginas truncadas em 2000 chars no contexto de queries. Para wikis grandes, considere migrar para modelo com 128K tokens.
- **Detector de duplicatas é por hash exato.** Não detecta duas versões de um PDF.
- **Sem auth, sem multi-tenancy** — single-user local. Para produção multi-user, fase 2.
- **Streaming pode travar a UI** em modelos muito lentos. Streamlit re-renderiza a cada chunk.
- **Wikilinks no browser não são clicáveis** (limitação Streamlit) — eles aparecem como `📎 link` para visibilidade. Para navegação completa, use a sidebar.

## Como adaptar para seu domínio

1. Em **Configurações → Schema**, edite o `schema.md` para descrever seu objetivo, princípios e tom.
2. Em **Configurações → Categorias**, ajuste a estrutura de pastas. Para wiki de pesquisa: `metodos`, `resultados`, `autores`. Para due diligence: `empresas`, `mercados`, `riscos`.
3. Os prompts em `prompts/` também podem ser editados — eles controlam a forma das páginas geradas.

## Roadmap próximas iterações

- [ ] FTS5 para busca textual mais rápida
- [ ] Detector de duplicatas semântico (não só hash)
- [ ] Wikilinks clicáveis na visualização
- [ ] Export da wiki como zip
- [ ] Modo "monitorar pasta" — ingestão automática quando arquivos aparecem em `data/raw/`
- [ ] Cache de queries
- [ ] Roteamento de modelo (light vs main) baseado em complexidade da tarefa
- [ ] Avaliação automática de qualidade de páginas geradas
- [ ] Multi-user com auth
