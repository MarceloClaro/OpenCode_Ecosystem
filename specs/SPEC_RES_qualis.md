# SPEC_RES_qualis — Qualis Target Navigator

## API Contract

### Module: `navigator.py`

```python
@dataclass
class Journal:
    titulo: str
    issn: str
    qualis: str
    area_avaliacao: str
    escopo_keywords: list[str]
    acesso_aberto: bool = False
    apc_brl: float = 0.0
    tempo_medio_resposta_meses: float = 6.0
    taxa_aceitacao_pct: float = 30.0
    cite_score: float = 0.0
    sjr: float = 0.0
    h_index: float = 0.0
    def qualis_numeric(self) -> float

@dataclass
class ManuscriptProfile:
    titulo: str
    abstract: str
    keywords: list[str]
    area_capes: str

@dataclass
class JournalScore:
    journal: Journal
    score_total: float
    score_qualis: float
    score_scope: float
    score_tempo: float
    score_aceitacao: float
    score_acesso: float
    score_apc: float
    justificativa: str = ""

def jaccard_similarity(tokens_a: list[str], tokens_b: list[str]) -> float

def score_journal(manuscript: ManuscriptProfile, journal: Journal) -> JournalScore

def rank_journals(manuscript: ManuscriptProfile, journals: list[Journal],
                  top_n: int = 5) -> list[JournalScore]

def inferir_area_capes(keywords: list[str]) -> str
```

---

## CT-001: Jaccard Similarity (Mathematical)
**Entrada**: `jaccard_similarity(["IA", "educacao"], ["educacao", "tecnologia"])` → `> 0.0`; tokens disjuntos → `== 0.0`
**Esperado**: Retorna no intervalo `[0.0, 1.0]`

## CT-002: Score Journal — Qualis Peso (Normalization)
**Entrada**: Journal A1 → `score_journal(manuscript, journal_A1)`
**Esperado**: `score_qualis == QUALIS_SCORE["A1"] == 1.0`, `0.0 <= score_total <= 1.0`, justificativa nao vazia

## CT-003: Rank Journals — Monotonicidade (Ordering)
**Entrada**: `rank_journals(manuscript, journals, top_n=3)`
**Esperado**: Lista decrescente por `score_total`, len == 3, primeiro item score >= ultimo

## CT-004: Inferir Area CAPES (Heuristic)
**Entrada**: `inferir_area_capes(["inteligencia artificial", "computacao", "dados"])` → area com overlap maximo; `inferir_area_capes([])` → `"INTERDISCIPLINAR"`
**Esperado**: Sempre retorna string nao vazia, fallback = "INTERDISCIPLINAR"
