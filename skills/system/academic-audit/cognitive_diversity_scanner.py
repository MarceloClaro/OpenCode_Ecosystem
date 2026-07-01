#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CognitiveDiversityScanner v1.0 — Detector de Homogeneidade Cognitiva
======================================================================
SPEC-053 — 2026-06-25 — Cognitive Diversity Scanner

Conceito original: Interlocutor Externo (HiddenGapTheory)
Implementacao: Marcelo Claro Laranjeira

Detecta câmaras de eco e falsa diversidade em artefatos de conhecimento
através do Índice de Homogeneidade (HI), clusterização epistemológica
e análise de diversidade cross-cluster.

Pipeline:
  1. Registro de artefatos com vetores de cobertura epistemológica
  2. Clusterização por similaridade de perfil (distância euclidiana)
  3. Cálculo do HI: 1 - distância_média_observada / distância_máxima_possível
  4. Classificação: eco (HI > 0.8), baixa (0.6-0.8), moderada (0.3-0.6), alta (< 0.3)
  5. Geração de recomendações de diversificação
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, field, asdict
from typing import Any


# ═══════════════════════════════════════════════════════════════════════
# CONSTANTES
# ═══════════════════════════════════════════════════════════════════════

DEFAULT_CONFIG: dict[str, Any] = {
    "hi_threshold_echo": 0.8,        # HI > 0.8 = câmara de eco
    "hi_threshold_low": 0.6,         # HI 0.6-0.8 = baixa diversidade
    "hi_threshold_moderate": 0.3,    # HI 0.3-0.6 = diversidade moderada
    "min_cluster_size": 3,           # mínimo de artefatos para cluster válido
    "distance_metric": "euclidean",  # métrica de distância
    "cluster_algorithm": "kmeans",   # algoritmo de clusterização
    "max_clusters": 10,              # máximo de clusters a detectar
}

HI_CLASSIFICATIONS: list[tuple[float, str]] = [
    (0.8, "echo_chamber"),
    (0.6, "low_diversity"),
    (0.3, "moderate_diversity"),
    (0.0, "high_diversity"),
]


# ═══════════════════════════════════════════════════════════════════════
# DATA CLASSES
# ═══════════════════════════════════════════════════════════════════════

@dataclass
class ArtifactProfile:
    """Perfil epistemológico de um artefato de conhecimento."""
    artifact_id: str
    text_preview: str
    coverage_vector: dict[str, float]  # dimensão -> densidade [0, 1]
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ClusterResult:
    """Resultado da clusterização de artefatos."""
    cluster_id: int
    artifacts: list[ArtifactProfile]
    centroid: dict[str, float]
    internal_hi: float = 0.0  # homogeneidade interna do cluster
    size: int = 0

    def __post_init__(self):
        self.size = len(self.artifacts)


# ═══════════════════════════════════════════════════════════════════════
# SCANNER PRINCIPAL
# ═══════════════════════════════════════════════════════════════════════

class CognitiveDiversityScanner:
    """
    Scanner de Diversidade Cognitiva.

    Detecta câmaras de eco e homogeneidade excessiva em conjuntos
    de artefatos de conhecimento, usando o Índice de Homogeneidade (HI).
    """

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = {**DEFAULT_CONFIG, **(config or {})}
        self._artifacts: list[ArtifactProfile] = []
        self._clusters: list[ClusterResult] = []
        self._last_result: dict[str, Any] = {}

    # ─── Registro de artefatos ────────────────────────────────────────────

    def register_artifact(self, artifact: ArtifactProfile) -> None:
        """Registra um artefato para análise."""
        self._artifacts.append(artifact)

    def artifact_count(self) -> int:
        """Retorna o número de artefatos registrados."""
        return len(self._artifacts)

    def get_artifacts(self) -> list[ArtifactProfile]:
        """Retorna a lista de artefatos registrados."""
        return list(self._artifacts)

    def clear(self) -> None:
        """Limpa todos os artefatos e clusters."""
        self._artifacts.clear()
        self._clusters.clear()
        self._last_result = {}

    # ─── Inferência a partir do NoologicalScanner ─────────────────────────

    def infer_artifacts_from_noological(self, noological_result: Any) -> list[ArtifactProfile]:
        """
        Infere artefatos a partir do resultado do NoologicalScanner.
        Cria um artefato por dimensão com base nas densidades.
        """
        inferred = []
        dims = {}

        # Extrair dimensões do resultado
        if hasattr(noological_result, "dimensions"):
            dims = noological_result.dimensions
        elif hasattr(noological_result, "coverage_vector"):
            # Tratar como mock: criar artefato a partir do vetor
            vec = noological_result.coverage_vector
            profile = ArtifactProfile(
                artifact_id="noological_inferred_0",
                text_preview="Inferido do NoologicalScanner",
                coverage_vector={f"dim_{i}": v for i, v in enumerate(vec)},
            )
            inferred.append(profile)
            self._artifacts.append(profile)
            return inferred

        for dim_name, dim_data in dims.items():
            density = 0.0
            if isinstance(dim_data, dict):
                density = dim_data.get("density", 0.0)
            elif hasattr(dim_data, "density"):
                density = dim_data.density

            profile = ArtifactProfile(
                artifact_id=f"dim_{dim_name}",
                text_preview=f"Artefato inferido da dimensao {dim_name}",
                coverage_vector={dim_name: density},
            )
            inferred.append(profile)
            self._artifacts.append(profile)

        return inferred

    # ─── Cálculo do Índice de Homogeneidade (HI) ─────────────────────────

    def _extract_vectors(self) -> tuple[list[list[float]], list[str]]:
        """Extrai vetores numéricos e IDs dos artefatos."""
        vectors = []
        ids = []
        for art in self._artifacts:
            vec = list(art.coverage_vector.values())
            vectors.append(vec)
            ids.append(art.artifact_id)
        return vectors, ids

    def _euclidean_distance(self, v1: list[float], v2: list[float]) -> float:
        """Distância euclidiana entre dois vetores."""
        if len(v1) != len(v2):
            # Vetores de tamanhos diferentes: usar interseção
            return 1.0
        return math.sqrt(sum((a - b) ** 2 for a, b in zip(v1, v2)))

    def _normalized_distance(self, v1: list[float], v2: list[float]) -> float:
        """
        Distância normalizada para [0, 1].
        0 = idêntico, 1 = máximo diferentes.
        """
        raw = self._euclidean_distance(v1, v2)
        max_dist = math.sqrt(len(v1))  # máximo possível euclidiano
        if max_dist == 0:
            return 0.0
        return min(raw / max_dist, 1.0)

    def _pairwise_distances(self, vectors: list[list[float]]) -> list[float]:
        """Calcula todas as distâncias pareadas entre os vetores."""
        distances = []
        n = len(vectors)
        for i in range(n):
            for j in range(i + 1, n):
                d = self._normalized_distance(vectors[i], vectors[j])
                distances.append(d)
        return distances

    def _cluster_artifacts(self) -> list[ClusterResult]:
        """
        Clusteriza artefatos por similaridade de perfil.
        Usa k-means simplificado (distância ao centróide).
        """
        vectors, ids = self._extract_vectors()
        n = len(vectors)
        if n < self.config["min_cluster_size"]:
            return []

        # K-means simplificado com k = min(max_clusters, n//2)
        k = min(self.config["max_clusters"], max(2, n // 2))

        # Inicialização: k primeiros artefatos como centróides
        centroids = [vectors[i] for i in range(k)]
        clusters = [[] for _ in range(k)]

        # 5 iterações de convergência
        for _iteration in range(5):
            # Assignment step
            new_clusters = [[] for _ in range(k)]
            for idx, vec in enumerate(vectors):
                distances = [self._euclidean_distance(vec, c) for c in centroids]
                nearest = distances.index(min(distances))
                new_clusters[nearest].append(idx)

            # Update step
            for c_idx in range(k):
                if new_clusters[c_idx]:
                    cluster_vecs = [vectors[i] for i in new_clusters[c_idx]]
                    centroids[c_idx] = [sum(dim) / len(dim) for dim in zip(*cluster_vecs)]

            clusters = new_clusters

        # Construir ClusterResults
        results = []
        for c_idx, member_indices in enumerate(clusters):
            if len(member_indices) < self.config["min_cluster_size"]:
                continue

            artifacts = [self._artifacts[i] for i in member_indices]
            centroid = dict(zip(self._artifacts[0].coverage_vector.keys(),
                                centroids[c_idx]))

            results.append(ClusterResult(
                cluster_id=c_idx,
                artifacts=artifacts,
                centroid=centroid,
            ))

        return results

    def _compute_cluster_hi(self, cluster: ClusterResult) -> float:
        """Calcula o HI interno de um cluster."""
        vectors = [list(a.coverage_vector.values()) for a in cluster.artifacts]
        distances = self._pairwise_distances(vectors)

        if not distances:
            return 0.0

        avg_distance = sum(distances) / len(distances)
        return 1.0 - avg_distance

    def _classify_hi(self, hi: float) -> str:
        """Classifica o HI em categorias qualitativas."""
        for threshold, label in HI_CLASSIFICATIONS:
            if hi >= threshold:
                return label
        return "high_diversity"

    def _generate_recommendations(self, hi: float, clusters: list[ClusterResult]) -> list[str]:
        """Gera recomendações de diversificação baseadas no HI."""
        recs = []

        if hi >= self.config["hi_threshold_echo"]:
            recs.append("CAMARA DE ECO detectada. Buscar perspectivas epistemologicas alternativas alem do paradigma dominante.")
            recs.append("Recomendado: incluir artefatos de pelo menos 3 dimensoes epistemologicas diferentes.")
        elif hi >= self.config["hi_threshold_low"]:
            recs.append("Baixa diversidade cognitiva. Explorar metodologias e paradigmas complementares.")
            recs.append("Recomendado: revisar literatura em dominios adjacentes ao cluster principal.")

        if len(clusters) <= 1 and len(self._artifacts) >= self.config["min_cluster_size"]:
            recs.append("Apenas um cluster detectado. Considere expandir o escopo para incluir abordagens alternativas.")
        elif len(clusters) > 1:
            recs.append(f"Diversidade cross-cluster detectada: {len(clusters)} clusters. "
                       "Explorar conexoes entre clusters para identificar oportunidades de ponte.")

        # Recomendações baseadas em dimensões sub-representadas
        if self._artifacts:
            all_dims = set()
            for art in self._artifacts:
                all_dims.update(art.coverage_vector.keys())

            dim_means: dict[str, list[float]] = {d: [] for d in all_dims}
            for art in self._artifacts:
                for dim, val in art.coverage_vector.items():
                    dim_means[dim].append(val)

            for dim, vals in dim_means.items():
                if vals:
                    mean_val = sum(vals) / len(vals)
                    if mean_val < 0.2:
                        recs.append(f"Dim '{dim}' sub-representada (media={mean_val:.2f}). "
                                   "Explorar artefatos que utilizem esta dimensao.")

        if not recs:
            recs.append("Diversidade cognitiva saudavel. Manter estrategia atual de exploracao.")

        return recs

    def compute_homogeneity_index(self) -> dict[str, Any]:
        """
        Calcula o Índice de Homogeneidade (HI) global.

        Returns:
            dict com HI global, classificação, clusters e recomendações
        """
        n = len(self._artifacts)
        if n < self.config["min_cluster_size"]:
            self._last_result = {
                "global_hi": None,
                "error": f"Artefatos insuficientes: {n} registrados, "
                        f"minimo={self.config['min_cluster_size']}",
                "n_artifacts": n,
                "is_echo_chamber": False,
                "classification": "insufficient_data",
                "recommendations": ["Registre mais artefatos para análise significativa."],
                "cluster_info": {"n_clusters": 0, "silhouette_score": None},
            }
            return self._last_result

        # Clusterizar
        self._clusters = self._cluster_artifacts()

        # Calcular HI de cada cluster
        for cluster in self._clusters:
            cluster.internal_hi = self._compute_cluster_hi(cluster)

        # Calcular HI global: média ponderada pelo tamanho dos clusters
        if self._clusters:
            weighted_hi = sum(c.internal_hi * c.size for c in self._clusters) / sum(c.size for c in self._clusters)
        else:
            # Fallback: HI baseado em todas as distâncias pareadas
            vectors, _ = self._extract_vectors()
            distances = self._pairwise_distances(vectors)
            if distances:
                weighted_hi = 1.0 - (sum(distances) / len(distances))
            else:
                weighted_hi = 0.0

        # Calcular silhouette score simplificado
        silhouette = self._compute_silhouette()

        # Classificar
        classification = self._classify_hi(weighted_hi)
        is_echo = classification == "echo_chamber"

        # Recomendações
        recommendations = self._generate_recommendations(weighted_hi, self._clusters)

        # Informação dos clusters
        cluster_info = {
            "n_clusters": len(self._clusters),
            "clusters": [
                {
                    "cluster_id": c.cluster_id,
                    "size": c.size,
                    "internal_hi": round(c.internal_hi, 4),
                }
                for c in self._clusters
            ],
            "silhouette_score": round(silhouette, 4) if silhouette is not None else None,
        }

        self._last_result = {
            "global_hi": round(weighted_hi, 4),
            "classification": classification,
            "is_echo_chamber": is_echo,
            "n_artifacts": n,
            "n_clusters": len(self._clusters),
            "cluster_info": cluster_info,
            "recommendations": recommendations,
            "config": dict(self.config),
        }

        return self._last_result

    def _compute_silhouette(self) -> float | None:
        """
        Silhouette Score simplificado.
        Mede o quão bem separados estão os clusters.
        """
        if len(self._clusters) < 2:
            return None

        vectors, ids = self._extract_vectors()
        if len(vectors) < 3:
            return None

        # Mapa: artifact_id -> cluster_id
        art_to_cluster: dict[str, int] = {}
        for cluster in self._clusters:
            for art in cluster.artifacts:
                art_to_cluster[art.artifact_id] = cluster.cluster_id

        # Calcular silhouette médio
        scores = []
        for i, vec in enumerate(vectors):
            c_id = art_to_cluster.get(ids[i])
            if c_id is None:
                continue

            # a(i): distância média intra-cluster
            intra_dists = []
            inter_dists: dict[int, list[float]] = {}

            for j, other_vec in enumerate(vectors):
                if i == j:
                    continue
                d = self._normalized_distance(vec, other_vec)
                other_c_id = art_to_cluster.get(ids[j])

                if other_c_id == c_id:
                    intra_dists.append(d)
                elif other_c_id is not None:
                    inter_dists.setdefault(other_c_id, []).append(d)

            if not intra_dists:
                continue

            a = sum(intra_dists) / len(intra_dists)

            # b(i): menor distância média para outro cluster
            if inter_dists:
                b = min(sum(d) / len(d) for d in inter_dists.values())
            else:
                b = a  # se só tem um cluster

            # s(i) = (b - a) / max(a, b)
            denom = max(a, b)
            if denom > 0:
                s = (b - a) / denom
                scores.append(s)

        if not scores:
            return None

        return sum(scores) / len(scores)

    # ─── Integração com CognitiveDiversityInjector ─────────────────────

    def register_from_injector(self) -> int:
        """
        Carrega artefatos do CognitiveDiversityInjector (SPEC-056 R27).

        Importa o injector, gera os 8 artefatos de diversidade com
        paradigmas alternativos e os converte para ArtifactProfile.

        Returns:
            int: número de artefatos registrados pelo injector
        """
        try:
            from cognitive_diversity_injector import inject_diversity_artifacts

            artifacts = inject_diversity_artifacts()
            count = 0
            for art in artifacts:
                # Converte vetor 10D para dict nomeado
                dim_names = [
                    "paradigmas", "metodos", "teorias", "raciocinio",
                    "teoria_jogos", "niveis_analise", "temporalidade",
                    "populacao", "dados", "dominios",
                ]
                coverage_dict = {}
                for i, val in enumerate(art.coverage_vector):
                    if i < len(dim_names):
                        coverage_dict[dim_names[i]] = val

                profile = ArtifactProfile(
                    artifact_id=art.artifact_id,
                    text_preview=f"[INJECTOR] {art.title}: {art.description[:100]}",
                    coverage_vector=coverage_dict,
                    metadata={
                        "paradigm": art.paradigm,
                        "method": art.method,
                        "theory": art.theory,
                        "reasoning_types": art.reasoning_types,
                        "game_theory": art.game_theory,
                        "domain": art.domain,
                        "level_of_analysis": art.level_of_analysis,
                    },
                )
                self.register_artifact(profile)
                count += 1
            return count
        except ImportError:
            return 0
        except Exception:
            return 0

    # ─── Export ───────────────────────────────────────────────────────────

    def to_json(self, indent: int = 2) -> str:
        """Exporta o último resultado para JSON."""
        return json.dumps(self._last_result, indent=indent, default=str, ensure_ascii=False)

    def __repr__(self) -> str:
        return (f"CognitiveDiversityScanner("
                f"artifacts={len(self._artifacts)}, "
                f"clusters={len(self._clusters)})")
