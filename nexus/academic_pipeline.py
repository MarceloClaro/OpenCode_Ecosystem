#!/usr/bin/env python3
"""
Academic Pipeline — R45 Fase D.

Pipeline academico completo: SEEKER → MASWOS → PeerReview → TSAC → QualisA1
→ Export → ManusEvolve

Simula cada etapa para validacao academica Qualis A1.
"""

import json
import random
import re
import uuid
from pathlib import Path
from typing import Optional


# ── Dados simulados ────────────────────────────────────────────────────

SEEKER_PAPERS = [
    {"title": "Multi-Agent Systems: A Survey",
     "source": "arXiv", "doi": "10.48550/arXiv.2301.00001",
     "year": 2023, "citations": 45},
    {"title": "Cognitive Architecture for LLM Agents",
     "source": "NeurIPS", "doi": "10.48550/arXiv.2302.00002",
     "year": 2023, "citations": 120},
    {"title": "Efficient Multi-Agent Coordination",
     "source": "ICML", "doi": "10.48550/arXiv.2303.00003",
     "year": 2024, "citations": 32},
    {"title": "Agent Memory and Reasoning",
     "source": "ACL", "doi": "10.48550/arXiv.2304.00004",
     "year": 2024, "citations": 78},
    {"title": "Scalable Agent Architectures",
     "source": "AAAI", "doi": "10.48550/arXiv.2305.00005",
     "year": 2024, "citations": 15},
]

MASWOS_PHASES = [
    "Diagnostico de Escopo",
    "Busca e Curadoria",
    "Estrutura Argumentativa",
    "Revisao de Literatura",
    "Metodologia",
    "Resultados",
    "Discussao",
    "Conclusao",
]

TSAC_WORD_BLACKLIST = [
    "fundamental", "crucial", "essencial", "inovador",
    "revolucionario", "sem precedentes", "pioneiro",
    "indiscutivelmente", "obviamente", "claramente",
]

PEER_REVIEWER_NAMES = [
    "Dra. Ana Silva", "Dr. Carlos Santos", "Dr. Maria Oliveira",
    "Dr. Paulo Costa", "Dra. Julia Pereira",
]

QUALIS_CRITERIA = {
    "relevancia": 0.20,
    "originalidade": 0.20,
    "rigor_metodologico": 0.20,
    "clareza": 0.15,
    "referencias": 0.15,
    "impacto": 0.10,
}


class SeekerSimulator:
    """Simulador do SEEKER para busca academica."""

    def search(self, topic: str) -> dict:
        """Simula busca academica."""
        # Selecionar papers relevantes ao topic
        papers = SEEKER_PAPERS[:]
        # Embaralhar deterministicamente baseado no topic
        rng = random.Random(hash(topic) % 2**31)
        rng.shuffle(papers)

        return {
            "topic": topic,
            "papers": papers,
            "count": len(papers),
            "sources": list(set(p["source"] for p in papers)),
        }


class PeerReviewSimulator:
    """Simulador de revisao por pares."""

    def evaluate(self, draft: str) -> dict:
        """Avalia rascunho com 3-5 revisores."""
        if not draft or len(draft.strip()) < 20:
            return {
                "reviewers": [],
                "average_score": 0,
                "summary": "Draft muito curto para avaliacao.",
            }

        rng = random.Random(hash(draft) % 2**31)
        n_reviewers = min(3 + rng.randint(0, 2), len(PEER_REVIEWER_NAMES))

        reviewers = []
        for i in range(n_reviewers):
            score = rng.randint(65, 95)
            comments_pool = [
                "Metodologia bem definida e reprodutivel.",
                "Contribuicao original para area.",
                "Referencias precisam ser ampliadas.",
                "Resultados apresentados com clareza.",
                "Sugiro incluir analise estatistica adicional.",
                "Estrutura do artigo segue padrao ABNT.",
                "Discussao poderia ser aprofundada.",
                "Resumo e conclusao consistentes.",
            ]
            comments = rng.sample(comments_pool, 2)

            reviewers.append({
                "name": PEER_REVIEWER_NAMES[i],
                "score": score,
                "comments": comments,
                "recommendation": "accept" if score >= 80 else "minor_revision",
            })

        avg_score = sum(r["score"] for r in reviewers) / len(reviewers)

        return {
            "reviewers": reviewers,
            "average_score": round(avg_score, 1),
            "summary": f"Avaliado por {n_reviewers} revisores. "
                       f"Media: {avg_score:.0f}/100.",
        }


class TSACCorrector:
    """Corretor de padroes anti-IA (TSAC)."""

    def __init__(self):
        self.patterns = {
            r'\bportanto,\s+': '',       # conectivo enfatico
            r'\bdesta forma,\s+': '',     # conectivo enfatico
            r'\bem outras palavras': 'ou seja',
            r'\bé importante notar': 'note-se',
            r'\bcabe ressaltar': 'ressalte-se',
            r'\bvale a pena': '',
            r'\btorna-se evidente': 'evidencia-se',
            r'\b[ée] fundamental': 'e relevante',
            r'\b[ée] crucial': 'e importante',
        }

    def correct(self, text: str) -> dict:
        """Aplica correcao TSAC no texto."""
        original = text
        changes = []

        for word in TSAC_WORD_BLACKLIST:
            if word.lower() in text.lower():
                text = re.sub(
                    re.escape(word), f"[REVISADO:{word}]", text,
                    flags=re.IGNORECASE, count=1
                )
                changes.append(f"Blacklist word '{word}' marked for review")

        for pattern, replacement in self.patterns.items():
            if re.search(pattern, text, re.IGNORECASE):
                old_text = text[:]
                text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
                if text != old_text:
                    changes.append(f"Pattern '{pattern}' replaced")

        return {
            "original": original,
            "corrected": text,
            "changes": changes,
            "change_count": len(changes),
        }


class QualisA1Auditor:
    """Auditor de conformidade Qualis A1."""

    def audit(
        self,
        title: str,
        abstract: str,
        sections: list[str],
        references: list[str],
    ) -> dict:
        """Audita artigo contra criterios Qualis A1."""
        scores = {}
        total = 0.0

        # Relevancia: titulo e abstract tem termos academicos
        academic_terms = ["estudo", "analise", "metodo", "resultado",
                          "propoe", "arquitetura", "sistema"]
        term_count = sum(1 for t in academic_terms
                        if t.lower() in (title + " " + abstract).lower())
        scores["relevancia"] = min(term_count / 3, 1.0) * QUALIS_CRITERIA["relevancia"]

        # Originalidade: sections tem contribuicao
        scores["originalidade"] = QUALIS_CRITERIA["originalidade"] * 0.85

        # Rigor metodologico: tem secoes de metodo
        has_method = any("method" in s.lower() or "metodologia" in s.lower()
                        for s in sections)
        scores["rigor_metodologico"] = (
            QUALIS_CRITERIA["rigor_metodologico"] * (0.9 if has_method else 0.5)
        )

        # Clareza: estrutura basica presente
        required_sections = ["intro", "method", "result", "discussion", "conclusao"]
        has_required = sum(1 for rs in required_sections
                          for s in sections if rs in s.lower())
        scores["clareza"] = (
            QUALIS_CRITERIA["clareza"] * min(has_required / 3, 1.0)
        )

        # Referencias: quantidade minima
        ref_count = len(references)
        scores["referencias"] = (
            QUALIS_CRITERIA["referencias"] * min(ref_count / 5, 1.0)
        )

        # Impacto
        scores["impacto"] = QUALIS_CRITERIA["impacto"] * 0.80

        total = sum(scores.values())

        return {
            "score": round(total * 100, 1),
            "criteria": scores,
            "details": {k: round(v, 3) for k, v in scores.items()},
            "is_qualis_a1": total >= 0.70,
        }

    def validate_references(self, references: list[dict]) -> dict:
        """Valida referencias no formato ABNT."""
        valid = 0
        for ref in references:
            if ref.get("doi") and ref.get("author"):
                valid += 1

        return {
            "valid": valid == len(references),
            "count": len(references),
            "valid_count": valid,
            "format": "ABNT NBR 6023:2018",
        }


class ExportManager:
    """Gerenciador de exportacao LaTeX/PDF."""

    def to_latex(self, title: str, author: str,
                 sections: list[dict]) -> str:
        """Exporta para formato LaTeX."""
        latex = []
        latex.append(r"\documentclass{article}")
        latex.append(r"\usepackage[brazil]{babel}")
        latex.append(r"\usepackage{amsmath,amssymb}")
        latex.append(r"\usepackage[utf8]{inputenc}")
        latex.append(f"\\title{{{title}}}")
        latex.append(f"\\author{{{author}}}")
        latex.append(r"\begin{document}")
        latex.append(r"\maketitle")

        for section in sections:
            sec_title = section.get("title", "Secao")
            sec_content = section.get("content", "")
            latex.append(f"\\section{{{sec_title}}}")
            latex.append(sec_content)

        latex.append(r"\end{document}")
        return "\n\n".join(latex)

    def verify_export_ready(self, sections: list[dict],
                            references: Optional[list[str]] = None) -> dict:
        """Verifica se o documento esta pronto para exportacao."""
        issues = []

        if not sections:
            issues.append("Nenhuma secao definida")

        required_titles = ["intro", "method", "result", "discussion"]
        found_titles = set()
        for s in sections:
            t = s.get("title", "").lower()
            for rt in required_titles:
                if rt in t:
                    found_titles.add(rt)

        missing = set(required_titles) - found_titles
        if missing:
            issues.append(f"Secoes obrigatorias ausentes: {', '.join(missing)}")

        if references and len(references) < 3:
            issues.append(f"Poucas referencias ({len(references)})")

        return {
            "ready": len(issues) == 0,
            "issues": issues,
            "sections_count": len(sections),
            "references_count": len(references or []),
        }


class ManusEvolve:
    """Motor de aprendizado do ciclo (Manus Evolve)."""

    def learn(self, cycle_data: dict) -> dict:
        """Aprende padroes de um ciclo de execucao."""
        score_diff = cycle_data.get("score_final", 0) - cycle_data.get("score_initial", 0)
        improvements = cycle_data.get("improvements", [])
        duration = cycle_data.get("duration_seconds", 0)

        # Identificar padrao
        if score_diff > 15:
            pattern = "alta_melhoria"
            recommendation = (
                "Manter estrategias de correcao TSAC e revisao por pares. "
                "O ciclo mostrou efetividade significativa."
            )
        elif score_diff > 5:
            pattern = "melhoria_moderada"
            recommendation = (
                "Refinar pipeline de auditoria Qualis. "
                "Há espaco para melhoria na deteccao de padroes anti-IA."
            )
        else:
            pattern = "melhoria_baixa"
            recommendation = (
                "Revisar metodologia de revisao. "
                "Score inicial ja estava elevado."
            )

        return {
            "cycle_id": str(uuid.uuid4())[:8],
            "pattern": pattern,
            "score_diff": score_diff,
            "improvements_used": len(improvements),
            "duration_seconds": duration,
            "recommendation": recommendation,
        }


class AcademicPipeline:
    """Pipeline academico completo."""

    def __init__(self):
        self.seeker = SeekerSimulator()
        self.review = PeerReviewSimulator()
        self.corrector = TSACCorrector()
        self.auditor = QualisA1Auditor()
        self.export_mgr = ExportManager()
        self.evolve = ManusEvolve()

    def run_maswos(self, topic: str) -> dict:
        """Executa fase MASWOS."""
        if not topic:
            return {"phases": [], "draft": ""}

        phases = []
        draft_parts = []
        for phase in MASWOS_PHASES:
            content = f"[{phase}] Analise de {topic[:50]} concluida."
            phases.append({"name": phase, "content": content})
            draft_parts.append(content)

        return {
            "phases": phases,
            "draft": "\n\n".join(draft_parts),
            "phases_count": len(phases),
        }

    def run_full(self, topic: str) -> dict:
        """Executa pipeline academico completo."""
        # 1. SEEKER
        seeker_result = self.seeker.search(topic)

        # 2. MASWOS
        maswos_result = self.run_maswos(topic)

        # 3. Peer Review
        review_result = self.review.evaluate(maswos_result["draft"])

        # 4. TSAC
        tsac_result = self.corrector.correct(maswos_result["draft"])

        # 5. Qualis
        qualis_result = self.auditor.audit(
            title=topic,
            abstract=maswos_result["draft"][:200],
            sections=[p["name"] for p in maswos_result["phases"]],
            references=[p["doi"] for p in seeker_result["papers"]],
        )

        # 6. Export
        export_result = self.export_mgr.verify_export_ready(
            sections=[{"title": p["name"], "content": p["content"]}
                     for p in maswos_result["phases"]],
            references=[p["doi"] for p in seeker_result["papers"]],
        )

        # 7. Manus Evolve
        evolve_result = self.evolve.learn({
            "topic": topic,
            "score_initial": 75,
            "score_final": qualis_result["score"],
            "improvements": tsac_result["changes"],
            "duration_seconds": 150,
        })

        return {
            "seeker": seeker_result,
            "maswos": maswos_result,
            "peer_review": review_result,
            "tsac": tsac_result,
            "qualis": qualis_result,
            "export": export_result,
            "evolve": evolve_result,
            "final_score": qualis_result["score"],
        }

    def check_reproducibility(self, topic: str, params: dict) -> dict:
        """Verifica reprodutibilidade."""
        reproducible = bool(topic and params)

        factors = []
        if params.get("model"):
            factors.append("Modelo definido")
        if params.get("temperature") is not None:
            factors.append("Temperatura configurada")

        return {
            "reproducible": reproducible,
            "factors": factors,
            "missing": [] if reproducible else ["Parametros insuficientes"],
        }


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Academic Pipeline")
    parser.add_argument("--topic", type=str, default="Otimizacao de agentes cognitivos")
    parser.add_argument("--pipeline", action="store_true")
    args = parser.parse_args()

    if args.pipeline:
        pipeline = AcademicPipeline()
        result = pipeline.run_full(args.topic)
        print(f"=== Academic Pipeline ===")
        print(f"Seeker: {len(result['seeker']['papers'])} papers")
        print(f"MASWOS: {result['maswos']['phases_count']} phases")
        print(f"Review: {result['peer_review']['average_score']}/100")
        print(f"TSAC: {result['tsac']['change_count']} changes")
        print(f"Qualis: {result['qualis']['score']}/100")
        print(f"Export: {'Ready' if result['export']['ready'] else 'Issues'}")
        print(f"Evolve: {result['evolve']['pattern']}")
        print(f"Final Score: {result['final_score']}")
