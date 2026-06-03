#!/usr/bin/env python3
"""
Formalizador: Problema (LaTeX) → Declaração Lean 4

Converte enunciados de problemas de wiki Erdős para código Lean estruturado.

Uso:
    formalizador = ProblemFormalizerLean()
    theo_decl = formalizador.formalize_from_latex(problema_latex)
    print(theo_decl)
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ProblemFormalizerLean:
    """Converte enunciados de problemas para Lean 4."""
    
    # Mapeamento de domínios para imports Mathlib relevantes
    DOMAIN_IMPORTS = {
        "number_theory": [
            "import Mathlib.Data.Nat.Basic",
            "import Mathlib.Data.Int.Basic",
            "import Mathlib.NumberTheory.Divisors",
        ],
        "combinatorics": [
            "import Mathlib.Data.Finset.Basic",
            "import Mathlib.Combinatorics.Additive.SumFree",
            "import Mathlib.Combinatorics.Configuration",
        ],
        "geometry": [
            "import Mathlib.Geometry.Euclidean.Basic",
            "import Mathlib.Geometry.EuclideanGeometry.Basic",
        ],
        "analysis": [
            "import Mathlib.Analysis.SpecialFunctions.Real",
            "import Mathlib.Analysis.Calculus.Deriv.Basic",
        ],
        "algebra": [
            "import Mathlib.Algebra.Group.Basic",
            "import Mathlib.Algebra.Ring.Basic",
        ],
    }
    
    def __init__(self):
        """Inicializar formalizador."""
        self.pattern_quantifiers = self._compile_quantifier_patterns()
        self.pattern_operators = self._compile_operator_patterns()
    
    @staticmethod
    def _compile_quantifier_patterns() -> Dict[str, str]:
        """Compilar padrões para quantificadores e conectivos."""
        return {
            "forall": r"(?:para todo|para quaisquer|seja|sejam|qualquer)\s+(\w+)",
            "exists": r"(?:existe|existem|há)\s+(?:um|uma|pelo menos um)\s+(\w+)",
            "and": r"(?:e|além disso|também)",
            "or": r"(?:ou|um dos dois)",
            "implies": r"(?:então|logo|implica que|se.*então)",
            "iff": r"(?:se e somente se|sse|equivalente a)",
        }
    
    @staticmethod
    def _compile_operator_patterns() -> Dict[str, str]:
        """Compilar padrões para operadores matemáticos."""
        return {
            "divisible": r"(?:divide|divisível por|é divisor de)",
            "prime": r"(?:primo|primos)",
            "gcd": r"(?:máximo divisor comum|mdc)",
            "lcm": r"(?:mínimo múltiplo comum|mmc)",
            "sum": r"(?:soma|somatório)",
            "product": r"(?:produto|multiplicação)",
        }
    
    def formalize_from_latex(
        self,
        problem_latex: str,
        domain: str = "general",
        theorem_name: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Formalizar problema em LaTeX para Lean 4.
        
        Args:
            problem_latex: Enunciado em LaTeX (ex: "Prove that $n^2 > n$ for all $n > 1$")
            domain: Domínio (number_theory, combinatorics, geometry, etc.)
            theorem_name: Nome do teorema Lean (auto-gerado se None)
        
        Returns:
            {
                "theorem_name": str,
                "imports": List[str],
                "theorem_declaration": str,
                "proof_skeleton": str,
                "full_code": str
            }
        """
        
        # Passo 1: Limpar LaTeX
        cleaned = self._clean_latex(problem_latex)
        logger.info(f"Problema limpo: {cleaned[:80]}...")
        
        # Passo 2: Extrair componentes
        components = self._extract_components(cleaned)
        logger.info(f"Componentes: {components}")
        
        # Passo 3: Gerar nome do teorema
        if not theorem_name:
            theorem_name = self._generate_theorem_name(cleaned)
        
        # Passo 4: Montar declaração Lean
        imports = self.DOMAIN_IMPORTS.get(domain, self.get_default_imports())
        theo_decl = self._build_theorem_declaration(theorem_name, components, domain)
        
        # Passo 5: Esqueleto de prova
        proof_skeleton = self._build_proof_skeleton(components, domain)
        
        # Passo 6: Código completo
        full_code = self._assemble_full_code(imports, theo_decl, proof_skeleton)
        
        return {
            "theorem_name": theorem_name,
            "imports": imports,
            "theorem_declaration": theo_decl,
            "proof_skeleton": proof_skeleton,
            "full_code": full_code
        }
    
    @staticmethod
    def _clean_latex(text: str) -> str:
        """Remover marcadores LaTeX e normalizar."""
        # Remover delimitadores $...$
        text = re.sub(r'\$([^$]+)\$', r'\1', text)
        
        # Remover \text{...}
        text = re.sub(r'\\text\{([^}]+)\}', r'\1', text)
        
        # Normalizar espaços
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def _extract_components(self, problem_text: str) -> Dict:
        """
        Extrair componentes estruturados do enunciado.
        
        Returns:
            {
                "type": "prove" | "compute" | "characterize",
                "variables": List[str],
                "hypotheses": List[str],
                "conclusion": str,
                "domain_keywords": List[str]
            }
        """
        components = {
            "type": "prove",
            "variables": [],
            "hypotheses": [],
            "conclusion": "",
            "domain_keywords": []
        }
        
        # Detectar tipo de problema
        if any(word in problem_text.lower() for word in ["prove", "mostre", "demonstre", "prove que"]):
            components["type"] = "prove"
        elif any(word in problem_text.lower() for word in ["compute", "calcule", "determine"]):
            components["type"] = "compute"
        elif any(word in problem_text.lower() for word in ["characterize", "caracterize", "descreva"]):
            components["type"] = "characterize"
        
        # Extrair variáveis (padrão: "seja x", "para todo n", etc.)
        var_matches = re.findall(r'(?:seja|sejam|para todo|para quaisquer)\s+([a-zA-Z_]\w*)', problem_text, re.IGNORECASE)
        components["variables"] = list(set(var_matches))
        
        # Extrair conclusão (após "prove que", "então", "logo")
        conclusion_match = re.search(
            r'(?:prove que|mostre que|demonstre que|then|então|logo)\s+(.+?)(?:\.|$)',
            problem_text,
            re.IGNORECASE
        )
        if conclusion_match:
            components["conclusion"] = conclusion_match.group(1).strip()
        else:
            components["conclusion"] = problem_text  # Fallback: texto inteiro
        
        # Extrair keywords de domínio
        domain_keywords = []
        for keyword_set, keywords in [
            ("number_theory", ["divisível", "primo", "mdc", "número inteiro", "divisor"]),
            ("combinatorics", ["conjunto", "finito", "combinação", "permutação"]),
            ("geometry", ["ponto", "linha", "distância", "ângulo", "triângulo"]),
        ]:
            if any(kw.lower() in problem_text.lower() for kw in keywords):
                domain_keywords.append(keyword_set)
        components["domain_keywords"] = domain_keywords
        
        return components
    
    @staticmethod
    def _generate_theorem_name(problem_text: str) -> str:
        """Gerar nome do teorema a partir do enunciado."""
        # Estratégia: extrair primeiras 3-5 palavras, sanitizar
        words = re.findall(r'\b[a-zA-Z]+\b', problem_text.lower())
        
        # Filtrar palavras comuns
        common_words = {"prove", "mostre", "demonstre", "que", "para", "seja", "sejam"}
        words = [w for w in words if w not in common_words][:4]
        
        theorem_name = "_".join(words) if words else "theorem"
        
        # Sanitizar
        theorem_name = re.sub(r'[^a-z0-9_]', '', theorem_name)
        
        return theorem_name or "theorem"
    
    def _build_theorem_declaration(self, name: str, components: Dict, domain: str) -> str:
        """Montar declaração do teorema."""
        vars_str = " ".join([f"({var} : ℕ)" for var in components.get("variables", ["n"])])
        conclusion = components.get("conclusion", "True")
        
        theo_decl = f"""theorem {name} {vars_str} : {conclusion} := by
  sorry"""
        
        return theo_decl
    
    def _build_proof_skeleton(self, components: Dict, domain: str) -> str:
        """Montar esqueleto de prova com táticas relevantes."""
        proof_type = components.get("type", "prove")
        
        if proof_type == "prove":
            skeleton = """  -- Introduza hipóteses
  intro h₁
  -- Desdobra definições
  unfold <PREDICATE>
  -- Aplique lemas/teoremas conhecidos
  apply <LEMMA>
  -- Complete os subgoals
  sorry"""
        elif proof_type == "compute":
            skeleton = """  -- Simplifique expressões
  simp [<DEFINITIONS>]
  -- Calcule passo a passo
  norm_num
  sorry"""
        else:  # characterize
            skeleton = """  -- Mostre que ↔ em ambas as direções
  constructor
  · -- Direção 1
    sorry
  · -- Direção 2
    sorry"""
        
        return skeleton
    
    @staticmethod
    def _assemble_full_code(imports: List[str], theo_decl: str, skeleton: str) -> str:
        """Montar código Lean completo."""
        code = "\n".join(imports) + "\n"
        code += "import Mathlib.Tactic\n\n"
        code += theo_decl
        
        return code
    
    @staticmethod
    def get_default_imports():
        """Retornar imports padrão."""
        return [
            "import Mathlib.Data.Nat.Basic",
            "import Mathlib.Data.Real.Basic",
            "import Mathlib.Tactic",
        ]


def main():
    """Testar formalizador."""
    formalizador = ProblemFormalizerLean()
    
    # Problema de teste (número theory)
    problema_1 = r"""
    Prove that for all natural numbers $n > 1$, 
    if $n$ is prime, then $n$ divides $(n-1)! + 1$.
    """
    
    logger.info("=== Formalizar Problema 1 (Number Theory) ===")
    resultado_1 = formalizador.formalize_from_latex(problema_1, domain="number_theory")
    print(resultado_1["full_code"])
    print("\n" + "="*60 + "\n")
    
    # Problema de teste (combinatorics)
    problema_2 = r"""
    Let $A$ be a finite set of integers. Prove that there exists 
    a subset $B \subseteq A$ such that the sum of elements in $B$ 
    is divisible by $|A|$.
    """
    
    logger.info("=== Formalizar Problema 2 (Combinatorics) ===")
    resultado_2 = formalizador.formalize_from_latex(problema_2, domain="combinatorics")
    print(resultado_2["full_code"])
    

if __name__ == "__main__":
    main()
