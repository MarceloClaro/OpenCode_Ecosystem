#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TDD Test Suite for Metacognitive Learner v1.0
==============================================
8 Casos de Teste (CTs) — pytest

Autor: OpenCode Ecosystem (2026) — R27: TDD
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "skills" / "research" / "dissertation-generator"))

from metacognitive_learner import (
    MetacognitiveLearner,
    LessonLearned,
    PatternDetected,
    initialize_learnings,
)


# ═══════════════════════════════════════════════════════════════════════════
# CT-ML.01: Learner initialization
# ═══════════════════════════════════════════════════════════════════════════

def test_ct_ml01_learner_init():
    """CT-ML.01: MetacognitiveLearner initializes with empty state."""
    learner = MetacognitiveLearner()
    assert isinstance(learner.learnings, list)
    assert isinstance(learner.patterns, list)


# ═══════════════════════════════════════════════════════════════════════════
# CT-ML.02: Record lesson
# ═══════════════════════════════════════════════════════════════════════════

def test_ct_ml02_record_lesson():
    """CT-ML.02: record_lesson adds lesson to list."""
    learner = MetacognitiveLearner()
    initial_count = len(learner.learnings)

    lesson = LessonLearned(
        lesson_id="TEST-001",
        cycle="test",
        category="encoding",
        description="Test lesson",
        impact="low",
        fix_applied="Test fix",
        prevention="Test prevention"
    )
    learner.record_lesson(lesson)

    assert len(learner.learnings) == initial_count + 1
    assert learner.learnings[-1].lesson_id == "TEST-001"
    assert learner.learnings[-1].timestamp != ""


# ═══════════════════════════════════════════════════════════════════════════
# CT-ML.03: Pattern detection (3+ same category)
# ═══════════════════════════════════════════════════════════════════════════

def test_ct_ml03_pattern_detection():
    """CT-ML.03: Pattern detected when 3+ lessons in same category."""
    learner = MetacognitiveLearner()
    initial_patterns = len(learner.patterns)

    # Use unique category to avoid conflito com lessons pre-existentes
    import uuid
    unique_cat = f"test_pattern_{uuid.uuid4().hex[:8]}"

    for i in range(3):
        learner.record_lesson(LessonLearned(
            lesson_id=f"PATTERN-{i}",
            cycle="test",
            category=unique_cat,
            description=f"Test pattern issue {i}",
            impact="low",
            fix_applied="fix",
            prevention="prevent"
        ))

    assert len(learner.patterns) >= initial_patterns + 1


# ═══════════════════════════════════════════════════════════════════════════
# CT-ML.04: Get recommendations
# ═══════════════════════════════════════════════════════════════════════════

def test_ct_ml04_get_recommendations():
    """CT-ML.04: get_recommendations returns relevant suggestions."""
    learner = MetacognitiveLearner()
    learner.record_lesson(LessonLearned(
        lesson_id="REC-001",
        cycle="R26-dissertation",
        category="encoding",
        description="Test",
        impact="high",
        fix_applied="fix",
        prevention="Use ASCII labels"
    ))

    recs = learner.get_recommendations("encoding")
    assert len(recs) > 0
    assert "ASCII" in recs[0]


# ═══════════════════════════════════════════════════════════════════════════
# CT-ML.05: Get stats
# ═══════════════════════════════════════════════════════════════════════════

def test_ct_ml05_get_stats():
    """CT-ML.05: get_stats returns accurate counts."""
    learner = MetacognitiveLearner()
    stats = learner.get_stats()
    assert "total_lessons" in stats
    assert "total_patterns" in stats
    assert "last_cycle" in stats


# ═══════════════════════════════════════════════════════════════════════════
# CT-ML.06: Initialize R26 lessons
# ═══════════════════════════════════════════════════════════════════════════

def test_ct_ml06_initialize_r26():
    """CT-ML.06: initialize_learnings loads R26 lessons."""
    learner = initialize_learnings()
    r26_lessons = [l for l in learner.learnings if l.cycle == "R26-dissertation"]
    assert len(r26_lessons) >= 7


# ═══════════════════════════════════════════════════════════════════════════
# CT-ML.07: LessonLearned dataclass
# ═══════════════════════════════════════════════════════════════════════════

def test_ct_ml07_lesson_dataclass():
    """CT-ML.07: LessonLearned dataclass works correctly."""
    lesson = LessonLearned(
        lesson_id="DC-001",
        cycle="test",
        category="test",
        description="Test",
        impact="low",
        fix_applied="fix",
        prevention="prevent"
    )
    assert lesson.lesson_id == "DC-001"
    assert lesson.impact == "low"
    assert lesson.timestamp == ""


# ═══════════════════════════════════════════════════════════════════════════
# CT-ML.08: PatternDetected dataclass
# ═══════════════════════════════════════════════════════════════════════════

def test_ct_ml08_pattern_dataclass():
    """CT-ML.08: PatternDetected dataclass works correctly."""
    pattern = PatternDetected(
        pattern_id="P-001",
        description="Test pattern",
        frequency=5,
        affected_components=["comp1", "comp2"],
        recommendation="Fix it"
    )
    assert pattern.pattern_id == "P-001"
    assert pattern.frequency == 5
    assert len(pattern.affected_components) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
