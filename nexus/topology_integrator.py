#!/usr/bin/env python3
"""
Topology Integrator — Track 2 da SPEC-R44.

Mapeia a topologia epistêmica do ecossistema (ilhas, pontes, buracos)
e calcula o Rupture Potential Index (RPI) baseado nos artefatos
injetados pelo EpistemicInjector (Track 1).

Integracao: usa saída da topologia para guiar a injecao e vice-versa.
"""

import json
import math
from pathlib import Path
from typing import Optional

# Pontos epistemicos base do ecossistema
BASE_EPISTEMIC_POINTS = {
    "skills": {"x": 0.04, "y": -0.05},
    "mcps": {"x": 0.03, "y": -0.04},
    "specs": {"x": 0.02, "y": -0.06},
    "agentes": {"x": 0.06, "y": -0.03},
}


def _euclidean(p1: dict, p2: dict) -> float:
    """Distancia euclidiana entre dois pontos."""
    return math.sqrt((p1["x"] - p2["x"]) ** 2 + (p1["y"] - p2["y"]) ** 2)


def _load_artifacts(artifacts_dir: str) -> list[dict]:
    """Carrega artefatos do diretorio de persistencia."""
    apath = Path(artifacts_dir)
    artifacts = []
    if apath.exists():
        for fpath in sorted(apath.glob("*.json")):
            try:
                artifacts.append(json.loads(fpath.read_text()))
            except (json.JSONDecodeError, OSError):
                continue
    return artifacts


def scan_topology(artifacts_dir: str = "nexus/artifacts") -> dict:
    """Escaneia a topologia epistêmica do ecossistema.

    Retorna dicionario com:
    - num_points: total de pontos
    - islands: ilhas epistemicas (grupos isolados)
    - bridge_potential: potencial de ponte de cada ponto
    - holes: buracos topologicos
    """
    artifacts = _load_artifacts(artifacts_dir)

    # Construir mapa de pontos baseado nos artefatos
    points = dict(BASE_EPISTEMIC_POINTS)

    # Adicionar pontos derivados dos artefatos por dimensao
    dim_coords = {
        "dominios": (0.10, -0.10),
        "metodos": (0.08, -0.08),
        "paradigmas": (0.12, -0.06),
        "raciocinio": (0.06, -0.10),
        "dados": (0.14, -0.04),
        "niveis_analise": (0.04, -0.12),
        "temporalidade": (0.16, -0.02),
        "populacao": (0.02, -0.14),
        "teorias": (0.18, 0.00),
        "teoria_jogos": (0.00, -0.16),
    }

    dim_count = {}
    for art in artifacts:
        dim = art.get("dimension", "unknown")
        dim_count[dim] = dim_count.get(dim, 0) + 1

    for dim, coord in dim_coords.items():
        if dim in dim_count and dim_count[dim] > 0:
            # Deslocar ligeiramente baseado na quantidade de artefatos
            offset = min(dim_count[dim] * 0.002, 0.05)
            points[f"art_{dim}"] = {
                "x": coord[0] + offset,
                "y": coord[1] - offset * 0.5,
            }

    # Identificar ilhas (clusters isolados por distancia)
    point_ids = list(points.keys())
    island_assignment: dict[str, int] = {}
    cluster_id = 0

    for pid in point_ids:
        if pid in island_assignment:
            continue
        # Encontrar pontos proximos (distancia < 0.15)
        cluster_points = [pid]
        island_assignment[pid] = cluster_id
        for other in point_ids:
            if other not in island_assignment:
                dist = _euclidean(points[pid], points[other])
                if dist < 0.15:
                    island_assignment[other] = cluster_id
                    cluster_points.append(other)
        cluster_id += 1

    # Agrupar por cluster
    clusters: dict[int, list[str]] = {}
    for pid, cid in island_assignment.items():
        if cid not in clusters:
            clusters[cid] = []
        clusters[cid].append(pid)

    # Calcular centros dos clusters
    cluster_centers = {}
    for cid, members in clusters.items():
        xs = [points[m]["x"] for m in members]
        ys = [points[m]["y"] for m in members]
        cluster_centers[cid] = {
            "x": sum(xs) / len(xs),
            "y": sum(ys) / len(ys),
        }

    # Identificar ilhas
    islands = []

    if len(clusters) <= 1:
        # Cluster unico = ecossistema integrado (sem ilhas)
        pass
    else:
        for cid, members in clusters.items():
            if len(members) <= 1:
                continue
            centroid = cluster_centers[cid]
            distances_to_others = []
            for other_cid, other_center in cluster_centers.items():
                if other_cid != cid:
                    distances_to_others.append(
                        _euclidean(centroid, other_center)
                    )
            isolation = 0.5  # default moderate
            if distances_to_others:
                min_dist = min(distances_to_others)
                isolation = round(1.0 - min(min_dist / 0.5, 1.0), 4)

            islands.append({
                "island_id": f"island_{cid}",
                "point_ids": members,
                "centroid": [centroid["x"], centroid["y"]],
                "isolation_index": isolation,
                "size": len(members),
            })

    # Calcular bridge potential (por ponto individual, nao por cluster)
    bridge_potential = []
    # Usar todos os pontos base + derivados como candidatos a ponte
    all_candidates = list(BASE_EPISTEMIC_POINTS.keys()) + [
        f"art_{dim}" for dim in dim_coords
    ]

    for pid in all_candidates:
        if pid not in points:
            continue
        p = points[pid]
        connections = 0
        total_dist = 0
        connected_to = []
        for other_pid, other_p in points.items():
            if other_pid != pid:
                dist = _euclidean(p, other_p)
                if dist < 0.30:
                    connections += 1
                    connected_to.append(other_pid)
                    total_dist += dist

        # Bridge potential: centralidade no grafo
        # Quanto mais pontos proximos, maior o potencial de ponte
        if connections > 0:
            avg_dist = total_dist / connections
            # Normalizar: max connections = len(points)-1
            conn_ratio = connections / max(len(points) - 1, 1)
            # Dist: 0 = perfeito, 0.30 = medio
            dist_factor = 1.0 - min(avg_dist / 0.30, 1.0)
            pp_score = round(0.6 * conn_ratio + 0.4 * dist_factor, 4)
        else:
            pp_score = 0.0

        bridge_potential.append({
            "point_id": pid,
            "pp_score": pp_score,
            "connected_clusters": list(set(
                island_assignment.get(op, -1)
                for op in connected_to
            )) if connected_to else [],
            "avg_inter_cluster_distance": round(
                total_dist / max(connections, 1), 4
            ),
        })

    # Ordenar por pp_score descendente
    bridge_potential.sort(key=lambda b: b["pp_score"], reverse=True)

    # Identificar buracos (regioes com baixa densidade de pontos)
    holes = []
    if points:
        xs = [p["x"] for p in points.values()]
        ys = [p["y"] for p in points.values()]
        x_min, x_max = min(xs), max(xs)
        y_min, y_max = min(ys), max(ys)
        # Grid 3x3 para detectar celulas vazias
        for i in range(3):
            for j in range(3):
                x_start = x_min + (x_max - x_min) * i / 3
                x_end = x_min + (x_max - x_min) * (i + 1) / 3
                y_start = y_min + (y_max - y_min) * j / 3
                y_end = y_min + (y_max - y_min) * (j + 1) / 3
                count = sum(
                    1 for p in points.values()
                    if x_start <= p["x"] <= x_end and y_start <= p["y"] <= y_end
                )
                if count == 0:
                    holes.append({
                        "region": [
                            round(x_start, 4), round(y_start, 4),
                            round(x_end, 4), round(y_end, 4),
                        ],
                        "severity": "low",
                    })

    return {
        "num_points": len(points),
        "islands": islands,
        "bridge_potential": sorted(
            bridge_potential, key=lambda b: b["pp_score"], reverse=True
        ),
        "holes": holes,
        "num_clusters": len(clusters),
        "artifacts_loaded": len(artifacts),
    }


def calculate_rpi(artifacts_dir: str = "nexus/artifacts") -> float:
    """Calcula Rupture Potential Index (RPI) baseado nos artefatos.

    RPI = 0-100, onde:
    - < 30: rotina (baixo potencial de ruptura)
    - 30-50: melhoria incremental
    - 50-70: ruptura segura
    - > 70: ruptura especulativa

    O RPI leva em conta:
    1. Diversidade de dimensoes cobertas
    2. EPS medio dos artefatos
    3. Numero de clusters topologicos
    4. Bridge potential medio
    """
    artifacts = _load_artifacts(artifacts_dir)
    if not artifacts:
        return 40.5  # baseline do scanner

    # 1. Diversidade de dimensoes (0-25 pontos)
    dims = set(a.get("dimension", "") for a in artifacts)
    dim_diversity = min(len(dims) / 10.0, 1.0) * 25

    # 2. EPS medio (0-35 pontos)
    eps_scores = [a.get("eps_score", 50.0) for a in artifacts]
    avg_eps = sum(eps_scores) / len(eps_scores)
    eps_component = (avg_eps / 100.0) * 35

    # 3. Bridge potential medio (0-25 pontos)
    topology = scan_topology(artifacts_dir)
    bridges = topology.get("bridge_potential", [])
    avg_bridge = (
        sum(b.get("pp_score", 0) for b in bridges) / max(len(bridges), 1)
    )
    bridge_component = avg_bridge * 25

    # 4. Taxa de inovacao (0-15 pontos)
    # Quanto mais categorias unicas por dimensao, maior
    cats_by_dim: dict[str, set] = {}
    for a in artifacts:
        dim = a.get("dimension", "")
        cat = a.get("category", "")
        if dim not in cats_by_dim:
            cats_by_dim[dim] = set()
        cats_by_dim[dim].add(cat)
    avg_cats_per_dim = sum(len(c) for c in cats_by_dim.values()) / max(
        len(cats_by_dim), 1
    )
    innovation_rate = min(avg_cats_per_dim / 5.0, 1.0) * 15

    rpi = round(dim_diversity + eps_component + bridge_component + innovation_rate, 1)
    return min(rpi, 100.0)


def get_quadrant(rpi: float) -> str:
    """Retorna o quadrante do portfólio EPS x RPI."""
    if rpi < 30:
        return "rotina"
    elif rpi < 50:
        return "melhoria_incremental"
    elif rpi < 70:
        return "ruptura_segura"
    else:
        return "ruptura_especulativa"


class TopologyIntegrator:
    """Integrador de topologia que combina Track 1 (injection) e Track 2 (topology).

    Fornece uma interface unificada para:
    - Escaneamento topologico
    - Calculo de RPI
    - Recomendacoes de injecao baseadas na topologia
    """

    def __init__(self, artifacts_dir: str = "nexus/artifacts"):
        self.artifacts_dir = artifacts_dir

    def scan(self) -> dict:
        """Escaneia a topologia."""
        return scan_topology(artifacts_dir=self.artifacts_dir)

    def get_rpi(self) -> float:
        """Calcula o RPI atual."""
        return calculate_rpi(artifacts_dir=self.artifacts_dir)

    def get_recommendations(self) -> list[dict]:
        """Recomenda acoes baseadas na topologia."""
        topology = self.scan()
        recs = []

        # Recomendar conexao de ilhas
        for island in topology.get("islands", []):
            if island.get("isolation_index", 0) > 0.5:
                recs.append({
                    "type": "connect_island",
                    "target": island["island_id"],
                    "reason": f"Island with isolation {island['isolation_index']:.2f}",
                    "suggested_bridge": max(
                        topology.get("bridge_potential", []),
                        key=lambda b: b.get("pp_score", 0),
                        default={},
                    ).get("point_id", "skills"),
                })

        # Recomendar preenchimento de buracos
        for hole in topology.get("holes", []):
            recs.append({
                "type": "fill_hole",
                "region": hole["region"],
                "reason": "Empty region in epistemic space",
            })

        # Recomendar fortalecimento de pontes fracas
        for bp in topology.get("bridge_potential", []):
            if bp.get("pp_score", 0) < 0.6:
                recs.append({
                    "type": "strengthen_bridge",
                    "target": bp["point_id"],
                    "current_score": bp["pp_score"],
                    "reason": f"Bridge potential below 0.6 ({bp['pp_score']:.2f})",
                })

        return recs


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Topology Integrator — R44")
    parser.add_argument("--scan", action="store_true", help="Escaneiar topologia")
    parser.add_argument("--rpi", action="store_true", help="Calcular RPI")
    parser.add_argument("--dir", default="nexus/artifacts",
                        help="Diretorio de artefatos")
    args = parser.parse_args()

    if args.scan:
        result = scan_topology(artifacts_dir=args.dir)
        print(f"=== Topology Scan ===")
        print(f"Points: {result['num_points']}")
        print(f"Clusters: {result['num_clusters']}")
        print(f"Islands: {len(result['islands'])}")
        for island in result['islands']:
            print(f"  {island['island_id']}: isolation={island['isolation_index']}, "
                  f"size={island['size']}")
        print(f"Bridges:")
        for bp in result['bridge_potential']:
            print(f"  {bp['point_id']}: pp_score={bp['pp_score']}, "
                  f"connects_to={bp['connected_clusters']}")
        print(f"Holes: {len(result['holes'])}")
        print(f"Artifacts loaded: {result['artifacts_loaded']}")

    if args.rpi:
        rpi = calculate_rpi(artifacts_dir=args.dir)
        quadrant = get_quadrant(rpi)
        print(f"RPI: {rpi} — {quadrant}")
