"""Testes para AutoSwarmBuilder (logica pura)."""

import sys,json; from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"nexus"/"scripts"))
import pytest
from auto_swarm_builder import AutoSwarmBuilder,AgentSpec,SwarmRouterConfig,BuiltInTaskAnalyzers

class TestAutoSwarm:
    def test_default_init(self):
        assert AutoSwarmBuilder().execution_type=="return-config"
    def test_agent_spec_defaults(self):
        s=AgentSpec(name="n",description="d",system_prompt="p")
        assert s.model_name=="big-pickle"
    def test_run_return_config(self):
        b=AutoSwarmBuilder()
        r=b.run("t",lambda p,t:json.dumps({"name":"sw","swarm_type":"seq","agents":[{"name":"a","description":"d","system_prompt":"p"}]}))
        assert isinstance(r,SwarmRouterConfig) and r.name=="sw"
    def test_run_return_agents(self):
        b=AutoSwarmBuilder(execution_type="return-agents")
        a=b.run("t",lambda p,t:json.dumps({"name":"sw","swarm_type":"seq","agents":[{"name":"a1","description":"d","system_prompt":"p"}]}))
        assert len(a)==1 and a[0].name=="a1"
    def test_run_return_json(self):
        b=AutoSwarmBuilder(execution_type="return-json")
        assert "sw" in b.run("t",lambda p,t:'{"name":"sw"}')
    def test_invalid_json(self):
        with pytest.raises(ValueError):
            AutoSwarmBuilder().run("t",lambda p,t:"bad json")
    def test_batch_run(self):
        b=AutoSwarmBuilder(execution_type="return-json")
        r=b.batch_run(["a","b","c"],lambda p,t:json.dumps({"n":"s"}))
        assert len(r)==3
    def test_builtin_analyzers(self):
        assert BuiltInTaskAnalyzers.research_task_analyzer()["name"]=="research-swarm"
        assert BuiltInTaskAnalyzers.code_review_task_analyzer()["name"]=="code-review-swarm"
        assert BuiltInTaskAnalyzers.content_creation_task_analyzer()["name"]=="content-swarm"
