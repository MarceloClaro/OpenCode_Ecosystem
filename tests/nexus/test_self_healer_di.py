"""Testes para SelfHealer refatorado com DI."""

import sys; from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"_reversa_sdd"/"reconstruction"))
import pytest
from core.mock_services import MockStateManager,MockEventBus
from nexus_self_healer import SelfHealer

class TestSelfHealerInit:
    def test_with_mocks(self):
        sm=MockStateManager(); eb=MockEventBus()
        h=SelfHealer(state_manager=sm,event_bus=eb)
        assert h._sm is sm; assert h._eb is eb

class TestSelfHealerChecks:
    def test_cjk_empty_workspace(self,tmp_path):
        h=SelfHealer(state_manager=MockStateManager(),event_bus=MockEventBus())
        h.WORKSPACE=tmp_path
        assert h.check_cjk_leaks()==[]
    def test_frontmatter_no_issues(self,tmp_path):
        h=SelfHealer(state_manager=MockStateManager(),event_bus=MockEventBus())
        d=tmp_path/"test"; d.mkdir(); (d/"SKILL.md").write_text("---\nname: x\ndescription: x\n---\ncontent")
        h.WORKSPACE=tmp_path
        assert h.check_frontmatter()==[]
    def test_fix_frontmatter(self,tmp_path):
        h=SelfHealer(state_manager=MockStateManager(),event_bus=MockEventBus())
        d=tmp_path/"ts"; d.mkdir(); f=d/"SKILL.md"; f.write_text("no frontmatter")
        h.WORKSPACE=tmp_path
        n=h.fix_frontmatter(h.check_frontmatter())
        assert n==1; assert "---" in f.read_text("utf-8")
    def test_skill_sizes_large(self,tmp_path):
        h=SelfHealer(state_manager=MockStateManager(),event_bus=MockEventBus())
        d=tmp_path/"large"; d.mkdir(); (d/"SKILL.md").write_text("x"*3000)
        h.WORKSPACE=tmp_path
        assert len(h.check_skill_sizes())==1

class TestSelfHealerReport:
    def test_check_and_report(self,tmp_path):
        h=SelfHealer(state_manager=MockStateManager(),event_bus=MockEventBus())
        h.WORKSPACE=tmp_path
        r=h.check_and_report()
        assert "timestamp" in r and "totals" in r
    def test_auto_fix(self,tmp_path):
        h=SelfHealer(state_manager=MockStateManager(),event_bus=MockEventBus())
        d=tmp_path/"sk"; d.mkdir(); (d/"SKILL.md").write_text("texto com \u4e2d\u6587 CJK")
        h.WORKSPACE=tmp_path
        r=h.check_and_report(); result=h.auto_fix(r)
        assert result["correcoes"].get("cjk_fixed",0)>0
