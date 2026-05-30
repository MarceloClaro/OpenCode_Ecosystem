"""Testes para MicroReasoningEngine (logica pura)."""

import sys; from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"nexus"/"scripts"))
import pytest
from micro_reasoning_types import MicroReasoningEngine,ReasoningType,ReasoningCategory

class TestMicroReasoning:
    def test_init_has_types(self):
        e=MicroReasoningEngine(); assert len(e.reasoning_types)>=8
    def test_valid_types(self):
        for rt in MicroReasoningEngine().reasoning_types.values():
            assert 0<=rt.complexity<=1 and 0<=rt.confidence<=1
    def test_select_returns_tuple(self):
        rt,s=MicroReasoningEngine().select_reasoning_type({"available_data":["implication","premise"]},"validacao",{})
        assert isinstance(rt,ReasoningType) and 0<=s<=1
    def test_get_by_name(self):
        rt=MicroReasoningEngine().get_reasoning_type("modus_ponens")
        assert rt is not None and rt.name=="Modus Ponens"
    def test_get_nonexistent(self):
        assert MicroReasoningEngine().get_reasoning_type("x") is None
    def test_report(self):
        assert "Total Reasoning Types" in MicroReasoningEngine().generate_reasoning_report()
