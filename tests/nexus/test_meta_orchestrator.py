"""Testes para meta_orchestrate() (funcao pura)."""

import sys; from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"nexus"/"scripts"))
from meta_orchestrator import meta_orchestrate

class TestMetaOrchestrate:
    def test_returns_true(self):
        assert meta_orchestrate("x") is True
    def test_output_steps(self,capsys):
        meta_orchestrate("test")
        o=capsys.readouterr().out
        assert all(s in o for s in ["SB0.1","SB0.2","SB0.3","SB0.4","SB0.5"])
