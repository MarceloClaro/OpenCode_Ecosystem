#!/usr/bin/env python3
"""
Gerador de Provas com OpenCode Big Pickle

Usa modelo big-pickle do ecossistema OpenCode para gerar provas em:
  1. Linguagem natural (interpretável, para revisão)
  2. Código Lean direto (verificável)

Contexto: até 8K tokens (margem de segurança para iteração)

Uso:
    generator = ProofGeneratorOpenCode()
    result = generator.generate(
        problem_statement="...",
        lean_skeleton="...",
        domain="number_theory"
    )
    # result = {
    #     "natural_proof": "...",
    #     "lean_code": "...",
    #     "confidence": 0.75,
    #     "reasoning": "..."
    # }
"""

import json
import logging
from pathlib import Path
from typing import Dict, Optional, List
from dataclasses import dataclass, asdict
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class ProofCandidate:
    """Candidato de prova gerado."""
    problem_id: str
    natural_proof: str
    lean_code: str
    confidence: float  # 0.0-1.0
    reasoning: str
    tokens_used: int
    model: str
    timestamp: str


class ProofGeneratorOpenCode:
    """
    Gerador de provas usando OpenCode big-pickle.
    
    Pipeline:
      1. Carregar configuração OpenCode
      2. Preparar prompt multi-shot com exemplos
      3. Chamar modelo com problema + skeleton Lean
      4. Extrair prova natural + código Lean
      5. Validar sintaxe básica
    """
    
    def __init__(self, config_path: str = "~/.config/opencode/opencode.json"):
        """
        Inicializar gerador.
        
        Args:
            config_path: Path à configuração OpenCode
        """
        self.config_path = Path(config_path).expanduser()
        self.config = self._load_config()
        self.model = self.config.get("model", "opencode/big-pickle")
        
        logger.info(f"✓ ProofGeneratorOpenCode inicializado")
        logger.info(f"  Modelo: {self.model}")
    
    def _load_config(self) -> Dict:
        """Carregar configuração OpenCode."""
        if not self.config_path.exists():
            logger.warning(f"Config não encontrado em {self.config_path}")
            return {"model": "opencode/big-pickle"}
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Erro carregando config: {e}")
            return {"model": "opencode/big-pickle"}
    
    def _build_prompt(
        self,
        problem_statement: str,
        lean_skeleton: str,
        domain: str = "general"
    ) -> str:
        """
        Construir prompt multi-shot para geração de prova.
        
        Estrutura:
          1. Instrução de sistema
          2. 2-3 exemplos (few-shot)
          3. Problema alvo
          4. Skeleton Lean
          5. Solicitar: natural proof + Lean code
        
        Contexto: ~7K tokens (deixar margem para resposta)
        """
        
        system_instruction = """Você é um matemático especialista em provas formais e verificação com Lean 4.

Sua tarefa: gerar DUAS saídas para cada problema:
  1. PROVA NATURAL: explicação passo-a-passo em português, interpretável para humanos
  2. CÓDIGO LEAN: implementação verificável em Lean 4

Regras:
  - Prova natural: clara, rigorosa, com justificativas de cada passo
  - Código Lean: sintaticamente correto, compilável com as importações dadas
  - Se você não tiver certeza, use `sorry` e explique a lacuna
  - Evite suposições não declaradas; sempre cite definições usadas

Formato de resposta:
```
PROVA NATURAL:
<texto em português>

CÓDIGO LEAN:
<código Lean>
```"""

        # Exemplos few-shot
        examples = self._get_few_shot_examples(domain)
        
        # Prompt final
        prompt = f"""{system_instruction}

{examples}

---

PROBLEMA ALVO:

Enunciado:
{problem_statement}

Skeleton Lean fornecido:
```lean
{lean_skeleton}
```

Gere a prova natural e o código Lean completo."""
        
        return prompt
    
    def _get_few_shot_examples(self, domain: str) -> str:
        """Retornar exemplos few-shot por domínio."""
        
        examples = {
            "number_theory": """
EXEMPLO 1 (Número Theory):

Problema: Prove que se p é primo e p | a*b, então p | a ou p | b.

PROVA NATURAL:
Seja p primo. Suponha p | ab e suponha p ∤ a. Precisamos mostrar p | b.
Como p é primo e p ∤ a, temos mdc(p, a) = 1 (pois os únicos divisores de p são 1 e p).
Pelo Lema de Bézout, existem inteiros x, y tais que px + ay = 1.
Multiplicando por b: pbx + aby = b.
Como p | ab (por hipótese), temos p | aby.
Claramente p | pbx.
Logo, p | (pbx + aby) = b.

CÓDIGO LEAN:
theorem prime_divides_mul_iff_divides_left {p a b : ℕ} (hp : Prime p) :
    p ∣ a * b ↔ p ∣ a ∨ p ∣ b := by
  constructor
  · intro h
    cases' hp.eq_one_or_self_of_dvd a (dvd_mul_right_cancel h) with h1 h2
    · sorry  -- caso p = 1, absurdo
    · right
      exact hp.dvd_mul_of_dvd_left (dvd_mul_right a b) h
  · intro h
    cases h with
    | inl ha => exact dvd_mul_of_dvd_left ha b
    | inr hb => exact dvd_mul_of_dvd_right hb a
""",
            
            "combinatorics": """
EXEMPLO 1 (Combinatorics):

Problema: Prove que em qualquer grupo de 6 pessoas, ou 3 são amigos mútuos ou 3 são estranhos mútuos.

PROVA NATURAL:
Este é o Teorema de Ramsey R(3,3) = 6.
Fixe uma pessoa P. Ela tem 5 outras pessoas.
Pela pigeonhole, entre essas 5, ou ≥3 são amigas de P, ou ≥3 são inimigas de P.
Caso 1: 3 amigas de P (digamos A, B, C).
  Se A-B são amigos: (P, A, B) são amigos mútuos. ✓
  Se A-B são inimigos: então A, C ou B, C são inimigos? 
    Se A-C inimigos e B-C inimigos: (A, B, C) são inimigos mútuos. ✓
Caso 2: análogo com inimigos.

CÓDIGO LEAN:
-- Simulação: pigeonhole + casework
theorem ramsey_3_3 : ∀ (G : SimpleGraph (Fin 6)),
    (∃ s : Finset (Fin 6), s.card = 3 ∧ s.allPairsAdjacent G) ∨
    (∃ s : Finset (Fin 6), s.card = 3 ∧ s.allPairsNonAdjacent G) := by
  sorry  -- verificação casework de Ramsey, combinatorialmente intensiva
""",
            
            "general": """
EXEMPLO 1 (General):

Problema: Prove que a soma dos primeiros n números naturais é n(n+1)/2.

PROVA NATURAL:
Usamos indução sobre n.
Base (n=0): 0 = 0·1/2. ✓
Passo: Assuma Σᵢ₌₀ⁿ i = n(n+1)/2.
Queremos: Σᵢ₌₀ⁿ⁺¹ i = (n+1)(n+2)/2.
Σᵢ₌₀ⁿ⁺¹ i = (Σᵢ₌₀ⁿ i) + (n+1)
           = n(n+1)/2 + (n+1)
           = (n+1)(n/2 + 1)
           = (n+1)(n+2)/2 ✓

CÓDIGO LEAN:
theorem sum_nat_eq_triangular (n : ℕ) :
    (∑ i in Finset.range (n + 1), i) = n * (n + 1) / 2 := by
  induction n with
  | zero => norm_num
  | succ n ih =>
      simp [Finset.sum_range_succ, ih]
      ring
"""
        }
        
        return examples.get(domain, examples["general"])
    
    def generate(
        self,
        problem_statement: str,
        lean_skeleton: str,
        problem_id: str = "unknown",
        domain: str = "general"
    ) -> ProofCandidate:
        """
        Gerar prova para problema.
        
        Args:
            problem_statement: Enunciado do problema
            lean_skeleton: Skeleton Lean fornecido
            problem_id: ID do problema
            domain: Domínio (number_theory, combinatorics, etc)
        
        Returns:
            ProofCandidate com prova natural + Lean code
        """
        logger.info(f"\n{'='*70}")
        logger.info(f"GERAÇÃO DE PROVA: {problem_id}")
        logger.info(f"{'='*70}")
        
        # 1. Construir prompt
        prompt = self._build_prompt(problem_statement, lean_skeleton, domain)
        
        logger.info(f"  [1/3] Prompt construído ({len(prompt)} chars)")
        
        # 2. Chamar modelo
        logger.info(f"  [2/3] Chamando {self.model}...")
        try:
            response = self._call_model(prompt)
        except Exception as e:
            logger.error(f"  ✗ Erro ao chamar modelo: {e}")
            return ProofCandidate(
                problem_id=problem_id,
                natural_proof="<erro ao gerar>",
                lean_code="sorry",
                confidence=0.0,
                reasoning=f"Erro: {str(e)}",
                tokens_used=0,
                model=self.model,
                timestamp=datetime.now().isoformat()
            )
        
        logger.info(f"  ✓ Resposta recebida ({len(response)} chars)")
        
        # 3. Extrair natural proof + Lean code
        logger.info(f"  [3/3] Extraindo componentes...")
        natural_proof, lean_code = self._extract_proofs(response)
        
        # 4. Validar
        confidence = self._assess_confidence(natural_proof, lean_code)
        
        logger.info(f"  ✓ Prova gerada (confiança: {confidence:.0%})")
        
        return ProofCandidate(
            problem_id=problem_id,
            natural_proof=natural_proof,
            lean_code=lean_code,
            confidence=confidence,
            reasoning=f"Gerado com {self.model}",
            tokens_used=len(prompt.split()) + len(response.split()),
            model=self.model,
            timestamp=datetime.now().isoformat()
        )
    
    def _call_model(self, prompt: str) -> str:
        """
        Chamar modelo OpenCode big-pickle.
        
        IMPORTANTE: Em produção, isto faria uma chamada real à API.
        Para teste, simulamos uma resposta realista.
        
        Args:
            prompt: Prompt formatado
        
        Returns:
            Resposta do modelo
        """
        # TODO: Integrar com API real do OpenCode
        # Por agora, simulamos com resposta estruturada
        
        logger.warning(f"  ⚠️  Usando simulação (integração real de API pendente)")
        
        # Simulação realista
        simulated_response = """PROVA NATURAL:
Consideramos os casos principais:
1. Se o problema é sobre estruturas finitas, aplicamos contagem/pigeonhole
2. Se sobre números, usamos propriedades de divisibilidade ou congruência
3. Se sobre conjuntos, usamos teoria de conjuntos básica

O argumento prossegue por indução/casework/contradição conforme necessário.

CÓDIGO LEAN:
theorem main_theorem : ∀ x, P x := by
  intro x
  -- caso 1
  by_cases h : Q x
  · exact sorry  -- prova do caso positivo
  · push_neg at h
    exact sorry  -- prova do caso negativo
"""
        return simulated_response
    
    def _extract_proofs(self, response: str) -> tuple[str, str]:
        """
        Extrair prova natural e código Lean da resposta.
        
        Procura por marcadores:
          - "PROVA NATURAL:" ou "NATURAL PROOF:"
          - "CÓDIGO LEAN:" ou "LEAN CODE:"
        
        Returns:
            (natural_proof, lean_code)
        """
        natural_proof = ""
        lean_code = ""
        
        # Buscar PROVA NATURAL
        if "PROVA NATURAL:" in response:
            parts = response.split("PROVA NATURAL:", 1)
            if len(parts) > 1:
                natural_part = parts[1]
                # Buscar fim (antes de CÓDIGO LEAN ou fim)
                if "CÓDIGO LEAN:" in natural_part:
                    natural_proof = natural_part.split("CÓDIGO LEAN:")[0].strip()
                else:
                    natural_proof = natural_part.strip()
        
        # Buscar CÓDIGO LEAN
        if "CÓDIGO LEAN:" in response:
            parts = response.split("CÓDIGO LEAN:", 1)
            if len(parts) > 1:
                lean_part = parts[1].strip()
                # Remover marcas de código se presentes
                if lean_part.startswith("```"):
                    lean_part = lean_part[3:]
                if lean_part.endswith("```"):
                    lean_part = lean_part[:-3]
                lean_code = lean_part.strip()
        
        if not natural_proof:
            natural_proof = response[:500]  # fallback
        if not lean_code:
            lean_code = "sorry"  # fallback seguro
        
        return natural_proof, lean_code
    
    def _assess_confidence(self, natural_proof: str, lean_code: str) -> float:
        """
        Avaliar confiança da prova gerada.
        
        Heurísticas:
          - Tem "sorry"? → confiança baixa (0.3-0.5)
          - Tem prova natural estruturada? → +0.2
          - Lean code bem-formado? → +0.2
          - Tem por que/porque? → +0.1
        
        Returns:
            Confiança em [0.0, 1.0]
        """
        confidence = 0.5  # base
        
        # Penalidades
        if "sorry" in lean_code.lower():
            confidence -= 0.2
        
        if len(natural_proof) < 50:
            confidence -= 0.15
        
        # Bônus
        if any(word in natural_proof.lower() for word in 
               ["por indução", "por contradição", "por casos", "lema", "pelo teorema"]):
            confidence += 0.15
        
        if any(word in lean_code.lower() for word in
               ["theorem", "proof", "by", "simp", "ring"]):
            confidence += 0.15
        
        # Clamped
        return max(0.0, min(1.0, confidence))
    
    def save_candidate(
        self,
        candidate: ProofCandidate,
        output_dir: str = "results/proof_candidates"
    ) -> Path:
        """Salvar candidato em JSON."""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        file_path = output_path / f"{candidate.problem_id}_candidate.json"
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(asdict(candidate), f, indent=2, ensure_ascii=False)
        
        logger.info(f"  ✓ Candidato salvo: {file_path}")
        return file_path


    def _simulate_response(self, prompt: str) -> str:
        """
        Simular resposta do modelo (para fase refinement).
        
        Usado em Phase C quando tentamos refinar provas baseado em erros Lean.
        Retorna uma prova genérica estruturada.
        """
        # Resposta genérica estruturada
        return """
PROVA NATURAL:
Consideramos a estrutura do problema e aplicamos técnicas padrão de prova:
1. Se envolve contagem ou desigualdades, usamos pigeonhole/induction
2. Se envolve números, usamos propriedades aritméticas
3. Se envolve conjuntos, usamos teoria de conjuntos

CÓDIGO LEAN:
```lean
theorem refined_proof : ∀ x, P x := by
  intro x
  -- Análise de casos
  by_cases h : Q x
  · -- Caso positivo
    sorry
  · -- Caso negativo
    push_neg at h
    sorry
```
"""


def main():
    """Test proof generation."""
    generator = ProofGeneratorOpenCode()
    
    test_problem = "Prove que a soma dos primeiros n números naturais é n(n+1)/2."
    test_skeleton = """
    theorem sum_nat_eq_triangular (n : ℕ) :
        (∑ i in Finset.range (n + 1), i) = n * (n + 1) / 2 := by
      sorry
    """
    
    test_skeleton = """
    theorem sum_nat_eq_triangular (n : ℕ) :
        (∑ i in Finset.range (n + 1), i) = n * (n + 1) / 2 := by
      sorry
    """
    
    candidate = generator.generate(
        problem_statement=test_problem,
        lean_skeleton=test_skeleton,
        problem_id="TEST0001",
        domain="number_theory"
    )
    
    print("\n" + "="*70)
    print("RESULTADO")
    print("="*70)
    print(f"Confiança: {candidate.confidence:.0%}")
    print(f"\nProva Natural:\n{candidate.natural_proof}\n")
    print(f"Código Lean:\n{candidate.lean_code}\n")
    
    generator.save_candidate(candidate)


if __name__ == "__main__":
    main()
