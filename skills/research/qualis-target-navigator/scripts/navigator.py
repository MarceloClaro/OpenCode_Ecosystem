"""
Qualis Target Navigator — Motor de Ranqueamento de Periodicos

Calcula compatibilidade manuscrito-periodico usando:
  - Jaccard similarity (palavras-chave do manuscrito vs escopo do periodico)
  - Qualis strata score normalizado
  - Prazo estimado de resposta (heuristica baseada em area)
  - Taxa de aceitacao estimada (heuristica por estrato)
  - APC (Article Processing Charge) e flag de acesso aberto
"""

from dataclasses import dataclass, field
from typing import Optional
import json
import math

QUALIS_SCORE = {
    "A1": 1.00, "A2": 0.875, "A3": 0.75, "A4": 0.625,
    "B1": 0.50, "B2": 0.375, "B3": 0.25, "B4": 0.125, "C": 0.0
}

QUALIS_ORDER = ["A1", "A2", "A3", "A4", "B1", "B2", "B3", "B4", "C"]

CAPES_AREAS = [
    "MATEMATICA / PROBABILIDADE E ESTATISTICA",
    "CIENCIA DA COMPUTACAO",
    "ASTRONOMIA / FISICA",
    "QUIMICA",
    "GEOCIENCIAS",
    "BIODIVERSIDADE",
    "CIENCIAS BIOLOGICAS I",
    "CIENCIAS BIOLOGICAS II",
    "CIENCIAS BIOLOGICAS III",
    "ENGENHARIAS I", "ENGENHARIAS II", "ENGENHARIAS III", "ENGENHARIAS IV",
    "MEDICINA I", "MEDICINA II", "MEDICINA III",
    "ODONTOLOGIA", "FARMACIA", "ENFERMAGEM",
    "NUTRICAO", "SAUDE COLETIVA",
    "EDUCACAO FISICA",
    "CIENCIAS AGRARIAS I", "MEDICINA VETERINARIA",
    "ZOOTECNIA / RECURSOS PESQUEIROS",
    "CIENCIA E TECNOLOGIA DE ALIMENTOS",
    "ADMINISTRACAO PUBLICA E DE EMPRESAS, CIENCIAS CONTABEIS E TURISMO",
    "ARQUITETURA, URBANISMO E DESIGN",
    "COMUNICACAO E INFORMACAO",
    "DIREITO", "ECONOMIA",
    "PLANEJAMENTO URBANO E REGIONAL / DEMOGRAFIA",
    "SERVICO SOCIAL",
    "ANTROPOLOGIA / ARQUEOLOGIA",
    "CIENCIA POLITICA E RELACOES INTERNACIONAIS",
    "EDUCACAO", "FILOSOFIA", "GEOGRAFIA",
    "HISTORIA", "PSICOLOGIA", "SOCIOLOGIA",
    "TEOLOGIA / CIENCIAS DA RELIGIAO",
    "ARTES", "LINGUISTICA E LITERATURA",
    "BIOTECNOLOGIA", "CIENCIAS AMBIENTAIS",
    "ENSINO", "INTERDISCIPLINAR", "MATERIAIS"
]


@dataclass
class Journal:
    titulo: str
    issn: str
    qualis: str
    area_avaliacao: str
    escopo_keywords: list[str] = field(default_factory=list)
    acesso_aberto: bool = False
    apc_brl: float = 0.0
    tempo_medio_resposta_meses: float = 6.0
    taxa_aceitacao_pct: float = 30.0
    cite_score: float = 0.0
    sjr: float = 0.0
    h_index: float = 0.0

    def qualis_numeric(self) -> float:
        return QUALIS_SCORE.get(self.qualis, 0.0)


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


def jaccard_similarity(tokens_a: list[str], tokens_b: list[str]) -> float:
    set_a = set(t.lower() for t in tokens_a)
    set_b = set(t.lower() for t in tokens_b)
    if not set_a or not set_b:
        return 0.0
    intersection = set_a & set_b
    union = set_a | set_b
    return len(intersection) / len(union) if union else 0.0


def normalizar_tempo(tempo_meses: float) -> float:
    """Quanto menor o tempo, maior o score (nunca < 0)."""
    if tempo_meses <= 0:
        return 1.0
    return max(0.0, 1.0 - (tempo_meses / 24.0))


def normalizar_aceitacao(taxa_pct: float) -> float:
    """Taxa de aceitacao mais alta = mais facil = score maior."""
    return min(1.0, taxa_pct / 60.0)


def normalizar_apc(apc_brl: float) -> float:
    """APC 0 = score maximo. Acima de 3000 BRL = score minimo."""
    if apc_brl <= 0:
        return 1.0
    return max(0.0, 1.0 - (apc_brl / 6000.0))


PESOS = {
    "qualis": 0.30,
    "scope": 0.25,
    "qualidade": 0.15,
    "tempo": 0.12,
    "aceitacao": 0.10,
    "acesso": 0.05,
    "apc": 0.03,
}


def score_journal(manuscript: ManuscriptProfile, journal: Journal) -> JournalScore:
    s_qualis = journal.qualis_numeric()
    s_scope = jaccard_similarity(manuscript.keywords, journal.escopo_keywords)
    s_tempo = normalizar_tempo(journal.tempo_medio_resposta_meses)
    s_aceitacao = normalizar_aceitacao(journal.taxa_aceitacao_pct)
    s_acesso = 1.0 if journal.acesso_aberto else 0.5
    s_apc = normalizar_apc(journal.apc_brl)
    s_qualidade = min(1.0, (journal.cite_score / 10.0 + journal.sjr / 2.0) / 2.0)

    total = (
        PESOS["qualis"] * s_qualis +
        PESOS["scope"] * s_scope +
        PESOS["qualidade"] * s_qualidade +
        PESOS["tempo"] * s_tempo +
        PESOS["aceitacao"] * s_aceitacao +
        PESOS["acesso"] * s_acesso +
        PESOS["apc"] * s_apc
    )

    justificativa_parts = []
    if s_qualis >= 0.75:
        justificativa_parts.append(f"Qualis {journal.qualis} (alta)")
    if s_scope >= 0.5:
        justificativa_parts.append("alto alinhamento tematico")
    if s_aceitacao >= 0.5:
        justificativa_parts.append("taxa de aceitacao favoravel")
    if journal.acesso_aberto:
        justificativa_parts.append("acesso aberto")

    return JournalScore(
        journal=journal,
        score_total=round(total, 4),
        score_qualis=round(s_qualis, 4),
        score_scope=round(s_scope, 4),
        score_tempo=round(s_tempo, 4),
        score_aceitacao=round(s_aceitacao, 4),
        score_acesso=round(s_acesso, 4),
        score_apc=round(s_apc, 4),
        justificativa="; ".join(justificativa_parts) if justificativa_parts else "avaliacao neutra"
    )


def rank_journals(
    manuscript: ManuscriptProfile,
    journals: list[Journal],
    top_n: int = 5
) -> list[JournalScore]:
    scored = [score_journal(manuscript, j) for j in journals]
    scored.sort(key=lambda s: s.score_total, reverse=True)
    return scored[:top_n]


def export_json(scores: list[JournalScore], output_path: str) -> None:
    data = []
    for s in scores:
        data.append({
            "titulo": s.journal.titulo,
            "issn": s.journal.issn,
            "qualis": s.journal.qualis,
            "area": s.journal.area_avaliacao,
            "score_total": s.score_total,
            "score_qualis": s.score_qualis,
            "score_scope": s.score_scope,
            "score_tempo": s.score_tempo,
            "score_aceitacao": s.score_aceitacao,
            "justificativa": s.justificativa,
        })
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def inferir_area_capes(keywords: list[str]) -> str:
    """Heuristica: maior sobreposicao de keywords com areas CAPES."""
    area_keywords = {
        "CIENCIA DA COMPUTACAO": ["computacao", "algoritmo", "software", "ia", "machine learning", "dados", "redes", "seguranca"],
        "EDUCACAO": ["educacao", "ensino", "aprendizagem", "pedagogia", "didatica", "escola", "curriculo", "formacao"],
        "ENGENHARIAS IV": ["eletrica", "eletronica", "computacao", "automacao", "controle", "robotica", "processamento"],
        "INTERDISCIPLINAR": ["interdisciplinar", "multidisciplinar", "sustentabilidade", "inovacao", "tecnologia social"],
        "ADMINISTRACAO PUBLICA E DE EMPRESAS": ["administracao", "gestao", "estrategia", "marketing", "financas", "inovacao"],
        "MATEMATICA / PROBABILIDADE E ESTATISTICA": ["matematica", "estatistica", "probabilidade", "modelagem", "otimizacao"],
        "BIOTECNOLOGIA": ["biotecnologia", "genetica", "molecular", "bioinformatica", "proteinas"],
        "CIENCIAS AMBIENTAIS": ["ambiental", "sustentabilidade", "ecologia", "clima", "biodiversidade", "conservacao"],
        "DIREITO": ["direito", "juridico", "legislacao", "constitucional", "penal", "tributario"],
        "PSICOLOGIA": ["psicologia", "comportamento", "cognitivo", "saude mental", "terapia"],
    }
    best_area = "INTERDISCIPLINAR"
    best_score = 0
    kw_lower = [k.lower() for k in keywords]
    for area, tokens in area_keywords.items():
        overlap = sum(1 for k in kw_lower if any(t in k for t in tokens))
        if overlap > best_score:
            best_score = overlap
            best_area = area
    return best_area


if __name__ == "__main__":
    manuscript = ManuscriptProfile(
        titulo="Impacto da Inteligencia Artificial na Educacao Superior Brasileira",
        abstract="Este estudo investiga como ferramentas de IA generativa estao transformando praticas pedagogicas no ensino superior do Brasil...",
        keywords=["inteligencia artificial", "educacao superior", "chatgpt", "ensino", "tecnologia educacional", "formacao docente"],
        area_capes="EDUCACAO"
    )

    sample_journals = [
        Journal("Computers & Education", "0360-1315", "A1", "EDUCACAO",
                ["educacao", "tecnologia", "computador", "ensino", "aprendizagem", "digital"],
                acesso_aberto=False, apc_brl=18000, tempo_medio_resposta_meses=4, taxa_aceitacao_pct=15, cite_score=17.6, sjr=3.02),
        Journal("Educacao & Sociedade", "0101-7330", "A1", "EDUCACAO",
                ["educacao", "sociedade", "politica educacional", "formacao", "ensino"],
                acesso_aberto=True, apc_brl=0, tempo_medio_resposta_meses=8, taxa_aceitacao_pct=25, cite_score=1.2, sjr=0.32),
        Journal("Revista Brasileira de Informatica na Educacao", "1414-5685", "A2", "EDUCACAO",
                ["informatica", "educacao", "tecnologia", "ensino", "computador", "ia"],
                acesso_aberto=True, apc_brl=0, tempo_medio_resposta_meses=5, taxa_aceitacao_pct=30, cite_score=1.5, sjr=0.28),
        Journal("ET&D - Educacao Tematica Digital", "1676-2592", "A2", "EDUCACAO",
                ["educacao", "digital", "tecnologia", "midia", "ensino", "cultura digital"],
                acesso_aberto=True, apc_brl=0, tempo_medio_resposta_meses=6, taxa_aceitacao_pct=35, cite_score=0.8, sjr=0.20),
        Journal("British Journal of Educational Technology", "0007-1013", "A1", "EDUCACAO",
                ["educational", "technology", "learning", "digital", "online", "ai"],
                acesso_aberto=False, apc_brl=22000, tempo_medio_resposta_meses=3, taxa_aceitacao_pct=12, cite_score=8.4, sjr=2.11),
    ]

    ranked = rank_journals(manuscript, sample_journals, top_n=5)

    print("\n=== Qualis Target Navigator — Resultados ===\n")
    for i, s in enumerate(ranked, 1):
        print(f"{i}. {s.journal.titulo} (Qualis {s.journal.qualis})")
        print(f"   ISSN: {s.journal.issn}")
        print(f"   Score: {s.score_total:.3f} | Scope: {s.score_scope:.3f} | Qualis: {s.score_qualis:.3f}")
        print(f"   Tempo: {s.journal.tempo_medio_resposta_meses}meses | Aceitacao: {s.journal.taxa_aceitacao_pct}% | APC: R${s.journal.apc_brl:,.0f}")
        print(f"   Justificativa: {s.justificativa}")
        print()

    area = inferir_area_capes(manuscript.keywords)
    print(f"Area CAPES inferida: {area}")
