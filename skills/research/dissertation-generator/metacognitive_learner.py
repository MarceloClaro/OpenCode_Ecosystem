#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Metacognitive Learning Module v1.0 — SPEC-052
=============================================
Aprende com ciclos anteriores de produção acadêmica.
Registra lições aprendidas, padrões de erro, e otimizações.

Autor: OpenCode Ecosystem (2026) — R27: Metacognitive Learning
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


BRAZIL_TZ = timezone.utc
LEARNINGS_FILE = Path(__file__).parent / "metacognitive_learnings.json"


@dataclass
class LessonLearned:
    """Lição aprendida de um ciclo."""
    lesson_id: str
    cycle: str              # e.g., "R26-dissertation"
    category: str           # e.g., "encoding", "compilation", "quality"
    description: str
    impact: str             # "critical" | "high" | "moderate" | "low"
    fix_applied: str
    prevention: str
    timestamp: str = ""


@dataclass
class PatternDetected:
    """Padrão detectado em múltiplos ciclos."""
    pattern_id: str
    description: str
    frequency: int
    affected_components: list[str]
    recommendation: str


class MetacognitiveLearner:
    """Aprende com ciclos de produção e otimiza pipeline."""

    def __init__(self):
        self.learnings: list[LessonLearned] = []
        self.patterns: list[PatternDetected] = []
        self._load_learnings()

    def _load_learnings(self):
        """Carrega lições salvas."""
        if LEARNINGS_FILE.exists():
            try:
                data = json.loads(LEARNINGS_FILE.read_text(encoding="utf-8"))
                self.learnings = [LessonLearned(**l) for l in data.get("learnings", [])]
                self.patterns = [PatternDetected(**p) for p in data.get("patterns", [])]
            except Exception:
                pass

    def _save_learnings(self):
        """Salva lições em disco."""
        data = {
            "learnings": [
                {
                    "lesson_id": l.lesson_id,
                    "cycle": l.cycle,
                    "category": l.category,
                    "description": l.description,
                    "impact": l.impact,
                    "fix_applied": l.fix_applied,
                    "prevention": l.prevention,
                    "timestamp": l.timestamp,
                }
                for l in self.learnings
            ],
            "patterns": [
                {
                    "pattern_id": p.pattern_id,
                    "description": p.description,
                    "frequency": p.frequency,
                    "affected_components": p.affected_components,
                    "recommendation": p.recommendation,
                }
                for p in self.patterns
            ],
            "last_updated": datetime.now(BRAZIL_TZ).isoformat(),
        }
        LEARNINGS_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    def record_lesson(self, lesson: LessonLearned):
        """Registra uma lição aprendida."""
        lesson.timestamp = datetime.now(BRAZIL_TZ).isoformat()
        self.learnings.append(lesson)
        self._detect_patterns()
        self._save_learnings()

    def _detect_patterns(self):
        """Detecta padrões recorrentes nas lições."""
        # Group by category
        by_category: dict[str, list[LessonLearned]] = {}
        for l in self.learnings:
            by_category.setdefault(l.category, []).append(l)

        # Detect patterns (3+ lessons in same category)
        self.patterns = []
        for cat, lessons in by_category.items():
            if len(lessons) >= 3:
                self.patterns.append(PatternDetected(
                    pattern_id=f"pattern-{cat}",
                    description=f"Padrão recorrente em {cat}: {len(lessons)} lições registradas",
                    frequency=len(lessons),
                    affected_components=list(set(
                        l.fix_applied[:50] for l in lessons
                    )),
                    recommendation=f"Automatizar correção para {cat} no pipeline"
                ))

    def get_recommendations(self, phase: str) -> list[str]:
        """Retorna recomendações para uma fase do pipeline."""
        recs = []
        for l in self.learnings:
            if phase.lower() in l.cycle.lower() or phase.lower() in l.category.lower():
                recs.append(f"[{l.impact}] {l.prevention}")
        return recs

    def get_stats(self) -> dict:
        """Retorna estatísticas de aprendizado."""
        return {
            "total_lessons": len(self.learnings),
            "total_patterns": len(self.patterns),
            "by_category": {},
            "by_impact": {},
            "last_cycle": self.learnings[-1].cycle if self.learnings else "none",
        }


# ═══════════════════════════════════════════════════════════════════════════
# R26 DISSERTATION CYCLE LESSONS
# ═══════════════════════════════════════════════════════════════════════════

R26_LESSONS = [
    LessonLearned(
        lesson_id="R26-001",
        cycle="R26-dissertation",
        category="encoding",
        description="Caracteres UTF-8 com acento (ç, ã) causam referências indefinidas em labels LaTeX",
        impact="critical",
        fix_applied="Substituição de caracteres acentuados por ASCII puro em labels",
        prevention="Sempre usar labels ASCII em \\label{} e \\ref{} — nunca acentos"
    ),
    LessonLearned(
        lesson_id="R26-002",
        cycle="R26-dissertation",
        category="bibliography",
        description="natbib+apalike não imprime URLs nas referências",
        impact="high",
        fix_applied="Migração para biblatex+biber com backend=biber,style=numeric",
        prevention="Usar biblatex+biber sempre que URLs forem obrigatórios"
    ),
    LessonLearned(
        lesson_id="R26-003",
        cycle="R26-dissertation",
        category="quality",
        description="Threshold anti-AI em 100% é inalcançável com texto acadêmico real",
        impact="high",
        fix_applied="Threshold ajustado para 85 (A) em vez de 100",
        prevention="Definir thresholds realistas baseados em benchmarks"
    ),
    LessonLearned(
        lesson_id="R26-004",
        cycle="R26-dissertation",
        category="citations",
        description="Notas de rodapé com (1) trecho original, (2) tradução, (3) resenha crítica melhoram rigor",
        impact="high",
        fix_applied="Padrão de nota de rodapé acadêmica documentado",
        prevention="Incluir padrão de footnote no template de dissertação"
    ),
    LessonLearned(
        lesson_id="R26-005",
        cycle="R26-dissertation",
        category="compilation",
        description="pdflatex precisa de 4 passos: pdflatex→biber→pdflatex→pdflatex",
        impact="moderate",
        fix_applied="Pipeline de compilação documentado no SPEC-052",
        prevention="Sempre executar pipeline completo de 4 passos"
    ),
    LessonLearned(
        lesson_id="R26-006",
        cycle="R26-dissertation",
        category="audio",
        description="edge-tts precisa de chunking para textos > 3500 caracteres",
        impact="moderate",
        fix_applied="Split em chunks de 3500 chars com concatenação binária",
        prevention="Usar chunk_size=3500 como padrão para edge-tts"
    ),
    LessonLearned(
        lesson_id="R26-007",
        cycle="R26-dissertation",
        category="docx",
        description="pandoc precisa de citeproc + APA CSL para bibliografia no DOCX",
        impact="moderate",
        fix_applied="Download automático de apa.csl + flag --citeproc",
        prevention="Incluir apa.csl no repositório da skill"
    ),
]


def initialize_learnings():
    """Inicializa lições do ciclo R26."""
    learner = MetacognitiveLearner()
    existing_ids = {l.lesson_id for l in learner.learnings}

    for lesson in R26_LESSONS:
        if lesson.lesson_id not in existing_ids:
            learner.record_lesson(lesson)

    stats = learner.get_stats()
    print(f"Metacognitive Learnings: {stats['total_lessons']} lições, {stats['total_patterns']} padrões")
    return learner


if __name__ == "__main__":
    learner = initialize_learnings()
    print(json.dumps(learner.get_stats(), indent=2))
