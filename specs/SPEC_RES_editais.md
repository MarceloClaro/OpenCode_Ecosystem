# SPEC_RES_editais — Editais-BR v7.1

## API Contract

### Module: `edital_search.py`

```python
@dataclass
class Edital:
    titulo: str
    url: str
    portal: str = ""
    score: float = 50.0
    fonte: str = "web"
    dimensoes: dict = field(default_factory=dict)

def classificar(titulo: str, url: str) -> dict
    # Returns dict with keys: area, perfil, mecanismo, abrangencia,
    #   status, faixa_valor, trl, contrapartida, competitividade, prazo

def calcular_score(dims: dict, tipo: str = "", perfil: str = "",
                   query_match_ratio: float = 0.0) -> float
    # Returns score 0.0–100.0

def buscar_sync(query: str, tipo: str = "", perfil: str = "pesquisador",
                max_results: int = 10, usar_cache: bool = True) -> list[dict]

async def buscar(query: str, tipo: str = "", perfil: str = "pesquisador",
                 max_results: int = 10, usar_cache: bool = True) -> list[dict]

def _carregar_curados() -> list[dict]

def _buscar_curados(query: str, max_results: int = 10) -> list[dict]
```

---

## CT-001: Edital Dataclass (Structural)
**Entrada**: `Edital(titulo="...", url="https://...", portal="fapesp")`
**Esperado**: `.score == 50.0`, `.fonte == "web"`, atributos acessíveis

## CT-002: Classificar Dimensoes (Functional)
**Entrada**: `classificar("Edital FAPESP Bolsa Mestrado IA em Saude", "https://fapesp.br/...")`
**Esperado**: Dict com 10 chaves (`area`, `perfil`, `mecanismo`, `abrangencia`, `status`, `faixa_valor`, `trl`, `contrapartida`, `competitividade`, `prazo`)

## CT-003: Calcular Score Range (Boundary)
**Entrada**: `calcular_score(dims, tipo="pesquisa", perfil="pesquisador")`
**Esperado**: `0.0 <= score <= 100.0`, tipo `float`

## CT-004: Curadoria Fallback (Resilience)
**Entrada**: `_buscar_curados("IA saude", max_results=5)`
**Esperado**: Lista com itens contendo `titulo`, `url`, `fonte = "curadoria"`. Fallback mesmo se DDG bloqueado.
