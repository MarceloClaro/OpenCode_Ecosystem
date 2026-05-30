"""Testes para SyncOrchestrator refatorado com DI."""

import sys; from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"_reversa_sdd"/"reconstruction"))
import pytest
from core.mock_services import MockStateManager
from nexus_sync_orchestrator import (SyncOrchestrator,DynamicScoringEngine,HealthEngine,
    ComponentDiscovery,AutoHealingEngine,CrossValidationEngine,ConflictDetector,SyncComponent)

class TestDynamicScoringEngine:
    def test_init_with_mock(self):
        sm=MockStateManager(); dse=DynamicScoringEngine(state_manager=sm)
        assert dse._sm is sm
    def test_record_and_get_score(self):
        sm=MockStateManager(); dse=DynamicScoringEngine(state_manager=sm)
        dse.record_usage("test",success=True,response_ms=100)
        assert dse.scores["test"].usage_count==1
    def test_get_underperforming(self):
        sm=MockStateManager(); dse=DynamicScoringEngine(state_manager=sm)
        for _ in range(5): dse.record_usage("bad",success=False,response_ms=9999)
        assert "bad" in dse.get_underperforming(threshold=60.0)
    def test_default_score(self):
        sm=MockStateManager(); dse=DynamicScoringEngine(state_manager=sm)
        assert dse.get_score("nonexistent")==85.0

class TestHealthEngine:
    def test_init_with_mock(self):
        sm=MockStateManager(); he=HealthEngine(state_manager=sm)
        assert he._sm is sm
    def test_compute_empty(self):
        sm=MockStateManager(); he=HealthEngine(state_manager=sm)
        assert he.compute([],[],0,{})==0.0

class TestSyncOrchestrator:
    def test_init_with_mock(self):
        sm=MockStateManager()
        orch=SyncOrchestrator(base_dir=Path(__file__).resolve().parents[2],state_manager=sm)
        assert orch._sm is sm

class TestComponentDiscovery:
    def test_discovery_empty(self):
        cd=ComponentDiscovery(Path("/nonexistent"))
        assert cd.discover_agents()==[]

class TestAutoHealingEngine:
    def test_assess(self):
        ah=AutoHealingEngine()
        assert ah.assess(96)=="healthy"; assert ah.assess(75)=="alert"; assert ah.assess(50)=="critical"

class TestConflictDetector:
    def test_detect_no_mcp(self):
        assert ConflictDetector().detect([])==[]
