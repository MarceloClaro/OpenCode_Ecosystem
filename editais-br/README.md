# editais-br

Sistema de monitoramento e análise automática de editais de fomento no Brasil e no exterior.

Monitora 22+ portais, extrai requisitos de editais (PDF/HTML) com agentes de IA e entrega ao usuário um resumo estruturado com 7 filtros de captação: área temática, perfil do proponente, mecanismo de financiamento, abrangência geográfica, status, faixa de valor e nível de maturidade tecnológica (TRL).

**Repositório:** https://github.com/ecodelearn/editais-br  
**Board:** https://github.com/users/ecodelearn/projects/8  
**Status:** 🟢 Fase 1 concluída — Fase 2 em planejamento

---

## O problema

Quem busca fomento precisa monitorar dezenas de portais manualmente, ler editais extensos em PDF e avaliar se seu projeto se enquadra nos critérios. Este sistema automatiza os três passos.

---

## Stack

| Camada | Tecnologia |
|---|---|
| Linguagem | Python 3.12 |
| Automação web (anti-bot) | Playwright + Camoufox |
| Scraping simples | httpx + BeautifulSoup4 |
| Extração de PDF | pdfplumber + pymupdf |
| Fila de tarefas | Celery + Redis |
| Agente 1 — extração de requisitos | DeepSeek V4 Flash (`deepseek-v4-flash`) — 1M ctx, $0.14/$0.28 |
| Agente 2 — análise de adequação | DeepSeek V4 Flash (`deepseek-v4-flash`) — 1M ctx |
| Reserva | DeepSeek V4 Pro (`deepseek-v4-pro`) — $0.435/$0.87 (75% off até 31/05/26) |
| API | FastAPI + Pydantic |
| Banco de dados | PostgreSQL 16 + SQLAlchemy 2 + Alembic |
| Infra | Docker Compose + Nginx |

---

## Arquitetura

```
Scheduler (Celery Beat)
  └─▶ crawl_portal(portal_id)       # conector por portal
        └─▶ extract_edital(id)       # PDF ou HTML → texto limpo
              └─▶ analyze_edital(id) # Agente 1 → JSON estruturado

API (FastAPI)
  GET  /editais              # lista com 7 filtros de captação
  GET  /editais/{id}         # detalhe + requisitos
  POST /editais/{id}/analisar # Agente 2 — adequação ao perfil do usuário
  POST /portais/{id}/crawl   # crawl manual
  GET  /jobs/{id}            # status do job
```

Cada portal tem um **conector isolado** em `worker/connectors/`. Dois modos:
- **HTTP** (`httpx`) — portais sem proteção
- **Browser** (`Camoufox`) — portais com Cloudflare/anti-bot, simula comportamento humano

---

## Portais monitorados

22+ portais em 5 categorias — ver [`mapeamento_editais_brasil_2026.md`](mapeamento_editais_brasil_2026.md) para detalhes completos.

**Fase 1 (MVP):** Prosas, FINEP, SEBRAE, CNPq, FAPEG  
**Fase 2:** restante dos 22+ portais

---

## Desenvolvimento

### Pré-requisitos

```bash
docker compose up        # sobe todos os serviços
```

### Rodar testes

```bash
pytest                          # testes unitários
pytest -m integration           # testes de integração (requer internet)
```

### Workflow de contribuição

> 📘 **Guia completo:** [`CONTRIBUTING.md`](CONTRIBUTING.md) — setup, TDD, padrões de código, checklist de PR.

1. Pegue uma issue do [board](https://github.com/users/ecodelearn/projects/8)
2. Crie branch: `git checkout -b feat/issue-N-descricao`
3. **TDD obrigatório:** escreva o teste (red) → implemente (green) → refatore
4. Abra PR referenciando a issue: `Closes #N`
5. PR só sobe com todos os testes passando

### Regras de desenvolvimento

- **TDD red/green** antes de qualquer feature ou correção
- **Desacoplamento total:** cada módulo (`connector`, `extractor`, `agent`) é independente e portável
- **Orientação a objetos:** herança via `BaseConnector`, `BaseExtractor`, `BaseAgent`
- **Sem over-engineering:** a solução mais simples que passa nos testes
- **Sprints lineares:** uma issue por vez, do backlog ao done

---

## Estrutura do projeto

```
editais_br/
├── README.md
├── CONTRIBUTING.md              # guia prático para contribuidores
├── AGENTS.md                    # handoff universal para qualquer LLM/CLI
├── CLAUDE.md                    # instruções específicas para Claude Code
├── docker-compose.yml
├── pyproject.toml
├── .env.example
├── mapeamento_editais_brasil_2026.md   # fonte de dados dos portais
├── api/
│   ├── main.py
│   ├── routers/
│   ├── models/                  # SQLAlchemy models
│   └── schemas/                 # Pydantic schemas
├── worker/
│   ├── celery_app.py
│   ├── tasks/
│   │   ├── crawl.py
│   │   ├── extract.py
│   │   └── analyze.py
│   └── connectors/              # um arquivo por portal
│       ├── base.py              # BaseConnector (ABC)
│       ├── prosas.py
│       ├── finep.py
│       └── ...
├── agents/
│   ├── base.py                  # BaseAgent (ABC)
│   ├── extractor.py             # Agente 1 — extração de requisitos
│   └── analyzer.py              # Agente 2 — análise de adequação
├── extractors/
│   ├── base.py                  # BaseExtractor (ABC)
│   ├── pdf.py                   # PDFExtractor
│   └── html.py                  # HTMLExtractor
├── tests/
│   ├── unit/
│   ├── integration/
│   └── fixtures/
└── .claude/                     # memória e specs para Claude Code
    ├── memory/MEMORY.md
    ├── specs/INDEX.md
    └── specs/filtros-captacao.md   # taxonomia dos 7 filtros de captação
```

---

## Fases

| Fase | Escopo | Status |
|---|---|---|
| **Fase 1 — MVP** | Docker + 5 conectores + Extractor + Agente 1 + API básica + Interface HTMX | 🟢 Concluída |
| **Fase 2 — Expansão** | Crawler inteligente + Playwright + Agente 2 + Pipeline automático | 🟡 10 issues abertas |
| **Fase 3 — Robustez** | Monitoramento + Cache IA + Painel admin | ⬜ Planejado |

Issues detalhadas: https://github.com/ecodelearn/editais-br/issues

### Backlog Fase 2 — próximas implementações

| # | Módulo | Título | Prioridade |
|---|---|---|---|
| #49 | scraper | Crawler inteligente: busca web + discovery automático de editais | 🔴 critical |
| #50 | scraper | Playwright + Camoufox: base anti-bot | 🔴 critical |
| #51 | scheduler | Pipeline automático: Celery Beat agendamento diário | 🔴 critical |
| #52 | scraper | Calibrar conectores contra sites reais | 🟠 high |
| #53 | agents | Agente 2: análise de adequação ao perfil do usuário | 🟠 high |
| #54 | frontend | Dashboard: paginação real com HTMX | 🟠 high |
| #55 | frontend | Dashboard: polling de status de jobs (HTMX 3s) | 🟠 high |
| #56 | infra | Deploy VPS: ativar CI/CD + secrets | 🟠 high |
| #57 | infra | Monitoramento: logs estruturados + alertas | 🟡 medium |
| #58 | docs | README: atualizar status e roadmap | 🟡 medium |
| #59 | api | API: endpoint de busca full-text nos editais | 🟡 medium |

---

## Variáveis de ambiente

Copie `.env.example` para `.env` e preencha:

```bash
# APIs de IA
DEEPSEEK_API_KEY=          # deepseek-v4-flash e deepseek-v4-pro

# Banco
POSTGRES_URL=postgresql://user:pass@postgres:5432/editais

# Redis
REDIS_URL=redis://redis:6379/0

# Opcional — credenciais de portais que exigem login
CNPQ_EMAIL=
CNPQ_PASSWORD=
```
