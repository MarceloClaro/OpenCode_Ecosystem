#!/usr/bin/env python3
"""
Seletor de Problemas Phase B (Versão 2)

Adaptado para estrutura real do dataset enriquecido v1.1:
  - ID: string (ex: "A0001")
  - domain: string (ex: "Arxiv", "MathOverflow")
  - statement: string (enunciado)
  - difficulty: string (easy, medium, hard)
  - theorem_type: string (theorem, lemma, def, etc.)
  - enrichment: dict (metadados enriquecidos)

Novo critério de viabilidade:
  1. Domínio matemático real (não "Arxiv" genérico)
  2. Dificuldade: medium ou easy (não hard)
  3. Theorem_type: theorem ou lemma (não def)
  4. Statement claro (não muito curto)
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


class ProblemSelectorV2:
    """Seletor adaptado à estrutura real do dataset."""
    
    # Mapeamento de categorias
    DOMAIN_MAPPING = {
        "Arxiv": None,  # Genérico, vai usar enrichment
        "MathOverflow": "general",
        "combinatorics": "combinatorics",
        "number_theory": "number_theory",
        "graph_theory": "graph_theory",
        "geometry": "geometry",
        "algebra": "algebra",
    }
    
    # Tipos de teorema aceitáveis
    VIABLE_THEOREM_TYPES = {"theorem", "lemma", "proposition", "corollary"}
    
    # Dificuldades aceitáveis
    VIABLE_DIFFICULTIES = {"easy", "medium"}  # Não "hard"
    
    def __init__(self, dataset_path: str = "data/erdos_718_enriched_v1.1.json"):
        self.dataset_path = Path(dataset_path)
        self.problems = self._load_dataset()
        logger.info(f"✓ Carregados {len(self.problems)} problemas")
    
    def _load_dataset(self) -> List[Dict]:
        """Carregar dataset."""
        if not self.dataset_path.exists():
            logger.error(f"✗ Dataset não encontrado: {self.dataset_path}")
            return []
        
        try:
            with open(self.dataset_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, dict):
                    return data.get('problems', [])
                return data if isinstance(data, list) else []
        except Exception as e:
            logger.error(f"✗ Erro ao carregar: {e}")
            return []
    
    def _assess_feasibility(self, problem: Dict) -> tuple[float, List[str]]:
        """
        Avaliar viabilidade.
        
        Returns:
            (score: float, reasoning: List[str])
        """
        score = 0.0
        reasoning = []
        
        # 1. Tipo de teorema
        theorem_type = problem.get('theorem_type', '').lower()
        if theorem_type in self.VIABLE_THEOREM_TYPES:
            score += 0.25
            reasoning.append(f"Tipo viável: {theorem_type}")
        else:
            score -= 0.3
            reasoning.append(f"Tipo não-viável: {theorem_type}")
        
        # 2. Dificuldade
        difficulty = problem.get('difficulty', '').lower()
        if difficulty in self.VIABLE_DIFFICULTIES:
            score += 0.25
            reasoning.append(f"Dificuldade aceitável: {difficulty}")
        elif difficulty == "hard":
            score -= 0.25
            reasoning.append(f"Dificuldade alta: {difficulty}")
        else:
            reasoning.append(f"Dificuldade desconhecida: {difficulty}")
        
        # 3. Enunciado claro
        statement = problem.get('statement', '')
        statement_len = len(statement.split())
        
        if 20 <= statement_len <= 300:
            score += 0.25
            reasoning.append(f"Enunciado bem-dimensionado ({statement_len} palavras)")
        elif statement_len < 10:
            score -= 0.2
            reasoning.append(f"Enunciado muito curto ({statement_len} palavras)")
        elif statement_len > 500:
            score -= 0.1
            reasoning.append(f"Enunciado muito longo ({statement_len} palavras)")
        else:
            score += 0.1
            reasoning.append(f"Comprimento razoável ({statement_len} palavras)")
        
        # 4. Enriquecimento (metadados)
        enrichment = problem.get('enrichment', {})
        enrichment_keys = len(enrichment.keys())
        if enrichment_keys >= 5:
            score += 0.15
            reasoning.append(f"Bem enriquecido ({enrichment_keys} metadados)")
        elif enrichment_keys > 0:
            score += 0.05
            reasoning.append(f"Algum enriquecimento ({enrichment_keys} metadados)")
        
        # 5. Não tem patterns de problemas abertos
        statement_lower = statement.lower()
        open_keywords = ["open", "unknown", "unsolved", "conjecture", "em aberto"]
        if any(kw in statement_lower for kw in open_keywords):
            score *= 0.6
            reasoning.append("Contém indicadores de problema aberto")
        else:
            score += 0.10
            reasoning.append("Não marcado como problema aberto")
        
        # Normalizar
        score = min(max(score, 0.0), 1.0)
        
        return score, reasoning
    
    def select_top_n(self, n: int = 10, min_score: float = 0.40) -> List[Dict]:
        """
        Selecionar top N problemas.
        
        Args:
            n: Número de problemas
            min_score: Score mínimo (lowered from 0.65)
        
        Returns:
            Lista de problemas selecionados
        """
        logger.info(f"\n{'='*70}")
        logger.info(f"SELEÇÃO DE PROBLEMAS - PHASE B")
        logger.info(f"{'='*70}\n")
        
        assessments = []
        
        for problem in self.problems:
            score, reasoning = self._assess_feasibility(problem)
            if score >= min_score:
                assessments.append({
                    "id": problem.get('id'),
                    "statement": problem.get('statement', '')[:150],
                    "domain": problem.get('domain'),
                    "theorem_type": problem.get('theorem_type'),
                    "difficulty": problem.get('difficulty'),
                    "score": score,
                    "reasoning": reasoning
                })
        
        # Ordenar por score
        assessments.sort(key=lambda x: x['score'], reverse=True)
        
        logger.info(f"Viáveis: {len(assessments)}/{len(self.problems)} problemas (score ≥ {min_score})")
        logger.info(f"Retornando top {min(n, len(assessments))}\n")
        
        return assessments[:n]
    
    def print_selection(self, problems: List[Dict]):
        """Exibir seleção formatada (com proteção de encoding)."""
        for i, p in enumerate(problems, 1):
            try:
                domain = p['domain']
                difficulty = p['difficulty']
                score = p['score']
                reasoning = p['reasoning'][:2]
                
                logger.info(f"{i:2d}. [{p['id']}] {domain} / {difficulty}")
                logger.info(f"     Score: {score:.2%}")
                logger.info(f"     Razões: {'; '.join(reasoning)}")
            except Exception as e:
                logger.warning(f"Erro ao exibir problema {i}: {e}")


def main():
    seletor = ProblemSelectorV2()
    
    # Selecionar top 10 (threshold: 0.40)
    selected = seletor.select_top_n(n=10, min_score=0.40)
    
    if selected:
        seletor.print_selection(selected)
        
        # Salvar
        output_path = Path("data/selected_problems_phase_b_v2.json")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(selected, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✓ Seleção salva em {output_path}")
    else:
        logger.warning("✗ Nenhum problema selecionado com critérios atuais")


if __name__ == "__main__":
    main()
