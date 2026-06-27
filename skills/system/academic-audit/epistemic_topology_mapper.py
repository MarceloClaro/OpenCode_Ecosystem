#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EpistemicTopologyMapper v1.0 — Mapeador Topológico do Espaço de Conhecimento
================================================================================
SPEC-054 — 2026-06-25 — Epistemic Topology Mapper

Conceito original: Interlocutor Externo (HiddenGapTheory)
Implementacao: Marcelo Claro Laranjeira

Projeta vetores epistemológicos (92D do NoologicalScanner) em espaço 2D/3D
e identifica estruturas topológicas: continentes, ilhas, pontes, zonas de vazio.

Pipeline:
  1. Registro de pontos com coordenadas N-dimensionais
  2. Projeção para 2D (preservação topológica)
  3. Cálculo de Distâncias Epistemológicas (DE)
  4. Detecção de Ilhas (II > threshold)
  5. Detecção de Buracos Epistemológicos (BE)
  6. Cálculo de Potencial de Ponte (PP)
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from typing import Any


# ═══════════════════════════════════════════════════════════════════════
# CONSTANTES
# ═══════════════════════════════════════════════════════════════════════

DEFAULT_CONFIG: dict[str, Any] = {
    "n_neighbors": 15,          # vizinhos para UMAP
    "min_dist": 0.1,            # distância mínima para UMAP
    "random_state": 42,         # seed para reprodutibilidade
    "island_threshold": 0.7,    # II > 0.7 = ilha
    "hole_density_threshold": 0.2,  # densidade < 0.2 = buraco
    "bridge_pp_threshold": 0.6,  # PP > 0.6 = ponte potencial
    "topology_preservation_target": 0.85,  # preservação topológica mínima
}


# ═══════════════════════════════════════════════════════════════════════
# DATA CLASSES
# ═══════════════════════════════════════════════════════════════════════

@dataclass
class TopologicalPoint:
    """Ponto no espaço epistemológico."""
    point_id: str
    coordinates: list[float]        # vetor N-dimensional
    label: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
    projected: list[float] | None = None  # coordenadas projetadas (2D/3D)


@dataclass
class EpistemicDistance:
    """Distância epistemológica entre dois pontos."""
    source_id: str
    target_id: str
    distance: float  # normalizado [0, 1]
    raw_distance: float = 0.0


@dataclass
class TopologicalHole:
    """Buraco epistemológico — zona de vazio entre clusters."""
    hole_id: str
    centroid: list[float]
    radius: float          # raio aproximado do buraco
    density: float         # densidade na região
    be_score: float = 0.0  # Buraco Epistemológico score
    bounding_points: list[str] = field(default_factory=list)


@dataclass
class EpistemicIsland:
    """Ilha epistemológica — cluster isolado."""
    island_id: str
    point_ids: list[str]
    centroid: list[float]
    isolation_index: float = 0.0
    size: int = 0

    def __post_init__(self):
        self.size = len(self.point_ids)


@dataclass
class EpistemicBridge:
    """Ponte epistemológica — ponto que conecta clusters."""
    point_id: str
    pp_score: float       # Potencial de Ponte
    connected_clusters: list[int] = field(default_factory=list)
    connected_points: list[str] = field(default_factory=list)


# ═══════════════════════════════════════════════════════════════════════
# MAPPER PRINCIPAL
# ═══════════════════════════════════════════════════════════════════════

class EpistemicTopologyMapper:
    """
    Mapeador Topológico do Espaço de Conhecimento.

    Projeta pontos no espaço epistemológico, calcula distâncias,
    detecta ilhas, buracos e pontes entre clusters.
    """

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = {**DEFAULT_CONFIG, **(config or {})}
        self._points: dict[str, TopologicalPoint] = {}
        self._projected_coords: dict[str, list[float]] = {}
        self._distances: list[EpistemicDistance] = []
        self._clusters: list[list[str]] = []
        self._last_projection: dict[str, Any] = {}

    # ─── Registro de pontos ───────────────────────────────────────────────

    def add_point(self, point: TopologicalPoint) -> None:
        """Registra um ponto topológico."""
        self._points[point.point_id] = point

    def point_count(self) -> int:
        """Retorna o número de pontos registrados."""
        return len(self._points)

    def get_point(self, point_id: str) -> TopologicalPoint | None:
        """Retorna um ponto pelo ID."""
        return self._points.get(point_id)

    def get_all_points(self) -> list[TopologicalPoint]:
        """Retorna todos os pontos."""
        return list(self._points.values())

    def clear(self) -> None:
        """Limpa todos os dados."""
        self._points.clear()
        self._projected_coords.clear()
        self._distances.clear()
        self._clusters.clear()
        self._last_projection = {}

    # ─── Projeção ─────────────────────────────────────────────────────────

    def project(self, dimensions: int = 2) -> dict[str, Any]:
        """
        Projeta pontos no espaço de dimensões reduzidas.

        Implementa projeção simplificada (MDS-like) quando UMAP não
        está disponível. Preserva distâncias relativas entre pontos.

        Args:
            dimensions: 2 ou 3

        Returns:
            dict com projected_coords e métricas
        """
        n = len(self._points)
        if n < 2:
            return {"projected_coords": [], "n_points": n, "error": "Pontos insuficientes"}

        point_ids = list(self._points.keys())
        vectors = [self._points[pid].coordinates for pid in point_ids]

        # Verificar dimensionalidade consistente
        dim = len(vectors[0])
        if not all(len(v) == dim for v in vectors):
            return {"projected_coords": [], "n_points": n, "error": "Dimensionalidade inconsistente"}

        # Projeção: PCA simplificado ou MDS (métrica clássica)
        # Como não temos dependências externas, usamos MDS clássico
        projected = self._mds_projection(vectors, dimensions)

        # Armazenar coordenadas projetadas
        self._projected_coords = {}
        for i, pid in enumerate(point_ids):
            self._points[pid].projected = projected[i]
            self._projected_coords[pid] = projected[i]

        # Calcular preservação topológica
        preservation = self._compute_topology_preservation(vectors, projected)

        # Clusterizar no espaço projetado
        self._clusters = self._cluster_projected(projected, point_ids)

        result = {
            "projected_coords": [
                {"point_id": pid, "coordinates": self._projected_coords[pid]}
                for pid in point_ids
            ],
            "n_points": n,
            "dimensions": dimensions,
            "topology_preservation": round(preservation, 4),
            "n_clusters": len(self._clusters),
            "algorithm": "mds_classical",
        }

        self._last_projection = result
        return result

    def _compute_distance_matrix(self, vectors: list[list[float]]) -> list[list[float]]:
        """Matriz de distância euclidiana entre todos os vetores."""
        n = len(vectors)
        matrix = [[0.0] * n for _ in range(n)]
        for i in range(n):
            for j in range(i + 1, n):
                d = math.sqrt(sum((a - b) ** 2 for a, b in zip(vectors[i], vectors[j])))
                matrix[i][j] = d
                matrix[j][i] = d
        return matrix

    def _mds_projection(self, vectors: list[list[float]],
                        dimensions: int) -> list[list[float]]:
        """
        PCA via Power Iteration na matriz de covariância.

        Projeta vetores N-dimensionais em `dimensions` dimensões
        preservando a estrutura de variância dos dados.

        Mais estável numericamente que MDS clássico quando os dados
        têm baixa variância ou pontos muito próximos.
        """
        n = len(vectors)
        dim = len(vectors[0])
        if n == 1:
            return [[0.0] * dimensions]

        # 1. Centralizar os dados
        means = [sum(v[i] for v in vectors) / n for i in range(dim)]
        centered = [[v[i] - means[i] for i in range(dim)] for v in vectors]

        # 2. Matriz de covariância: C = X^T * X / (n-1)
        #    Forma: dim × dim (menor que n × n quando dim < n)
        cov_dim = min(dim, n)  # usar o menor para eficiência
        cov = [[0.0] * cov_dim for _ in range(cov_dim)]

        if dim <= n:
            # C = (1/(n-1)) * centered^T * centered
            for i in range(dim):
                for j in range(dim):
                    cov[i][j] = sum(centered[k][i] * centered[k][j]
                                   for k in range(n)) / (n - 1 if n > 1 else 1)
        else:
            # Usar matriz menor: G = (1/(n-1)) * centered * centered^T
            for i in range(n):
                for j in range(n):
                    cov[i][j] = sum(centered[i][k] * centered[j][k]
                                   for k in range(dim)) / (n - 1 if n > 1 else 1)

        # 3. Power iteration na matriz de covariância
        k = min(dimensions, cov_dim)
        eigenpairs = self._power_iteration(cov, k)

        # 4. Projetar usando os autovetores
        projected = []
        for i in range(n):
            pt = []
            for eigvec, eigval in eigenpairs:
                if abs(eigval) > 1e-10:
                    if dim <= n:
                        # Projeção direta: ponto · autovetor
                        coord = sum(centered[i][j] * eigvec[j] for j in range(dim))
                    else:
                        # Projeção via matriz G: precaução numérica
                        coord = sum(eigvec[j] * sum(centered[i][k] * eigvec[k]
                                   for k in range(dim)) for j in range(n))
                    pt.append(coord)
                else:
                    pt.append(0.0)
            projected.append(pt)

        return projected

    def _power_iteration(self, matrix: list[list[float]],
                         k: int, max_iter: int = 100) -> list[tuple[list[float], float]]:
        """
        Power iteration para extrair k autovetores/autovalores principais.
        Usa deflação para encontrar múltiplos autovetores.
        """
        n = len(matrix)
        eigenpairs = []

        # Cópia da matriz para deflação
        A = [row[:] for row in matrix]

        for _ in range(k):
            # Inicializar vetor aleatório determinístico
            v = [1.0 / math.sqrt(n)] * n

            # Power iteration
            for _ in range(max_iter):
                # Av = A * v
                Av = [sum(A[i][j] * v[j] for j in range(n)) for i in range(n)]

                # Normalizar
                norm = math.sqrt(sum(x * x for x in Av))
                if norm < 1e-10:
                    break
                v_new = [x / norm for x in Av]

                # Verificar convergência
                diff = math.sqrt(sum((v_new[i] - v[i]) ** 2 for i in range(n)))
                v = v_new
                if diff < 1e-6:
                    break

            # Calcular autovalor (Quociente de Rayleigh)
            Av = [sum(A[i][j] * v[j] for j in range(n)) for i in range(n)]
            eigval = sum(v[i] * Av[i] for i in range(n))

            eigenpairs.append((v, eigval))

            # Deflação: A = A - eigval * v * v^T
            for i in range(n):
                for j in range(n):
                    A[i][j] -= eigval * v[i] * v[j]

        return eigenpairs

    def _compute_topology_preservation(self, original: list[list[float]],
                                       projected: list[list[float]]) -> float:
        """
        Calcula a preservação topológica: correlação de Spearman
        entre distâncias originais e projetadas.
        """
        n = len(original)
        if n < 3:
            return 1.0

        # Distâncias originais e projetadas
        orig_dists = []
        proj_dists = []
        for i in range(n):
            for j in range(i + 1, n):
                od = math.sqrt(sum((a - b) ** 2 for a, b in zip(original[i], original[j])))
                pd = math.sqrt(sum((a - b) ** 2 for a, b in zip(projected[i], projected[j])))
                orig_dists.append(od)
                proj_dists.append(pd)

        if not orig_dists:
            return 1.0

        # Correlação de Pearson como aproximação
        n_dists = len(orig_dists)
        mean_od = sum(orig_dists) / n_dists
        mean_pd = sum(proj_dists) / n_dists

        num = sum((orig_dists[i] - mean_od) * (proj_dists[i] - mean_pd) for i in range(n_dists))
        den_od = math.sqrt(sum((orig_dists[i] - mean_od) ** 2 for i in range(n_dists)))
        den_pd = math.sqrt(sum((proj_dists[i] - mean_pd) ** 2 for i in range(n_dists)))

        if den_od * den_pd == 0:
            return 1.0

        correlation = num / (den_od * den_pd)
        return max(0.0, min(1.0, (correlation + 1) / 2))  # normalizar [0, 1]

    def _cluster_projected(self, projected: list[list[float]],
                           point_ids: list[str]) -> list[list[str]]:
        """Clusteriza pontos no espaço projetado (k-means simplificado)."""
        n = len(projected)
        if n < 2:
            return [[pid] for pid in point_ids]

        k = min(5, n // 2)

        # Inicializar centróides
        centroids = [projected[i] for i in range(k)]
        clusters = [[] for _ in range(k)]

        for _ in range(10):
            new_clusters = [[] for _ in range(k)]
            for idx, pt in enumerate(projected):
                dists = [math.sqrt(sum((pt[j] - c[j]) ** 2 for j in range(len(pt))))
                         for c in centroids]
                nearest = dists.index(min(dists))
                new_clusters[nearest].append(idx)

            # Atualizar centróides
            for c_idx in range(k):
                if new_clusters[c_idx]:
                    cluster_pts = [projected[i] for i in new_clusters[c_idx]]
                    centroids[c_idx] = [sum(dim) / len(dim) for dim in zip(*cluster_pts)]

            clusters = new_clusters

        return [[point_ids[i] for i in c] for c in clusters if c]

    # ─── Distância Epistemológica ─────────────────────────────────────────

    def compute_epistemic_distance(self, point_a: TopologicalPoint,
                                   point_b: TopologicalPoint) -> float:
        """
        Calcula a Distância Epistemológica (DE) entre dois pontos.
        Normalizada para [0, 1].
        """
        v1 = point_a.coordinates
        v2 = point_b.coordinates

        if not v1 or not v2:
            return 1.0

        # Alinhar tamanhos se necessário
        min_len = min(len(v1), len(v2))
        v1 = v1[:min_len]
        v2 = v2[:min_len]

        if min_len == 0:
            return 1.0

        raw = math.sqrt(sum((a - b) ** 2 for a, b in zip(v1, v2)))
        max_dist = math.sqrt(min_len)  # máximo possível
        return min(raw / max_dist, 1.0) if max_dist > 0 else 0.0

    # ─── Índice de Isolamento ────────────────────────────────────────────

    def compute_isolation_index(self, point_id: str) -> float | None:
        """
        Calcula o Índice de Isolamento (II) para um ponto específico.

        II = 1 - densidade_local / densidade_global
        Quanto maior o II, mais isolado o ponto.
        """
        point = self._points.get(point_id)
        if not point:
            return None

        if not self._projected_coords:
            return None

        # Coordenadas projetadas
        all_coords = list(self._projected_coords.values())
        target_coord = self._projected_coords.get(point_id)

        if not target_coord or len(all_coords) < 3:
            return None

        # Distância média para k vizinhos mais próximos
        k = min(5, len(all_coords) // 2)
        distances = []

        for pid, coord in self._projected_coords.items():
            if pid == point_id:
                continue
            d = math.sqrt(sum((a - b) ** 2 for a, b in zip(target_coord, coord)))
            distances.append(d)

        distances.sort()
        if not distances:
            return 0.0

        avg_k_dist = sum(distances[:k]) / k

        # Distância média global
        global_dists = []
        all_ids = list(self._projected_coords.keys())
        for i in range(len(all_ids)):
            for j in range(i + 1, len(all_ids)):
                c1 = self._projected_coords[all_ids[i]]
                c2 = self._projected_coords[all_ids[j]]
                d = math.sqrt(sum((a - b) ** 2 for a, b in zip(c1, c2)))
                global_dists.append(d)

        avg_global = sum(global_dists) / len(global_dists) if global_dists else 1.0

        # II normalizado
        if avg_global > 0:
            ii = min(avg_k_dist / avg_global, 1.0)
        else:
            ii = 0.0

        return ii

    def detect_islands(self) -> list[dict[str, Any]]:
        """
        Detecta ilhas epistemológicas (clusters com alto isolamento).
        """
        if not self._projected_coords or not self._clusters:
            return []

        islands = []
        for c_idx, cluster_ids in enumerate(self._clusters):
            # II médio do cluster
            ii_values = []
            for pid in cluster_ids:
                ii = self.compute_isolation_index(pid)
                if ii is not None:
                    ii_values.append(ii)

            if not ii_values:
                continue

            avg_ii = sum(ii_values) / len(ii_values)

            if avg_ii >= self.config["island_threshold"]:
                # Centróide do cluster
                coords = [self._projected_coords[pid] for pid in cluster_ids if pid in self._projected_coords]
                centroid = [sum(dim) / len(dim) for dim in zip(*coords)] if coords else []

                islands.append({
                    "island_id": f"island_{c_idx}",
                    "point_ids": cluster_ids,
                    "centroid": centroid,
                    "isolation_index": round(avg_ii, 4),
                    "size": len(cluster_ids),
                })

        return islands

    # ─── Buracos Epistemológicos ─────────────────────────────────────────

    def detect_holes(self) -> list[dict[str, Any]]:
        """
        Detecta buracos epistemológicos — zonas de vazio entre clusters.

        BE score = área_estimada * (1 - densidade)
        """
        if not self._projected_coords or len(self._clusters) < 2:
            return []

        holes = []

        # Para cada par de clusters, detectar buraco entre eles
        for i in range(len(self._clusters)):
            for j in range(i + 1, len(self._clusters)):
                # Pontos dos dois clusters
                points_i = [self._projected_coords[pid] for pid in self._clusters[i] if pid in self._projected_coords]
                points_j = [self._projected_coords[pid] for pid in self._clusters[j] if pid in self._projected_coords]

                if not points_i or not points_j:
                    continue

                # Centróides
                ci = [sum(dim) / len(dim) for dim in zip(*points_i)]
                cj = [sum(dim) / len(dim) for dim in zip(*points_j)]

                # Distância entre centróides
                d_centroid = math.sqrt(sum((a - b) ** 2 for a, b in zip(ci, cj)))

                # Raios aproximados (distância média ao centróide)
                ri = math.sqrt(sum(
                    math.sqrt(sum((pt[k] - ci[k]) ** 2 for k in range(len(pt))))
                    for pt in points_i
                )) / len(points_i) if points_i else 0.0

                rj = math.sqrt(sum(
                    math.sqrt(sum((pt[k] - cj[k]) ** 2 for k in range(len(pt))))
                    for pt in points_j
                )) / len(points_j) if points_j else 0.0

                # Gap entre clusters
                gap = max(0.0, d_centroid - ri - rj)

                if gap > 0:
                    # Densidade na região do gap
                    mid_point = [(ci[k] + cj[k]) / 2 for k in range(len(ci))]
                    density = self._estimate_density(mid_point, 0.5)

                    # BE = gap * (1 - density)
                    be_score = gap * (1.0 - density)

                    if be_score > 0.01:
                        holes.append({
                            "hole_id": f"hole_{i}_{j}",
                            "cluster_pair": [i, j],
                            "centroid": mid_point,
                            "radius": gap / 2,
                            "density": round(density, 4),
                            "gap": round(gap, 4),
                            "be_score": round(be_score, 4),
                            "bounding_points": self._clusters[i][:3] + self._clusters[j][:3],
                        })

        # Ordenar por BE score (maior primeiro)
        holes.sort(key=lambda h: h["be_score"], reverse=True)
        return holes

    def _estimate_density(self, point: list[float], radius: float) -> float:
        """
        Estima a densidade de pontos em torno de uma coordenada.
        """
        if not self._projected_coords:
            return 0.0

        count = 0
        for coord in self._projected_coords.values():
            d = math.sqrt(sum((a - b) ** 2 for a, b in zip(point, coord)))
            if d <= radius:
                count += 1

        total = len(self._projected_coords)
        return count / total if total > 0 else 0.0

    # ─── Potencial de Ponte ──────────────────────────────────────────────

    def compute_bridge_potential(self) -> list[dict[str, Any]]:
        """
        Calcula o Potencial de Ponte (PP) para todos os pontos.
        PP alto = ponto que conecta clusters diferentes.
        """
        if not self._projected_coords or len(self._clusters) < 2:
            return []

        bridges = []

        # Mapa: point_id -> cluster_id
        point_to_cluster: dict[str, int] = {}
        for c_idx, cluster_ids in enumerate(self._clusters):
            for pid in cluster_ids:
                point_to_cluster[pid] = c_idx

        for pid, coord in self._projected_coords.items():
            cluster_of_point = point_to_cluster.get(pid)

            # Distância para clusters diferentes
            inter_cluster_dists = []
            for other_pid, other_coord in self._projected_coords.items():
                if other_pid == pid:
                    continue
                other_cluster = point_to_cluster.get(other_pid)
                if other_cluster is not None and other_cluster != cluster_of_point:
                    d = math.sqrt(sum((a - b) ** 2 for a, b in zip(coord, other_coord)))
                    inter_cluster_dists.append((other_pid, other_cluster, d))

            if not inter_cluster_dists:
                continue

            # PP = 1 / (1 + distância_média_inter_cluster)
            avg_inter_dist = sum(d for _, _, d in inter_cluster_dists) / len(inter_cluster_dists)
            pp = 1.0 / (1.0 + avg_inter_dist) if avg_inter_dist > 0 else 0.0

            if pp >= self.config["bridge_pp_threshold"]:
                unique_clusters = set(c for _, c, _ in inter_cluster_dists)
                bridges.append({
                    "point_id": pid,
                    "pp_score": round(pp, 4),
                    "connected_clusters": list(unique_clusters),
                    "avg_inter_cluster_distance": round(avg_inter_dist, 4),
                })

        # Ordenar por PP (maior primeiro)
        bridges.sort(key=lambda b: b["pp_score"], reverse=True)
        return bridges

    # ─── Export ───────────────────────────────────────────────────────────

    def to_json(self, indent: int = 2) -> str:
        """Exporta o estado completo para JSON."""
        export = {
            "config": self.config,
            "n_points": len(self._points),
            "projection": self._last_projection,
            "n_clusters": len(self._clusters),
            "clusters": [{"cluster_id": i, "point_ids": c}
                         for i, c in enumerate(self._clusters)],
            "points": {
                pid: {
                    "coordinates": pt.coordinates,
                    "projected": pt.projected,
                    "label": pt.label,
                }
                for pid, pt in self._points.items()
            },
        }
        return json.dumps(export, indent=indent, default=str, ensure_ascii=False)

    def __repr__(self) -> str:
        return (f"EpistemicTopologyMapper("
                f"points={len(self._points)}, "
                f"clusters={len(self._clusters)})")
