---
project: editais-br
repo: local/editais_br
stack: Python 3.12 + FastAPI + Playwright/Camoufox + Celery + PostgreSQL + Redis + Docker
language: pt-br
---

# Mapeamento Estratégico de Editais Brasil — Memória do Projeto

> Lido automaticamente a cada sessão. Mantenha conciso e atualizado.
> Última atualização: 2026-05-06

## Contexto

Sistema online de monitoramento e análise de editais de fomento no Brasil e exterior.
Monitora 22+ portais automaticamente, extrai requisitos de editais (PDF/HTML) com agentes de IA e entrega resumo estruturado ao usuário — filtrável por tema, valor, data e perfil do proponente.
Deploy em VPS com Docker. Público-alvo: desenvolvedores, startups, OSCs e pesquisadores que buscam financiamento.

## Stack

- **Linguagem:** Python 3.12
- **Automação web:** Playwright + Camoufox (anti-bot/fingerprint humano)
- **Scraping simples:** httpx + BeautifulSoup4
- **Extração PDF:** pdfplumber + pymupdf
- **Fila:** Celery + Redis
- **Agentes IA:** DeepSeek V4 Flash via DeepSeek API ($0.14/$0.28, 1M ctx) para Agente 1 e 2 | DeepSeek V4 Pro (reserva, $0.435/$0.87, 75% off até 31/05/26)
- **API:** FastAPI + Pydantic
- **Banco:** PostgreSQL 16 + SQLAlchemy 2 + Alembic
- **Infra:** Docker Compose + Nginx

## Regras não-negociáveis

- Respeitar rate limiting por domínio (máx. 1 req/3s por portal)
- Verificar URLs e janelas de submissão antes de qualquer recomendação
- Não commitar credenciais — usar .env (nunca versionado)
- Cada portal tem seu próprio conector em `worker/connectors/`

## Estado atual

2026-05-08 — Taxonomia de filtros de captação definida (7 filtros essenciais). Modelo EditalRequisitos
atualizado no AGENTS.md. Spec dedicada em `.claude/specs/filtros-captacao.md`.
**Próxima sessão:** responder questões abertas em decisions.md → confirmar specs → iniciar implementação pela issue #1.

## Integrações ativas

- DeepSeek API — V4 Flash (`deepseek-v4-flash`), Agente 1 e 2
- DeepSeek API — V4 Pro (`deepseek-v4-pro`), reserva
- Base URL: `https://api.deepseek.com` (OpenAI-compatible)
