# -*- coding: utf-8 -*-
# SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL
# Toda resposta ao usuário DEVE ser em português do Brasil formal.
# Contexto em chinês para eficiência de tokens (densidade +40%%).
# Modelo: big-pickle (OpenCode Zen, 200K ctx, 128K out, gratuito)

#!/usr/bin/env python3
"""
Domain Discovery Engine - TMA v4.0

Descobre automaticamente características de novo domínio e aprende
conceitos fundamentais sem treinamento prévio.

Permite que agentes funcionem autonomamente em QUALQUER área.

Author: TMA Autonomy Team
Version: 4.0
Date: 2026-04-14
"""

import json
import re
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Set, Any, Optional
from enum import Enum
from datetime import datetime
from collections import defaultdict, Counter
import numpy as np


# ============================================================================
# DOMAIN DISCOVERY CORE
# ============================================================================

class DomainCharacteristic(Enum):
    """Características que definem um domínio"""
    DETERMINISTIC = "deterministic"  # Resultados previsíveis
    STOCHASTIC = "stochastic"  # Resultados probabilísticos
    DISCRETE = "discrete"  # Espaço discreto
    CONTINUOUS = "continuous"  # Espaço contínuo
    HIERARCHICAL = "hierarchical"  # Estrutura hierárquica
    NETWORKED = "networked"  # Estrutura de rede
    TEMPORAL = "temporal"  # Evolução no tempo
    SPATIAL = "spatial"  # Estrutura espacial
    SYMBOLIC = "symbolic"  # Raciocínio simbólico
    NUMERIC = "numeric"  # Raciocínio numérico
    ADVERSARIAL = "adversarial"  # Ambiente adversarial
    COOPERATIVE = "cooperative"  # Ambiente cooperativo


@dataclass
class DomainProfile:
    """Perfil de um domínio descoberto"""
    domain_name: str
    characteristics: Set[DomainCharacteristic]
    key_concepts: Dict[str, str]  # conceito → definição
    relationships: Dict[str, List[str]]  # conceito → conceitos relacionados
    fundamental_laws: List[str]  # Leis/princípios fundamentais
    problem_types: List[str]  # Tipos de problemas típicos
    solution_strategies: Dict[str, List[str]]  # estratégia → passos
    success_metrics: List[str]  # Métricas de sucesso
    complexity_level: float  # 0-1, nível de complexidade
    maturity_level: float  # 0-1, quanto conhecemos do domínio
    confidence: float  # 0-1, confiança nas descobertas
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict:
        return {
            "domain_name": self.domain_name,
            "characteristics": [c.value for c in self.characteristics],
            "key_concepts": self.key_concepts,
            "relationships": self.relationships,
            "fundamental_laws": self.fundamental_laws,
            "problem_types": self.problem_types,
            "solution_strategies": self.solution_strategies,
            "success_metrics": self.success_metrics,
            "complexity_level": self.complexity_level,
            "maturity_level": self.maturity_level,
            "confidence": self.confidence,
            "timestamp": self.timestamp
        }


# ============================================================================
# DOMAIN DISCOVERY ENGINE
# ============================================================================

class DomainDiscoveryEngine:
    """
    Motor de Descoberta de Domínio: mapeia automaticamente novo domínio.
    
    Capacidades:
    - Análise de texto para extrair conceitos
    - Identificação de características do domínio
    - Descoberta de relações entre conceitos
    - Inferência de leis fundamentais
    - Classificação de tipos de problemas
    - Síntese de estratégias de solução
    """
    
    def __init__(self):
        self.discovered_domains: Dict[str, DomainProfile] = {}
        self.concept_database: Dict[str, Dict] = {}
        self.domain_patterns: Dict[str, List[str]] = {}
        self.learning_history: List[Dict] = []
        
    # ========================================================================
    # CONCEPT EXTRACTION
    # ========================================================================
    
    def extract_concepts(self, text: str, top_n: int = 20) -> List[Tuple[str, float]]:
        """
        Extrair conceitos principais de um texto.
        
        Usa heurísticas:
        - Palavras capitalizadas (nomes próprios)
        - Palavras frequentes
        - Palavras técnicas (contêm sufixos específicos)
        - Colocações (palavras que aparecem juntas)
        """
        
        # Tokenização
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        
        # Filtrar stopwords comuns
        stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'is', 'are', 'was', 'were'}
        words = [w for w in words if w not in stopwords and len(w) > 2]
        
        # Contar frequência
        word_freq = Counter(words)
        
        # Scoring: frequência + comprimento + sufixos técnicos
        scores = {}
        technical_suffixes = ['tion', 'ism', 'ity', 'ness', 'ment', 'ence', 'ance', 'ology', 'graphy']
        
        for word, freq in word_freq.items():
            score = freq
            
            # Bônus para palavras técnicas
            if any(word.endswith(suffix) for suffix in technical_suffixes):
                score *= 1.5
            
            # Bônus para palavras longas (mais específicas)
            score *= (1 + len(word) / 20)
            
            scores[word] = score
        
        # Retornar top conceitos
        top_concepts = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_n]
        
        return top_concepts
    
    # ========================================================================
    # CHARACTERISTIC DETECTION
    # ========================================================================
    
    def detect_characteristics(self, text: str, concepts: List[str]) -> Set[DomainCharacteristic]:
        """
        Detectar características do domínio baseado em palavras-chave.
        """
        
        characteristics = set()
        text_lower = text.lower()
        
        # Padrões para cada característica
        patterns = {
            DomainCharacteristic.DETERMINISTIC: ['deterministic', 'certain', 'predictable', 'fixed', 'invariant'],
            DomainCharacteristic.STOCHASTIC: ['random', 'probabilistic', 'uncertain', 'stochastic', 'noise'],
            DomainCharacteristic.DISCRETE: ['discrete', 'integer', 'countable', 'finite', 'digital'],
            DomainCharacteristic.CONTINUOUS: ['continuous', 'real', 'smooth', 'analog', 'infinite'],
            DomainCharacteristic.HIERARCHICAL: ['hierarchy', 'tree', 'parent', 'child', 'level', 'nested'],
            DomainCharacteristic.NETWORKED: ['network', 'graph', 'connection', 'node', 'edge', 'link'],
            DomainCharacteristic.TEMPORAL: ['time', 'temporal', 'sequence', 'evolution', 'dynamic', 'change'],
            DomainCharacteristic.SPATIAL: ['space', 'spatial', 'geometry', 'location', 'distance', 'dimension'],
            DomainCharacteristic.SYMBOLIC: ['symbol', 'logic', 'reasoning', 'semantic', 'meaning'],
            DomainCharacteristic.NUMERIC: ['number', 'numeric', 'calculation', 'computation', 'quantitative'],
            DomainCharacteristic.ADVERSARIAL: ['adversary', 'competition', 'conflict', 'game', 'strategy'],
            DomainCharacteristic.COOPERATIVE: ['cooperation', 'collaboration', 'team', 'collective', 'consensus'],
        }
        
        for characteristic, keywords in patterns.items():
            if any(keyword in text_lower for keyword in keywords):
                characteristics.add(characteristic)
        
        return characteristics
    
    # ========================================================================
    # RELATIONSHIP DISCOVERY
    # ========================================================================
    
    def discover_relationships(self, text: str, concepts: List[str]) -> Dict[str, List[str]]:
        """
        Descobrir relações entre conceitos.
        
        Padrões:
        - "A is a B" (hierarquia)
        - "A causes B" (causalidade)
        - "A relates to B" (associação)
        - "A depends on B" (dependência)
        """
        
        relationships = defaultdict(list)
        
        # Padrões de relação
        patterns = [
            (r'(\w+)\s+is\s+a\s+(\w+)', 'is_a'),
            (r'(\w+)\s+causes\s+(\w+)', 'causes'),
            (r'(\w+)\s+depends\s+on\s+(\w+)', 'depends_on'),
            (r'(\w+)\s+relates\s+to\s+(\w+)', 'relates_to'),
            (r'(\w+)\s+affects\s+(\w+)', 'affects'),
        ]
        
        for pattern, rel_type in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                source = match.group(1).lower()
                target = match.group(2).lower()
                
                if source in concepts and target in concepts:
                    relationships[source].append(f"{target}({rel_type})")
        
        return dict(relationships)
    
    # ========================================================================
    # FUNDAMENTAL LAW INFERENCE
    # ========================================================================
    
    def infer_fundamental_laws(self, characteristics: Set[DomainCharacteristic], 
                               concepts: List[str]) -> List[str]:
        """
        Inferir leis fundamentais baseado em características.
        """
        
        laws = []
        
        # Leis baseadas em características
        if DomainCharacteristic.DETERMINISTIC in characteristics:
            laws.append("Determinism: Same inputs produce same outputs")
        
        if DomainCharacteristic.STOCHASTIC in characteristics:
            laws.append("Probabilistic Behavior: Outcomes follow probability distributions")
        
        if DomainCharacteristic.HIERARCHICAL in characteristics:
            laws.append("Hierarchical Composition: Complex entities composed of simpler ones")
        
        if DomainCharacteristic.NETWORKED in characteristics:
            laws.append("Network Effects: Behavior depends on connections and topology")
        
        if DomainCharacteristic.TEMPORAL in characteristics:
            laws.append("Temporal Evolution: State changes over time following patterns")
        
        if DomainCharacteristic.SPATIAL in characteristics:
            laws.append("Spatial Locality: Nearby entities more related than distant ones")
        
        if DomainCharacteristic.ADVERSARIAL in characteristics:
            laws.append("Strategic Interaction: Agents optimize against each other")
        
        if DomainCharacteristic.COOPERATIVE in characteristics:
            laws.append("Collective Benefit: Cooperation yields better outcomes than individual action")
        
        return laws
    
    # ========================================================================
    # PROBLEM TYPE CLASSIFICATION
    # ========================================================================
    
    def classify_problem_types(self, characteristics: Set[DomainCharacteristic]) -> List[str]:
        """
        Classificar tipos de problemas típicos do domínio.
        """
        
        problem_types = []
        
        if DomainCharacteristic.OPTIMIZATION in characteristics or \
           DomainCharacteristic.NUMERIC in characteristics:
            problem_types.append("Optimization: Find best solution in solution space")
        
        if DomainCharacteristic.SEARCH in characteristics or \
           DomainCharacteristic.DISCRETE in characteristics:
            problem_types.append("Search: Find solution in discrete space")
        
        if DomainCharacteristic.PREDICTION in characteristics or \
           DomainCharacteristic.TEMPORAL in characteristics:
            problem_types.append("Prediction: Forecast future states")
        
        if DomainCharacteristic.CLASSIFICATION in characteristics:
            problem_types.append("Classification: Assign entities to categories")
        
        if DomainCharacteristic.CLUSTERING in characteristics:
            problem_types.append("Clustering: Group similar entities")
        
        if DomainCharacteristic.INFERENCE in characteristics or \
           DomainCharacteristic.SYMBOLIC in characteristics:
            problem_types.append("Inference: Derive conclusions from evidence")
        
        if DomainCharacteristic.PLANNING in characteristics or \
           DomainCharacteristic.TEMPORAL in characteristics:
            problem_types.append("Planning: Find sequence of actions to achieve goal")
        
        if DomainCharacteristic.GAME in characteristics or \
           DomainCharacteristic.ADVERSARIAL in characteristics:
            problem_types.append("Game: Strategic interaction with opponents")
        
        return problem_types
    
    # ========================================================================
    # STRATEGY SYNTHESIS
    # ========================================================================
    
    def synthesize_strategies(self, characteristics: Set[DomainCharacteristic],
                            problem_types: List[str]) -> Dict[str, List[str]]:
        """
        Sintetizar estratégias de solução para o domínio.
        """
        
        strategies = {}
        
        # Estratégias gerais
        strategies["Exploration"] = [
            "Random sampling",
            "Systematic search",
            "Adaptive sampling",
            "Importance sampling"
        ]
        
        strategies["Exploitation"] = [
            "Greedy selection",
            "Local optimization",
            "Hill climbing",
            "Gradient descent"
        ]
        
        strategies["Learning"] = [
            "Supervised learning",
            "Unsupervised learning",
            "Reinforcement learning",
            "Transfer learning"
        ]
        
        strategies["Reasoning"] = [
            "Deductive reasoning",
            "Inductive reasoning",
            "Abductive reasoning",
            "Analogical reasoning"
        ]
        
        # Estratégias específicas por característica
        if DomainCharacteristic.TEMPORAL in characteristics:
            strategies["Temporal"] = [
                "Sequence modeling",
                "Time series forecasting",
                "State tracking",
                "Event prediction"
            ]
        
        if DomainCharacteristic.NETWORKED in characteristics:
            strategies["Network"] = [
                "Graph traversal",
                "Centrality analysis",
                "Community detection",
                "Path finding"
            ]
        
        if DomainCharacteristic.ADVERSARIAL in characteristics:
            strategies["Adversarial"] = [
                "Minimax strategy",
                "Game tree search",
                "Equilibrium finding",
                "Robust optimization"
            ]
        
        return strategies
    
    # ========================================================================
    # DOMAIN DISCOVERY ORCHESTRATION
    # ========================================================================
    
    def discover_domain(self, domain_name: str, description: str, 
                       examples: List[str] = None) -> DomainProfile:
        """
        Descobrir completo de um novo domínio.
        """
        
        # Combinar descrição com exemplos
        full_text = description
        if examples:
            full_text += " " + " ".join(examples)
        
        # Extrair conceitos
        concepts_with_scores = self.extract_concepts(full_text)
        concepts = [c[0] for c in concepts_with_scores]
        
        # Detectar características
        characteristics = self.detect_characteristics(full_text, concepts)
        
        # Descobrir relações
        relationships = self.discover_relationships(full_text, concepts)
        
        # Inferir leis fundamentais
        fundamental_laws = self.infer_fundamental_laws(characteristics, concepts)
        
        # Classificar tipos de problemas
        problem_types = self.classify_problem_types(characteristics)
        
        # Sintetizar estratégias
        solution_strategies = self.synthesize_strategies(characteristics, problem_types)
        
        # Definir métricas de sucesso
        success_metrics = [
            "Accuracy/Precision",
            "Efficiency/Speed",
            "Robustness/Reliability",
            "Scalability",
            "Interpretability"
        ]
        
        # Calcular complexidade e maturidade
        complexity_level = min(1.0, len(concepts) / 50)  # Mais conceitos = mais complexo
        maturity_level = 0.3  # Começamos com baixa maturidade
        confidence = 0.6 + (len(concepts_with_scores) / 100)  # Mais conceitos = mais confiança
        
        # Criar perfil
        profile = DomainProfile(
            domain_name=domain_name,
            characteristics=characteristics,
            key_concepts={c: f"Concept in {domain_name}" for c in concepts[:10]},
            relationships=relationships,
            fundamental_laws=fundamental_laws,
            problem_types=problem_types,
            solution_strategies=solution_strategies,
            success_metrics=success_metrics,
            complexity_level=complexity_level,
            maturity_level=maturity_level,
            confidence=confidence
        )
        
        # Armazenar
        self.discovered_domains[domain_name] = profile
        self.learning_history.append({
            "timestamp": datetime.now().isoformat(),
            "domain": domain_name,
            "action": "discovered"
        })
        
        return profile
    
    # ========================================================================
    # CONTINUOUS LEARNING
    # ========================================================================
    
    def update_domain_knowledge(self, domain_name: str, new_information: Dict) -> None:
        """
        Atualizar conhecimento de domínio com novas informações.
        """
        
        if domain_name not in self.discovered_domains:
            raise ValueError(f"Domain {domain_name} not discovered yet")
        
        profile = self.discovered_domains[domain_name]
        
        # Atualizar conceitos
        if "new_concepts" in new_information:
            profile.key_concepts.update(new_information["new_concepts"])
        
        # Atualizar relações
        if "new_relationships" in new_information:
            for concept, rels in new_information["new_relationships"].items():
                if concept not in profile.relationships:
                    profile.relationships[concept] = []
                profile.relationships[concept].extend(rels)
        
        # Atualizar leis
        if "new_laws" in new_information:
            profile.fundamental_laws.extend(new_information["new_laws"])
        
        # Aumentar maturidade
        profile.maturity_level = min(1.0, profile.maturity_level + 0.1)
        
        self.learning_history.append({
            "timestamp": datetime.now().isoformat(),
            "domain": domain_name,
            "action": "updated",
            "changes": new_information
        })
    
    # ========================================================================
    # REPORTING
    # ========================================================================
    
    def generate_discovery_report(self, domain_name: str) -> Dict:
        """
        Gerar relatório de descoberta de domínio.
        """
        
        if domain_name not in self.discovered_domains:
            return {"error": f"Domain {domain_name} not found"}
        
        profile = self.discovered_domains[domain_name]
        
        return {
            "timestamp": datetime.now().isoformat(),
            "domain": domain_name,
            "profile": profile.to_dict(),
            "discovery_confidence": profile.confidence,
            "maturity": profile.maturity_level,
            "next_steps": [
                "Validate key concepts with domain experts",
                "Refine relationships through testing",
                "Discover edge cases and exceptions",
                "Optimize solution strategies",
                "Build domain-specific tools"
            ]
        }


# ============================================================================
# EXEMPLO DE USO
# ============================================================================

if __name__ == "__main__":
    engine = DomainDiscoveryEngine()
    
    print("=" * 80)
    print("Domain Discovery Engine v4.0")
    print("=" * 80)
    
    # Descobrir novo domínio: Quantum Computing
    domain_description = """
    Quantum computing uses quantum bits (qubits) that can exist in superposition,
    allowing parallel computation. Key concepts include entanglement, quantum gates,
    quantum algorithms, and quantum error correction. Quantum computers can solve
    certain problems exponentially faster than classical computers.
    """
    
    examples = [
        "Shor's algorithm for factoring",
        "Grover's algorithm for search",
        "Quantum Fourier Transform",
        "Quantum phase estimation"
    ]
    
    print("\n1. DISCOVERING DOMAIN: Quantum Computing")
    profile = engine.discover_domain("Quantum Computing", domain_description, examples)
    
    print(f"\n   Characteristics: {[c.value for c in profile.characteristics]}")
    print(f"   Key Concepts: {list(profile.key_concepts.keys())[:5]}")
    print(f"   Complexity Level: {profile.complexity_level:.2f}")
    print(f"   Confidence: {profile.confidence:.2f}")
    
    print("\n2. FUNDAMENTAL LAWS")
    for law in profile.fundamental_laws:
        print(f"   - {law}")
    
    print("\n3. PROBLEM TYPES")
    for ptype in profile.problem_types:
        print(f"   - {ptype}")
    
    print("\n4. SOLUTION STRATEGIES")
    for strategy, steps in profile.solution_strategies.items():
        print(f"   {strategy}:")
        for step in steps[:2]:
            print(f"     - {step}")
    
    print("\n" + "=" * 80)
    print("DISCOVERY REPORT")
    print("=" * 80)
    report = engine.generate_discovery_report("Quantum Computing")
    print(json.dumps(report, indent=2, default=str))
