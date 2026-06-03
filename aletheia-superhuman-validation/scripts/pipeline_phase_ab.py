#!/usr/bin/env python3
"""
Pipeline Integrado: Phase A → B

Conecta seletor → formalizador → verificador em um workflow único.

Uso:
    pipeline = AletheiaPipelineAB()
    results = pipeline.run(top_n=5, max_iterations=3)
    
Saída:
    - results.json com status de cada problema
    - Relatório textual de sucessos/falhas
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

from lean_verifier import LeanVerifier, IterativeSolver
from formalize_to_lean import ProblemFormalizerLean
from problem_selector_v2 import ProblemSelectorV2

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class ProblemAttemptResult:
    """Resultado da tentativa de resolver um problema."""
    problem_id: str
    status: str  # "success", "partial", "failed"
    iterations: int
    proof_found: Optional[str]
    lean_code: Optional[str]
    errors: List[Dict]
    timestamp: str


class AletheiaPipelineAB:
    """Pipeline integrado Phase A → B."""
    
    def __init__(
        self,
        dataset_path: str = "data/erdos_718_enriched_v1.1.json",
        selected_problems_path: str = "data/selected_problems_phase_b_v2.json"
    ):
        """
        Inicializar pipeline.
        
        Args:
            dataset_path: Path ao dataset enriquecido
            selected_problems_path: Path aos problemas selecionados (Phase A)
        """
        self.dataset_path = Path(dataset_path)
        self.selected_path = Path(selected_problems_path)
        
        self.selector = ProblemSelectorV2(str(dataset_path))
        self.formalizador = ProblemFormalizerLean()
        self.verifier = LeanVerifier(use_remote=True)
        self.solver = IterativeSolver(self.verifier, max_iterations=5)
        
        logger.info("Pipeline Phase A→B inicializado")
    
    def _load_selected_problems(self, top_n: int = 10) -> List[Dict]:
        """Carregar problemas pré-selecionados (Phase A)."""
        if self.selected_path.exists():
            with open(self.selected_path, 'r', encoding='utf-8') as f:
                selected = json.load(f)[:top_n]
                logger.info(f"Carregados {len(selected)} problemas pré-selecionados")
                return selected
        else:
            # Fallback: usar seletor
            logger.warning(f"Arquivo de seleção não encontrado. Gerando...")
            problems = self.selector.select_top_n(n=top_n, min_score=0.40)
            return [asdict(p) for p in problems]
    
    def _find_problem_in_dataset(self, problem_id: str) -> Optional[Dict]:
        """Buscar problema completo no dataset pelo ID."""
        for problem in self.selector.problems:
            if problem.get('id') == problem_id:
                return problem
        return None
    
    def attempt_problem(
        self,
        problem_id: str,
        max_iterations: int = 3
    ) -> ProblemAttemptResult:
        """
        Tentar resolver um problema único.
        
        Workflow:
          1. Localizar problema no dataset
          2. Extrair enunciado + domínio
          3. Formalizar para Lean
          4. Tentar verificação/refinamento iterativo
        
        Args:
            problem_id: ID do problema (ex: "A0004")
            max_iterations: Número máximo de iterações
        
        Returns:
            ProblemAttemptResult com status e metadados
        """
        logger.info(f"\n{'='*70}")
        logger.info(f"TENTATIVA: Problema {problem_id}")
        logger.info(f"{'='*70}")
        
        # 1. Localizar problema
        problem = self._find_problem_in_dataset(problem_id)
        if not problem:
            logger.error(f"Problema {problem_id} não encontrado no dataset")
            return ProblemAttemptResult(
                problem_id=problem_id,
                status="failed",
                iterations=0,
                proof_found=None,
                lean_code=None,
                errors=[{"error": "Problema não encontrado"}],
                timestamp=datetime.now().isoformat()
            )
        
        statement = problem.get('statement', '')
        domain = problem.get('domain', 'general')
        
        logger.info(f"  Domínio: {domain}")
        logger.info(f"  Enunciado: {statement[:80]}...")
        
        # 2. Formalizar
        logger.info("  [1/3] Formalizando...")
        try:
            formalized = self.formalizador.formalize_from_latex(
                statement,
                domain=self._map_domain(domain)
            )
            lean_code = formalized["full_code"]
            logger.info(f"  ✓ Formalização concluída")
        except Exception as e:
            logger.error(f"  ✗ Falha na formalização: {e}")
            return ProblemAttemptResult(
                problem_id=problem_id,
                status="failed",
                iterations=1,
                proof_found=None,
                lean_code=None,
                errors=[{"stage": "formalization", "error": str(e)}],
                timestamp=datetime.now().isoformat()
            )
        
        # 3. Tentar verificação iterativa
        logger.info("  [2/3] Tentando verificação iterativa...")
        errors = []
        best_result = None
        
        for iteration in range(1, max_iterations + 1):
            logger.info(f"    Iteração {iteration}/{max_iterations}...")
            
            result = self.verifier.verify_proof(lean_code)
            
            if result["success"]:
                logger.info(f"    ✅ SUCESSO na iteração {iteration}!")
                best_result = result
                break
            else:
                errors.append({
                    "iteration": iteration,
                    "error": result.get("error", "Unknown"),
                    "error_type": result.get("error_type")
                })
                logger.warning(f"    ✗ Falha: {result.get('error_type')}")
        
        # 4. Determinar status final
        if best_result and best_result["success"]:
            status = "success"
            logger.info("  ✅ PROBLEMA RESOLVIDO")
        else:
            status = "partial" if errors else "failed"
            logger.warning(f"  ⚠️  Status: {status}")
        
        logger.info(f"  [3/3] Completado")
        
        return ProblemAttemptResult(
            problem_id=problem_id,
            status=status,
            iterations=len(errors) if errors else 1,
            proof_found="<generated_by_model>" if status == "success" else None,
            lean_code=lean_code,
            errors=errors,
            timestamp=datetime.now().isoformat()
        )
    
    @staticmethod
    def _map_domain(domain: str) -> str:
        """Mapear domain do dataset para domínio do formalizador."""
        mapping = {
            "Arxiv": "algebra",
            "Books": "general",
            "ErdosProblems": "number_theory",
            "MathOverflow": "combinatorics",
        }
        return mapping.get(domain, "general")
    
    def run(self, top_n: int = 5, max_iterations: int = 3) -> Dict:
        """
        Executar pipeline completo.
        
        Args:
            top_n: Número de problemas a tentar
            max_iterations: Iterações por problema
        
        Returns:
            {
                "timestamp": ISO datetime,
                "total_problems": int,
                "success_count": int,
                "partial_count": int,
                "results": List[ProblemAttemptResult]
            }
        """
        logger.info("\n" + "="*70)
        logger.info("ALETHEIA PIPELINE PHASE A→B")
        logger.info("="*70)
        
        selected = self._load_selected_problems(top_n)
        results = []
        
        success_count = 0
        partial_count = 0
        
        for i, problem_meta in enumerate(selected, 1):
            problem_id = problem_meta.get('id')
            
            logger.info(f"\n[{i}/{len(selected)}]", extra={"markup": True})
            
            try:
                result = self.attempt_problem(problem_id, max_iterations)
                results.append(result)
                
                if result.status == "success":
                    success_count += 1
                elif result.status == "partial":
                    partial_count += 1
            
            except Exception as e:
                logger.error(f"Erro fatal ao processar {problem_id}: {e}")
                results.append(ProblemAttemptResult(
                    problem_id=problem_id,
                    status="failed",
                    iterations=0,
                    proof_found=None,
                    lean_code=None,
                    errors=[{"error": str(e)}],
                    timestamp=datetime.now().isoformat()
                ))
        
        # Resumo final
        logger.info("\n" + "="*70)
        logger.info("RESUMO FINAL")
        logger.info("="*70)
        logger.info(f"Total de problemas: {len(results)}")
        logger.info(f"✅ Sucessos: {success_count}")
        logger.info(f"🟡 Parciais: {partial_count}")
        logger.info(f"❌ Falhas: {len(results) - success_count - partial_count}")
        logger.info(f"Taxa de sucesso: {success_count/len(results)*100:.1f}%")
        
        return {
            "timestamp": datetime.now().isoformat(),
            "total_problems": len(results),
            "success_count": success_count,
            "partial_count": partial_count,
            "failed_count": len(results) - success_count - partial_count,
            "success_rate": success_count / len(results) if results else 0.0,
            "results": [asdict(r) for r in results]
        }
    
    def save_results(self, results: Dict, output_path: str = "results/pipeline_phase_ab_results.json"):
        """Salvar resultados em JSON."""
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"\n✓ Resultados salvos em {output_file}")


def main():
    """Executar pipeline."""
    pipeline = AletheiaPipelineAB()
    results = pipeline.run(top_n=3, max_iterations=2)  # Teste com 3 problemas
    pipeline.save_results(results)


if __name__ == "__main__":
    main()
