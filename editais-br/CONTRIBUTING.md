# Contribuindo com o editais-br

> Guia rápido para novos contribuidores. Leia antes de começar a codar.

---

## 🚀 Setup inicial (5 minutos)

```bash
# 1. Clone o repo
git clone git@github.com:ecodelearn/editais-br.git
cd editais-br

# 2. Python 3.12 + venv
python3.12 -m venv .venv
source .venv/bin/activate

# 3. Instale as dependências
pip install -e ".[dev]"

# 4. Copie as variáveis de ambiente
cp .env.example .env
# Preencha DEEPSEEK_API_KEY (obrigatório) e demais opcionais

# 5. Suba os serviços de infra (PostgreSQL, Redis)
docker compose up -d postgres redis

# 6. Rode as migrations
alembic upgrade head

# 7. Rode os testes pra validar
pytest
```

**Pronto.** Se `pytest` passar sem erros, seu ambiente está OK.

---

## 🔄 Fluxo de trabalho (sempre linear)

```
Backlog → Pegar Issue → Branch → TDD (RED) → Implementar (GREEN) → PR → Done
```

Nunca pule etapas. Uma issue por vez.

### 1. Pegue uma issue

```bash
# Veja as issues abertas
gh issue list --repo ecodelearn/editais-br --state open

# Pegue a de menor número (prioridade)
```

Se for sua primeira contribuição, peça no grupo do WhatsApp para te atribuírem a issue.

### 2. Crie a branch

```bash
git checkout main
git pull origin main
git checkout -b feat/issue-N-descricao-curta
# ou fix/issue-N-descricao-curta (se for correção)
```

### 3. Escreva o teste (RED) 🔴

SEMPRE comece pelo teste. Nunca escreva implementação antes do teste.

```bash
# Crie o arquivo de teste
# tests/unit/test_modulo.py
```

O teste deve falhar (RED) porque o código ainda não existe.

```bash
pytest tests/unit/test_modulo.py -v
# ❌ FAILED — é isso mesmo
```

### 4. Implemente (GREEN) 🟢

Escreva o código MÍNIMO para o teste passar. Sem over-engineering.

```bash
pytest tests/unit/test_modulo.py -v
# ✅ PASSED — agora sim
```

### 5. Rode TODOS os testes

```bash
pytest                    # todos os testes
pytest tests/unit/        # só unitários
pytest -m "integration"   # só integração (precisa da infra up)
```

**Todos devem estar verdes antes de commitar.**

### 6. Commit e PR

```bash
git add .
git commit -m "feat: descrição clara do que foi feito (Closes #N)"
git push origin feat/issue-N-descricao-curta

# Abra o PR
gh pr create --title "feat: descrição" --body "Closes #N"
```

O PR fecha a issue automaticamente se você colocar `Closes #N` no body ou na mensagem de commit.

---

## 🧪 TDD na prática

Modelo mental: **Arrange → Act → Assert**

```python
# tests/unit/test_httpextractor.py
import pytest
from extractors.html import HTMLExtractor

def test_extrai_texto_de_html_simples():
    # Arrange
    html = "<html><body><p>Edital de fomento 2026</p></body></html>"
    extractor = HTMLExtractor()

    # Act
    resultado = extractor.extract(html)

    # Assert
    assert "Edital de fomento 2026" in resultado
```

Executa → falha → implementa → passa → próximo teste.

---

## 📁 Onde colocar cada coisa

| Módulo | Onde criar |
|---|---|
| Conector de portal | `worker/connectors/nome_do_portal.py` |
| Extrator (PDF/HTML) | `extractors/pdf.py` ou `extractors/html.py` |
| Agente de IA | `agents/nome_do_agente.py` |
| Modelo SQLAlchemy | `api/models/nome.py` |
| Schema Pydantic | `api/schemas/nome.py` |
| Task Celery | `worker/tasks/nome.py` |
| Rota da API | `api/routes/nome.py` |
| Teste unitário | `tests/unit/test_nome_do_modulo.py` |
| Teste de integração | `tests/integration/test_nome.py` |
| Fixture (mock) | `tests/fixtures/nome.html` ou `.pdf` |

---

## 🏗️ Padrões de código

### Herança de classes base (OBRIGATÓRIO)

```python
from connectors.base import BaseConnector, EditalRaw

class ProsasConnector(BaseConnector):
    mode = "http"
    base_url = "https://prosas.com.br/editais"
    crawl_interval_hours = 6

    def fetch_editais(self) -> list[EditalRaw]:
        # Sua implementação aqui
        ...

    def parse(self, content: str) -> list[EditalRaw]:
        # Sua implementação aqui
        ...
```

### Tipagem SEMPRE

```python
# ✅ Correto
def fetch_editais(self) -> list[EditalRaw]:
    ...

# ❌ Errado
def fetch_editais(self):
    ...
```

### Dataclasses e Pydantic

```python
# Dados brutos → dataclass (leve, sem validação)
from dataclasses import dataclass

@dataclass
class EditalRaw:
    titulo: str
    url: str
    ...

# Dados processados → Pydantic (validação, serialização)
from pydantic import BaseModel

class EditalRequisitos(BaseModel):
    titulo: str
    valor_min: float | None
    ...
```

### Nomes de arquivo

- Nome do conector = nome do portal (ex: `finep.py`, `prosas.py`, `sebrae.py`)
- Teste = `test_` + nome do módulo (ex: `test_finep.py`, `test_httpextractor.py`)

---

## 🔌 Interfaces que você PRECISA conhecer

### BaseConnector — para criar conectores de portal

```python
class BaseConnector(ABC):
    mode: Literal['http', 'browser']  # http = httpx, browser = Playwright/Camoufox
    base_url: str
    crawl_interval_hours: int

    @abstractmethod
    def fetch_editais(self) -> list[EditalRaw]: ...
    @abstractmethod
    def parse(self, content: str) -> list[EditalRaw]: ...
```

### BaseExtractor — para extrair texto de documentos

```python
class BaseExtractor(ABC):
    @abstractmethod
    def extract(self, raw: bytes | str) -> str: ...
```

### BaseAgent — para agentes de IA

```python
class BaseAgent(ABC):
    model: str
    api_key: str

    @abstractmethod
    def execute(self, input_data: str) -> dict: ...
```

---

## ⚠️ Regras INEGOCIÁVEIS

1. **TDD sempre** — teste antes do código, SEMPRE
2. **Uma issue por vez** — fluxo linear, sem paralelismo por pessoa
3. **Herança das classes base** — BaseConnector, BaseExtractor, BaseAgent
4. **Solução mais simples** — sem over-engineering, código mínimo que passa no teste
5. **Branch por issue** — `feat/issue-N-descricao` ou `fix/issue-N-descricao`
6. **PR fecha issue** — `Closes #N` no body do PR ou mensagem de commit
7. **Nunca commitar `.env`** — use `.env.example` como referência
8. **Tipagem em todas as funções** — `mypy` deve passar limpo

---

## ✅ Checklist antes de abrir o PR

Antes de commitar, confirme:

- [ ] Testes escritos PRIMEIRO (TDD)
- [ ] `pytest` passa com 100% verde
- [ ] `mypy` sem erros de tipo
- [ ] Branch nomeada `feat/issue-N-...` ou `fix/issue-N-...`
- [ ] Commit com mensagem clara + `Closes #N`
- [ ] Herdou da classe base correta
- [ ] Sem `.env` no commit
- [ ] Código mínimo, sem firulas

---

## 🐳 Comandos úteis do dia a dia

```bash
# Subir tudo
docker compose up -d

# Só a infra (PostgreSQL + Redis)
docker compose up -d postgres redis

# Rodar testes
pytest -v                          # verboso
pytest -x                          # para no primeiro erro
pytest tests/unit/test_xpto.py     # arquivo específico
pytest -k "test_nome_do_teste"     # teste específico
pytest -m "not integration"        # pula integração

# Ver logs
docker compose logs -f postgres
docker compose logs -f redis

# Type checking
mypy .

# Formatação (se configurado)
ruff check .
ruff format .

# Resetar o banco de dados
docker compose down -v postgres
docker compose up -d postgres
alembic upgrade head
```

---

## 🆘 Dúvidas?

- **WhatsApp do projeto** — peça o link de convite
- **Issues no GitHub** — comente na issue que está trabalhando
- **PRs** — marque @ecodelearn para review

---

*Última atualização: Maio 2026 — editais-br Fase 1*
