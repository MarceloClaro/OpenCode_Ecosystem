# -*- coding: utf-8 -*-
# SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL
# Toda resposta ao usuário DEVE ser em português do Brasil formal.
# Contexto em chinês para eficiência de tokens (densidade +40%%).
# Modelo: big-pickle (OpenCode Zen, 200K ctx, 128K out, gratuito)

#!/usr/bin/env python3
"""
Knowledge Graphs for TMA v3.0

Representação estruturada de conhecimento avançado em forma de grafos,
ontologias e redes semânticas para raciocínio PhD-level.

Author: TMA Evolution Team
Version: 3.0
Date: 2026-04-14
"""

import json
import networkx as nx
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Set, Any, Optional
from enum import Enum
from datetime import datetime
import numpy as np


# ============================================================================
# KNOWLEDGE GRAPH CORE
# ============================================================================

class RelationType(Enum):
    """Tipos de relações em grafos de conhecimento"""
    IS_A = "is_a"  # Hierarquia
    PART_OF = "part_of"  # Composição
    RELATED_TO = "related_to"  # Associação
    CAUSES = "causes"  # Causalidade
    DEPENDS_ON = "depends_on"  # Dependência
    SIMILAR_TO = "similar_to"  # Similaridade
    CONTRADICTS = "contradicts"  # Contradição
    IMPLIES = "implies"  # Implicação lógica
    INSTANTIATES = "instantiates"  # Instanciação
    SPECIALIZES = "specializes"  # Especialização


class EntityType(Enum):
    """Tipos de entidades no grafo"""
    CONCEPT = "concept"
    THEORY = "theory"
    ALGORITHM = "algorithm"
    DOMAIN = "domain"
    PRINCIPLE = "principle"
    METHOD = "method"
    TOOL = "tool"
    PERSON = "person"
    PUBLICATION = "publication"
    DATA_STRUCTURE = "data_structure"


@dataclass
class Entity:
    """Entidade no grafo de conhecimento"""
    id: str
    name: str
    entity_type: EntityType
    description: str
    properties: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.8
    source: str = "unknown"
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "entity_type": self.entity_type.value,
            "description": self.description,
            "properties": self.properties,
            "confidence": self.confidence,
            "source": self.source,
            "timestamp": self.timestamp
        }


@dataclass
class Relation:
    """Relação entre entidades"""
    source_id: str
    target_id: str
    relation_type: RelationType
    weight: float = 1.0  # Força da relação
    confidence: float = 0.8
    properties: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "source": self.source_id,
            "target": self.target_id,
            "relation_type": self.relation_type.value,
            "weight": self.weight,
            "confidence": self.confidence,
            "properties": self.properties
        }


# ============================================================================
# KNOWLEDGE GRAPH
# ============================================================================

class KnowledgeGraph:
    """
    Grafo de Conhecimento: representação estruturada de conhecimento avançado.
    
    Capacidades:
    - Armazenar entidades e relações
    - Consultar e navegar
    - Raciocínio sobre relações
    - Detecção de padrões
    - Análise de comunidades
    """
    
    def __init__(self, name: str = "TMA_KG"):
        self.name = name
        self.graph = nx.DiGraph()
        self.entities: Dict[str, Entity] = {}
        self.relations: List[Relation] = []
        self.ontology: Dict[str, List[str]] = {}  # classe → subclasses
        self.creation_timestamp = datetime.now().isoformat()
        
    # ========================================================================
    # ENTITY MANAGEMENT
    # ========================================================================
    
    def add_entity(self, entity: Entity) -> None:
        """Adicionar entidade ao grafo"""
        self.entities[entity.id] = entity
        self.graph.add_node(entity.id, **entity.to_dict())
    
    def get_entity(self, entity_id: str) -> Optional[Entity]:
        """Recuperar entidade"""
        return self.entities.get(entity_id)
    
    def search_entities(self, query: str, entity_type: Optional[EntityType] = None) -> List[Entity]:
        """Buscar entidades por nome ou descrição"""
        results = []
        query_lower = query.lower()
        
        for entity in self.entities.values():
            if entity_type and entity.entity_type != entity_type:
                continue
            
            if (query_lower in entity.name.lower() or 
                query_lower in entity.description.lower()):
                results.append(entity)
        
        return results
    
    # ========================================================================
    # RELATION MANAGEMENT
    # ========================================================================
    
    def add_relation(self, relation: Relation) -> None:
        """Adicionar relação entre entidades"""
        if relation.source_id not in self.entities or relation.target_id not in self.entities:
            raise ValueError("Entidades não existem no grafo")
        
        self.relations.append(relation)
        self.graph.add_edge(
            relation.source_id, 
            relation.target_id,
            **relation.to_dict()
        )
    
    def get_relations(self, source_id: str, relation_type: Optional[RelationType] = None) -> List[Relation]:
        """Obter relações de uma entidade"""
        results = []
        for rel in self.relations:
            if rel.source_id == source_id:
                if relation_type is None or rel.relation_type == relation_type:
                    results.append(rel)
        return results
    
    # ========================================================================
    # ONTOLOGY
    # ========================================================================
    
    def add_hierarchy(self, parent_id: str, child_id: str) -> None:
        """Adicionar relação hierárquica (parent is_a child)"""
        parent = self.get_entity(parent_id)
        child = self.get_entity(child_id)
        
        if not parent or not child:
            raise ValueError("Entidades não existem")
        
        # Adicionar relação is_a
        relation = Relation(
            source_id=child_id,
            target_id=parent_id,
            relation_type=RelationType.IS_A,
            confidence=0.95
        )
        self.add_relation(relation)
        
        # Atualizar ontologia
        if parent_id not in self.ontology:
            self.ontology[parent_id] = []
        self.ontology[parent_id].append(child_id)
    
    def get_hierarchy(self, entity_id: str, direction: str = "down") -> Dict:
        """Obter hierarquia de uma entidade"""
        hierarchy = {entity_id: []}
        
        if direction == "down":  # Subclasses
            if entity_id in self.ontology:
                for child_id in self.ontology[entity_id]:
                    hierarchy[entity_id].append(child_id)
                    hierarchy.update(self.get_hierarchy(child_id, "down"))
        
        elif direction == "up":  # Superclasses
            for parent_id, children in self.ontology.items():
                if entity_id in children:
                    hierarchy[entity_id].append(parent_id)
                    hierarchy.update(self.get_hierarchy(parent_id, "up"))
        
        return hierarchy
    
    # ========================================================================
    # REASONING
    # ========================================================================
    
    def transitive_closure(self, source_id: str, relation_type: RelationType) -> Set[str]:
        """
        Fechamento transitivo: encontrar todas as entidades alcançáveis
        através de um tipo de relação.
        """
        visited = set()
        stack = [source_id]
        
        while stack:
            current = stack.pop()
            if current in visited:
                continue
            visited.add(current)
            
            # Encontrar vizinhos com relação específica
            for rel in self.get_relations(current, relation_type):
                if rel.target_id not in visited:
                    stack.append(rel.target_id)
        
        visited.discard(source_id)  # Remover fonte
        return visited
    
    def find_paths(self, source_id: str, target_id: str, max_length: int = 5) -> List[List[str]]:
        """Encontrar todos os caminhos entre duas entidades"""
        try:
            paths = list(nx.all_simple_paths(self.graph, source_id, target_id, cutoff=max_length))
            return paths
        except nx.NetworkXNoPath:
            return []
    
    def find_shortest_path(self, source_id: str, target_id: str) -> Optional[List[str]]:
        """Encontrar caminho mais curto entre entidades"""
        try:
            path = nx.shortest_path(self.graph, source_id, target_id)
            return path
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return None
    
    def semantic_similarity(self, entity_id1: str, entity_id2: str) -> float:
        """
        Calcular similaridade semântica entre entidades.
        
        Baseado em:
        - Proximidade no grafo
        - Vizinhos comuns
        - Relações comuns
        """
        
        if entity_id1 not in self.entities or entity_id2 not in self.entities:
            return 0.0
        
        # Vizinhos comuns
        neighbors1 = set(self.graph.successors(entity_id1)) | set(self.graph.predecessors(entity_id1))
        neighbors2 = set(self.graph.successors(entity_id2)) | set(self.graph.predecessors(entity_id2))
        
        common_neighbors = neighbors1 & neighbors2
        all_neighbors = neighbors1 | neighbors2
        
        if not all_neighbors:
            return 0.0
        
        neighbor_similarity = len(common_neighbors) / len(all_neighbors)
        
        # Distância no grafo
        try:
            distance = nx.shortest_path_length(self.graph, entity_id1, entity_id2)
            distance_similarity = 1 / (1 + distance)
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            distance_similarity = 0.0
        
        # Similaridade combinada
        return 0.6 * neighbor_similarity + 0.4 * distance_similarity
    
    # ========================================================================
    # PATTERN DETECTION
    # ========================================================================
    
    def find_cycles(self) -> List[List[str]]:
        """Encontrar ciclos no grafo (contradições potenciais)"""
        try:
            cycles = list(nx.simple_cycles(self.graph))
            return cycles
        except Exception:
            return []
    
    def find_communities(self) -> Dict[int, Set[str]]:
        """Encontrar comunidades de entidades relacionadas"""
        # Converter para grafo não-dirigido para análise de comunidades
        undirected = self.graph.to_undirected()
        
        communities = {}
        for i, community in enumerate(nx.community.greedy_modularity_communities(undirected)):
            communities[i] = community
        
        return communities
    
    def find_hubs(self, top_n: int = 10) -> List[Tuple[str, int]]:
        """Encontrar entidades mais conectadas (hubs)"""
        degree_centrality = nx.degree_centrality(self.graph)
        sorted_hubs = sorted(degree_centrality.items(), key=lambda x: x[1], reverse=True)
        return sorted_hubs[:top_n]
    
    # ========================================================================
    # INFERENCE
    # ========================================================================
    
    def infer_new_relations(self) -> List[Relation]:
        """Inferir novas relações baseado em padrões existentes"""
        inferred = []
        
        # Regra 1: Transitividade de is_a
        for entity_id in self.entities:
            ancestors = self.transitive_closure(entity_id, RelationType.IS_A)
            for ancestor in ancestors:
                # Verificar se relação já existe
                existing = [r for r in self.relations 
                           if r.source_id == entity_id and r.target_id == ancestor]
                if not existing:
                    inferred.append(Relation(
                        source_id=entity_id,
                        target_id=ancestor,
                        relation_type=RelationType.IS_A,
                        confidence=0.7,
                        properties={"inferred": True}
                    ))
        
        # Regra 2: Simetria de similar_to
        for rel in self.relations:
            if rel.relation_type == RelationType.SIMILAR_TO:
                reverse_exists = any(r.source_id == rel.target_id and r.target_id == rel.source_id
                                    for r in self.relations)
                if not reverse_exists:
                    inferred.append(Relation(
                        source_id=rel.target_id,
                        target_id=rel.source_id,
                        relation_type=RelationType.SIMILAR_TO,
                        confidence=rel.confidence * 0.9,
                        properties={"inferred": True}
                    ))
        
        return inferred
    
    # ========================================================================
    # EXPORT & VISUALIZATION
    # ========================================================================
    
    def to_dict(self) -> Dict:
        """Exportar grafo como dicionário"""
        return {
            "name": self.name,
            "creation_timestamp": self.creation_timestamp,
            "entities": {eid: e.to_dict() for eid, e in self.entities.items()},
            "relations": [r.to_dict() for r in self.relations],
            "ontology": self.ontology,
            "statistics": {
                "num_entities": len(self.entities),
                "num_relations": len(self.relations),
                "num_communities": len(self.find_communities()),
                "num_cycles": len(self.find_cycles())
            }
        }
    
    def generate_report(self) -> Dict:
        """Gerar relatório completo do grafo"""
        hubs = self.find_hubs(5)
        communities = self.find_communities()
        cycles = self.find_cycles()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "graph_name": self.name,
            "statistics": {
                "total_entities": len(self.entities),
                "total_relations": len(self.relations),
                "density": nx.density(self.graph),
                "average_clustering": nx.average_clustering(self.graph.to_undirected()),
                "num_communities": len(communities),
                "num_cycles": len(cycles)
            },
            "top_hubs": [{"entity": eid, "centrality": score} for eid, score in hubs],
            "communities": {i: list(comm) for i, comm in communities.items()},
            "potential_contradictions": cycles
        }


# ============================================================================
# DOMAIN-SPECIFIC KNOWLEDGE GRAPHS
# ============================================================================

class ComputerScienceKG(KnowledgeGraph):
    """Grafo de conhecimento especializado em Ciência da Computação"""
    
    def __init__(self):
        super().__init__("CS_Knowledge_Graph")
        self._initialize_cs_concepts()
    
    def _initialize_cs_concepts(self):
        """Inicializar conceitos fundamentais de CS"""
        
        # Criar entidades principais
        concepts = [
            Entity("algorithm", "Algorithm", EntityType.CONCEPT, "Procedimento computacional"),
            Entity("data_structure", "Data Structure", EntityType.CONCEPT, "Organização de dados"),
            Entity("sorting", "Sorting", EntityType.ALGORITHM, "Ordenação de dados"),
            Entity("search", "Search", EntityType.ALGORITHM, "Busca em dados"),
            Entity("graph", "Graph", EntityType.DATA_STRUCTURE, "Estrutura de grafo"),
            Entity("tree", "Tree", EntityType.DATA_STRUCTURE, "Estrutura de árvore"),
            Entity("complexity", "Complexity Theory", EntityType.THEORY, "Análise de complexidade"),
        ]
        
        for concept in concepts:
            self.add_entity(concept)
        
        # Adicionar relações
        relations = [
            Relation("sorting", "algorithm", RelationType.IS_A),
            Relation("search", "algorithm", RelationType.IS_A),
            Relation("graph", "data_structure", RelationType.IS_A),
            Relation("tree", "data_structure", RelationType.IS_A),
            Relation("tree", "graph", RelationType.SPECIALIZES),
            Relation("algorithm", "complexity", RelationType.DEPENDS_ON),
        ]
        
        for rel in relations:
            self.add_relation(rel)


# ============================================================================
# EXEMPLO DE USO
# ============================================================================

if __name__ == "__main__":
    # Criar grafo de conhecimento
    kg = KnowledgeGraph("TMA_Knowledge_Graph")
    
    print("=" * 80)
    print("Knowledge Graphs for TMA v3.0")
    print("=" * 80)
    
    # Adicionar entidades
    print("\n1. ADDING ENTITIES")
    entities = [
        Entity("ml", "Machine Learning", EntityType.DOMAIN, "Aprendizado de máquina"),
        Entity("dl", "Deep Learning", EntityType.DOMAIN, "Aprendizado profundo"),
        Entity("nn", "Neural Networks", EntityType.ALGORITHM, "Redes neurais"),
        Entity("cnn", "Convolutional Neural Networks", EntityType.ALGORITHM, "CNNs"),
        Entity("transformer", "Transformer", EntityType.ALGORITHM, "Arquitetura Transformer"),
    ]
    
    for entity in entities:
        kg.add_entity(entity)
    print(f"   Adicionadas {len(entities)} entidades")
    
    # Adicionar relações
    print("\n2. ADDING RELATIONS")
    relations = [
        Relation("dl", "ml", RelationType.SPECIALIZES),
        Relation("nn", "ml", RelationType.DEPENDS_ON),
        Relation("cnn", "nn", RelationType.SPECIALIZES),
        Relation("transformer", "nn", RelationType.SPECIALIZES),
        Relation("cnn", "dl", RelationType.PART_OF),
        Relation("transformer", "dl", RelationType.PART_OF),
    ]
    
    for rel in relations:
        kg.add_relation(rel)
    print(f"   Adicionadas {len(relations)} relações")
    
    # Buscar entidades
    print("\n3. SEARCH")
    results = kg.search_entities("neural")
    print(f"   Encontradas {len(results)} entidades com 'neural'")
    
    # Encontrar caminhos
    print("\n4. PATHFINDING")
    path = kg.find_shortest_path("cnn", "ml")
    print(f"   Caminho mais curto CNN → ML: {path}")
    
    # Análise de comunidades
    print("\n5. COMMUNITY DETECTION")
    communities = kg.find_communities()
    print(f"   Comunidades encontradas: {len(communities)}")
    
    # Hubs
    print("\n6. HUBS")
    hubs = kg.find_hubs(3)
    print(f"   Top hubs: {hubs}")
    
    # Relatório
    print("\n" + "=" * 80)
    print("KNOWLEDGE GRAPH REPORT")
    print("=" * 80)
    report = kg.generate_report()
    print(json.dumps(report, indent=2, default=str))
