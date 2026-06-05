---
feature: sistema-monitoramento-editais
status: planning
created: 2026-05-06
updated: 2026-05-08
---

# Spec: Sistema de Monitoramento e Análise de Editais de Fomento

## Objetivo

Sistema online (VPS + Docker) que monitora automaticamente portais de editais de fomento no Brasil e no exterior, extrai e processa os documentos com agentes de IA, e entrega ao usuário um resumo estruturado dos requisitos de cada edital — filtrável por tema, valor, data e perfil do proponente.

---

## Problema a resolver

O usuário que busca fomento precisa:
1. Monitorar dezenas de portais manualmente (22+ mapeados)
2. Ler editais extensos em PDF para extrair requisitos
3. Avaliar se seu projeto se enquadra nos critérios

O sistema automatiza os três passos.

---

## Arquitetura Geral

```
┌─────────────────────────────────────────────────────────┐
│                        VPS (Docker)                      │
│                                                          │
│  ┌──────────┐    ┌──────────┐    ┌────────────────────┐ │
│  │ Scheduler│───▶│  Worker  │───▶│  Scraper Engine    │ │
│  │ (Celery  │    │ (Celery) │    │  Playwright +      │ │
│  │  Beat)   │    │          │    │  Camoufox          │ │
│  └──────────┘    └──────────┘    └────────┬───────────┘ │
│                                           │              │
│                                    ┌──────▼──────┐       │
│                                    │  Extractor  │       │
│                                    │  PDF/HTML   │       │
│                                    └──────┬──────┘       │
│                                           │              │
│                                    ┌──────▼──────┐       │
│                                    │  AI Agents  │       │
│                                    │  (análise)  │       │
│                                    └──────┬──────┘       │
│                                           │              │
│  ┌──────────┐    ┌──────────┐    ┌────────▼───────────┐ │
│  │  FastAPI │◀───│PostgreSQL│◀───│   Structured Data  │ │
│  │   (API)  │    │          │    │   (requisitos)     │ │
│  └──────────┘    └──────────┘    └────────────────────┘ │
│       ▲                                                  │
│  ┌────┴─────┐    ┌──────────┐                           │
│  │  Redis   │    │  Nginx   │                           │
│  │  (queue) │    │ (proxy)  │                           │
│  └──────────┘    └──────────┘                           │
└─────────────────────────────────────────────────────────┘
```

---

## Stack Definida

| Camada | Tecnologia | Justificativa |
|---|---|---|
| Linguagem | **Python 3.12** | Melhor ecossistema para scraping + IA |
| Automação web | **Playwright + Camoufox** | Fingerprint humano real, bypassa Cloudflare/anti-bot |
| Scraping simples | **httpx + BeautifulSoup4** | Sites sem proteção (mais rápido, sem overhead de browser) |
| Extração de PDF | **pdfplumber + pymupdf** | pdfplumber para texto estruturado, pymupdf para PDFs complexos |
| Fila de tarefas | **Celery + Redis** | Scraping assíncrono com retry e rate limiting por domínio |
| Agentes de IA | **DeepSeek V4 Flash** | $0.14/$0.28 — 1M ctx, MoE 284B/13B ativos, excelente em PT-BR |
| LLM reserva | **DeepSeek V4 Pro** | $0.435/$0.87 (75% off até 31/05/26) — 1M ctx, fallback premium |
| API | **FastAPI** | Async nativo, validação com Pydantic, OpenAPI automático |
| Banco de dados | **PostgreSQL 16** | Dados estruturados de editais, histórico, usuários |
| ORM | **SQLAlchemy 2 + Alembic** | Migrations versionadas |
| Containerização | **Docker + Docker Compose** | Deploy reproduzível em qualquer VPS |
| Proxy reverso | **Nginx** | SSL termination, rate limiting de API |
| Scheduler | **Celery Beat** | Agendamento de crawls por portal (frequência configurável) |

---

## Módulos do Sistema

### 1. Scraper Engine

Dois modos de operação por portal:

**Modo A — HTTP simples** (portais sem proteção)
```
httpx → BeautifulSoup4 → extrai links de editais
```

**Modo B — Browser headless** (portais com Cloudflare, JS obrigatório, login)
```
Camoufox (Firefox headless com fingerprint humano)
  → delays aleatórios entre ações
  → scroll simulado
  → user-agent rotativo
  → extrai links de editais
```

Cada portal tem um **conector** (`connectors/prosas.py`, `connectors/finep.py`, etc.) que define:
- URL base
- Modo (A ou B)
- Seletor CSS/XPath dos editais
- Frequência de crawl
- Campos a extrair (título, data, valor, link do PDF)

### 2. Extractor

Recebe URL ou arquivo PDF e retorna texto limpo:
- PDF: pdfplumber → texto por página → concatena
- HTML: BeautifulSoup → remove nav/footer/ads → texto principal
- Fallback: pymupdf para PDFs com layout complexo (tabelas, colunas)

### 3. AI Agents

Dois agentes em sequência:

**Agente 1 — Extrator de Requisitos** (DeepSeek V4 Flash — $0.14/$0.28, 1M context)
Recebe texto do edital e retorna JSON estruturado com os 7 filtros de captação
(ver `.claude/specs/filtros-captacao.md` para taxonomia completa):
```json
{
  "titulo": "...",
  "financiador": "...",
  "url_original": "...",
  "valor_min": 0,
  "valor_max": 0,
  "moeda": "BRL",
  "data_abertura": "YYYY-MM-DD",
  "data_encerramento": "YYYY-MM-DD",
  "eixos_tematicos": ["inovacao", "tecnologia_industrial"],
  "perfil_elegivel": ["startup_early_stage", "mpe"],
  "mecanismo_financiamento": "subvencao_economica",
  "abrangencia_geografica": {"tipo": "nacional"},
  "status": "inscricoes_abertas",
  "nivel_trl_min": 4,
  "nivel_trl_max": 7,
  "temas": ["inovação", "tecnologia"],
  "requisitos_obrigatorios": ["..."],
  "documentos_necessarios": ["..."],
  "contrapartida_exigida": true,
  "resumo": "...",
  "score_complexidade": 3
}
```

**Agente 2 — Analista de Adequação** (DeepSeek V4 Flash — sob demanda, 1M context)
Recebe perfil do usuário + JSON do edital e retorna:
- % de adequação
- gaps a resolver
- próximos passos recomendados

### 4. API (FastAPI)

Endpoints principais:
```
GET  /editais              → lista com 7 filtros de captação (ver spec filtros-captacao.md)
GET  /editais/{id}         → detalhe completo + requisitos extraídos
POST /editais/{id}/analisar → análise de adequação (requer perfil do usuário)
GET  /portais              → lista de portais monitorados + status
POST /portais/{id}/crawl   → dispara crawl manual
GET  /jobs/{id}            → status de processamento
```

### 4.1 Filtros de Captação (ver `.claude/specs/filtros-captacao.md`)

O sistema suporta 7 filtros essenciais no endpoint `GET /editais`:

1. **Área de Atuação / Eixo Temático** — inovação, impacto social, cultura, saúde, etc.
2. **Perfil do Proponente** — OSC, startup, MPE, ICT, pesquisador, pessoa física
3. **Mecanismo de Financiamento** — subvenção, crédito, matchfunding, renúncia fiscal
4. **Abrangência Geográfica** — nacional, regional, estadual, municipal
5. **Status do Edital** — inscrições abertas, em breve, encerrado, fluxo contínuo
6. **Faixa de Valor** — micro a mega (R$ 50 mil a R$ 5 milhões+)
7. **Nível de Maturidade Tecnológica (TRL)** — 1 a 9 (FINEP, SEBRAE, MCTI)

### 5. Scheduler

Celery Beat com frequências por portal:
- Portais de alta rotatividade (Prosas, SEBRAE): a cada 6h
- Portais governamentais (FINEP, CNPq): a cada 24h
- FAPs estaduais: a cada 48h
- Portais internacionais: a cada 72h

---

## Estratégia Anti-Bot por Portal

| Portal | Proteção Conhecida | Estratégia |
|---|---|---|
| Prosas | Baixa | httpx simples |
| FINEP | Média (Cloudflare) | Camoufox + delays |
| SEBRAE | Média | Camoufox |
| CNPq (Plataforma Carlos Chagas) | Alta (login obrigatório) | Camoufox + credenciais configuráveis |
| Portais gov.br | Baixa-Média | httpx + fallback Camoufox |
| Horizon Europe (FTOP) | Alta (EU Login) | Camoufox + credenciais |
| FAPs estaduais | Variável | Detecção automática → modo A ou B |

**Técnicas de evasão implementadas:**
- Delays aleatórios entre requisições (2–8s, distribuição gaussiana)
- Rotação de User-Agent (lista de browsers reais)
- Camoufox: fingerprint de canvas, WebGL, fonts idêntico a Firefox real
- Respeito a `robots.txt` (configurável por portal)
- Rate limiting por domínio (máx. 1 req/3s por padrão)

---

## Estrutura de Diretórios

```
editais_br/
├── docker-compose.yml
├── .env.example
├── api/
│   ├── Dockerfile
│   ├── main.py
│   ├── routers/
│   ├── models/          # SQLAlchemy models
│   ├── schemas/         # Pydantic schemas
│   └── services/
├── worker/
│   ├── Dockerfile
│   ├── celery_app.py
│   ├── tasks/
│   │   ├── crawl.py
│   │   ├── extract.py
│   │   └── analyze.py
│   └── connectors/      # um arquivo por portal
│       ├── base.py
│       ├── prosas.py
│       ├── finep.py
│       └── ...
├── agents/
│   ├── extractor.py     # Agente 1
│   └── analyzer.py      # Agente 2
└── nginx/
    └── nginx.conf
```

---

## Docker Compose — Serviços

```yaml
services:
  api:        FastAPI (porta 8000)
  worker:     Celery worker (scraping + extração + IA)
  beat:       Celery Beat (scheduler)
  postgres:   PostgreSQL 16
  redis:      Redis 7
  nginx:      Nginx (porta 80/443)
```

---

## Modelo de Dados (PostgreSQL)

**portais** — cadastro dos portais monitorados
**editais** — edital bruto (título, URL, PDF, texto extraído)
**requisitos** — JSON estruturado extraído pelo Agente 1 (modelo completo com 7 filtros de captação)
**crawl_jobs** — histórico de execuções por portal
**usuarios** — perfil do usuário para análise de adequação

---

## Fases de Implementação

### Fase 1 — MVP (prioridade)
- [ ] Docker Compose com todos os serviços
- [ ] 5 conectores iniciais: Prosas, FINEP, SEBRAE, CNPq, FAPEG
- [ ] Extractor (PDF + HTML)
- [ ] Agente 1 (extração de requisitos)
- [ ] API com endpoints de listagem e detalhe
- [ ] Scheduler básico

### Fase 2 — Expansão
- [ ] Restante dos 22+ conectores
- [ ] Agente 2 (análise de adequação)
- [ ] **Interface web: HTMX + Jinja2 + Bootstrap 5** (issue #16)
  - Servida pelo próprio FastAPI — sem segundo runtime
  - Filtros dinâmicos sem JavaScript manual (HTMX)
  - Migração futura para Node.js/Next.js é trivial — API REST já exposta
- [ ] Notificações (email/WhatsApp) para novos editais por tema

### Fase 3 — Robustez
- [ ] Monitoramento (Prometheus + Grafana)
- [ ] Fallback para DeepSeek V4 Pro quando V4 Flash indisponível
- [ ] Cache de resultados de IA (evitar reprocessar editais inalterados)
- [ ] Painel admin para gerenciar portais e jobs

---

## Decisões Técnicas Registradas

**Por que Python e não Node.js?**
Playwright existe em ambos, mas o ecossistema de IA (LangChain, pdfplumber, pymupdf) é muito mais maduro em Python. Não faz sentido dividir a stack.

**Por que Camoufox e não Selenium/Puppeteer?**
Camoufox é um fork do Firefox com patches específicos para evasão de fingerprinting. Detectado como humano em testes contra Cloudflare Bot Management e DataDome. Selenium e Puppeteer são trivialmente detectados por headless detection moderno.

**Por que Celery + Redis e não um cron simples?**
Scraping de 22+ portais com frequências diferentes, retries em falha, rate limiting por domínio e processamento de IA assíncrono exigem uma fila real. Cron não gerencia estado nem retry.

**Por que apenas DeepSeek V4 Flash?**
$0.14/1M input e $0.28/1M output com 1M tokens de contexto. Performance excelente em português brasileiro, MoE 284B parâmetros (13B ativos por token). Um único modelo cobre todos os casos de uso — extração em volume e análise de adequação — sem necessidade de roteamento por tamanho de contexto. Stack simplificada: API direta da DeepSeek (OpenAI-compatible, `base_url=https://api.deepseek.com`), dois modelos (Flash + Pro como reserva).

**Por que não GPT-5 nano, Gemini ou Ollama?**
Simplificação operacional: uma API key (`DEEPSEEK_API_KEY`), sem roteamento entre providers. DeepSeek V4 Flash tem 1M context — cobre editais de qualquer tamanho. Custo total estimado por edital (~200k tokens) ≈ $0.08 — competitivo sem a complexidade de múltiplos providers.

---

## Como retomar

1. Ler este arquivo e `MEMORY.md`
2. Verificar `specs/INDEX.md` para status atual das fases
3. Próximo passo: implementar Fase 1 — começar pelo `docker-compose.yml` e conector base
