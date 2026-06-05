#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, os, json, time, logging
from pathlib import Path
sys.path.insert(0, os.path.dirname(__file__))
from social_algorithms import Agent, SocialAlgorithms, SocialAlgorithmType
from auto_swarm_builder import AutoSwarmBuilder, BuiltInTaskAnalyzers
from aop_service_discovery import AOPServer
from context_offload import ContextOffloadManager

class NexusIntegration:
    def __init__(self, nexus_dir=None):
        self.nexus_dir = Path(nexus_dir or os.path.join(os.getcwd(), "nexus"))
        self.social_algorithms = {}
        self.aop_server = AOPServer(server_name="nexus-aop", verbose=False, queue_enabled=True)
        self.context_manager = ContextOffloadManager(base_dir=str(self.nexus_dir / "context_offload"))
        self.context_manager.create_session(project_id="nexus-integration")
        self.swarm_builder = AutoSwarmBuilder(verbose=False, execution_type="return-config")
        self._agent_registry = {}

    def register_agent(self, name, handler, description=""):
        agent = Agent(name, handler)
        self._agent_registry[name] = {"agent": agent, "description": description}
        self.aop_server.add_agent(name=name, description=description, handler=handler)

    def create_social_algorithm(self, name, agent_names, algorithm_type):
        agents = [self._agent_registry[a]["agent"] for a in agent_names if a in self._agent_registry]
        sa = SocialAlgorithms(name=name, agents=agents, algorithm_type=algorithm_type)
        self.social_algorithms[name] = sa
        return sa

    def execute_pipeline(self, task, algorithm_name, algorithm_args=None):
        if algorithm_name not in self.social_algorithms:
            raise ValueError(f"Algorithm not found: {algorithm_name}")
        sa = self.social_algorithms[algorithm_name]
        self.context_manager.add_entry(f"Task: {task[:100]}", priority=8)
        start = time.time()
        result = sa.run(task, algorithm_args=algorithm_args or {})
        self.context_manager.add_intermediate_result(algorithm_name, {
            "task": task, "success": result.success, "time": time.time() - start})
        return {"algorithm": algorithm_name, "success": result.success,
                "outputs": result.final_outputs, "execution_time": time.time() - start}

    def build_swarm_for_task(self, task, boss_agent_fn):
        config = self.swarm_builder.run(task, boss_agent_fn)
        agent_names = []
        for spec in config.agents:
            def make_handler(s): return lambda t, **kw: f"[{s.name}] {t}"
            self.register_agent(spec.name, make_handler(spec), spec.description)
            agent_names.append(spec.name)
        type_map = {"sequential": SocialAlgorithmType.SEQUENTIAL, "concurrent": SocialAlgorithmType.CONCURRENT,
                    "research_analysis_synthesis": SocialAlgorithmType.RESEARCH_ANALYSIS_SYNTHESIS,
                    "council_of_judges": SocialAlgorithmType.COUNCIL_OF_JUDGES,
                    "debate_with_judge": SocialAlgorithmType.DEBATE_WITH_JUDGE}
        algo_type = type_map.get(config.swarm_type, SocialAlgorithmType.SEQUENTIAL)
        self.create_social_algorithm(f"swarm-{config.name}", agent_names, algo_type)
        return {"config": config, "agents": agent_names, "algorithm_type": config.swarm_type}

    def get_context_summary(self):
        return self.context_manager.get_session_summary()

    def check_consistency(self, text):
        return self.context_manager.check_resume_consistency(self.context_manager.active_session, text)

    def get_status(self):
        return {"registered_agents": len(self._agent_registry),
                "social_algorithms": list(self.social_algorithms.keys()),
                "aop_stats": self.aop_server.get_server_stats(),
                "context_state": self.context_manager.get_session_state()}

if __name__ == "__main__":
    print("=" * 60)
    print("TESTE: Nexus Integration Layer")
    print("=" * 60)
    nexus = NexusIntegration()
    print("\n[1] Register Agents")
    nexus.register_agent("researcher", lambda t, **kw: f"Research: {t[:30]}", "Research specialist")
    nexus.register_agent("analyst", lambda t, **kw: f"Analysis: {t[:30]}", "Analysis specialist")
    nexus.register_agent("synthesizer", lambda t, **kw: f"Synthesis: {t[:30]}", "Synthesis specialist")
    print(f"  PASS - {len(nexus._agent_registry)} agents registered")
    print("\n[2] Create Social Algorithm")
    nexus.create_social_algorithm("research-pipeline", ["researcher", "analyst", "synthesizer"],
        SocialAlgorithmType.RESEARCH_ANALYSIS_SYNTHESIS)
    print(f"  PASS - Algorithm created")
    print("\n[3] Execute Pipeline")
    result = nexus.execute_pipeline("AI impact on healthcare", "research-pipeline")
    assert result["success"] and result["outputs"] is not None
    print(f"  PASS - Executed in {result['execution_time']:.3f}s")
    print("\n[4] Build Swarm for Task")
    swarm = nexus.build_swarm_for_task("Research trends", lambda p, t: json.dumps(BuiltInTaskAnalyzers.research_task_analyzer()))
    assert len(swarm["agents"]) == 3
    print(f"  PASS - Swarm with {len(swarm['agents'])} agents")
    print("\n[5] Context Tracking")
    summary = nexus.get_context_summary()
    consistency = nexus.check_consistency("AI impact research analysis")
    print(f"  PASS - Summary: {len(summary)} chars, Consistency: {consistency['status']}")
    print("\n[6] Status Report")
    status = nexus.get_status()
    assert status["registered_agents"] >= 3
    print(f"  PASS - {status['registered_agents']} agents, {len(status['social_algorithms'])} algorithms")
    print("\n" + "=" * 60)
    print("TODOS OS TESTES DE INTEGRACAO PASSARAM (6/6)")
    print("=" * 60)
