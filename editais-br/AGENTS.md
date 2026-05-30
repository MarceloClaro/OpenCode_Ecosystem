# AGENTS.md — Handoff Universal

> Este arquivo é lido automaticamente por Claude Code, Kiro CLI, OpenAI Codex, Gemini CLI e outros agentes de IA.
> Contém tudo que um agente precisa para continuar o trabalho sem briefing humano.

---

## Projeto

**editais-br** — Sistema de monitoramento e análise automática de editais de fomento no Brasil e exterior.

- **Repo:** https://github.com/ecodelearn/editais-br
- **Board:** https://github.com/users/ecodelearn/projects/8
- **Idioma:** Português brasileiro (código em inglês, comentários e docs em PT-BR)
- **Status:** Fase 1 em backlog — nenhum código de produção implementado ainda

---

## Contexto do sistema

O sistema monitora 22+ portais de editais de fomento, extrai o texto dos editais (PDF/HTML), processa com agentes de IA e entrega ao usuário um JSON estruturado com os requisitos de cada edital — filtrável por tema, valor, data e perfil do proponente.

Fonte de dados dos portais: [`mapeamento_editais_brasil_2026.md`](mapeamento_editais_brasil_2026.md)

---

## Stack

```
Python 3.12
FastAPI + Pydantic + SQLAlchemy 2 + Alembic
Celery + Redis
Playwright + Camoufox (anti-bot)
httpx + BeautifulSoup4
pdfplumber + pymupdf
Docker Compose + Nginx + PostgreSQL 16
```

**Modelos de IA:**
- `deepseek-v4-flash` (DeepSeek API) — Agente 1 e 2, 1M context, $0.14/$0.28
- `deepseek-v4-pro` (DeepSeek API) — reserva, $0.435/$0.87 (75% off até 31/05/2026)

---

## Regras inegociáveis

1. **TDD obrigatório:** escreva o teste (red) → implemente (green) → refatore. Nunca o contrário.
2. **Uma issue por vez:** fluxo linear, do backlog ao done.
3. **Desacoplamento total:** cada módulo (`connector`, `extractor`, `agent`) deve ser independente e portável.
4. **OOP:** use herança via classes base abstratas (`BaseConnector`, `BaseExtractor`, `BaseAgent`).
5. **Sem over-engineering:** a solução mais simples que passa nos testes.
6. **Branch por issue:** `feat/issue-N-descricao` ou `fix/issue-N-descricao`.
7. **PR fecha issue:** mensagem de commit ou PR body com `Closes #N`.
8. **Nunca commitar `.env`** — usar `.env.example` como referência.

---

## Modo autônomo (YOLO)

Quando receber uma tarefa, execute até o fim sem pedir confirmação:

1. **Não peça permissão** — execute as ferramentas direto (`bash`, `write`, `edit`)
2. **Escreva todos os arquivos** necessários de uma vez
3. **Rode os testes** automaticamente após implementar
4. **Se falhar, corrija e rode de novo** — loop automático até passar
5. **Só pare se:**
   - A tarefa estiver concluída (testes verdes, código funcionando)
   - Travar em algo que depende de decisão humana (ex: escolha entre duas abordagens conflitantes)
   - Precisar de credencial ou acesso que você não tem
6. **Ao final, confirme** o que foi feito com um resumo curto
7. **Commite e faça PR** automaticamente quando a issue estiver pronta

---

## Como retomar o trabalho

### 1. Ver o que está em andamento

```bash
# Issues abertas no board
gh issue list --repo ecodelearn/editais-br --state open

# Estado das specs
cat .claude/specs/INDEX.md
```

### 2. Pegar a próxima issue

```bash
# Próxima issue prioritária (menor número aberto)
gh issue list --repo ecodelearn/editais-br --state open --limit 1
```

### 3. Fluxo de trabalho padrão

```bash
# 1. Criar branch
git checkout -b feat/issue-N-descricao

# 2. Escrever teste (RED)
# tests/unit/test_modulo.py

# 3. Implementar (GREEN)
# código mínimo para passar o teste

# 4. Rodar testes
pytest tests/unit/

# 5. Commit e PR
git commit -m "feat: descrição (Closes #N)"
gh pr create --title "feat: descrição" --body "Closes #N"
```

---

## Estrutura de diretórios

```
worker/connectors/base.py     ← BaseConnector (ABC) — SEMPRE herdar daqui
worker/connectors/prosas.py   ← exemplo de conector HTTP
worker/connectors/finep.py    ← exemplo de conector Browser (Camoufox)
agents/base.py                ← BaseAgent (ABC)
agents/extractor.py           ← Agente 1 (DeepSeek V4 Flash)
agents/analyzer.py            ← Agente 2 (DeepSeek V4 Flash)
extractors/base.py            ← BaseExtractor (ABC)
extractors/pdf.py             ← PDFExtractor (pdfplumber → pymupdf fallback)
extractors/html.py            ← HTMLExtractor (BeautifulSoup4)
api/main.py                   ← FastAPI app
api/models/                   ← SQLAlchemy models
api/schemas/                  ← Pydantic schemas
worker/tasks/crawl.py         ← Celery task: crawl_portal()
worker/tasks/extract.py       ← Celery task: extract_edital()
worker/tasks/analyze.py       ← Celery task: analyze_edital()
tests/unit/                   ← testes unitários (sem I/O real)
tests/integration/            ← testes de integração (@pytest.mark.integration)
tests/fixtures/               ← HTMLs e PDFs mockados para testes
```

---

## Interfaces principais

### BaseConnector

```python
from abc import ABC, abstractmethod
from typing import Literal
from dataclasses import dataclass

@dataclass
class EditalRaw:
    titulo: str
    url: str
    pdf_url: str | None
    data_publicacao: str | None

class BaseConnector(ABC):
    mode: Literal['http', 'browser']
    base_url: str
    crawl_interval_hours: int

    @abstractmethod
    def fetch_editais(self) -> list[EditalRaw]: ...

    @abstractmethod
    def parse(self, content: str) -> list[EditalRaw]: ...
```

### AbrangenciaGeografica (modelo auxiliar)

```python
from pydantic import BaseModel
from typing import Literal

class AbrangenciaGeografica(BaseModel):
    tipo: Literal['nacional', 'regional', 'estadual', 'municipal']
    regioes: list[str] = []     # ex: ['sudeste', 'nordeste']
    estados: list[str] = []     # ex: ['SP', 'RJ']
    municipios: list[str] = []  # ex: ['São Paulo', 'Campinas']
```

### EditalRequisitos (output do Agente 1)

```python
from pydantic import BaseModel
from datetime import date
from typing import Literal

class EditalRequisitos(BaseModel):
    titulo: str
    financiador: str
    url_original: str
    valor_min: float | None
    valor_max: float | None
    moeda: str = 'BRL'
    data_abertura: date | None
    data_encerramento: date | None
    # --- Filtro 1: Área / Eixo Temático ---
    eixos_tematicos: list[str]  # taxonomia: .claude/specs/filtros-captacao.md
    # --- Filtro 2: Perfil do Proponente ---
    perfil_elegivel: list[str]  # osc, startup_early_stage, mpe, ict, pesquisador_individual, etc.
    # --- Filtro 3: Mecanismo de Financiamento ---
    mecanismo_financiamento: str | None
    # --- Filtro 4: Abrangência Geográfica ---
    abrangencia_geografica: AbrangenciaGeografica | None
    # --- Filtro 5: Status ---
    status: Literal['inscricoes_abertas', 'em_breve', 'encerrado', 'fluxo_continuo', 'suspenso', 'cancelado']
    # --- Filtro 6: Faixa de Valor já coberta por valor_min/valor_max ---
    # --- Filtro 7: TRL ---
    nivel_trl_min: int | None  # 1-9
    nivel_trl_max: int | None  # 1-9
    # --- Campos originais mantidos ---
    temas: list[str]            # tags livres (mantido para compatibilidade)
    requisitos_obrigatorios: list[str]
    documentos_necessarios: list[str]
    contrapartida_exigida: bool
    resumo: str
    score_complexidade: int  # 1-5
```

---

## Variáveis de ambiente necessárias

```bash
DEEPSEEK_API_KEY=        # deepseek-v4-flash e deepseek-v4-pro
POSTGRES_URL=postgresql://user:pass@postgres:5432/editais
REDIS_URL=redis://redis:6379/0
CNPQ_EMAIL=              # opcional — portais com login
CNPQ_PASSWORD=           # opcional
```

---

## Issues do backlog (Fase 1)

| # | Módulo | Título | Prioridade |
|---|---|---|---|
| #1 | infra | Docker Compose com todos os serviços | 🔴 critical |
| #2 | infra | Estrutura base Python (pyproject.toml + pytest) | 🔴 critical |
| #3 | infra | Models e migrations PostgreSQL | 🟠 high |
| #4 | scraper | BaseConnector — classe abstrata | 🔴 critical |
| #5 | scraper | Conector: Prosas | 🟠 high |
| #6 | scraper | Conector: FINEP | 🟠 high |
| #7 | scraper | Conector: SEBRAE | 🟡 medium |
| #8 | scraper | Conector: CNPq | 🟡 medium |
| #9 | scraper | Conector: FAPEG | 🟡 medium |
| #10 | extractor | PDFExtractor | 🔴 critical |
| #11 | extractor | HTMLExtractor | 🟠 high |
| #12 | agents | ExtractorAgent (Agente 1) | 🔴 critical |
| #21 | models | Schema Pydantic EditalRequisitos (7 filtros) | 🟠 high |
| #13 | scheduler | Celery tasks pipeline | 🟠 high |
| #14 | api | GET /editais e GET /editais/{id} | 🟠 high |
| #22 | api | Query params de filtro no GET /editais (7 filtros + facetas) | 🟠 high |
| #15 | api | POST /portais/{id}/crawl e GET /jobs/{id} | 🟡 medium |
| #17 | infra | CI/CD — GitHub Actions + deploy VPS | 🔴 critical |
| #18 | api | Health check GET /health | 🟠 high |
| #19 | pipeline | Deduplicação de editais | 🔴 critical |
| #20 | pipeline | OrchestratorAgent — supervisor do pipeline | 🟠 high |

**Ordem recomendada:** #1 → #17 → #2 → #3 → #18 → #4 → #19 → #20 → #10 → #11 → #12 → #21 → #5 → #6 → #13 → #14 → #22 → #7 → #8 → #9 → #15

## Configuração da VPS (secrets GitHub Actions)

Adicionar em https://github.com/ecodelearn/editais-br/settings/secrets/actions:
- `VPS_HOST` — IP ou domínio da VPS
- `VPS_USER` — usuário SSH (ex: `ubuntu`)
- `VPS_SSH_KEY` — chave privada SSH (conteúdo do `~/.ssh/id_rsa`)

---

## Memória do projeto (Claude Code)

Arquivos de contexto persistente em `.claude/`:

| Arquivo | Conteúdo |
|---|---|
| `.claude/memory/MEMORY.md` | Stack, contexto, estado atual |
| `.claude/specs/INDEX.md` | Estado de todas as features |
| `.claude/specs/sistema-monitoramento-editais.md` | Spec completa do sistema |
| `.claude/specs/filtros-captacao.md` | Taxonomia dos 7 filtros de captação |
| `.claude/memory/decisions.md` | Decisões arquiteturais com o porquê |
| `.claude/memory/lessons.md` | O que funcionou e o que não funcionou |
| `.claude/references.md` | URLs oficiais dos 40+ portais mapeados |
