#!/usr/bin/env python3
"""
Epistemic Artifact Injector — Track 1 da SPEC-R44.

Injeta artefatos epistemicos nas 57 categorias ausentes identificadas
pelo Scanner Noológico, seguindo ordem de prioridade baseada no EPS
(Epistemic Potential Score) do PotentialityEstimator v2.
"""

import json
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


# Ordem de prioridade de injecao (baseada no EPS medio do scanner noologico)
INJECTION_PRIORITY = [
    "dominios",       # EPS 62.8 — cobertura 10%
    "metodos",        # EPS 57.8 — cobertura 20%
    "paradigmas",     # EPS 64.6 — cobertura 25%
    "raciocinio",     # EPS 53.0 — cobertura 50%
    "dados",          # EPS 49.5 — cobertura 25%
    "niveis_analise", # EPS 44.2 — cobertura 50%
    "temporalidade",  # EPS 40.9 — cobertura 33%
    "populacao",      # EPS 40.9 — cobertura 33%
    "teorias",        # EPS 37.6 — cobertura 30%
    "teoria_jogos",   # EPS 73.0 — cobertura 100% (manter)
]

# Dimensoes e suas categorias ausentes (do scanner noologico)
NOOLOGICAL_GAPS = {
    "dominios": [
        "Psicologia clínica", "Neurociências", "Sociologia",
        "Antropologia", "Economia comportamental", "Filosofia da mente",
        "Psicofarmacologia", "Educação", "Inteligência Artificial / Tecnologia",
    ],
    "metodos": [
        "Qualitativo fenomenológico", "Qualitativo grounded theory",
        "Misto sequencial", "Misto convergente", "Revisão sistemática",
        "Meta-análise", "Estudo de caso", "Pesquisa-ação",
    ],
    "paradigmas": [
        "Positivista", "Interpretativista", "Pragmatista",
        "Fenomenológico", "Construtivista", "Pós-estruturalista",
    ],
    "raciocinio": [
        "Abdutivo", "Dialético", "Sistêmico",
        "Probabilístico", "Metacognitivo",
    ],
    "dados": [
        "Dados neurobiológicos", "Dados qualitativos (entrevistas)",
        "Dados observacionais", "Dados epidemiológicos",
        "Dados comparativos (cross-cultural)", "Metadados (revisões)",
    ],
    "niveis_analise": [
        "Individual/intrapsíquico", "Interpessoal/relacional",
        "Neurobiológico", "Cultural/antropológico",
    ],
    "temporalidade": [
        "Transversal (momento único)", "Longitudinal (curto prazo)",
        "Longitudinal (longo prazo)", "Prospectivo/preditivo",
    ],
    "populacao": [
        "Adultos", "Idosos", "Adolescentes",
        "Gênero feminino", "Gênero masculino", "Diversidade de gênero",
        "Contexto clínico", "Cross-cultural",
    ],
    "teorias": [
        "Psicanalítico", "Humanista", "Sistêmico",
        "Neurobiológico", "Social-crítico",
        "Fenomenológico-existencial", "Comportamental",
    ],
    "teoria_jogos": [],  # 100% coberto — sem gaps
}


@dataclass
class EpistemicArtifact:
    """Artefato epistemico injetado no ecossistema."""
    dimension: str
    category: str
    artifact_type: str  # reasoning_pattern | reference | method | paradigm
    content: str
    source_scanner: str
    eps_score: float
    cross_domain_impact: float = 0.0
    theoretical_fertility: float = 0.0
    artifact_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    injected_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    ttl_days: int = 365

    def is_expired(self) -> bool:
        """Verifica se o artefato expirou baseado no TTL."""
        injected = datetime.fromisoformat(self.injected_at)
        elapsed = (datetime.now(timezone.utc) - injected).days
        return elapsed > self.ttl_days


class EpistemicInjector:
    """Injetor de artefatos epistemicos no ecossistema.

    Responsabilidades:
    - Injetar artefatos individuais ou em lote
    - Persistir em arquivos JSON (um por artefato)
    - Detectar duplicatas
    - Calcular estatisticas de cobertura e HI
    """

    def __init__(self, artifacts_dir: str = "nexus/artifacts"):
        self.artifacts_dir = Path(artifacts_dir)
        self.artifacts_dir.mkdir(parents=True, exist_ok=True)
        self._cache: dict[str, EpistemicArtifact] = {}
        self._load_cache()

    def _load_cache(self):
        """Carrega todos os artefatos do diretorio de persistencia."""
        self._cache.clear()
        for fpath in sorted(self.artifacts_dir.glob("*.json")):
            try:
                data = json.loads(fpath.read_text())
                art = EpistemicArtifact(**data)
                if not art.is_expired():
                    self._cache[art.artifact_id] = art
                else:
                    fpath.unlink(missing_ok=True)
            except (json.JSONDecodeError, KeyError, TypeError):
                continue

    def _artifact_path(self, artifact_id: str) -> Path:
        return self.artifacts_dir / f"{artifact_id}.json"

    def _is_duplicate(self, dimension: str, category: str,
                      content: str) -> Optional[str]:
        """Retorna ID se artefato duplicado existir."""
        for art in self._cache.values():
            if (art.dimension == dimension
                    and art.category == category
                    and art.content == content):
                return art.artifact_id
        return None

    def inject(self, dimension: str, category: str,
               artifact_type: str = "reference",
               content: str = "",
               source_scanner: str = "manual",
               eps_score: float = 50.0,
               cross_domain_impact: float = 5.0,
               theoretical_fertility: float = 5.0) -> str:
        """Injeta um artefato epistemico. Retorna ID.

        Se duplicata, retorna ID do existente.
        """
        dup_id = self._is_duplicate(dimension, category, content)
        if dup_id:
            return dup_id

        artifact = EpistemicArtifact(
            dimension=dimension,
            category=category,
            artifact_type=artifact_type,
            content=content,
            source_scanner=source_scanner,
            eps_score=eps_score,
            cross_domain_impact=cross_domain_impact,
            theoretical_fertility=theoretical_fertility,
        )

        # Persistir
        fpath = self._artifact_path(artifact.artifact_id)
        with open(fpath, "w", encoding="utf-8") as f:
            json.dump(asdict(artifact), f, ensure_ascii=False, indent=2)

        self._cache[artifact.artifact_id] = artifact
        return artifact.artifact_id

    def inject_batch(self, artifacts: list[dict]) -> list[str]:
        """Injeta multiplos artefatos em lote."""
        ids = []
        for a in artifacts:
            aid = self.inject(**a)
            ids.append(aid)
        return ids

    def get_artifact(self, artifact_id: str) -> Optional[EpistemicArtifact]:
        """Recupera artefato por ID."""
        self._load_cache()  # refresh
        return self._cache.get(artifact_id)

    def list_artifacts(self) -> list[EpistemicArtifact]:
        """Lista todos os artefatos ativos."""
        self._load_cache()
        return list(self._cache.values())

    def get_coverage_stats(self) -> dict:
        """Retorna estatisticas de cobertura por dimensao."""
        self._load_cache()

        total_categories = sum(len(v) for v in NOOLOGICAL_GAPS.values())
        categories_covered: dict[str, set[str]] = {}
        artifacts_by_dim: dict[str, int] = {}

        for art in self._cache.values():
            dim = art.dimension
            if dim not in categories_covered:
                categories_covered[dim] = set()
                artifacts_by_dim[dim] = 0
            categories_covered[dim].add(art.category)
            artifacts_by_dim[dim] += 1

        # Cobertura por dimensao
        dim_coverage = {}
        for dim, total_cats in NOOLOGICAL_GAPS.items():
            covered = len(categories_covered.get(dim, set()))
            total = max(len(total_cats), 1)  # evitar divisao por zero
            dim_coverage[dim] = {
                "covered": min(covered, total),
                "total": total,
                "pct": round(min(covered / total, 1.0) * 100, 1),
                "artifacts": artifacts_by_dim.get(dim, 0),
            }

        total_covered_all = sum(
            min(len(categories_covered.get(d, set())), max(len(v), 1))
            for d, v in NOOLOGICAL_GAPS.items()
        )

        return {
            "total_artifacts": len(self._cache),
            "dimensions_covered": len(categories_covered),
            "total_categories": total_categories,
            "categories_covered_total": total_covered_all,
            "coverage_pct": round(
                min(total_covered_all / max(total_categories, 1), 1.0) * 100, 1
            ),
            "by_dimension": dim_coverage,
        }

    def calculate_homogeneity_index(self) -> float:
        """Calcula Homogeneity Index (HI) baseado nos artefatos.

        HI = 1 - (dimensoes_distintas / total_artefatos)
        Quanto mais concentrado, maior o HI.
        """
        self._load_cache()

        if not self._cache:
            return 0.0

        dims = set(a.dimension for a in self._cache.values())
        n_dims = len(dims)
        n_arts = len(self._cache)

        if n_arts == 0:
            return 0.0

        # HI baseado na distribuicao por dimensao
        # Quanto mais uniforme a distribuicao, menor o HI
        dim_counts = {}
        for a in self._cache.values():
            dim_counts[a.dimension] = dim_counts.get(a.dimension, 0) + 1

        # Desvio padrao normalizado das contagens
        if len(dim_counts) <= 1:
            return 1.0

        mean = n_arts / len(dim_counts)
        variance = sum((c - mean) ** 2 for c in dim_counts.values()) / len(dim_counts)
        std = variance ** 0.5

        # Normalizar para [0, 1]
        max_std = mean * (len(dim_counts) - 1) ** 0.5 if len(dim_counts) > 1 else 1
        hi = min(std / max(max_std, 1), 1.0) if max_std > 0 else 0.5

        return round(hi, 4)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Epistemic Injector — R44")
    parser.add_argument("--inject", nargs=3,
                        metavar=("DIM", "CAT", "TYPE"),
                        help="Injetar artefato: dimensao categoria tipo")
    parser.add_argument("--batch", action="store_true",
                        help="Injetar lote pre-definido")
    parser.add_argument("--stats", action="store_true",
                        help="Mostrar estatisticas de cobertura")
    parser.add_argument("--hi", action="store_true",
                        help="Calcular Homogeneity Index")
    parser.add_argument("--dir", default="nexus/artifacts",
                        help="Diretorio de artefatos")
    args = parser.parse_args()

    injector = EpistemicInjector(artifacts_dir=args.dir)

    if args.inject:
        dim, cat, atype = args.inject
        aid = injector.inject(dimension=dim, category=cat, artifact_type=atype,
                              content=f"CLI injection: {dim}/{cat}")
        print(f"Injected: {aid}")

    if args.batch:
        from nexus.epistemic_injector import NOOLOGICAL_GAPS
        count = 0
        for dim, cats in NOOLOGICAL_GAPS.items():
            for cat in cats[:2]:  # 2 por dimensao
                injector.inject(dimension=dim, category=cat,
                                artifact_type="reference",
                                content=f"Batch: {dim}/{cat}",
                                source_scanner="noological",
                                eps_score=55.0)
                count += 1
        print(f"Batch injected: {count} artifacts")

    if args.stats:
        stats = injector.get_coverage_stats()
        print(f"=== Coverage Stats ===")
        print(f"Total artifacts: {stats['total_artifacts']}")
        print(f"Coverage: {stats['coverage_pct']}% ({stats['categories_covered_total']}/{stats['total_categories']})")
        for dim, info in stats.get("by_dimension", {}).items():
            print(f"  {dim}: {info['pct']}% ({info['covered']}/{info['total']}) [{info['artifacts']} artifacts]")

    if args.hi:
        hi = injector.calculate_homogeneity_index()
        print(f"Homogeneity Index (HI): {hi:.4f}")
