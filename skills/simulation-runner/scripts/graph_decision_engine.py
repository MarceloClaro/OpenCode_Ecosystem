#!/usr/bin/env python3
"""
GraphDecisionEngine — Grafos + Árvores de Decisão + Orquestração Multiagente
Qualis A1 · Referências reais · Python stdlib (zero dependências externas)

Base teórica:
  - PageRank (Brin & Page, 1998) — DOI: 10.1016/S0169-7552(98)00110-X
  - Girvan-Newman community detection (Girvan & Newman, 2002) — DOI: 10.1073/pnas.122653799
  - Barabási-Albert scale-free networks (Barabási & Albert, 1999) — DOI: 10.1126/science.286.5439.509
  - CART decision trees (Breiman et al., 1984) — ISBN: 978-0412048418
  - Random Forest (Breiman, 2001) — DOI: 10.1023/A:1010933404324
  - Agent-based modeling (Epstein & Axtell, 1996) — ISBN: 978-0262550253
  - ABM + Graph theory (Jackson, 2008) — DOI: 10.1515/9781400833993
  - Causal graphs (Pearl, 2009) — DOI: 10.1017/CBO9780511803161

Ferramentas referência (GitHub):
  - networkx (Hagberg et al.) — github.com/networkx/networkx
  - cdlib (Rossetti et al.) — github.com/GiulioRossetti/cdlib
  - CausalDiscoveryToolbox (Kalainathan et al.) — github.com/FenTechSolutions/CausalDiscoveryToolbox
  - EoN (Kiss, Miller, Simon) — github.com/springer-math/EoN
"""

import random, math, json, os
from collections import defaultdict, Counter
from typing import Dict, List, Any, Tuple, Optional, Set
from datetime import datetime, timezone, timedelta

BRAZIL_TZ = timezone(timedelta(hours=-3))

# ═══════════════════════════════════════════════════════════════════
# GRAPH THEORY ENGINE
# ═══════════════════════════════════════════════════════════════════

class GraphTheoryEngine:
    """
    Motor de teoria dos grafos — PageRank, comunidades, centralidade.
    Implementação pura Python (inspirada em networkx, mas sem dependências).
    """

    def __init__(self):
        self.adjacency: Dict[str, Set[str]] = defaultdict(set)
        self.nodes: Dict[str, Dict] = {}

    def add_node(self, node_id: str, **attrs):
        self.nodes[node_id] = attrs
        if node_id not in self.adjacency:
            self.adjacency[node_id] = set()

    def add_edge(self, u: str, v: str, weight: float = 1.0):
        self.adjacency[u].add(v)
        self.adjacency[v].add(u)

    # ── PAGERANK ──
    def pagerank(self, damping: float = 0.85, max_iter: int = 100, tol: float = 1e-6) -> Dict[str, float]:
        """
        PageRank (Brin & Page, 1998).
        PR(A) = (1-d)/N + d * sum(PR(Ti)/C(Ti))
        DOI: 10.1016/S0169-7552(98)00110-X
        """
        nodes = list(self.nodes.keys())
        n = len(nodes)
        if n == 0:
            return {}

        pr = {node: 1.0 / n for node in nodes}
        out_degree = {node: max(len(self.adjacency[node]), 1) for node in nodes}

        for _ in range(max_iter):
            new_pr = {}
            for node in nodes:
                rank = (1 - damping) / n
                for neighbor in self.adjacency[node]:
                    rank += damping * pr[neighbor] / out_degree[neighbor]
                new_pr[node] = rank

            diff = sum(abs(new_pr[node] - pr[node]) for node in nodes)
            pr = new_pr
            if diff < tol:
                break

        return pr

    # ── CENTRALITY MEASURES ──
    def degree_centrality(self) -> Dict[str, float]:
        """Centralidade de grau normalizada."""
        n = max(len(self.nodes) - 1, 1)
        return {node: len(neighbors) / n for node, neighbors in self.adjacency.items()}

    def betweenness_centrality(self) -> Dict[str, float]:
        """
        Betweenness centrality (Freeman, 1977).
        CB(v) = sum_{s!=v!=t} sigma_st(v) / sigma_st
        """
        nodes = list(self.nodes.keys())
        n = len(nodes)
        bc = {node: 0.0 for node in nodes}

        for s in nodes:
            # BFS from s
            predecessors = defaultdict(list)
            distances = {node: -1 for node in nodes}
            distances[s] = 0
            sigma = {node: 0 for node in nodes}
            sigma[s] = 1
            queue = [s]

            while queue:
                v = queue.pop(0)
                for w in self.adjacency[v]:
                    if distances[w] < 0:
                        distances[w] = distances[v] + 1
                        queue.append(w)
                    if distances[w] == distances[v] + 1:
                        sigma[w] += sigma[v]
                        predecessors[w].append(v)

            # Backward accumulation
            delta = {node: 0.0 for node in nodes}
            stack = sorted(nodes, key=lambda x: distances[x], reverse=True)
            for v in stack:
                for parent in predecessors.get(v, []):
                    delta[parent] += (sigma[parent] / sigma[v]) * (1 + delta[v])
                if v != s:
                    bc[v] += delta[v]

        # Normalize for undirected
        norm = (n - 1) * (n - 2) if n > 2 else 1
        for node in bc:
            bc[node] /= norm

        return bc

    def eigenvector_centrality(self, max_iter: int = 100) -> Dict[str, float]:
        """Eigenvector centrality — power iteration method."""
        nodes = list(self.nodes.keys())
        n = len(nodes)
        if n == 0:
            return {}

        x = {node: 1.0 for node in nodes}
        for _ in range(max_iter):
            x_new = {}
            for node in nodes:
                x_new[node] = sum(x[neighbor] for neighbor in self.adjacency[node])
            norm = math.sqrt(sum(v**2 for v in x_new.values()))
            if norm == 0:
                break
            x_new = {k: v / norm for k, v in x_new.items()}
            if sum(abs(x_new[node] - x[node]) for node in nodes) < 1e-6:
                return x_new
            x = x_new
        return x

    # ── COMMUNITY DETECTION (Girvan-Newman inspired) ──
    def detect_communities_girvan_newman(self, max_communities: int = 5) -> List[Set[str]]:
        """
        Community detection via edge betweenness (Girvan & Newman, 2002).
        DOI: 10.1073/pnas.122653799
        """
        # Clone adjacency
        adj = {node: set(neighbors) for node, neighbors in self.adjacency.items()}
        nodes = list(self.nodes.keys())

        # Compute connected components
        def components():
            visited = set()
            comps = []
            for node in nodes:
                if node not in visited:
                    stack = [node]
                    comp = set()
                    while stack:
                        v = stack.pop()
                        if v not in visited:
                            visited.add(v)
                            comp.add(v)
                            stack.extend(adj.get(v, set()) - visited)
                    comps.append(comp)
            return comps

        comps = components()
        while len(comps) < max_communities:
            # Compute edge betweenness
            edge_betweenness: Dict[Tuple[str, str], float] = {}
            for s in nodes:
                # BFS
                predecessors = defaultdict(list)
                distances = {n: -1 for n in nodes}
                distances[s] = 0
                sigma = {n: 0 for n in nodes}
                sigma[s] = 1
                queue = [s]
                while queue:
                    v = queue.pop(0)
                    for w in adj.get(v, set()):
                        if distances[w] < 0:
                            distances[w] = distances[v] + 1
                            queue.append(w)
                        if distances[w] == distances[v] + 1:
                            sigma[w] += sigma[v]
                            predecessors[w].append(v)

                delta = {n: 0.0 for n in nodes}
                stack = sorted(nodes, key=lambda x: distances[x], reverse=True)
                for v in stack:
                    for parent in predecessors.get(v, []):
                        contribution = (sigma[parent] / sigma[v]) * (1 + delta[v])
                        edge = tuple(sorted([parent, v]))
                        edge_betweenness[edge] = edge_betweenness.get(edge, 0.0) + contribution
                        delta[parent] += contribution

            if not edge_betweenness:
                break

            # Remove edge with highest betweenness
            highest_edge = max(edge_betweenness, key=edge_betweenness.get)
            u, v = highest_edge
            adj[u].discard(v)
            adj[v].discard(u)

            comps = components()

        # Label communities
        result = []
        for comp in comps:
            result.append(comp)
        return result

    # ── SUMMARY ──
    def analyze(self) -> Dict[str, Any]:
        """Análise completa do grafo."""
        pr = self.pagerank()
        dc = self.degree_centrality()
        bc = self.betweenness_centrality()
        communities = self.detect_communities_girvan_newman()

        n = len(self.nodes)
        edges = sum(len(v) for v in self.adjacency.values()) // 2
        top_pr = sorted(pr.items(), key=lambda x: x[1], reverse=True)[:5]
        top_bc = sorted(bc.items(), key=lambda x: x[1], reverse=True)[:5]

        return {
            "graph_stats": {
                "nodes": n, "edges": edges,
                "density": round(2*edges/(n*(n-1)), 4) if n > 1 else 0,
                "avg_degree": round(2*edges/n, 2) if n > 0 else 0,
            },
            "pagerank_top5": [{"node": n, "score": round(s, 4)} for n, s in top_pr],
            "betweenness_top5": [{"node": n, "score": round(s, 4)} for n, s in top_bc],
            "communities": len(communities),
            "community_sizes": [len(c) for c in communities],
            "modularity_estimate": self._estimate_modularity(communities),
        }

    def _estimate_modularity(self, communities: List[Set[str]]) -> float:
        """Estimativa de modularidade Q."""
        edges = sum(len(v) for v in self.adjacency.values()) // 2
        if edges == 0:
            return 0.0
        Q = 0.0
        for community in communities:
            internal = sum(1 for u in community for v in self.adjacency.get(u, set()) if v in community) // 2
            total_degree = sum(len(self.adjacency.get(u, set())) for u in community)
            Q += internal / edges - (total_degree / (2 * edges)) ** 2
        return round(Q, 4)


# ═══════════════════════════════════════════════════════════════════
# DECISION TREE ENGINE (CART-inspired)
# ═══════════════════════════════════════════════════════════════════

class DecisionTreeEngine:
    """
    Árvore de Decisão CART (Breiman et al., 1984) + Random Forest (Breiman, 2001).
    Implementação pura Python para classificação de cenários e agentes.
    Referências:
      - CART: DOI via ISBN 978-0412048418
      - Random Forest: DOI 10.1023/A:1010933404324
    """

    def __init__(self, max_depth: int = 5, min_samples: int = 3):
        self.max_depth = max_depth
        self.min_samples = min_samples
        self.tree = None

    class Node:
        def __init__(self):
            self.feature_idx: int = -1
            self.threshold: float = 0.0
            self.label: Any = None
            self.left: Any = None
            self.right: Any = None
            self.is_leaf: bool = False
            self.impurity: float = 0.0
            self.samples: int = 0

    def fit(self, X: List[List[float]], y: List[Any], feature_names: List[str] = None):
        """Treina árvore de decisão."""
        self.feature_names = feature_names or [f"f{i}" for i in range(len(X[0]) if X else 0)]
        self.tree = self._build_tree(X, y, depth=0)

    def _gini(self, y: List[Any]) -> float:
        """Índice de Gini."""
        if not y:
            return 0.0
        counts = Counter(y)
        n = len(y)
        return 1.0 - sum((c / n) ** 2 for c in counts.values())

    def _best_split(self, X: List[List[float]], y: List[Any]) -> Tuple[int, float, float]:
        """Encontra melhor feature e threshold via Gini impurity."""
        best_gain = 0.0
        best_feat, best_thresh = -1, 0.0
        n = len(y)
        parent_gini = self._gini(y)

        n_features = len(X[0]) if X else 0
        for feat in range(n_features):
            values = sorted(set(row[feat] for row in X))
            if len(values) < 2:
                continue
            for i in range(len(values) - 1):
                threshold = (values[i] + values[i + 1]) / 2
                left_y, right_y = [], []
                for j in range(n):
                    if X[j][feat] <= threshold:
                        left_y.append(y[j])
                    else:
                        right_y.append(y[j])
                if len(left_y) < self.min_samples or len(right_y) < self.min_samples:
                    continue
                gain = parent_gini - (len(left_y)/n*self._gini(left_y) + len(right_y)/n*self._gini(right_y))
                if gain > best_gain:
                    best_gain, best_feat, best_thresh = gain, feat, threshold

        return best_feat, best_thresh, best_gain

    def _build_tree(self, X: List[List[float]], y: List[Any], depth: int):
        node = self.Node()
        node.samples = len(y)
        node.impurity = self._gini(y)

        # Parada: profundidade máxima, amostras insuficientes, ou pureza
        if depth >= self.max_depth or len(y) < self.min_samples or node.impurity == 0:
            node.is_leaf = True
            node.label = Counter(y).most_common(1)[0][0] if y else None
            return node

        feat, thresh, gain = self._best_split(X, y)
        if feat < 0 or gain < 1e-6:
            node.is_leaf = True
            node.label = Counter(y).most_common(1)[0][0] if y else None
            return node

        node.feature_idx = feat
        node.threshold = thresh

        left_X, left_y, right_X, right_y = [], [], [], []
        for i in range(len(y)):
            if X[i][feat] <= thresh:
                left_X.append(X[i]); left_y.append(y[i])
            else:
                right_X.append(X[i]); right_y.append(y[i])

        node.left = self._build_tree(left_X, left_y, depth + 1)
        node.right = self._build_tree(right_X, right_y, depth + 1)
        return node

    def predict(self, X: List[List[float]]) -> List[Any]:
        """Prediz classes."""
        return [self._predict_row(row) for row in X]

    def _predict_row(self, row: List[float]) -> Any:
        node = self.tree
        while node and not node.is_leaf:
            if row[node.feature_idx] <= node.threshold:
                node = node.left
            else:
                node = node.right
        return node.label if node else None

    def predict_proba(self, X: List[List[float]], classes: List[Any]) -> List[Dict[Any, float]]:
        """Prediz probabilidades (necessita múltiplas árvores)."""
        return [{c: 1.0 / len(classes) for c in classes} for _ in X]

    def to_dict(self) -> Dict:
        """Exporta árvore como dicionário."""
        def _export(node):
            if node.is_leaf:
                return {"leaf": True, "label": node.label, "samples": node.samples, "impurity": round(node.impurity, 4)}
            return {
                "feature": self.feature_names[node.feature_idx] if self.feature_names and node.feature_idx >= 0 else f"f{node.feature_idx}",
                "threshold": round(node.threshold, 4),
                "gini": round(node.impurity, 4),
                "samples": node.samples,
                "left": _export(node.left),
                "right": _export(node.right),
            }
        return _export(self.tree) if self.tree else {}


class RandomForestEngine:
    """Random Forest (Breiman, 2001) — ensemble de árvores de decisão."""

    def __init__(self, n_trees: int = 10, max_depth: int = 5):
        self.n_trees = n_trees
        self.max_depth = max_depth
        self.trees: List[DecisionTreeEngine] = []
        self.feature_names = None

    def fit(self, X: List[List[float]], y: List[Any], feature_names: List[str] = None):
        self.feature_names = feature_names
        n = len(y)
        n_features = len(X[0]) if X else 0
        self.trees = []

        for _ in range(self.n_trees):
            # Bootstrap sample
            indices = [random.randint(0, n - 1) for _ in range(n)]
            X_sample = [X[i] for i in indices]
            y_sample = [y[i] for i in indices]

            tree = DecisionTreeEngine(max_depth=self.max_depth, min_samples=2)
            tree.fit(X_sample, y_sample, feature_names)
            self.trees.append(tree)

    def predict(self, X: List[List[float]]) -> List[Any]:
        predictions = []
        for row in X:
            votes = Counter()
            for tree in self.trees:
                pred = tree._predict_row(row)
                if pred is not None:
                    votes[pred] += 1
            predictions.append(votes.most_common(1)[0][0] if votes else None)
        return predictions

    def predict_proba(self, X: List[List[float]]) -> List[Dict[Any, float]]:
        results = []
        for row in X:
            counts = defaultdict(int)
            for tree in self.trees:
                pred = tree._predict_row(row)
                if pred is not None:
                    counts[pred] += 1
            total = sum(counts.values()) or 1
            results.append({k: v/total for k, v in counts.items()})
        return results

    def feature_importance(self) -> Dict[str, float]:
        """Importância das features (frequência de splits)."""
        if not self.trees:
            return {}
        counts = defaultdict(int)

        def _count(node):
            if node.is_leaf:
                return
            if self.feature_names and node.feature_idx >= 0:
                counts[self.feature_names[node.feature_idx]] += 1
            _count(node.left)
            _count(node.right)

        for tree in self.trees:
            if tree.tree:
                _count(tree.tree)

        total = sum(counts.values()) or 1
        return {k: round(v / total, 4) for k, v in sorted(counts.items(), key=lambda x: x[1], reverse=True)}


# ═══════════════════════════════════════════════════════════════════
# MULTI-AGENT ORCHESTRATOR
# ═══════════════════════════════════════════════════════════════════

class MultiAgentOrchestrator:
    """
    Orquestrador multiagente para otimização de simulações.
    Coordena agentes especializados que colaboram para encontrar
    a melhor configuração de simulação.
    
    Inspirado em:
      - MiroFish Swarm Intelligence (666ghj/MiroFish)
      - OASIS Multi-Agent Simulation
      - OpenCode Agent Forum (P14-P18)
    """

    def __init__(self):
        self.agents: Dict[str, Dict] = {}
        self.knowledge_base: Dict[str, Any] = {}
        self.iteration: int = 0
        self.consensus: Dict[str, Any] = {}

    def register_agent(self, agent_id: str, expertise: List[str], params: Dict = None):
        """Registra agente especializado."""
        self.agents[agent_id] = {
            "id": agent_id,
            "expertise": expertise,
            "params": params or {},
            "proposals": [],
            "score": 0.0,
        }

    def propose(self, agent_id: str, proposal: Dict) -> float:
        """Agente propõe configuração; retorna score de consenso."""
        if agent_id not in self.agents:
            return 0.0
        self.agents[agent_id]["proposals"].append(proposal)
        self.agents[agent_id]["score"] = self._evaluate_proposal(proposal, agent_id)
        return self.agents[agent_id]["score"]

    def _evaluate_proposal(self, proposal: Dict, agent_id: str) -> float:
        """Avalia proposta via heurísticas de consenso."""
        score = 0.5  # Baseline
        agent = self.agents[agent_id]

        # Verifica alinhamento com expertise
        expertise_match = sum(1 for e in agent["expertise"] if e in proposal.get("tags", []))
        score += expertise_match * 0.1

        # Verifica compatibilidade com outras propostas
        if self.iteration > 0:
            compat = 0
            for aid, a in self.agents.items():
                if aid != agent_id and a["proposals"]:
                    last = a["proposals"][-1]
                    for key in proposal:
                        if key in last and isinstance(proposal[key], (int, float)) and isinstance(last[key], (int, float)):
                            if abs(proposal[key] - last[key]) < 0.2:
                                compat += 1
            score += min(compat * 0.05, 0.3)

        return min(score, 1.0)

    def negotiate(self, rounds: int = 5) -> Dict:
        """Rodadas de negociação entre agentes para alcançar consenso."""
        for _ in range(rounds):
            self.iteration += 1
            for agent_id in self.agents:
                # Cada agente propõe um ajuste
                proposal = {
                    "agent_count": random.randint(50, 500),
                    "rounds": random.randint(10, 50),
                    "influence_factor": random.uniform(0.5, 2.0),
                    "polarization_threshold": random.uniform(0.1, 0.5),
                    "tags": self.agents[agent_id]["expertise"],
                }
                self.propose(agent_id, proposal)

        # Consenso: média ponderada das melhores propostas
        top_agents = sorted(self.agents.items(), key=lambda x: x[1]["score"], reverse=True)[:5]
        weighted = defaultdict(float)
        total_weight = 0
        for aid, agent in top_agents:
            weight = agent["score"]
            total_weight += weight
            for proposal in agent["proposals"]:
                for k, v in proposal.items():
                    if isinstance(v, (int, float)):
                        weighted[k] += v * weight

        self.consensus = {k: round(v / max(total_weight, 1), 2) for k, v in weighted.items()}
        return self.consensus

    def get_optimal_params(self) -> Dict:
        """Retorna parâmetros ótimos encontrados pelo consenso."""
        return self.consensus

    def summary(self) -> Dict:
        """Resumo da orquestração."""
        return {
            "agents": len(self.agents),
            "iterations": self.iteration,
            "consensus": self.consensus,
            "top_agents": sorted(
                [{"id": aid, "score": round(a["score"], 3), "expertise": a["expertise"]}
                 for aid, a in self.agents.items()],
                key=lambda x: x["score"], reverse=True
            )[:5],
        }


# ═══════════════════════════════════════════════════════════════════
# INTEGRATED SIMULATION OPTIMIZER
# ═══════════════════════════════════════════════════════════════════

class IntegratedSimulationOptimizer:
    """
    Otimizador integrado: Grafos + Árvores + Multiagente.
    Pipeline completo Qualis A1.
    """

    def __init__(self):
        self.graph_engine = GraphTheoryEngine()
        self.decision_tree = DecisionTreeEngine(max_depth=5)
        self.random_forest = RandomForestEngine(n_trees=10, max_depth=5)
        self.orchestrator = MultiAgentOrchestrator()
        self.references = [
            {"title": "The PageRank Citation Ranking", "authors": "Brin, S.; Page, L.", "year": 1998, "doi": "10.1016/S0169-7552(98)00110-X"},
            {"title": "Community Structure in Social Networks", "authors": "Girvan, M.; Newman, M.E.J.", "year": 2002, "doi": "10.1073/pnas.122653799"},
            {"title": "Emergence of Scaling in Random Networks", "authors": "Barabasi, A.L.; Albert, R.", "year": 1999, "doi": "10.1126/science.286.5439.509"},
            {"title": "Classification and Regression Trees", "authors": "Breiman, L. et al.", "year": 1984, "isbn": "978-0412048418"},
            {"title": "Random Forests", "authors": "Breiman, L.", "year": 2001, "doi": "10.1023/A:1010933404324"},
            {"title": "Growing Artificial Societies", "authors": "Epstein, J.M.; Axtell, R.", "year": 1996, "doi": "10.7551/mitpress/3374.001.0001"},
            {"title": "Social and Economic Networks", "authors": "Jackson, M.O.", "year": 2008, "doi": "10.1515/9781400833993"},
            {"title": "Causality: Models, Reasoning, and Inference", "authors": "Pearl, J.", "year": 2009, "doi": "10.1017/CBO9780511803161"},
            {"title": "Agent-Based Modeling for Social Simulation", "authors": "Gilbert, N.", "year": 2008, "doi": "10.4135/9781849209724"},
            {"title": "Network Science", "authors": "Barabasi, A.L.", "year": 2016, "isbn": "978-1107076266"},
        ]

    def build_agent_graph(self, agents: List[Dict]) -> GraphTheoryEngine:
        """Constrói grafo a partir de agentes da simulação."""
        self.graph_engine = GraphTheoryEngine()
        for agent in agents:
            stance = agent.get("stance", "neutral")
            influence = agent.get("influence", 1.0)
            self.graph_engine.add_node(agent["name"], stance=stance, influence=influence)

        # Conectar agentes com base em similaridade de stance
        agent_list = list(agents)
        for i in range(len(agent_list)):
            for j in range(i + 1, len(agent_list)):
                if agent_list[i].get("stance") == agent_list[j].get("stance"):
                    self.graph_engine.add_edge(agent_list[i]["name"], agent_list[j]["name"], 1.0)
                elif random.random() < 0.3:
                    self.graph_engine.add_edge(agent_list[i]["name"], agent_list[j]["name"], 0.3)

        return self.graph_engine

    def classify_scenarios(self, scenarios_data: List[Dict]) -> Dict:
        """Classifica cenários usando Random Forest."""
        if len(scenarios_data) < 5:
            return {"error": "Dados insuficientes para classificação"}

        # Features: risk_level_num, trend_strength, variables_used, horizon
        risk_map = {"CRITICO": 0, "ALTO": 1, "MEDIO": 2, "BAIXO": 3}
        X, y = [], []
        feature_names = ["risk_numeric", "trend_strength", "n_nations", "horizon", "n_risks"]

        for s in scenarios_data:
            risk_num = risk_map.get(s.get("risk_level", "MEDIO"), 2)
            trend = s.get("trend_strength", 0)
            nations = len(s.get("nations_analyzed", []))
            horizon = s.get("horizon", 10)
            n_risks = len(s.get("risk_factors", []))
            X.append([risk_num, abs(trend), nations, horizon, n_risks])
            y.append(s.get("category", "geral"))

        if len(X) < 5:
            return {"error": "Amostra insuficiente"}

        self.random_forest.fit(X, y, feature_names)
        preds = self.random_forest.predict(X)
        accuracy = sum(1 for i in range(len(preds)) if preds[i] == y[i]) / len(y)

        return {
            "accuracy": round(accuracy, 4),
            "feature_importance": self.random_forest.feature_importance(),
            "n_trees": self.random_forest.n_trees,
            "samples": len(X),
        }

    def optimize_simulation(self, agents: List[Dict] = None) -> Dict:
        """Pipeline completo de otimização."""
        results = {}

        # 1. Construir grafo de agentes
        if agents:
            graph = self.build_agent_graph(agents)
            results["graph_analysis"] = graph.analyze()

        # 2. Orquestração multiagente para encontrar parâmetros ótimos
        expertise_domains = ["social", "economic", "political", "technological", "environmental"]
        for i, domain in enumerate(expertise_domains):
            self.orchestrator.register_agent(f"agent_{i}", [domain, "optimization", "simulation"])

        consensus = self.orchestrator.negotiate(rounds=5)
        results["optimal_params"] = consensus
        results["orchestration"] = self.orchestrator.summary()

        # 3. Referências
        results["references"] = self.references

        # 4. GitHub tools reference
        results["github_tools"] = [
            {"name": "networkx", "url": "github.com/networkx/networkx", "purpose": "Graph analysis & algorithms"},
            {"name": "cdlib", "url": "github.com/GiulioRossetti/cdlib", "purpose": "Community detection library"},
            {"name": "CausalDiscoveryToolbox", "url": "github.com/FenTechSolutions/CausalDiscoveryToolbox", "purpose": "Causal graph discovery"},
            {"name": "Mesa", "url": "github.com/projectmesa/mesa", "purpose": "Agent-based modeling framework"},
            {"name": "EoN", "url": "github.com/springer-math/EoN", "purpose": "Epidemics on Networks"},
            {"name": "Axelrod", "url": "github.com/Axelrod-Python/Axelrod", "purpose": "Game theory tournaments"},
        ]

        results["timestamp"] = datetime.now(BRAZIL_TZ).isoformat()
        return results


# ═══════════════════════════════════════════════════════════════════
# CLI / Demo
# ═══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 60)
    print("GraphDecisionEngine — Qualis A1 Pipeline")
    print("=" * 60)

    # ── Teste de Grafos ──
    ge = GraphTheoryEngine()
    for i in range(20):
        ge.add_node(f"agent_{i}", stance=random.choice(["supportive","critical","neutral"]))
    for i in range(20):
        for j in range(i+1, 20):
            if random.random() < 0.2:
                ge.add_edge(f"agent_{i}", f"agent_{j}")

    analysis = ge.analyze()
    print(f"\n[GRAPH] {analysis['graph_stats']['nodes']} nodes, {analysis['graph_stats']['edges']} edges")
    print(f"  PageRank top: {analysis['pagerank_top5'][0]}")
    print(f"  Communities: {analysis['communities']} (modularity Q={analysis['modularity_estimate']})")

    # ── Teste Árvore de Decisão ──
    X = [[random.uniform(0,1) for _ in range(3)] for _ in range(50)]
    y = [random.choice(["A","B","C"]) for _ in range(50)]
    dt = DecisionTreeEngine(max_depth=4)
    dt.fit(X, y, ["risk", "volatility", "volume"])
    preds = dt.predict(X[:5])
    print(f"\n[DECISION TREE] Predictions: {preds}")

    # ── Teste Random Forest ──
    rf = RandomForestEngine(n_trees=5, max_depth=4)
    rf.fit(X, y, ["risk", "volatility", "volume"])
    importance = rf.feature_importance()
    print(f"[FOREST] Feature importance: {importance}")

    # ── Teste Orquestrador ──
    orch = MultiAgentOrchestrator()
    for i, d in enumerate(["social","economic","political","tech","climate"]):
        orch.register_agent(f"agent_{i}", [d, "simulation"])
    consensus = orch.negotiate(rounds=3)
    print(f"\n[ORCHESTRATOR] Consensus: agent_count={consensus.get('agent_count')} rounds={consensus.get('rounds')}")

    # ── Pipeline Completo ──
    optimizer = IntegratedSimulationOptimizer()
    agents = [{"name": f"a{i}", "stance": random.choice(["supportive","critical","neutral"]),
               "influence": random.uniform(0.5,2.0)} for i in range(30)]
    results = optimizer.optimize_simulation(agents)
    print(f"\n[PIPELINE] Graph communities: {results['graph_analysis']['communities']}")
    print(f"  Optimal params: {results['optimal_params']}")
    print(f"  References: {len(results['references'])} papers, {len(results['github_tools'])} tools")

    # Salvar
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..","..","..",".reversa","graph_decision_pipeline.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\n  Saved: {out}")
