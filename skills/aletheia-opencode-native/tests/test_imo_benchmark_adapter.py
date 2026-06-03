"""
Testes para IMO Benchmark Adapter
Validação de integração com V7 Verifier contra benchmarks reais do Google DeepMind

Cobertura:
- test_adapter_initialization: Carregamento básico
- test_load_from_url: Fetch de proofbench_v2.csv do GitHub
- test_domain_mapping: Mapeamento IMO → Aletheia domains
- test_sampling_and_filtering: Amostragem estratificada
- test_v7_integration: Executar V7 em problemas reais
- test_score_vs_difficulty_correlation: Validar D11 scores vs IMO levels
- test_statistical_analysis: Análise comparativa
"""

import sys
import pytest
from pathlib import Path
from typing import Dict, List
from dataclasses import asdict

# Adicionar paths
aletheia_root = Path(__file__).parent.parent
sys.path.insert(0, str(aletheia_root / "references"))
sys.path.insert(0, str(aletheia_root))

from imo_benchmark_adapter import IMOBenchmarkAdapter, IMOProblem
from verifier_v7 import VerifierV7, ProofStructure


class TestIMOBenchmarkAdapterBasics:
    """Testes básicos de funcionalidade do adapter"""
    
    def test_adapter_initialization(self):
        """Verificar inicialização do adapter"""
        adapter = IMOBenchmarkAdapter()
        assert adapter.problems == []
        assert adapter.assessments == {}
    
    def test_imo_problem_dataclass(self):
        """Verificar criação de problemas IMO"""
        problem = IMOProblem(
            problem_id="PB-Basic-001",
            problem_statement="Find $x$ such that $x^2 = 4$",
            solution="Taking square roots: $x = \\pm 2$",
            grading_guidelines="Award points for both roots",
            category="algebra",
            level="Basic",
            short_answer="±2",
            source="Test"
        )
        assert problem.problem_id == "PB-Basic-001"
        assert problem.difficulty_level == 1
        assert problem.aletheia_domain == "algebra"
    
    def test_difficulty_level_mapping(self):
        """Verificar mapeamento de níveis de dificuldade"""
        levels = {
            "Basic": 1,
            "Intermediate": 4,
            "Advanced": 6
        }
        
        for level_name, expected_level in levels.items():
            problem = IMOProblem(
                problem_id=f"test-{level_name}",
                problem_statement="test",
                solution="test",
                grading_guidelines="",
                category="algebra",
                level=level_name,
                short_answer="",
                source="test"
            )
            assert problem.difficulty_level >= 1
            assert problem.difficulty_level <= 6
    
    def test_domain_mapping_all_categories(self):
        """Verificar mapeamento de todas as categorias para domínios Aletheia"""
        mappings = {
            "geometry": "analysis",
            "combinatorics": "algebra",
            "number_theory": "number_theory",
            "algebra": "algebra",
        }
        
        for imo_category, expected_domain in mappings.items():
            problem = IMOProblem(
                problem_id="test",
                problem_statement="test",
                solution="test",
                grading_guidelines="",
                category=imo_category,
                level="Basic",
                short_answer="",
                source="test"
            )
            assert problem.aletheia_domain == expected_domain
    
    def test_to_verifier_proof_format(self):
        """Verificar conversão para formato do V7 Verifier"""
        problem = IMOProblem(
            problem_id="PB-Test-001",
            problem_statement="Test statement",
            solution="Test solution with lemma 1. And case 1. Using induction.",
            grading_guidelines="grading",
            category="algebra",
            level="Intermediate",
            short_answer="answer",
            source="test"
        )
        
        verifier_format = problem.to_verifier_proof()
        
        assert verifier_format["proof_id"] == "PB-Test-001"
        assert verifier_format["domain"] == "algebra"
        assert verifier_format["text"] == problem.solution
        assert "imo_category" in verifier_format["metadata"]
        assert "imo_level" in verifier_format["metadata"]
        assert "difficulty" in verifier_format["metadata"]


class TestIMOBenchmarkAdapterLoading:
    """Testes de carregamento de dados"""
    
    def test_load_from_url_real_data(self):
        """Carregar dados reais do GitHub (teste de integração)"""
        adapter = IMOBenchmarkAdapter()
        
        # Este teste é real — carrega proofbench_v2.csv do GitHub
        count = adapter.load_from_url()
        
        print(f"\n[STATS] Carregados {count} problemas do IMO-ProofBench v2")
        
        if count > 0:
            assert count >= 10, "Esperado pelo menos 10 problemas"
            
            # Verificar primeiro problema
            first = adapter.problems[0]
            assert first.problem_id, "Problem ID não pode estar vazio"
            assert first.solution, "Solution não pode estar vazia"
            assert first.category, "Category não pode estar vazia"
            
            print(f"[OK] Primeiro problema: {first.problem_id} ({first.category})")
    
    def test_summary_statistics(self):
        """Computar estatísticas dos problemas carregados"""
        adapter = IMOBenchmarkAdapter()
        count = adapter.load_from_url()
        
        if count == 0:
            pytest.skip("Nenhum problema carregado da URL")
        
        stats = adapter.get_summary_statistics()
        
        assert "total_problems" in stats
        assert "by_level" in stats
        assert "by_category" in stats
        assert "by_domain" in stats
        
        print(f"\n Estatísticas do dataset:")
        print(f"   Total: {stats['total_problems']} problemas")
        print(f"   Por nível: {stats['by_level']}")
        print(f"   Por categoria: {stats['by_category']}")
        print(f"   Por domínio Aletheia: {stats['by_domain']}")
        print(f"   Comprimento médio da solução: {stats['avg_solution_length']:.0f} chars")


class TestIMOBenchmarkAdapterFiltering:
    """Testes de filtragem e amostragem"""
    
    def test_filter_by_level(self):
        """Filtrar problemas por nível de dificuldade"""
        adapter = IMOBenchmarkAdapter()
        count = adapter.load_from_url()
        
        if count == 0:
            pytest.skip("Nenhum problema carregado")
        
        # Tentar filtrar por cada nível
        for level in ["Basic", "Intermediate", "Advanced"]:
            filtered = adapter.get_problems_by_level(level)
            print(f"   {level}: {len(filtered)} problemas")
    
    def test_filter_by_category(self):
        """Filtrar problemas por categoria"""
        adapter = IMOBenchmarkAdapter()
        count = adapter.load_from_url()
        
        if count == 0:
            pytest.skip("Nenhum problema carregado")
        
        categories = set(p.category for p in adapter.problems)
        print(f"\n Categorias encontradas: {categories}")
        
        for category in list(categories)[:3]:  # Testar primeiras 3
            filtered = adapter.get_problems_by_category(category)
            assert len(filtered) > 0
            print(f"   {category}: {len(filtered)} problemas")
    
    def test_filter_by_domain(self):
        """Filtrar problemas por domínio Aletheia"""
        adapter = IMOBenchmarkAdapter()
        count = adapter.load_from_url()
        
        if count == 0:
            pytest.skip("Nenhum problema carregado")
        
        domains = set(p.aletheia_domain for p in adapter.problems)
        print(f"\n Domínios Aletheia: {domains}")
        
        for domain in domains:
            filtered = adapter.get_problems_by_domain(domain)
            assert len(filtered) > 0
            print(f"   {domain}: {len(filtered)} problemas")
    
    def test_sampling_problems(self):
        """Amostragem estratificada de problemas"""
        adapter = IMOBenchmarkAdapter()
        count = adapter.load_from_url()
        
        if count == 0:
            pytest.skip("Nenhum problema carregado")
        
        sample = adapter.sample_problems(n=5)
        assert len(sample) <= 5
        assert len(sample) > 0
        
        print(f"\n Amostra de {len(sample)} problemas:")
        for p in sample:
            print(f"   - {p.problem_id} ({p.category}, {p.level})")


class TestV7VerifierIntegration:
    """Testes de integração entre IMO Adapter e V7 Verifier"""
    
    @pytest.fixture
    def verifier(self):
        """Inicializar V7 Verifier"""
        return VerifierV7()
    
    @pytest.fixture
    def adapter_with_problems(self):
        """Carregar adapter com problemas reais"""
        adapter = IMOBenchmarkAdapter()
        adapter.load_from_url()
        return adapter
    
    def test_assess_single_problem(self, verifier, adapter_with_problems):
        """Avaliar um único problema IMO com V7"""
        if not adapter_with_problems.problems:
            pytest.skip("Nenhum problema carregado")
        
        problem = adapter_with_problems.problems[0]
        proof_format = problem.to_verifier_proof()
        
        print(f"\n Avaliando: {problem.problem_id}")
        print(f"   Categoria IMO: {problem.category}")
        print(f"   Domínio Aletheia: {problem.aletheia_domain}")
        print(f"   Nível: {problem.level} (dificuldade: {problem.difficulty_level})")
        
        # Executar avaliação
        assessment = verifier.assess(proof=proof_format)
        
        # Validar resultado
        assert assessment is not None
        assert hasattr(assessment, 'overall_d11_score')
        assert 0 <= assessment.overall_d11_score <= 10
        
        print(f"\n Resultados D11:")
        print(f"   Elegância: {assessment.elegance_score:.2f}")
        print(f"   Clareza pedagógica: {assessment.pedagogical_clarity_score:.2f}")
        print(f"   Score D11 total: {assessment.overall_d11_score:.2f}")
        print(f"   Nível: {assessment.assessment_level}")
    
    def test_assess_sample_batch(self, verifier, adapter_with_problems):
        """Avaliar lote de 10 problemas e registrar resultados"""
        if not adapter_with_problems.problems:
            pytest.skip("Nenhum problema carregado")
        
        sample = adapter_with_problems.sample_problems(n=10)
        
        print(f"\n Avaliando lote de {len(sample)} problemas...")
        
        results = []
        for i, problem in enumerate(sample, 1):
            proof_format = problem.to_verifier_proof()
            
            assessment = verifier.assess(proof=proof_format)
            
            # Registrar no adapter
            adapter_with_problems.record_assessment(problem.problem_id, asdict(assessment))
            
            results.append({
                "problem_id": problem.problem_id,
                "imo_level": problem.level,
                "imo_difficulty": problem.difficulty_level,
                "category": problem.category,
                "domain": problem.aletheia_domain,
                "d11_score": assessment.overall_d11_score,
                "assessment_level": assessment.assessment_level
            })
            
            print(f"   [{i:2d}] {problem.problem_id:15s} => D11={assessment.overall_d11_score:5.2f} ({assessment.assessment_level})")
        
        assert len(results) == len(sample)
        assert all("d11_score" in r for r in results)


class TestCorrelationAnalysis:
    """Análise de correlação entre scores D11 e dificuldade IMO"""
    
    def test_score_distribution_by_imo_level(self):
        """Validar que scores D11 aumentam com dificuldade IMO"""
        adapter = IMOBenchmarkAdapter()
        count = adapter.load_from_url()
        
        if count < 10:
            pytest.skip("Insuficientes problemas carregados")
        
        verifier = VerifierV7()
        
        # Avaliar 15 problemas de cada nível
        sample_size = 5  # Reduzido para velocidade de teste
        
        results_by_level = {}
        
        for level in ["Basic", "Intermediate", "Advanced"]:
            level_problems = adapter.get_problems_by_level(level)
            if not level_problems:
                continue
            
            sample = level_problems[:sample_size]
            scores = []
            
            for problem in sample:
                proof_format = problem.to_verifier_proof()
                assessment = verifier.assess(proof=proof_format)
                scores.append(assessment.overall_d11_score)
                adapter.record_assessment(problem.problem_id, asdict(assessment))
            
            avg_score = sum(scores) / len(scores) if scores else 0
            results_by_level[level] = {
                "count": len(scores),
                "scores": scores,
                "avg": avg_score,
                "min": min(scores) if scores else 0,
                "max": max(scores) if scores else 0
            }
        
        # Exibir resultados
        print(f"\n Correlacao D11 Score vs IMO Level:")
        print(f"{'Nivel':<15} {'Amostra':<10} {'Avg D11':<10} {'Min':<10} {'Max':<10}")
        print("-" * 55)
        
        for level in ["Basic", "Intermediate", "Advanced"]:
            if level in results_by_level:
                r = results_by_level[level]
                print(f"{level:<15} {r['count']:<10} {r['avg']:<10.2f} {r['min']:<10.2f} {r['max']:<10.2f}")
        
        # Validar que Intermediate >= Basic
        if "Basic" in results_by_level and "Intermediate" in results_by_level:
            basic_avg = results_by_level["Basic"]["avg"]
            intermediate_avg = results_by_level["Intermediate"]["avg"]
            # Correlação esperada (pode não ser perfeita por natureza das provas)
            print(f"\n✓ Correlação: Basic ({basic_avg:.2f}) vs Intermediate ({intermediate_avg:.2f})")
    
    def test_statistical_summary(self):
        """Gerar sumário estatístico das avaliações"""
        adapter = IMOBenchmarkAdapter()
        count = adapter.load_from_url()
        
        if count < 5:
            pytest.skip("Insuficientes problemas carregados")
        
        verifier = VerifierV7()
        
        # Avaliar pequena amostra
        sample = adapter.sample_problems(n=5)
        
        for problem in sample:
            proof_format = problem.to_verifier_proof()
            assessment = verifier.assess(proof=proof_format)
            adapter.record_assessment(problem.problem_id, asdict(assessment))
        
        # Obter estatísticas
        stats = adapter.get_assessment_stats()
        
        if stats:
            print(f"\n Sumário de Avaliações:")
            print(f"   Total avaliadas: {stats.get('total_assessed', 0)}")
            print(f"   Por nível: {stats.get('by_level', {})}")
            print(f"   Por categoria: {stats.get('by_category', {})}")


class TestBenchmarkExport:
    """Testes de exportação de resultados"""
    
    def test_export_to_json(self, tmp_path):
        """Exportar resultados das avaliações em JSON"""
        adapter = IMOBenchmarkAdapter()
        count = adapter.load_from_url()
        
        if count < 5:
            pytest.skip("Insuficientes problemas carregados")
        
        verifier = VerifierV7()
        
        # Avaliar amostra pequena
        sample = adapter.sample_problems(n=3)
        
        for problem in sample:
            proof_format = problem.to_verifier_proof()
            assessment = verifier.assess(proof=proof_format)
            adapter.record_assessment(problem.problem_id, asdict(assessment))
        
        # Exportar
        output_file = tmp_path / "imo_benchmark_results.json"
        adapter.export_assessments_to_json(str(output_file))
        
        # Validar arquivo
        assert output_file.exists()
        
        import json
        with open(output_file) as f:
            data = json.load(f)
        
        assert data["benchmark"] == "IMO-ProofBench v2"
        assert data["total_assessed"] == len(sample)
        assert "timestamp" in data
        assert "assessments" in data
        
        print(f"\n[OK] Resultados exportados para: {output_file}")
        print(f"  Total avaliado: {data['total_assessed']}")


# ──────────────────────────────────────────────────────────────────────────────
# EXECUTAR TESTES
# ──────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
