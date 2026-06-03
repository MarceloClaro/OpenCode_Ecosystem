#!/usr/bin/env python
# =====================================================================
# SYNTHESIS ENGINE v1 — 4 Estratégias de Síntese Multi-Cadeia
# =====================================================================
# WeightedVote, Debate, Ensemble, BestOf — combinam resultados de
# múltiplas cadeias de raciocínio em uma resposta consolidada.
# =====================================================================

import math, re
from dataclasses import dataclass, field
from typing import Optional


# =====================================================================
# DATA STRUCTURES
# =====================================================================

@dataclass
class SynthesisResult:
    """Resultado da síntese de múltiplas cadeias."""
    final_answer: str
    strategy: str
    confidence: float
    chain_count: int
    sources: list[str] = field(default_factory=list)
    disagreements: list[str] = field(default_factory=list)
    elapsed_ms: float = 0.0


# =====================================================================
# SYNTHESIS ENGINE
# =====================================================================

STRATEGIES = ["weighted_vote", "debate", "ensemble", "best_of"]


class SynthesisEngine:
    """
    Engine de síntese com 4 estratégias.
    
    Estratégias:
      weighted_vote: Voto ponderado por PCI de cada cadeia
      debate:       Identifica divergências e resolve
      ensemble:     Combina múltiplas perspectivas
      best_of:      Seleciona a melhor cadeia (maior PCI)
    """
    
    def __init__(self, strategy: str = "weighted_vote"):
        if strategy not in STRATEGIES:
            strategy = "weighted_vote"
        self.strategy = strategy
    
    def synthesize(
        self,
        chains: list,
        strategy: Optional[str] = None,
    ) -> SynthesisResult:
        """
        Sintetiza resultados de múltiplas cadeias.
        
        Args:
            chains: Lista de ChainResult (de parallel_chain)
            strategy: Estratégia (opcional, sobrescreve default)
        
        Returns:
            SynthesisResult com resposta consolidada
        """
        import time
        start = time.time()
        
        if strategy is None:
            strategy = self.strategy
        
        if strategy not in STRATEGIES:
            strategy = "weighted_vote"
        
        if not chains:
            return SynthesisResult(
                final_answer="No chains to synthesize",
                strategy=strategy,
                confidence=0.0,
                chain_count=0,
                sources=[],
                disagreements=["Empty chain list"],
                elapsed_ms=(time.time() - start) * 1000,
            )
        
        # Roteia para estratégia correta
        router = {
            "weighted_vote": self._weighted_vote,
            "debate": self._debate_synthesis,
            "ensemble": self._ensemble_synthesis,
            "best_of": self._best_of_synthesis,
        }
        
        handler = router.get(strategy, self._weighted_vote)
        result = handler(chains)
        result.elapsed_ms = (time.time() - start) * 1000
        return result
    
    # ----------------------------------------------------------------
    # ESTRATÉGIA 1: Weighted Vote
    # ----------------------------------------------------------------
    
    def _weighted_vote(self, chains: list) -> SynthesisResult:
        """
        Voto ponderado por PCI.
        
        Cada cadeia contribui proporcionalmente ao seu PCI.
        Resposta final: segmentos mais frequentes × peso.
        """
        total_weight = sum(max(c.pci_score, 0.1) for c in chains if not c.error)
        
        if total_weight <= 0 or not chains:
            return SynthesisResult(
                final_answer="No valid chains for weighted vote",
                strategy="weighted_vote",
                confidence=0.0,
                chain_count=len(chains),
                disagreements=["All chains failed"],
            )
        
        # Coleta sentenças de cada cadeia com peso
        weighted_sentences: dict[str, float] = {}
        sources = []
        
        for c in chains:
            if c.error:
                continue
            weight = max(c.pci_score, 0.1) / total_weight
            sources.append(f"Chain {c.chain_id} ({c.mode}, PCI={c.pci_score:.1f})")
            
            # Extrai sentenças da solução
            sentences = re.split(r'[.!?\n]+', c.solution_text)
            for sent in sentences:
                sent = sent.strip()
                if len(sent) > 5:  # Ignora sentenças muito curtas
                    weighted_sentences[sent] = weighted_sentences.get(sent, 0.0) + weight
        
        # Ordena por peso decrescente
        ranked = sorted(weighted_sentences.items(), key=lambda x: -x[1])
        
        # Concatena top sentenças (cobertura > 50%)
        top_sentences = []
        covered = 0.0
        for sent, weight in ranked:
            top_sentences.append(sent)
            covered += weight
            if covered > 0.5:
                break
        
        final = ". ".join(top_sentences[:5])
        if not final:
            final = chains[0].solution_text if chains else "No synthesis available"
        
        confidence = min(1.0, sum(max(c.pci_score, 0) for c in chains if not c.error) / 100.0)
        
        # Disagreements: cadeias com PCI muito diferentes
        disagreements = []
        pci_values = [c.pci_score for c in chains if not c.error and c.pci_score > 0]
        if len(pci_values) >= 2:
            avg_pci = sum(pci_values) / len(pci_values)
            for c in chains:
                if c.error:
                    disagreements.append(f"Chain {c.chain_id} failed: {c.error}")
                elif abs(c.pci_score - avg_pci) > 20:
                    disagreements.append(
                        f"Chain {c.chain_id} PCI={c.pci_score:.1f} diverges from mean {avg_pci:.1f}"
                    )
        
        return SynthesisResult(
            final_answer=final,
            strategy="weighted_vote",
            confidence=round(confidence, 4),
            chain_count=len(chains),
            sources=sources,
            disagreements=disagreements,
        )
    
    # ----------------------------------------------------------------
    # ESTRATÉGIA 2: Debate
    # ----------------------------------------------------------------
    
    def _debate_synthesis(self, chains: list) -> SynthesisResult:
        """
        Síntese baseada em debate.
        
        1. Identifica divergências entre cadeias
        2. Seleciona cadeias com maior PCI para resolver
        3. Concilia diferenças
        """
        if not chains:
            return SynthesisResult(
                final_answer="No chains for debate", strategy="debate",
                confidence=0.0, chain_count=0,
                disagreements=["Empty"],
            )
        
        valid = [c for c in chains if not c.error]
        if not valid:
            return SynthesisResult(
                final_answer="All chains failed", strategy="debate",
                confidence=0.0, chain_count=len(chains),
                disagreements=[f"Chain {c.chain_id}: {c.error}" for c in chains if c.error],
            )
        
        # Ordena por PCI
        ranked = sorted(valid, key=lambda c: c.pci_score, reverse=True)
        best = ranked[0]
        
        # Identifica divergências: cadeias com solução diferente da melhor
        disagreements = []
        best_keywords = set(re.findall(r'\b\w{4,}\b', best.solution_text.lower()))
        
        for c in ranked[1:]:
            c_keywords = set(re.findall(r'\b\w{4,}\b', c.solution_text.lower()))
            if best_keywords and c_keywords:
                jaccard = len(best_keywords & c_keywords) / len(best_keywords | c_keywords)
                if jaccard < 0.3:
                    disagreements.append(
                        f"Chain {c.chain_id} ({c.mode}, PCI={c.pci_score:.1f}) "
                        f"diverges from best (Jaccard={jaccard:.2f})"
                    )
        
        # Se há divergências, tenta reconciliar
        if disagreements and len(ranked) >= 2:
            # Usa top 2 cadeias para resposta reconciliada
            top2 = ranked[:2]
            combined = f"{top2[0].solution_text}\n\n[Debate Resolution]\n{top2[1].solution_text}"
            confidence = top2[0].pci_score / 100.0 * 0.7 + top2[1].pci_score / 100.0 * 0.3
        else:
            combined = best.solution_text
            confidence = best.pci_score / 100.0
        
        sources = [f"Chain {c.chain_id} ({c.mode}, PCI={c.pci_score:.1f})" for c in valid]
        
        return SynthesisResult(
            final_answer=combined,
            strategy="debate",
            confidence=round(min(1.0, confidence), 4),
            chain_count=len(chains),
            sources=sources,
            disagreements=disagreements,
        )
    
    # ----------------------------------------------------------------
    # ESTRATÉGIA 3: Ensemble
    # ----------------------------------------------------------------
    
    def _ensemble_synthesis(self, chains: list) -> SynthesisResult:
        """
        Síntese ensemble: combina múltiplas perspectivas.
        
        Cada cadeia contribui com seções numeradas,
        formando um relatório multi-perspectiva.
        """
        if not chains:
            return SynthesisResult(
                final_answer="No chains for ensemble", strategy="ensemble",
                confidence=0.0, chain_count=0,
                disagreements=["Empty"],
            )
        
        valid = [c for c in chains if not c.error]
        if not valid:
            return SynthesisResult(
                final_answer="All chains failed", strategy="ensemble",
                confidence=0.0, chain_count=len(chains),
                disagreements=[f"Chain {c.chain_id}: {c.error}" for c in chains if c.error],
            )
        
        sections = []
        sources = []
        
        for c in valid:
            section = (
                f"## Perspective {c.chain_id} ({c.mode.upper()}, PCI={c.pci_score:.1f})\n"
                f"{c.solution_text}"
            )
            sections.append(section)
            sources.append(f"Chain {c.chain_id} ({c.mode})")
        
        combined = "\n\n".join(sections)
        avg_pci = sum(c.pci_score for c in valid) / len(valid)
        
        return SynthesisResult(
            final_answer=combined,
            strategy="ensemble",
            confidence=round(min(1.0, avg_pci / 100.0), 4),
            chain_count=len(chains),
            sources=sources,
        )
    
    # ----------------------------------------------------------------
    # ESTRATÉGIA 4: Best Of
    # ----------------------------------------------------------------
    
    def _best_of_synthesis(self, chains: list) -> SynthesisResult:
        """
        Seleciona a melhor cadeia (maior PCI).
        Mais rápida, mas sem diversidade.
        """
        if not chains:
            return SynthesisResult(
                final_answer="No chains for best_of", strategy="best_of",
                confidence=0.0, chain_count=0,
                disagreements=["Empty"],
            )
        
        valid = [c for c in chains if not c.error]
        if not valid:
            return SynthesisResult(
                final_answer="All chains failed", strategy="best_of",
                confidence=0.0, chain_count=len(chains),
                disagreements=[f"Chain {c.chain_id}: {c.error}" for c in chains if c.error],
            )
        
        best = max(valid, key=lambda c: c.pci_score)
        
        return SynthesisResult(
            final_answer=best.solution_text,
            strategy="best_of",
            confidence=round(min(1.0, best.pci_score / 100.0), 4),
            chain_count=len(chains),
            sources=[f"Chain {best.chain_id} ({best.mode}, PCI={best.pci_score:.1f})"],
        )
