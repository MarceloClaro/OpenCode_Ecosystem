#!/usr/bin/env python3
"""
Seletor de Problemas para Phase B (Resolução)

Carrega dataset enriquecido (v1.1) e identifica problemas viáveis para 
tentativa de resolução com prova Lean.

Critérios de viabilidade:
  1. Domínio: number_theory, combinatorics, graph_theory (não geometry, topology)
  2. Complexidade: baixa-média (não problemas em aberto há 50+ anos)
  3. Qualidade dataset: score ≥ 0.85 (enunciado claro)
  4. Tem referências/trabalhos conhecidos (melhora viabilidade)

Uso:
    seletor = ProblemSelector()
    top_problems = seletor.select_top_n(n=10)
    for p in top_problems:
        print(f"{p['id']}: {p['statement'][:60]}... (viabilidade: {p['feasibility']})")
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class ProblemFeasibility:
    """Pontuação de viabilidade de um problema."""
    problem_id: int
    statement: str
    domain: str
    feasibility_score: float  # 0-1
    reasoning: List[str]
    is_selected: bool
    
    def __str__(self):
        return (
            f"Problema {self.problem_id} ({self.domain})\n"
            f"  Viabilidade: {self.feasibility_score:.2%}\n"
            f"  Razões: {'; '.join(self.reasoning[:2])}\n"
            f"  Selecionado: {'✓' if self.is_selected else '✗'}"
        )


class ProblemSelector:
    """Seletor de problemas viáveis."""
    
    # Domínios aceitáveis (exclusivamente)
    VIABLE_DOMAINS = {
        "number_theory": 1.0,
        "combinatorics": 1.0,
        "graph_theory": 0.9,
        "algebra": 0.85,
    }
    
    # Palavras-chave que indicam problema difícil/intratável
    HARD_KEYWORDS = {
        "unknown", "open", "conjectured", "unsolved",
        "não resolvido", "desconhecido", "conjecturado",
    }
    
    def __init__(self, dataset_path: str = "data/erdos_718_enriched_v1.1.json"):
        """
        Inicializar seletor.
        
        Args:
            dataset_path: Caminho do dataset enriquecido
        """
        self.dataset_path = Path(dataset_path)
        self.problems = self._load_dataset()
        logger.info(f"Carregados {len(self.problems)} problemas do dataset")
    
    def _load_dataset(self) -> List[Dict]:
        """Carregar dataset enriquecido."""
        if not self.dataset_path.exists():
            logger.error(f"Dataset não encontrado: {self.dataset_path}")
            return []
        
        try:
            with open(self.dataset_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Dataset pode ser lista ou dict com chave 'problems'
                if isinstance(data, dict):
                    return data.get('problems', [])
                return data if isinstance(data, list) else []
        except Exception as e:
            logger.error(f"Erro ao carregar dataset: {e}")
            return []
    
    def _assess_feasibility(self, problem: Dict) -> ProblemFeasibility:
        """
        Avaliar viabilidade de um problema.
        
        Returns:
            ProblemFeasibility com score 0-1 e raciocínio
        """
        problem_id = problem.get('id', 0)
        statement = problem.get('statement', '')
        domain = problem.get('domain', 'unknown')
        
        reasoning = []
        score = 0.0
        
        # 1. Verificar domínio
        if domain in self.VIABLE_DOMAINS:
            domain_weight = self.VIABLE_DOMAINS[domain]
            score += 0.25 * domain_weight
            reasoning.append(f"Domínio viável: {domain}")
        else:
            reasoning.append(f"Domínio menos viável: {domain}")
            score += 0.05
        
        # 2. Qualidade do enunciado
        quality_score = problem.get('quality_score', 0.7)
        if quality_score >= 0.85:
            score += 0.25
            reasoning.append(f"Enunciado claro (quality: {quality_score:.2f})")
        elif quality_score >= 0.70:
            score += 0.15
            reasoning.append(f"Enunciado adequado (quality: {quality_score:.2f})")
        else:
            reasoning.append(f"Enunciado incerto (quality: {quality_score:.2f})")
            score += 0.05
        
        # 3. Presença de trabalhos conhecidos
        known_results = problem.get('known_results', [])
        papers = problem.get('related_papers', [])
        num_references = len(known_results) + len(papers)
        
        if num_references >= 5:
            score += 0.25
            reasoning.append(f"Bem documentado ({num_references} referências)")
        elif num_references >= 2:
            score += 0.15
            reasoning.append(f"Alguns trabalhos conhecidos ({num_references} refs)")
        else:
            reasoning.append("Pouca documentação")
            score += 0.05
        
        # 4. Evitar problemas abertos
        is_open = problem.get('status', '').lower() in ['open', 'unsolved', 'em aberto']
        has_hard_keyword = any(
            kw.lower() in statement.lower()
            for kw in self.HARD_KEYWORDS
        )
        
        if is_open or has_hard_keyword:
            score *= 0.7  # Penalizar
            reasoning.append("Problema potencialmente aberto/difícil")
        else:
            score += 0.10
            reasoning.append("Não está marcado como aberto")
        
        # 5. Complexidade estimada (por tamanho do enunciado)
        statement_length = len(statement.split())
        if statement_length < 100:
            score += 0.10
            reasoning.append(f"Enunciado conciso ({statement_length} palavras)")
        elif statement_length > 200:
            score *= 0.85
            reasoning.append(f"Enunciado complexo ({statement_length} palavras)")
        
        # Normalizar score para [0, 1]
        score = min(max(score, 0.0), 1.0)
        
        return ProblemFeasibility(
            problem_id=problem_id,
            statement=statement,
            domain=domain,
            feasibility_score=score,
            reasoning=reasoning,
            is_selected=(score >= 0.65)
        )
    
    def select_top_n(self, n: int = 10) -> List[ProblemFeasibility]:
        """
        Selecionar top N problemas mais viáveis.
        
        Args:
            n: Número de problemas a selecionar
        
        Returns:
            Lista de ProblemFeasibility ordenada por score
        """
        logger.info(f"Avaliando {len(self.problems)} problemas...")
        
        assessments = []
        for problem in self.problems:
            assessment = self._assess_feasibility(problem)
            assessments.append(assessment)
        
        # Ordenar por score (descendente)
        assessments.sort(key=lambda x: x.feasibility_score, reverse=True)
        
        # Filtrar: apenas selecionados
        selected = [a for a in assessments if a.is_selected]
        
        logger.info(
            f"Viabilidade: {len(selected)}/{len(assessments)} problemas selecionáveis "
            f"(score ≥ 0.65)"
        )
        
        # Retornar top N
        top_n = selected[:n]
        logger.info(f"Retornando top {len(top_n)} problemas mais viáveis")
        
        return top_n
    
    def save_selection(self, problems: List[ProblemFeasibility], output_path: str):
        """Salvar seleção como JSON."""
        selection_data = {
            "timestamp": str(Path(self.dataset_path).stat().st_mtime),
            "total_problems_evaluated": len(self.problems),
            "selected_problems": len(problems),
            "problems": [
                {
                    "id": p.problem_id,
                    "statement": p.statement,
                    "domain": p.domain,
                    "feasibility_score": p.feasibility_score,
                    "reasoning": p.reasoning
                }
                for p in problems
            ]
        }
        
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(selection_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Seleção salva em {output_file}")


def main():
    """Executar seleção e exibir resultados."""
    seletor = ProblemSelector()
    
    # Selecionar top 10
    top_10 = seletor.select_top_n(n=10)
    
    print("\n" + "="*70)
    print("TOP 10 PROBLEMAS PARA FASE B (RESOLUÇÃO COM LEAN)")
    print("="*70 + "\n")
    
    for i, problema in enumerate(top_10, 1):
        print(f"{i}. {problema}")
        print()
    
    # Salvar seleção
    seletor.save_selection(top_10, "data/selected_problems_phase_b.json")
    
    print("="*70)
    print(f"Seleção completa: {len(top_10)} problemas salvos em data/selected_problems_phase_b.json")
    print("="*70)


if __name__ == "__main__":
    main()
