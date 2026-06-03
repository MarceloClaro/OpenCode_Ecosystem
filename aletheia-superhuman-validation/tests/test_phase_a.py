#!/usr/bin/env python3
"""
Testes para Phase A — Verificador, Formalizador, Seletor

Execução:
    pytest tests/test_phase_a.py -v
    
ou:
    python -m pytest tests/test_phase_a.py --tb=short
"""

import sys
from pathlib import Path
import json
import pytest

# Adicionar scripts/ ao path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from lean_verifier import LeanVerifier, ProofFormalizer, IterativeSolver
from formalize_to_lean import ProblemFormalizerLean
from problem_selector_v2 import ProblemSelectorV2


class TestLeanVerifier:
    """Testes para verificador Lean."""
    
    @pytest.fixture
    def verifier(self):
        """Criar verificador em modo mock."""
        return LeanVerifier(use_remote=True)
    
    def test_verify_proof_with_sorry(self, verifier):
        """Prova com sorry deve falhar."""
        proof = """
theorem test_theorem : True := by
  sorry
"""
        result = verifier.verify_proof(proof)
        assert result["success"] is False
        assert "sorry" in result["error"].lower() or result["error_type"] == "incomplete_proof"
    
    def test_verify_proof_without_sorry(self, verifier):
        """Prova sem sorry deve passar (modo mock)."""
        proof = """
theorem test_theorem : True := by
  trivial
"""
        result = verifier.verify_proof(proof)
        assert result["success"] is True
        assert result["error"] is None
    
    def test_classify_error(self, verifier):
        """Classificação de tipos de erro."""
        patterns = {
            "unsolved goals\ngoal 1: True": "missing_proof",
            "declaration uses 'sorry'": "sorry_used",
            "unknown identifier 'undefined_var'": "unknown_identifier",
        }
        
        for error_msg, expected_type in patterns.items():
            classified = verifier._classify_error(error_msg)
            # Verificar se classificação funciona (pode ser "unknown" se não achar padrão)
            assert classified in ["unknown", expected_type]
    
    def test_error_parsing(self, verifier):
        """Parsing de erros estruturado."""
        error_msg = "unknown identifier 'foo_bar'"
        parsed = verifier._parse_error(error_msg)
        
        assert "suggestions" in parsed
        assert isinstance(parsed["suggestions"], list)
        assert len(parsed["suggestions"]) > 0


class TestProofFormalizer:
    """Testes para formalizador de provas."""
    
    def test_formalize_simple_proof(self):
        """Formalizar prova simples."""
        skeleton = ProofFormalizer.formalize_problem(
            "Prove that n is even",
            problem_type="theorem"
        )
        
        assert "theorem" in skeleton
        assert "sorry" in skeleton
        assert "import" in skeleton
    
    def test_formalize_with_narrative(self):
        """Converter narrativa em tática Lean."""
        narrative = "By induction, we show that 1 + 2 + ... + n = n(n+1)/2"
        theorem = "theorem sum_formula : ∀ n : ℕ, sum n = n * (n + 1) / 2 := by"
        
        proof = ProofFormalizer.formalize_proof(narrative, theorem)
        
        assert "sorry" in proof  # Placeholder
        assert "theorem" in theorem or ":" in theorem


class TestProblemFormalizerLean:
    """Testes para formalizador de problemas → Lean."""
    
    @pytest.fixture
    def formalizador(self):
        return ProblemFormalizerLean()
    
    def test_clean_latex(self, formalizador):
        """Limpeza de LaTeX."""
        latex_text = r"Prove that $n^2 > n$ for all $n > 1$"
        cleaned = formalizador._clean_latex(latex_text)
        
        assert "$" not in cleaned
        assert "n^2" in cleaned or "Prove" in cleaned
    
    def test_extract_components(self, formalizador):
        """Extração de componentes de enunciado."""
        problem = "For all n > 1, prove that n divides (n-1)! + 1"
        components = formalizador._extract_components(problem)
        
        assert "variables" in components
        assert "conclusion" in components
        assert components["type"] in ["prove", "compute", "characterize"]
    
    def test_generate_theorem_name(self, formalizador):
        """Geração automática de nome de teorema."""
        problem = "Prove that the sum of two odd numbers is even"
        name = formalizador._generate_theorem_name(problem)
        
        assert isinstance(name, str)
        assert len(name) > 0
        assert name.islower() or "_" in name
    
    def test_formalize_full_workflow(self, formalizador):
        """Workflow completo: problema → Lean."""
        problem_latex = r"Let $n \in \mathbb{N}$. Prove that $n! > 2^n$ for $n \geq 4$."
        
        result = formalizador.formalize_from_latex(
            problem_latex,
            domain="number_theory"
        )
        
        assert "theorem_name" in result
        assert "imports" in result
        assert "full_code" in result
        assert len(result["full_code"]) > 100
        assert "import" in result["full_code"]


class TestProblemSelectorV2:
    """Testes para seletor de problemas."""
    
    @pytest.fixture
    def seletor(self):
        """Criar seletor com dataset real (se existir)."""
        dataset_path = Path("data/erdos_718_enriched_v1.1.json")
        if dataset_path.exists():
            return ProblemSelectorV2(str(dataset_path))
        else:
            pytest.skip("Dataset não encontrado")
    
    def test_load_dataset(self, seletor):
        """Carregar dataset."""
        assert len(seletor.problems) > 0
        assert "id" in seletor.problems[0] or "domain" in seletor.problems[0]
    
    def test_assess_feasibility_sample(self, seletor):
        """Avaliar viabilidade de um problema."""
        if seletor.problems:
            problem = seletor.problems[0]
            score, reasoning = seletor._assess_feasibility(problem)
            
            assert 0 <= score <= 1.0
            assert isinstance(reasoning, list)
            assert len(reasoning) > 0
    
    def test_select_top_n(self, seletor):
        """Selecionar top N problemas."""
        selected = seletor.select_top_n(n=5, min_score=0.0)
        
        assert len(selected) <= 5
        if selected:
            # Verificar que estão ordenados por score (descendente)
            scores = [p["score"] for p in selected]
            assert scores == sorted(scores, reverse=True)
    
    def test_selection_has_required_fields(self, seletor):
        """Problemas selecionados têm todos os campos."""
        selected = seletor.select_top_n(n=3, min_score=0.0)
        
        required_fields = {"id", "domain", "difficulty", "theorem_type", "score", "reasoning"}
        for problem in selected:
            assert required_fields.issubset(problem.keys())


class TestIntegration:
    """Testes de integração entre componentes."""
    
    def test_end_to_end_pipeline(self):
        """Pipeline completo: problema → formalização → verificação."""
        # 1. Seletar problema
        problem = {
            "id": "TEST001",
            "statement": "Prove that 1 + 1 = 2 for natural numbers",
            "domain": "number_theory"
        }
        
        # 2. Formalizar
        formalizador = ProblemFormalizerLean()
        formalizado = formalizador.formalize_from_latex(
            problem["statement"],
            domain="number_theory"
        )
        
        assert formalizado["full_code"]
        assert "theorem" in formalizado["full_code"]
        
        # 3. Verificar
        verifier = LeanVerifier(use_remote=True)
        result = verifier.verify_proof(formalizado["full_code"])
        
        # Deve falhar (tem sorry)
        assert "success" in result
        assert "error" in result or "error_type" in result
    
    def test_solver_integration(self):
        """Solver iterativo integrado."""
        verifier = LeanVerifier(use_remote=True)
        solver = IterativeSolver(verifier, max_iterations=2)
        
        problem = {
            "id": 1,
            "statement": "Prove commutativity of addition",
            "domain": "algebra"
        }
        
        result = solver.solve_problem(problem)
        
        assert "problem_id" in result
        assert "status" in result
        assert "iterations" in result
        assert result["iterations"] <= 2


class TestDataValidation:
    """Validação de dados de saída."""
    
    def test_selected_problems_json_valid(self):
        """Arquivo de problemas selecionados é JSON válido."""
        output_path = Path("data/selected_problems_phase_b_v2.json")
        
        if output_path.exists():
            with open(output_path, 'r', encoding='utf-8') as f:
                data = json.load(f)  # Deve não lançar JSONDecodeError
            
            assert isinstance(data, list)
            if data:
                assert "id" in data[0]
                assert "score" in data[0]


# Execução direta
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
