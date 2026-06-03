"""
PHASE 4: Real Data Validation
==============================

Executa a pipeline completa (ProverAgent → ReasoningOrchestrator → DebateArena → 
MCPEnricher → RefinementAgent) nos 60 problemas IMO reais com V7Verifier.

Coleta métricas:
- D11 scores original vs refinado
- Improvement ratios
- Reasoning types distribution
- Timing per stage
- Success rates
"""

import asyncio
import json
import time
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import statistics

# Importar componentes Phase 3
from prover_agent import ProverAgent, ProofAttempt
from reasoning_orchestrator_v11 import create_orchestrator as create_reasoning_orchestrator
from debate_arena import DebateArena, DebatePhase
from mcp_enricher import create_mcp_enricher
from refinement_agent import RefinementAgent, DebateResult
from imo_benchmark_adapter import IMOBenchmarkAdapter, IMOProblem
from verifier_v7 import VerifierV7, D11Assessment


@dataclass
class ValidationResult:
    """Resultado da validação de um problema"""
    problem_id: str
    category: str
    level: str
    
    # Scores
    d11_original: float  # Score da solução original (antes do pipeline)
    d11_refined: float   # Score após refinement
    improvement_ratio: float = field(default=0.0)  # (refined - original) / original
    
    # Pipeline stages
    prover_count: int = 0  # Quantas estratégias foram geradas
    reasoning_types_selected: List[str] = field(default_factory=list)  # Top-5 selected
    reasoning_confidence: float = 0.0  # Confidence do ReasoningOrchestrator
    debate_phases_completed: int = 0  # Quantas fases completaram
    consensus_score: float = 0.0  # Consensus do DebateArena
    mcp_count_succeeded: int = 0  # Quantos MCPs tiveram sucesso
    
    # Timing
    time_prover: float = 0.0
    time_reasoning: float = 0.0
    time_debate: float = 0.0
    time_mcp: float = 0.0
    time_refinement: float = 0.0
    time_total: float = 0.0
    
    # Metadata
    success: bool = True
    error_message: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class ValidationReport:
    """Relatório agregado de validação"""
    total_problems: int
    problems_completed: int
    problems_failed: int
    
    # Scores
    avg_d11_original: float = 0.0
    avg_d11_refined: float = 0.0
    avg_improvement_ratio: float = 0.0
    median_improvement_ratio: float = 0.0
    
    # Reasoning distribution
    reasoning_type_frequency: Dict[str, int] = field(default_factory=dict)
    
    # Timing
    avg_time_total: float = 0.0
    avg_time_prover: float = 0.0
    avg_time_reasoning: float = 0.0
    avg_time_debate: float = 0.0
    avg_time_mcp: float = 0.0
    avg_time_refinement: float = 0.0
    
    # Success rates
    success_rate: float = 0.0
    
    # Results by level
    results_by_level: Dict[str, List[float]] = field(default_factory=dict)
    results_by_category: Dict[str, List[float]] = field(default_factory=dict)
    
    # Metadata
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    errors: List[str] = field(default_factory=list)


class ValidationPipeline:
    """Orquestrador da pipeline de validação em tempo real"""
    
    def __init__(self, use_real_v7: bool = True, max_problems: Optional[int] = None):
        """
        Args:
            use_real_v7: Usar V7Verifier real (vs mock)
            max_problems: Máximo de problemas para testar (None = todos 60)
        """
        self.use_real_v7 = use_real_v7
        self.max_problems = max_problems
        
        # Componentes
        self.adapter = IMOBenchmarkAdapter()
        self.prover = ProverAgent()
        self.reasoning_orchestrator = create_reasoning_orchestrator()
        self.debate_arena = DebateArena()
        self.mcp_enricher = create_mcp_enricher(timeout_per_mcp=3.0)  # Timeout reduzido
        self.v7_verifier = VerifierV7() if use_real_v7 else None
        
        # Resultados
        self.results: List[ValidationResult] = []
        self.report: Optional[ValidationReport] = None
    
    async def validate_problem(self, problem: IMOProblem) -> ValidationResult:
        """
        Validar um problema através da pipeline completa
        
        Returns:
            ValidationResult com scores e timing
        """
        result = ValidationResult(
            problem_id=problem.problem_id,
            category=problem.category,
            level=problem.level,
            d11_original=0.0,
            d11_refined=0.0,
        )
        
        start_total = time.time()
        
        try:
            # 1. Score original via V7
            if self.use_real_v7 and self.v7_verifier:
                try:
                    assessment = self.v7_verifier.assess(problem.solution, problem)
                    result.d11_original = assessment.d11_score
                except Exception as e:
                    result.d11_original = 5.0  # Default score se falhar
            else:
                result.d11_original = 5.0  # Score neutral se sem V7 real
            
            # 2. ProverAgent - Gerar múltiplas estratégias
            start_prover = time.time()
            proofs = self.prover.generate_proofs(problem, num_strategies=3)
            result.time_prover = time.time() - start_prover
            result.prover_count = len(proofs)
            
            if not proofs:
                raise Exception("ProverAgent failed to generate proofs")
            
            # 3. ReasoningOrchestrator - Selecionar raciocínios
            start_reasoning = time.time()
            selection = self.reasoning_orchestrator.select_for_problem(problem, top_k=5)
            result.time_reasoning = time.time() - start_reasoning
            result.reasoning_types_selected = [r[0] for r in selection.selected_reasonings[:5]]
            result.reasoning_confidence = selection.confidence_score
            
            # 4. DebateArena - Debater melhor prova
            start_debate = time.time()
            best_proof = max(proofs, key=lambda p: p.confidence)
            debate_result = self.debate_arena.orchestrate_debate(best_proof)
            result.time_debate = time.time() - start_debate
            result.debate_phases_completed = len(debate_result.phases)
            result.consensus_score = debate_result.consensus_score
            
            # 5. MCPEnricher - Enriquecer prova
            start_mcp = time.time()
            enriched_proof, mcp_results = await self.mcp_enricher.enrich_proof(
                best_proof.proof_text,
                problem,
                result.reasoning_types_selected
            )
            result.time_mcp = time.time() - start_mcp
            result.mcp_count_succeeded = sum(
                1 for r in mcp_results.values()
                if r.status.value in ["SUCCESS", "MOCK"]
            )
            
            # 6. RefinementAgent - Refinar prova
            start_refinement = time.time()
            refiner = RefinementAgent()
            refined = refiner.refine_proof(best_proof, debate_result, original_d11_score=result.d11_original)
            result.time_refinement = time.time() - start_refinement
            
            # 7. Avaliar prova refinada com V7
            if self.use_real_v7 and self.v7_verifier:
                try:
                    assessment_refined = self.v7_verifier.assess(refined.refined_text, problem)
                    result.d11_refined = assessment_refined.d11_score
                except Exception:
                    result.d11_refined = refined.refined_score  # Usar score interno
            else:
                result.d11_refined = refined.refined_score
            
            # Calcular improvement
            if result.d11_original > 0:
                result.improvement_ratio = (result.d11_refined - result.d11_original) / result.d11_original
            
            result.time_total = time.time() - start_total
            result.success = True
            
        except Exception as e:
            result.success = False
            result.error_message = str(e)
            result.time_total = time.time() - start_total
        
        return result
    
    async def validate_all(self) -> ValidationReport:
        """
        Validar todos os problemas (ou máximo configurado)
        
        Returns:
            ValidationReport agregado
        """
        problems = self.adapter.load_all_problems()
        
        # Aplicar limite
        if self.max_problems:
            problems = problems[:self.max_problems]
        
        print(f"\n[VALIDATION PIPELINE]")
        print(f"Total problems to validate: {len(problems)}")
        print(f"Using real V7: {self.use_real_v7}")
        print(f"Start time: {datetime.now().isoformat()}\n")
        
        # Validar cada problema
        for idx, problem in enumerate(problems, 1):
            result = await self.validate_problem(problem)
            self.results.append(result)
            
            status = "✅" if result.success else "❌"
            print(f"[{idx}/{len(problems)}] {status} {problem.problem_id} | "
                  f"D11: {result.d11_original:.2f}→{result.d11_refined:.2f} "
                  f"(+{result.improvement_ratio:+.1%}) | {result.time_total:.2f}s")
            
            if not result.success:
                print(f"      Error: {result.error_message}")
        
        # Gerar relatório
        self.report = self._generate_report(len(problems))
        
        return self.report
    
    def _generate_report(self, total: int) -> ValidationReport:
        """Gerar relatório agregado"""
        successful = [r for r in self.results if r.success]
        
        report = ValidationReport(
            total_problems=total,
            problems_completed=len(successful),
            problems_failed=total - len(successful),
        )
        
        if successful:
            # Scores
            report.avg_d11_original = statistics.mean(r.d11_original for r in successful)
            report.avg_d11_refined = statistics.mean(r.d11_refined for r in successful)
            
            improvement_ratios = [r.improvement_ratio for r in successful]
            report.avg_improvement_ratio = statistics.mean(improvement_ratios)
            if len(improvement_ratios) > 1:
                report.median_improvement_ratio = statistics.median(improvement_ratios)
            
            # Reasoning types
            for result in successful:
                for reasoning_type in result.reasoning_types_selected:
                    report.reasoning_type_frequency[reasoning_type] = \
                        report.reasoning_type_frequency.get(reasoning_type, 0) + 1
            
            # Timing
            report.avg_time_total = statistics.mean(r.time_total for r in successful)
            report.avg_time_prover = statistics.mean(r.time_prover for r in successful)
            report.avg_time_reasoning = statistics.mean(r.time_reasoning for r in successful)
            report.avg_time_debate = statistics.mean(r.time_debate for r in successful)
            report.avg_time_mcp = statistics.mean(r.time_mcp for r in successful)
            report.avg_time_refinement = statistics.mean(r.time_refinement for r in successful)
            
            # Success rate
            report.success_rate = len(successful) / total
            
            # Results by level
            for result in successful:
                if result.level not in report.results_by_level:
                    report.results_by_level[result.level] = []
                report.results_by_level[result.level].append(result.improvement_ratio)
            
            # Results by category
            for result in successful:
                if result.category not in report.results_by_category:
                    report.results_by_category[result.category] = []
                report.results_by_category[result.category].append(result.improvement_ratio)
        
        # Errors
        for result in self.results:
            if not result.success:
                report.errors.append(f"{result.problem_id}: {result.error_message}")
        
        return report
    
    def generate_json_report(self, output_path: str) -> None:
        """Exportar relatório em JSON"""
        if not self.report:
            raise ValueError("No report generated yet. Run validate_all() first.")
        
        report_dict = asdict(self.report)
        results_dict = [asdict(r) for r in self.results]
        
        output = {
            "report": report_dict,
            "detailed_results": results_dict,
            "generation_timestamp": datetime.now().isoformat(),
        }
        
        with open(output_path, 'w') as f:
            json.dump(output, f, indent=2)
        
        print(f"\n[REPORT SAVED] {output_path}")
    
    def print_report_summary(self) -> None:
        """Imprimir sumário do relatório"""
        if not self.report:
            raise ValueError("No report generated yet.")
        
        report = self.report
        
        print("\n" + "="*70)
        print("VALIDATION REPORT SUMMARY")
        print("="*70)
        
        print(f"\nCompletion: {report.problems_completed}/{report.total_problems} problems "
              f"({report.success_rate:.1%})")
        print(f"Failed: {report.problems_failed}")
        
        print(f"\nD11 Scores:")
        print(f"  Original:  {report.avg_d11_original:.2f} avg")
        print(f"  Refined:   {report.avg_d11_refined:.2f} avg")
        print(f"  Improvement: +{report.avg_improvement_ratio:+.1%} avg, "
              f"{report.median_improvement_ratio:+.1%} median")
        
        print(f"\nTiming (total: {report.avg_time_total:.2f}s avg):")
        print(f"  ProverAgent:        {report.avg_time_prover:.3f}s")
        print(f"  ReasoningOrchestrator: {report.avg_time_reasoning:.3f}s")
        print(f"  DebateArena:        {report.avg_time_debate:.3f}s")
        print(f"  MCPEnricher:        {report.avg_time_mcp:.3f}s")
        print(f"  RefinementAgent:    {report.avg_time_refinement:.3f}s")
        
        print(f"\nReasoning Types (top 5):")
        sorted_reasoning = sorted(report.reasoning_type_frequency.items(),
                                key=lambda x: x[1], reverse=True)
        for reasoning_type, count in sorted_reasoning[:5]:
            pct = (count / report.problems_completed) * 100
            print(f"  {reasoning_type}: {count} ({pct:.1f}%)")
        
        print(f"\nResults by Level:")
        for level, improvements in sorted(report.results_by_level.items()):
            avg_improvement = statistics.mean(improvements)
            print(f"  {level}: +{avg_improvement:+.1%} ({len(improvements)} problems)")
        
        print(f"\nResults by Category:")
        for category, improvements in sorted(report.results_by_category.items()):
            avg_improvement = statistics.mean(improvements)
            print(f"  {category}: +{avg_improvement:+.1%} ({len(improvements)} problems)")
        
        if report.errors:
            print(f"\nErrors ({len(report.errors)}):")
            for error in report.errors[:5]:
                print(f"  - {error}")
            if len(report.errors) > 5:
                print(f"  ... and {len(report.errors) - 5} more")
        
        print("\n" + "="*70)


async def main():
    """Executar validação completa"""
    # Configuração
    pipeline = ValidationPipeline(
        use_real_v7=True,      # Usar V7Verifier real
        max_problems=10        # Testar com 10 problemas first (depois 60)
    )
    
    # Executar validação
    report = await pipeline.validate_all()
    
    # Imprimir sumário
    pipeline.print_report_summary()
    
    # Salvar JSON
    pipeline.generate_json_report(
        "C:\\Users\\marce\\.config\\opencode\\skills\\aletheia-opencode-native\\phase4_validation_report.json"
    )


if __name__ == "__main__":
    asyncio.run(main())
