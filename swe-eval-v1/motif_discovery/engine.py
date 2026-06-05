"""
Motif Discovery Engine (MDE) — Extracao de motivos estruturais recorrentes
no ecossistema OpenCode. Opera ANTES da evolucao, identificando padroes
que guiam a descoberta e otimizacao de skills.

Fases: GRAPH → MINE → CLASSIFY → EXTRACT → GUIDE

Integra-se ao pipeline /evolve como fase MOTIF (entre SENSE e DISCOVER).
"""

import json
import hashlib
from collections import defaultdict, Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


# ============================================================
# ESTRUTURAS DE DADOS
# ============================================================

@dataclass
class EcosystemNode:
    """No no grafo do ecossistema: skill, agente, MCP ou artefato."""
    node_id: str
    node_type: str  # skill, agent, mcp, artifact, layer, pipeline
    name: str
    metadata: dict = field(default_factory=dict)
    connections_out: list[str] = field(default_factory=list)
    connections_in: list[str] = field(default_factory=list)


@dataclass
class StructuralMotif:
    """Motivo estrutural recorrente no ecossistema."""
    motif_id: str
    name: str
    description: str
    pattern: list[tuple[str, str, str]]  # (node_type_a, relation, node_type_b)
    frequency: int = 0
    locations: list[list[str]] = field(default_factory=list)  # onde aparece
    confidence: float = 0.0
    is_invariant: bool = False  # persiste entre ciclos?
    cycles_survived: int = 0


@dataclass
class MotifDiscoveryReport:
    """Relatorio de descoberta de motivos."""
    total_nodes: int = 0
    total_edges: int = 0
    motifs_found: int = 0
    invariants_found: int = 0
    motifs: list[StructuralMotif] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    evolution_directions: list[str] = field(default_factory=list)


# ============================================================
# GRAFO DO ECOSSISTEMA
# ============================================================

class EcosystemGraph:
    """Grafo direcionado do ecossistema: skills, agentes, MCPs, camadas."""

    def __init__(self):
        self.nodes: dict[str, EcosystemNode] = {}
        self.edges: list[tuple[str, str, str]] = []  # (from, to, relation_type)

    def add_node(self, node_id: str, node_type: str, name: str, **metadata):
        self.nodes[node_id] = EcosystemNode(
            node_id=node_id, node_type=node_type, name=name,
            metadata=metadata
        )

    def add_edge(self, from_id: str, to_id: str, relation_type: str):
        self.edges.append((from_id, to_id, relation_type))
        if from_id in self.nodes:
            self.nodes[from_id].connections_out.append(to_id)
        if to_id in self.nodes:
            self.nodes[to_id].connections_in.append(from_id)

    def node_type_distribution(self) -> dict[str, int]:
        dist = Counter(n.node_type for n in self.nodes.values())
        return dict(dist)

    def edge_type_distribution(self) -> dict[str, int]:
        dist = Counter(e[2] for e in self.edges)
        return dict(dist)

    def get_subgraph(self, node_ids: list[str]) -> "EcosystemGraph":
        sub = EcosystemGraph()
        for nid in node_ids:
            if nid in self.nodes:
                sub.nodes[nid] = self.nodes[nid]
        for (f, t, r) in self.edges:
            if f in node_ids and t in node_ids:
                sub.edges.append((f, t, r))
        return sub

    def export_graphml(self) -> str:
        """Exporta para formato GraphML."""
        lines = ['<?xml version="1.0" encoding="UTF-8"?>',
                 '<graphml xmlns="http://graphml.graphdrawing.org/xmlns">',
                 '<graph id="ecosystem" edgedefault="directed">']
        for nid, node in self.nodes.items():
            lines.append(f'  <node id="{nid}">')
            lines.append(f'    <data key="type">{node.node_type}</data>')
            lines.append(f'    <data key="name">{node.name}</data>')
            lines.append(f'  </node>')
        for i, (f, t, r) in enumerate(self.edges):
            lines.append(f'  <edge id="e{i}" source="{f}" target="{t}">')
            lines.append(f'    <data key="relation">{r}</data>')
            lines.append(f'  </edge>')
        lines.append('</graph></graphml>')
        return '\n'.join(lines)

    @classmethod
    def from_registry(cls, registry_path: str) -> "EcosystemGraph":
        """Constroi grafo a partir do Registry v2.0."""
        graph = cls()
        data = json.loads(Path(registry_path).read_text(encoding="utf-8"))
        for skill in data if isinstance(data, list) else data.get("skills", []):
            sid = skill.get("name", "unknown")
            graph.add_node(sid, "skill", sid,
                          version=skill.get("version", "0.1.0"),
                          permissions=skill.get("permissions", []))
        return graph

    @classmethod
    def from_ecosystem_scan(cls, root_path: str) -> "EcosystemGraph":
        """Constroi grafo scannerizando diretorios do ecossistema."""
        graph = cls()
        root = Path(root_path)

        known_layers = {
            "core": "Camada 0 — Fundacao",
            "plugins": "Camada 2 — Integracao",
            "skills": "Camada 3 — Servicos",
            "agents": "Camada 5 — Interface",
            "nexus": "Camada 4 — Orquestracao",
            "swe-eval-v1": "Camada 1 — Infraestrutura",
            "commands": "Camada 5 — Interface",
        }

        for layer_name, layer_desc in known_layers.items():
            layer_dir = root / layer_name
            if layer_dir.exists():
                lid = f"layer:{layer_name}"
                graph.add_node(lid, "layer", layer_name, description=layer_desc)

        skills_dir = root / "skills"
        if skills_dir.exists():
            for skill_dir in skills_dir.iterdir():
                if skill_dir.is_dir() and not skill_dir.name.startswith("__"):
                    sid = f"skill:{skill_dir.name}"
                    graph.add_node(sid, "skill", skill_dir.name)
                    graph.add_edge(sid, "layer:skills", "belongs_to")

                    skill_md = skill_dir / "SKILL.md"
                    if skill_md.exists():
                        content = skill_md.read_text(encoding="utf-8", errors="ignore")
                        for dep_match in __import__("re").finditer(r'depends_on.*?[`"\'](\w+)[`"\']', content):
                            graph.add_edge(sid, f"skill:{dep_match.group(1)}", "depends_on")

        agents_dir = root / "agents"
        if agents_dir.exists():
            for agent_file in agents_dir.glob("*.md"):
                aid = f"agent:{agent_file.stem}"
                graph.add_node(aid, "agent", agent_file.stem)
                graph.add_edge(aid, "layer:agents", "belongs_to")

                content = agent_file.read_text(encoding="utf-8", errors="ignore")
                for skill_match in __import__("re").finditer(r'skill[s]?\s*[:=]\s*\[?([^\]]+)\]?', content):
                    for skill_name in skill_match.group(1).split(","):
                        skill_name = skill_name.strip().strip('"').strip("'")
                        if skill_name:
                            graph.add_edge(aid, f"skill:{skill_name}", "uses")

        return graph


# ============================================================
# MINERADOR DE MOTIVOS
# ============================================================

class MotifMiner:
    """Descobre motivos estruturais recorrentes no grafo do ecossistema."""

    KNOWN_MOTIFS: list[StructuralMotif] = [
        StructuralMotif(
            motif_id="MOTIF-001",
            name="Pipeline Sequencial",
            description="Agente → Skill → MCP: o padrao fundamental de execucao do ecossistema",
            pattern=[("agent", "uses", "skill"), ("skill", "calls", "mcp")],
            is_invariant=True, cycles_survived=18
        ),
        StructuralMotif(
            motif_id="MOTIF-002",
            name="Verificacao Multi-Agente",
            description="N agentes verificadores em paralelo → barreira → consenso",
            pattern=[("agent", "verifies", "artifact"), ("agent", "reports_to", "orchestrator")],
            is_invariant=True, cycles_survived=18
        ),
        StructuralMotif(
            motif_id="MOTIF-003",
            name="Dependencia em Camadas",
            description="Skill depende de MCP, que depende de Infraestrutura — injecao de dependencia",
            pattern=[("skill", "depends_on", "mcp"), ("mcp", "runs_on", "infrastructure")],
            is_invariant=True, cycles_survived=18
        ),
        StructuralMotif(
            motif_id="MOTIF-004",
            name="Especializacao Progressiva",
            description="Skill generica → N skills especializadas (code-review → python, ts, latex)",
            pattern=[("skill", "specializes_into", "skill"), ("skill", "specializes_into", "skill")],
            is_invariant=False, cycles_survived=8
        ),
        StructuralMotif(
            motif_id="MOTIF-005",
            name="Composicao Funcional",
            description="Skill A + Skill B → Skill C (nova capacidade por composicao)",
            pattern=[("skill", "composes_with", "skill"), ("skill", "produces", "skill")],
            is_invariant=False, cycles_survived=12
        ),
        StructuralMotif(
            motif_id="MOTIF-006",
            name="Feedback Loop Iterativo",
            description="Spec → Plan → Tasks → Code → Test → Review → Spec (ciclo SDD+TDD)",
            pattern=[("artifact", "derives", "artifact"), ("artifact", "validates_against", "artifact")],
            is_invariant=True, cycles_survived=12
        ),
        StructuralMotif(
            motif_id="MOTIF-007",
            name="Gate de Qualidade",
            description="Artefato → Verificador → Decisao (PASS/FAIL) — padrao SWE-EVAL",
            pattern=[("artifact", "checked_by", "verifier"), ("verifier", "decides", "gate")],
            is_invariant=True, cycles_survived=1
        ),
        StructuralMotif(
            motif_id="MOTIF-008",
            name="Reuso Cross-Dominio",
            description="Skill do dominio A → adaptada → Skill no dominio B (heranca de skills)",
            pattern=[("skill", "adapted_from", "skill"), ("skill", "applied_to", "domain")],
            is_invariant=False, cycles_survived=8
        ),
    ]

    def __init__(self, graph: EcosystemGraph):
        self.graph = graph
        self.discovered: list[StructuralMotif] = []

    def mine(self) -> list[StructuralMotif]:
        """Minera motivos no grafo atual do ecossistema."""
        self.discovered = []
        for motif in self.KNOWN_MOTIFS:
            locations = self._find_motif_occurrences(motif)
            if locations:
                motif.frequency = len(locations)
                motif.locations = locations
                motif.confidence = min(1.0, motif.frequency / max(1, len(self.graph.nodes)))
                self.discovered.append(motif)
        return self.discovered

    def _find_motif_occurrences(self, motif: StructuralMotif) -> list[list[str]]:
        """Encontra ocorrencias do padrao no grafo."""
        locations = []
        for (from_type, relation, to_type) in motif.pattern:
            for (f, t, r) in self.graph.edges:
                f_type = self.graph.nodes.get(f, EcosystemNode(f, "", "")).node_type if f in self.graph.nodes else ""
                t_type = self.graph.nodes.get(t, EcosystemNode(t, "", "")).node_type if t in self.graph.nodes else ""
                if f_type == from_type and t_type == to_type and r == relation:
                    locations.append([f, t])
        return locations[:50]  # limitar para performance

    def discover_novel_motifs(self, min_frequency: int = 2) -> list[StructuralMotif]:
        """Descobre motivos novos (nao catalogados) com mineracao de subgrafos frequentes."""
        novel = []
        edge_signatures: dict[str, list[tuple[str, str]]] = defaultdict(list)

        for (f, t, r) in self.graph.edges:
            f_type = self.graph.nodes.get(f, EcosystemNode(f, "", "")).node_type if f in self.graph.nodes else "unknown"
            t_type = self.graph.nodes.get(t, EcosystemNode(t, "", "")).node_type if t in self.graph.nodes else "unknown"
            sig = f"{f_type}--[{r}]-->{t_type}"
            edge_signatures[sig].append((f, t))

        idx = len(self.KNOWN_MOTIFS) + 1
        for sig, occurrences in edge_signatures.items():
            if len(occurrences) >= min_frequency:
                parts = sig.split("--[")
                rel = parts[1].split("]-->")[0] if len(parts) > 1 else "unknown"
                novel.append(StructuralMotif(
                    motif_id=f"MOTIF-N{idx:03d}",
                    name=f"Padrao {sig}",
                    description=f"Motivo descoberto automaticamente: {len(occurrences)} ocorrencias de {sig}",
                    pattern=[(sig.split("--")[0], rel, sig.split("-->")[-1])],
                    frequency=len(occurrences),
                    locations=[list(o) for o in occurrences[:10]],
                    confidence=min(1.0, len(occurrences) / max(1, len(self.graph.edges)))
                ))
                idx += 1
        return novel


# ============================================================
# EXTRATOR DE INVARIANTES
# ============================================================

class InvariantExtractor:
    """Identifica motivos que persistem como invariantes entre ciclos de evolucao."""

    def __init__(self, miner: MotifMiner):
        self.miner = miner

    def extract_invariants(self, cycle_history: list[dict]) -> list[StructuralMotif]:
        """Extrai invariantes analisando presenca de motivos em multiplos ciclos."""
        invariants = []
        for motif in self.miner.discovered + self.miner.KNOWN_MOTIFS:
            survival_count = 0
            for cycle in cycle_history:
                if motif.motif_id in cycle.get("motifs_found", []):
                    survival_count += 1

            if survival_count >= len(cycle_history) * 0.5:
                motif.is_invariant = True
                motif.cycles_survived = survival_count
                invariants.append(motif)

        return invariants

    def detect_breaking_invariants(self, current_motifs: list[str],
                                   previous_cycle: dict) -> list[str]:
        """Detecta invariantes que foram quebrados no ciclo atual."""
        breaking = []
        prev_motifs = set(previous_cycle.get("motifs_found", []))
        for m in current_motifs:
            if m not in prev_motifs and any(
                m.startswith(p) for p in prev_motifs
            ):
                breaking.append(m)
        return breaking


# ============================================================
# CLASSIFICADOR DE PADROES
# ============================================================

class PatternClassifier:
    """Classifica motivos descobertos por tipo e relevancia evolutiva."""

    EVOLUTION_CLASSES = {
        "foundational": "Motivo fundamental — alterar quebra o ecossistema",
        "optimization": "Motivo otimizavel — pode ser melhorado",
        "emergent": "Motivo emergente — surgiu recentemente, monitorar",
        "deprecated": "Motivo em declinio — pode desaparecer",
        "anomaly": "Motivo anomalo — unica ocorrencia, investigar",
    }

    def classify(self, motifs: list[StructuralMotif]) -> dict[str, list[StructuralMotif]]:
        classified: dict[str, list[StructuralMotif]] = {k: [] for k in self.EVOLUTION_CLASSES}

        for motif in motifs:
            if motif.is_invariant and motif.cycles_survived >= 10:
                classified["foundational"].append(motif)
            elif motif.frequency == 1 and motif.cycles_survived == 0:
                classified["anomaly"].append(motif)
            elif motif.cycles_survived <= 2:
                classified["emergent"].append(motif)
            elif motif.frequency >= 5 and not motif.is_invariant:
                classified["optimization"].append(motif)
            else:
                classified["deprecated"].append(motif)

        return classified

    def generate_recommendations(self, classified: dict) -> list[str]:
        recs = []
        if classified["foundational"]:
            recs.append(f"PROTEGER: {len(classified['foundational'])} motivos fundacionais — nao alterar sem auditoria")
        if classified["optimization"]:
            recs.append(f"OTIMIZAR: {len(classified['optimization'])} motivos candidatos a melhoria")
        if classified["emergent"]:
            recs.append(f"MONITORAR: {len(classified['emergent'])} motivos emergentes — evoluir com cautela")
        if classified["anomaly"]:
            recs.append(f"INVESTIGAR: {len(classified['anomaly'])} anomalias — possiveis bugs ou anti-padroes")
        return recs


# ============================================================
# ENGINE PRINCIPAL
# ============================================================

class MotifDiscoveryEngine:
    """Motor completo de descoberta de motivos estruturais."""

    def __init__(self, ecosystem_root: str, cycle_history_path: Optional[str] = None):
        self.root = ecosystem_root
        self.graph = EcosystemGraph.from_ecosystem_scan(ecosystem_root)
        self.miner = MotifMiner(self.graph)
        self.invariant_extractor = InvariantExtractor(self.miner)
        self.classifier = PatternClassifier()

        self.cycle_history: list[dict] = []
        if cycle_history_path and Path(cycle_history_path).exists():
            self.cycle_history = json.loads(
                Path(cycle_history_path).read_text(encoding="utf-8")
            )

    def run(self) -> MotifDiscoveryReport:
        """Executa pipeline completo de descoberta de motivos."""
        report = MotifDiscoveryReport(
            total_nodes=len(self.graph.nodes),
            total_edges=len(self.graph.edges),
        )

        known_motifs = self.miner.mine()
        novel_motifs = self.miner.discover_novel_motifs(min_frequency=2)
        all_motifs = known_motifs + novel_motifs

        report.motifs = all_motifs
        report.motifs_found = len(all_motifs)

        if self.cycle_history:
            invariants = self.invariant_extractor.extract_invariants(self.cycle_history)
            report.invariants_found = len(invariants)

        classified = self.classifier.classify(all_motifs)
        report.recommendations = self.classifier.generate_recommendations(classified)
        report.evolution_directions = self._generate_evolution_directions(all_motifs, classified)

        return report

    def _generate_evolution_directions(self, motifs: list[StructuralMotif],
                                       classified: dict) -> list[str]:
        directions = []
        if classified["optimization"]:
            top = classified["optimization"][0]
            directions.append(f"REFINAR {top.name}: {top.frequency} ocorrencias — otimizar via especializacao")
        if classified["emergent"]:
            for m in classified["emergent"][:2]:
                directions.append(f"ESTABILIZAR {m.name}: padrao recente — adicionar testes de regressao")
        if classified["foundational"]:
            directions.append(f"AUDITAR motivos fundacionais: {len(classified['foundational'])} invariantes criticos")
        return directions


# ============================================================
# RELATORIO
# ============================================================

def generate_motif_report_markdown(report: MotifDiscoveryReport) -> str:
    lines = [
        "# Motif Discovery Report",
        "",
        f"| Metrica | Valor |",
        f"|---------|-------|",
        f"| Nos no grafo | {report.total_nodes} |",
        f"| Arestas | {report.total_edges} |",
        f"| Motivos descobertos | {report.motifs_found} |",
        f"| Invariantes estruturais | {report.invariants_found} |",
        "",
    ]

    if report.motifs:
        lines.append("## Motivos Descobertos")
        for m in report.motifs[:10]:
            inv = "INVARIANTE" if m.is_invariant else "variavel"
            lines.extend([
                f"### {m.motif_id}: {m.name}",
                f"- **Descricao:** {m.description}",
                f"- **Frequencia:** {m.frequency} ocorrencias",
                f"- **Confianca:** {m.confidence:.2f}",
                f"- **Estabilidade:** {inv} ({m.cycles_survived} ciclos)",
                "",
            ])

    if report.recommendations:
        lines.append("## Recomendacoes Evolutivas")
        for r in report.recommendations:
            lines.append(f"- {r}")
        lines.append("")

    if report.evolution_directions:
        lines.append("## Direcoes de Evolucao")
        for d in report.evolution_directions:
            lines.append(f"- {d}")
        lines.append("")

    return "\n".join(lines)
