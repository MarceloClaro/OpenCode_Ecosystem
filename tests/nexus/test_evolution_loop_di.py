"""Testes para EvolutionLoop refatorado com DI."""

import sys; from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"_reversa_sdd"/"reconstruction"))
import pytest
from core.mock_services import MockStateManager
from nexus_evolution_loop import FeedbackLoopEngine,OutcomeRecord,LearningRecord,EvolutionCycle

class TestFeedbackLoopEngine:
    def test_init_with_mock(self):
        sm=MockStateManager(); fb=FeedbackLoopEngine(state_manager=sm)
        assert fb._sm is sm
    def test_record_outcome(self):
        sm=MockStateManager(); fb=FeedbackLoopEngine(state_manager=sm)
        r=fb.record_outcome("comp","act",True,85.0,100.0)
        assert isinstance(r,OutcomeRecord); assert r.component=="comp"
    def test_extract_learnings_empty(self):
        fb=FeedbackLoopEngine(state_manager=MockStateManager())
        assert fb.extract_learnings()==[]
    def test_extract_learnings_with_data(self):
        fb=FeedbackLoopEngine(state_manager=MockStateManager())
        for _ in range(10): fb.record_outcome("c","a",True,90.0,50)
        L=fb.extract_learnings(min_confidence=0.5)
        assert any("reliable" in l.pattern for l in L)
    def test_rotate_outcomes(self):
        fb=FeedbackLoopEngine(state_manager=MockStateManager())
        for _ in range(150): fb.record_outcome("c","a",True,80,30)
        assert fb.rotate_outcomes(max_keep=100)==50
    def test_pagination(self):
        fb=FeedbackLoopEngine(state_manager=MockStateManager())
        for i in range(25): fb.record_outcome(f"c{i}","a",True,80,30)
        p1=fb.get_outcomes_paginated(page=1,page_size=10)
        assert len(p1["outcomes"])==10 and p1["has_next"]
    def test_cycle_summary(self):
        fb=FeedbackLoopEngine(state_manager=MockStateManager())
        assert fb.get_cycle_summary()["total_cycles"]==0
