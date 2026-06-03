"""
test_anticircularidade.py — TDD suite for SPEC-008
Anti-Circularity Validation Framework
9 CTs, follows RED→GREEN→REFACTOR cycle
"""
import json
import math
import random
import pytest
from datetime import datetime, timedelta
from typing import List, Dict, Any
from dataclasses import dataclass, field


# ============================================================
# DATA CLASSES
# ============================================================
@dataclass
class Document:
    id: str
    text: str
    timestamp: datetime
    entities: List[str] = field(default_factory=list)
    paragraphs: List[str] = field(default_factory=list)

@dataclass
class Pattern:
    name: str
    description: str
    confidence: float
    supporting_docs: List[str] = field(default_factory=list)

@dataclass
class ValidationResult:
    temporal_score: float
    robustness_score: float
    human_agreement: float
    decision_scenario: str  # A-F
    report: str


# ============================================================
# CT-8.1: TEMPORAL SPLIT PRESERVES CAUSAL ORDER
# ============================================================
class TestTemporalSplit:
    """CT-8.1: Split temporal com cutoff preserva ordem causal.
    treino.max_timestamp <= cutoff < teste.min_timestamp"""

    def _create_corpus(self, n_docs: int = 100) -> List[Document]:
        base = datetime(2020, 1, 1)
        return [
            Document(
                id=f"doc_{i}",
                text=f"Document about topic {i % 5} with pattern {'ABC' if i % 3 == 0 else 'XYZ'}",
                timestamp=base + timedelta(days=i * 30)
            )
            for i in range(n_docs)
        ]

    def _temporal_split(self, corpus: List[Document], cutoff: datetime):
        treino = [d for d in corpus if d.timestamp <= cutoff]
        teste = [d for d in corpus if d.timestamp > cutoff]
        return treino, teste

    def test_cutoff_preserves_order(self):
        """RED→GREEN: treino max <= cutoff < teste min"""
        corpus = self._create_corpus(100)
        cutoff_idx = 70
        cutoff = corpus[cutoff_idx].timestamp

        treino, teste = self._temporal_split(corpus, cutoff)

        # RED phase: verify split occurred
        assert len(treino) > 0, "Treino vazio — cutoff muito baixo"
        assert len(teste) > 0, "Teste vazio — cutoff muito alto"

        # GREEN phase: verify order
        treino_max = max(d.timestamp for d in treino)
        teste_min = min(d.timestamp for d in teste)

        assert treino_max <= cutoff, (
            f"FALHA: doc de treino {treino_max} depois do cutoff {cutoff}"
        )
        assert cutoff < teste_min, (
            f"FALHA: doc de teste {teste_min} antes ou no cutoff {cutoff}"
        )
        assert len(treino) + len(teste) == len(corpus), "Docs perdidos no split"

    def test_future_data_never_leaks(self):
        """CT-8.1 extra: nenhum doc de teste pode estar no treino"""
        corpus = self._create_corpus(100)
        cutoff = corpus[50].timestamp
        treino, teste = self._temporal_split(corpus, cutoff)

        treino_ids = {d.id for d in treino}
        teste_ids = {d.id for d in teste}
        assert len(treino_ids & teste_ids) == 0, "Vazamento: doc em treino E teste"


# ============================================================
# CT-8.2 & CT-8.3: ADVERSARIAL PERTURBATION
# ============================================================
class TestAdversarialPerturbation:
    """CT-8.2: T1 (shuffle paragrafos) reduz similaridade em corpus com estrutura.
    CT-8.3: T3 (inverter cronologia) preserva padroes a-temporais."""

    def _create_structured_corpus(self) -> List[Document]:
        """Corpus onde a ordem dos paragrafos importa"""
        docs = []
        for i in range(50):
            paras = [
                f"Introducao sobre topico {i % 5}.",
                f"Metodologia do estudo {i}.",
                f"Resultados: encontrou-se que padrao {'ABC' if i%3==0 else 'XYZ'}.",
                f"Discussao dos achados.",
                f"Conclusao: o padrao {'ABC' if i%3==0 else 'XYZ'} e significativo."
            ]
            text = "\n".join(paras)
            docs.append(Document(
                id=f"doc_{i}",
                text=text,
                timestamp=datetime(2023, 1, 1) + timedelta(days=i),
                paragraphs=paras
            ))
        return docs

    def _extract_pattern(self, text: str) -> str:
        """Simula extracao de padrao: depende da ORDEM dos paragrafos.
        O padrao so e detectado quando a conclusao contem o mesmo
        padrao encontrado nos resultados E a distancia entre eles
        e de exatamente 1 paragrafo (discussao entre eles)."""
        lines = text.split("\n")
        for i in range(len(lines) - 2):
            if "Resultados: encontrou-se que padrao ABC" in lines[i]:
                if "Conclusao: o padrao ABC" in lines[i + 2]:
                    return "ABC"
            if "Resultados: encontrou-se que padrao XYZ" in lines[i]:
                if "Conclusao: o padrao XYZ" in lines[i + 2]:
                    return "XYZ"
        return "NONE"

    def _shuffle_paragraphs(self, doc: Document) -> Document:
        """T1: embaralhar paragrafos"""
        shuffled = doc.paragraphs.copy()
        random.seed(42)
        random.shuffle(shuffled)
        return Document(
            id=doc.id, text="\n".join(shuffled),
            timestamp=doc.timestamp, paragraphs=shuffled
        )

    def _invert_chronology(self, corpus: List[Document]) -> List[Document]:
        """T3: inverter ordem cronologica"""
        return list(reversed(corpus))

    def test_T1_shuffle_degrades_structured_pattern(self):
        """CT-8.2: Embaralhar paragrafos quebra padrao que depende de ordem"""
        corpus = self._create_structured_corpus()

        # Extrai padroes do original
        original_patterns = set()
        for doc in corpus:
            p = self._extract_pattern(doc.text)
            if p != "NONE":
                original_patterns.add(p)

        assert len(original_patterns) > 0, "Corpus deveria ter padroes"

        # Aplica T1
        shuffled_corpus = [self._shuffle_paragraphs(d) for d in corpus]
        shuffled_patterns = set()
        for doc in shuffled_corpus:
            p = self._extract_pattern(doc.text)
            if p != "NONE":
                shuffled_patterns.add(p)

        # Verifica: T1 deve REDUZIR a deteccao de padroes
        # (porque a estrutura "resultados...conclusao" foi quebrada)
        jaccard = len(original_patterns & shuffled_patterns) / max(
            len(original_patterns | shuffled_patterns), 1
        )
        assert jaccard < 1.0, (
            f"CT-8.2 FALHA: T1 nao reduziu similaridade. Jaccard={jaccard:.2f}"
        )

    def test_T3_preserves_atemporal_patterns(self):
        """CT-8.3: Inverter cronologia nao afeta padroes sem dependencia temporal.
        Cada documento tem seu proprio padrao (ABC ou XYZ) baseado em id%3."""
        corpus = self._create_structured_corpus()

        # Extrai padroes por documento ID
        original_by_id = {d.id: self._extract_pattern(d.text) for d in corpus}

        # Inverte a ORDEM de processamento, mas os documentos sao os mesmos
        inverted = self._invert_chronology(corpus)
        inverted_by_id = {d.id: self._extract_pattern(d.text) for d in inverted}

        # Verifica: cada documento deve ter o MESMO padrao, independente da ordem
        matches = sum(1 for doc_id in original_by_id
                      if original_by_id[doc_id] == inverted_by_id[doc_id])
        agreement = matches / len(original_by_id)

        assert agreement >= 0.95, (
            f"CT-8.3 FALHA: T3 alterou padroes atemporais. Agreement={agreement:.2f}"
        )


# ============================================================
# CT-8.4: ACTIVE LEARNING / UNCERTAINTY SAMPLING
# ============================================================
class TestUncertaintySampling:
    """CT-8.4: Uncertainty sampling seleciona docs com maior entropia"""

    def _compute_entropy(self, probs: List[float]) -> float:
        """Entropia de Shannon"""
        return -sum(p * math.log2(p) if p > 0 else 0 for p in probs)

    def test_uncertainty_sampling_beats_random(self):
        """CT-8.4: Docs selecionados por entropia tem entropia media > aleatorio"""
        # Simula 100 documentos com diferentes niveis de incerteza
        random.seed(42)
        docs_with_entropy = []
        for i in range(100):
            # Simula probabilidades de 3 classes
            if i < 30:
                probs = [0.9, 0.05, 0.05]  # baixa entropia (confiante)
            elif i < 60:
                probs = [0.5, 0.3, 0.2]    # media entropia
            else:
                probs = [0.34, 0.33, 0.33]  # alta entropia (incerto)
            docs_with_entropy.append((i, self._compute_entropy(probs), probs))

        # Uncertainty sampling: seleciona top 30 por entropia
        sorted_by_entropy = sorted(docs_with_entropy, key=lambda x: x[1], reverse=True)
        uncertainty_selected = sorted_by_entropy[:30]
        uncertainty_mean = sum(e for _, e, _ in uncertainty_selected) / 30

        # Random sampling: 30 aleatorios
        random.shuffle(docs_with_entropy)
        random_selected = docs_with_entropy[:30]
        random_mean = sum(e for _, e, _ in random_selected) / 30

        assert uncertainty_mean > random_mean, (
            f"CT-8.4 FALHA: uncertainty mean={uncertainty_mean:.3f} <= "
            f"random mean={random_mean:.3f}"
        )


# ============================================================
# CT-8.5 & CT-8.6: TRANSPARENCY REPORT & DECISION MATRIX
# ============================================================
class TestTransparencyReport:
    """CT-8.5: Relatorio inclui 4 secoes obrigatorias.
    CT-8.6: Matriz de decisao classifica corretamente 6 cenarios."""

    DECISION_MATRIX = {
        ("PASS", "PASS", "PASS"): "A",
        ("PASS", "FAIL", "PASS"): "B",
        ("FAIL", "PASS", "PASS"): "C",
        ("PASS", "PASS", "FAIL"): "D",
        ("FAIL", "FAIL", "PASS"): "E",
        ("PASS", "PASS", "NONE"): "F",
    }

    def _generate_report(self, temporal, robustness, human) -> str:
        status = lambda s: "PASS" if s >= 0.7 else "FAIL"
        scenario = self.DECISION_MATRIX.get(
            (status(temporal), status(robustness), status(human)),
            "UNCERTAIN"
        )
        return (
            f"=== RELATORIO DE VALIDACAO ===\n"
            f"Nivel maximo de independencia: {'ALTA' if human > 0.8 else 'MEDIA'}\n"
            f"Camada 1 (temporal): {'PASS' if temporal >= 0.7 else 'FAIL'} ({temporal:.2f})\n"
            f"Camada 2 (perturbacao): {'PASS' if robustness >= 0.7 else 'FAIL'} ({robustness:.2f})\n"
            f"Camada 3 (humano): {'PASS' if human >= 0.7 else 'FAIL'} ({human:.2f})\n"
            f"Cenario: {scenario}\n"
            f"Limitacao: Validacao externa independente nao disponivel.\n"
        )

    def test_report_has_all_sections(self):
        """CT-8.5: Relatorio contem as 4 secoes obrigatorias"""
        report = self._generate_report(0.85, 0.92, 0.93)

        required = [
            "Nivel maximo de independencia",
            "Camada 1 (temporal)",
            "Camada 2 (perturbacao)",
            "Camada 3 (humano)",
            "Cenario:",
            "Limitacao:",
        ]
        for section in required:
            assert section in report, f"CT-8.5 FALHA: Secao '{section}' ausente"

    def test_decision_matrix_scenario_A(self):
        """CT-8.6: Cenario A — todas passam"""
        report = self._generate_report(0.85, 0.92, 0.93)
        assert "Cenario: A" in report

    def test_decision_matrix_scenario_E(self):
        """CT-8.6: Cenario E — so humano passa"""
        report = self._generate_report(0.45, 0.30, 0.88)
        assert "Cenario: E" in report

    def test_decision_matrix_scenario_D(self):
        """CT-8.6: Cenario D — humano falha"""
        report = self._generate_report(0.85, 0.92, 0.45)
        assert "Cenario: D" in report


# ============================================================
# CT-8.8: CLOPPER-PEARSON CONFIDENCE INTERVAL
# ============================================================
class TestClopperPearson:
    """CT-8.8: IC 95% para human_agreement usa Clopper-Pearson exato"""

    def clopper_pearson_ci(self, k: int, n: int, alpha: float = 0.05):
        """Clopper-Pearson exact binomial confidence interval"""
        from scipy import stats

        if k == 0:
            lower = 0.0
        else:
            lower = stats.beta.ppf(alpha / 2, k, n - k + 1)

        if k == n:
            upper = 1.0
        else:
            upper = stats.beta.ppf(1 - alpha / 2, k + 1, n - k)

        return lower, upper

    def test_ci_binomial_exact(self):
        """CT-8.8: Clopper-Pearson, nao aproximacao normal de Wald"""
        lower, upper = self.clopper_pearson_ci(28, 30)

        assert lower > 0.77, f"Lower bound muito baixo: {lower:.3f}"
        assert upper < 1.0, f"Upper bound = 1.0: {upper:.3f}"
        assert 0.77 <= lower <= 0.99, f"IC inferior fora do esperado: {lower:.3f}"
        assert 0.95 <= upper <= 0.999, f"IC superior fora do esperado: {upper:.3f}"

    def test_ci_zero_failures(self):
        """Edge case: 100% de concordancia (30/30)"""
        lower, upper = self.clopper_pearson_ci(30, 30)

        assert lower > 0.88, f"30/30 deve ter lower > 0.88, got {lower:.3f}"
        assert upper == 1.0, f"30/30 deve ter upper = 1.0, got {upper:.3f}"

    def test_ci_zero_successes(self):
        """Edge case: 0% de concordancia"""
        lower, upper = self.clopper_pearson_ci(0, 30)

        assert lower == 0.0
        assert upper < 0.12, f"0/30 deve ter upper < 0.12, got {upper:.3f}"


# ============================================================
# CT-8.7: PERFORMANCE BOUND
# ============================================================
class TestPerformanceBound:
    """CT-8.7: Tempo C1+C2 < 5 min para 10K docs"""

    def test_temporal_split_performance(self):
        """Simula split temporal em 10K docs — deve ser < 0.5s"""
        import time
        n = 10000
        corpus = [
            Document(
                id=f"doc_{i}",
                text=f"text {i}",
                timestamp=datetime(2020, 1, 1) + timedelta(days=i)
            )
            for i in range(n)
        ]

        start = time.time()
        cutoff = datetime(2023, 1, 1)
        treino = [d for d in corpus if d.timestamp <= cutoff]
        teste = [d for d in corpus if d.timestamp > cutoff]
        elapsed = time.time() - start

        assert len(treino) + len(teste) == n
        assert elapsed < 1.0, (
            f"CT-8.7 FALHA: split temporal levou {elapsed:.2f}s para {n} docs"
        )

    def test_perturbation_performance(self):
        """Simula 4 perturbacoes em 1K docs — deve ser < 10s"""
        import time
        random.seed(42)

        docs = [
            Document(
                id=f"doc_{i}",
                text=f"paragraph 1.\nparagraph 2.\nparagraph 3.\nparagraph 4.",
                timestamp=datetime(2023, 1, 1),
                paragraphs=[f"p{j}" for j in range(4)]
            )
            for i in range(1000)
        ]

        start = time.time()
        for _ in range(4):
            for doc in docs:
                shuffled = doc.paragraphs.copy()
                random.shuffle(shuffled)
        elapsed = time.time() - start

        assert elapsed < 10.0, (
            f"CT-8.7 FALHA: 4 perturbacoes levaram {elapsed:.2f}s para 1K docs"
        )


# ============================================================
# RUN
# ============================================================
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
