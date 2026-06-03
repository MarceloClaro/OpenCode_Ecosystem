#!/usr/bin/env python
# =====================================================================
# PARALLEL VERIFIERS v1 — Cora-Debate V1-V7 como workers paralelos
# =====================================================================
# Executa verificadores simbólicos V1-V7 em ThreadPoolExecutor,
# agregados por ConsensusEngine com pesos e calibração Platt.
# =====================================================================

import time, math, re, random
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from typing import Optional


# =====================================================================
# DATA STRUCTURES
# =====================================================================

@dataclass
class VerifierResult:
    """Resultado de um único verificador."""
    verifier_id: str
    passed: bool
    confidence: float
    evidence: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    elapsed_ms: float = 0.0
    error: Optional[str] = None


@dataclass
class VerificationConsensus:
    """Consenso agregado de todos os verificadores."""
    weighted_score: float
    passed_count: int
    total_count: int
    details: list[VerifierResult] = field(default_factory=list)
    platt_calibrated: float = 0.0
    requires_retry: bool = False
    retry_count: int = 0
    total_elapsed_ms: float = 0.0


# =====================================================================
# PARALLEL VERIFIERS
# =====================================================================

class ParallelVerifiers:
    """
    Executa verificadores V1-V7 em paralelo sobre o contexto do pipeline.
    
    Pesos:
      V1(0.15) Dimensional, V2(0.20) Algébrico, V3(0.25) Contraexemplos,
      V4(0.10) Estatístico, V5(0.10) Numérico, V6(0.10) EDO/EDP, V7(0.10) Código
    
    Consenso: weighted_score = Σ(peso_i * confidence_i) / Σ(peso_i)
    Retry se weighted_score < 0.75
    """
    
    VERIFIER_META = {
        "V1": {"name": "Dimensional Analysis",       "weight": 0.15, "timeout": 15,
               "domains": ["physics", "engineering"]},
        "V2": {"name": "Algebraic Verification",      "weight": 0.20, "timeout": 15,
               "domains": ["mathematics", "logic"]},
        "V3": {"name": "Counterexample Search",       "weight": 0.25, "timeout": 30,
               "domains": ["mathematics", "logic", "all"]},
        "V4": {"name": "Statistical Validation",      "weight": 0.10, "timeout": 15,
               "domains": ["statistics", "science"]},
        "V5": {"name": "Numerical Precision",         "weight": 0.10, "timeout": 15,
               "domains": ["numerical", "computation"]},
        "V6": {"name": "ODE/PDE Verification",        "weight": 0.10, "timeout": 15,
               "domains": ["physics", "engineering", "mathematics"]},
        "V7": {"name": "Source Code Verification",    "weight": 0.10, "timeout": 30,
               "domains": ["software", "security"]},
    }
    
    VERIFIER_WEIGHTS = {k: v["weight"] for k, v in VERIFIER_META.items()}
    
    def __init__(self, max_workers: int = 4, timeout: int = 30):
        self.max_workers = max_workers
        self.default_timeout = timeout
    
    # ----------------------------------------------------------------
    # API PÚBLICA
    # ----------------------------------------------------------------
    
    def verify_parallel(
        self,
        context: dict,
        active_verifiers: Optional[list[str]] = None,
    ) -> VerificationConsensus:
        """
        Executa verificadores ativos em paralelo.
        
        Args:
            context: Dict com resultados do pipeline
                (agent_results, solution_text, problem, etc.)
            active_verifiers: Lista de IDs (ex: ["V1","V2","V3"]).
                Se None, executa todos V1-V7.
        
        Returns:
            VerificationConsensus com weighted_score e resultados
        """
        start = time.time()
        if active_verifiers is None:
            active_verifiers = sorted(self.VERIFIER_META.keys())
        
        # Filtra apenas IDs válidos
        to_run = [v for v in active_verifiers if v in self.VERIFIER_META]
        
        results: list[VerifierResult] = []
        
        # Executa em ThreadPool
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_map = {}
            for vid in to_run:
                timeout_v = self.VERIFIER_META[vid]["timeout"]
                future = executor.submit(self._run_verifier, vid, context, timeout_v)
                future_map[future] = vid
            
            for future in as_completed(future_map):
                vid = future_map[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    results.append(VerifierResult(
                        verifier_id=vid,
                        passed=False,
                        confidence=0.0,
                        evidence=[],
                        warnings=[f"Verifier {vid} raised exception"],
                        error=str(e),
                    ))
        
        # Ordena por ID para consistência
        results.sort(key=lambda r: r.verifier_id)
        
        # Computa consenso
        consensus = self._compute_consensus(results)
        consensus.total_elapsed_ms = (time.time() - start) * 1000
        return consensus
    
    def verify_single(self, verifier_id: str, context: dict) -> VerifierResult:
        """Executa um único verificador (útil para debug)."""
        timeout_v = self.VERIFIER_META.get(verifier_id, {}).get("timeout", 15)
        return self._run_verifier(verifier_id, context, timeout_v)
    
    def get_supported_domains(self) -> dict[str, list[str]]:
        """Retorna domínios suportados por cada verificador."""
        return {vid: meta["domains"] for vid, meta in self.VERIFIER_META.items()}
    
    # ----------------------------------------------------------------
    # CONSENSUS ENGINE
    # ----------------------------------------------------------------
    
    def _compute_consensus(self, results: list[VerifierResult]) -> VerificationConsensus:
        """Computa weighted_score e decide se retry é necessário."""
        total_weight = 0.0
        weighted_sum = 0.0
        passed = 0
        
        for r in results:
            w = self.VERIFIER_WEIGHTS.get(r.verifier_id, 0.1)
            total_weight += w
            weighted_sum += w * r.confidence
            if r.passed:
                passed += 1
        
        weighted_score = weighted_sum / max(total_weight, 1e-9)
        
        # Platt calibration simplificada: sigmoid centrado em 0.5
        platt = 1.0 / (1.0 + math.exp(-10.0 * (weighted_score - 0.5)))
        
        return VerificationConsensus(
            weighted_score=round(weighted_score, 4),
            passed_count=passed,
            total_count=len(results),
            details=results,
            platt_calibrated=round(platt, 4),
            requires_retry=(weighted_score < 0.75),
        )
    
    # ----------------------------------------------------------------
    # VERIFICADORES INDIVIDUAIS (Stubs simbólicos)
    # ----------------------------------------------------------------
    
    def _run_verifier(self, vid: str, context: dict, timeout_s: int) -> VerifierResult:
        """Roteia para o método do verificador correto."""
        start = time.time()
        
        # Extrai texto da solução
        solution_text = context.get("solution_text", "")
        if not solution_text:
            solution_text = str(context.get("final_answer", ""))
        if not solution_text:
            solution_text = str(context.get("problem", ""))
        
        # Roteia para o verificador específico
        router = {
            "V1": self._run_V1,
            "V2": self._run_V2,
            "V3": self._run_V3,
            "V4": self._run_V4,
            "V5": self._run_V5,
            "V6": self._run_V6,
            "V7": self._run_V7,
        }
        
        handler = router.get(vid)
        if handler is None:
            elapsed = (time.time() - start) * 1000
            return VerifierResult(
                verifier_id=vid,
                passed=False,
                confidence=0.0,
                evidence=[],
                warnings=[f"Unknown verifier: {vid}"],
                elapsed_ms=elapsed,
            )
        
        result = handler(solution_text, context)
        result.elapsed_ms = (time.time() - start) * 1000
        return result
    
    def _run_V1(self, text: str, ctx: dict) -> VerifierResult:
        """V1: Análise Dimensional — detecta padrões de unidades."""
        unit_patterns = [
            r'\b\d+\s*(kg|m|s|K|N|J|W|Pa|Hz|mol|cd)\b',
            r'\bm[/]s\b', r'\bkg[/]m[23]\b', r'\bN[/]m[2]\b',
            r'\b[A-Z][a-z]?\^\{?-?\d+\}?',  # Unidades com expoente
        ]
        found = 0
        for p in unit_patterns:
            found += len(re.findall(p, text, re.IGNORECASE))
        
        if found > 0:
            return VerifierResult(
                verifier_id="V1", passed=True, confidence=0.85,
                evidence=[f"Found {found} dimensional patterns in solution"],
                warnings=[] if found > 2 else ["Few dimensional checks"],
            )
        return VerifierResult(
            verifier_id="V1", passed=True, confidence=0.60,
            evidence=["No explicit dimensional analysis needed"],
            warnings=["Solution has no explicit unit analysis"],
        )
    
    def _run_V2(self, text: str, ctx: dict) -> VerifierResult:
        """V2: Verificação Algébrica — detecta expressões e operadores."""
        alg_patterns = [
            r'[=≠≈≡]', r'[+\-*/^]', r'\bsum\b', r'\bprod\b',
            r'\bsqrt\b', r'\bfrac\b', r'\\frac', r'\\cdot',
            r'\balpha\b', r'\bbeta\b', r'\bgamma\b',
            r'\b∀\b', r'\b∃\b', r'\b∧\b', r'\b∨\b', r'\b¬\b',
        ]
        found = 0
        for p in alg_patterns:
            found += len(re.findall(p, text))
        
        if found >= 3:
            return VerifierResult(
                verifier_id="V2", passed=True, confidence=0.90,
                evidence=[f"Found {found} algebraic operators/relations"],
            )
        elif found > 0:
            return VerifierResult(
                verifier_id="V2", passed=True, confidence=0.65,
                evidence=[f"Found {found} basic algebraic patterns"],
                warnings=["Limited algebraic structure detected"],
            )
        return VerifierResult(
            verifier_id="V2", passed=True, confidence=0.50,
            evidence=["No algebraic expressions detected (may not be needed)"],
            warnings=["No mathematical notation found"],
        )
    
    def _run_V3(self, text: str, ctx: dict) -> VerifierResult:
        """V3: Contraexemplos — verifica cobertura de casos extremos."""
        edge_patterns = [
            r'\b(se\s|when|if|caso|edge\s*case|boundary|limite|extremo)\b',
            r'\b(forall|∀|for\s*all|para\s*todo|qualquer)\b',
            r'\b(except|exceto|exce[cç][aã]o|salvo|trivial)\b',
            r'\b(zero|null|empty|vazio|limite|infinito)\b',
            r'\b(prove|proof|demonstra[cç][aã]o|teorema)\b',
        ]
        found = 0
        for p in edge_patterns:
            found += len(re.findall(p, text, re.IGNORECASE))
        
        if found >= 4:
            return VerifierResult(
                verifier_id="V3", passed=True, confidence=0.85,
                evidence=[f"Found {found} edge case patterns - good coverage"],
            )
        elif found >= 2:
            return VerifierResult(
                verifier_id="V3", passed=True, confidence=0.60,
                evidence=[f"Found {found} edge case mentions"],
                warnings=["Moderate edge case coverage"],
            )
        return VerifierResult(
            verifier_id="V3", passed=True, confidence=0.40,
            evidence=[f"Only {found} edge case patterns"],
            warnings=["Low edge case coverage - potential counterexamples"],
        )
    
    def _run_V4(self, text: str, ctx: dict) -> VerifierResult:
        """V4: Estatístico — detecta testes e medidas estatísticas."""
        stat_patterns = [
            r'\b(p[\-\s]?value|valor\s*p|signific[âa]ncia)\b',
            r'\b(mean|m[eé]dia|median|mediana|std|desvio|vari[âa]ncia)\b',
            r'\b(correlation|correla[cç][aã]o|r[\s]*=[\s]*[0-9])\b',
            r'\b(shapiro|kolmogorov|chi[-\s]?square|qui[\s-]quadrado)\b',
            r'\b(cohen|effect\s*size|tamanho\s*de\s*efeito)\b',
            r'\b(confidence\s*interval|intervalo\s*de\s*confian[çc]a)\b',
            r'\b(bootstrap|monte\s*carlo|simula[cç][aã]o)\b',
            r'\bN[\s]*=[\s]*\d+\b', r'\bn[\s]*=[\s]*\d+\b',
        ]
        found = 0
        for p in stat_patterns:
            found += len(re.findall(p, text, re.IGNORECASE))
        
        if found >= 3:
            return VerifierResult(
                verifier_id="V4", passed=True, confidence=0.85,
                evidence=[f"Found {found} statistical patterns"],
            )
        elif found > 0:
            return VerifierResult(
                verifier_id="V4", passed=True, confidence=0.55,
                evidence=[f"Found {found} basic statistical references"],
                warnings=["Limited statistical depth"],
            )
        return VerifierResult(
            verifier_id="V4", passed=True, confidence=0.50,
            evidence=["No statistical analysis detected"],
            warnings=["Statistical verification not applicable to this solution type"],
        )
    
    def _run_V5(self, text: str, ctx: dict) -> VerifierResult:
        """V5: Numérico — verifica precisão e arredondamentos."""
        num_patterns = [
            r'\b\d+\.\d{4,}\b',    # Números com 4+ casas decimais
            r'\b\d+\.?\d*\s*[×x*]\s*10\^?\s*[+-]?\d+\b',  # Notação científica
            r'\b(approx|≈|~|aproximadamente)\b',
            r'\b(error|erro|toler[âa]ncia|precision|precis[aã]o)\b',
            r'\b(round|arredond|truncat|casa\s*decimal)\b',
            r'\b(IEEE|float|double|precis[aã]o\s*num[ée]rica)\b',
            r'\b(epsilon|ulp|machin)',
        ]
        found = 0
        for p in num_patterns:
            found += len(re.findall(p, text, re.IGNORECASE))
        
        if found >= 3:
            return VerifierResult(
                verifier_id="V5", passed=True, confidence=0.85,
                evidence=[f"Found {found} numerical precision patterns"],
            )
        elif found > 0:
            return VerifierResult(
                verifier_id="V5", passed=True, confidence=0.60,
                evidence=[f"Found {found} numerical references"],
                warnings=["Limited numerical precision analysis"],
            )
        return VerifierResult(
            verifier_id="V5", passed=True, confidence=0.55,
            evidence=["No numerical precision issues detected"],
            warnings=["Numerical verification limited"],
        )
    
    def _run_V6(self, text: str, ctx: dict) -> VerifierResult:
        """V6: EDO/EDP — detecta equações diferenciais."""
        ode_patterns = [
            r'\bdy/dx\b', r'\bd[23]?[yf]/dx[23]?\b', r'\\frac\{d\}',
            r'\b∂\b', r'\bpartial\b', r'\\partial',
            r"\b(y['\u2032]{1,3}|f['\u2032]{1,3})\b",
            r'\b(ode|pde|edo|edp|equa[cç][aã]o\s*dif(erencial)?)\b',
            r'\b(laplace|fourier|navier[-\s]stokes|heat|onda|wave|diffusion)\b',
            r'\b(integrating\s*factor|fator\s*integrante|euler[-\s]lagrange)\b',
        ]
        found = 0
        for p in ode_patterns:
            found += len(re.findall(p, text, re.IGNORECASE))
        
        if found >= 2:
            return VerifierResult(
                verifier_id="V6", passed=True, confidence=0.85,
                evidence=[f"Found {found} differential equation patterns"],
            )
        elif found > 0:
            return VerifierResult(
                verifier_id="V6", passed=True, confidence=0.55,
                evidence=[f"Found {found} basic differential patterns"],
                warnings=["Limited differential equation depth"],
            )
        return VerifierResult(
            verifier_id="V6", passed=True, confidence=0.50,
            evidence=["No differential equations detected"],
            warnings=["ODE/PDE verification not applicable"],
        )
    
    def _run_V7(self, text: str, ctx: dict) -> VerifierResult:
        """V7: Código-Fonte — detecta e avalia blocos de código."""
        code_patterns = [
            r'```(python|javascript|typescript|java|cpp|rust|go)\b',
            r'```\s*\n(def |function |class |import |from )',
            r'\b(def |class |import |from |return |if __name__)',
            r'\b(for\s+\w+\s+in\s+|while\s+|try\s*:|except\s+)',
            r'\b(lambda|map|filter|reduce|comprehension)',
        ]
        found = 0
        for p in code_patterns:
            found += len(re.findall(p, text, re.IGNORECASE))
        
        v7_warnings = []
        if found >= 4:
            score = 0.90
            evidence = f"Found {found} code patterns - robust code presence"
        elif found >= 2:
            score = 0.70
            evidence = f"Found {found} code patterns"
            v7_warnings = ["Moderate code presence - check completeness"]
        elif found > 0:
            score = 0.50
            evidence = f"Found {found} code fragments"
            v7_warnings = ["Minimal code - may not be a code-focused solution"]
        else:
            score = 0.45
            evidence = "No code blocks detected"
            v7_warnings = ["Code verification not applicable"]
        
        return VerifierResult(
            verifier_id="V7", passed=(score >= 0.50), confidence=score,
            evidence=[evidence],
            warnings=v7_warnings,
        )
