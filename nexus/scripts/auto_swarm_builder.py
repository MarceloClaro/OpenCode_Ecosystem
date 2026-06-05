#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AutoSwarmBuilder - Automatic Multi-Agent Pipeline Creation
"""
import json, logging
from typing import Any, Optional
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

@dataclass
class AgentSpec:
    name: str
    description: str
    system_prompt: str
    model_name: str = "big-pickle"
    max_loops: int = 1
    tools: list = field(default_factory=list)

@dataclass
class SwarmRouterConfig:
    name: str
    description: str
    agents: list
    swarm_type: str
    rules: Optional[str] = None
    task: str = ""

BOSS_SYSTEM_PROMPT = '''You are an expert Multi-Agent Architect.
Analyze the task and return JSON with: name, description, swarm_type, agents[], rules.
Available swarm_types: sequential, concurrent, hierarchical, research_analysis_synthesis, debate_with_judge, council_of_judges'''

class AutoSwarmBuilder:
    def __init__(self, name="auto-swarm-builder", description="Auto Swarm Builder",
                 verbose=True, max_loops=1, model_name="big-pickle",
                 execution_type="return-config", system_prompt=BOSS_SYSTEM_PROMPT):
        self.name = name
        self.description = description
        self.verbose = verbose
        self.max_loops = max_loops
        self.model_name = model_name
        self.execution_type = execution_type
        self.system_prompt = system_prompt
        self.agents_pool = []

    def run(self, task: str, boss_agent_fn) -> Any:
        if self.verbose:
            logger.info(f"Analyzing task: {task[:100]}...")
        boss_response = boss_agent_fn(self.system_prompt, task)
        try:
            config = json.loads(boss_response)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON from boss agent: {boss_response[:500]}")

        agents = []
        for ad in config.get("agents", []):
            agents.append(AgentSpec(name=ad["name"], description=ad["description"],
                system_prompt=ad["system_prompt"], model_name=ad.get("model_name", self.model_name),
                max_loops=ad.get("max_loops", self.max_loops)))

        if self.execution_type == "return-agents":
            return agents
        elif self.execution_type == "return-config":
            return SwarmRouterConfig(name=config.get("name", self.name),
                description=config.get("description", self.description), agents=agents,
                swarm_type=config.get("swarm_type", "sequential"),
                rules=config.get("rules"), task=task)
        elif self.execution_type == "return-json":
            return boss_response
        else:
            raise ValueError(f"Unknown execution_type: {self.execution_type}")

    def batch_run(self, tasks: list, boss_agent_fn) -> list:
        results = []
        for i, task in enumerate(tasks):
            if self.verbose:
                logger.info(f"Batch task {i+1}/{len(tasks)}")
            results.append(self.run(task, boss_agent_fn))
        return results

    @staticmethod
    def create_agents_from_specs(specs: list, agent_factory) -> list:
        return [agent_factory(spec) for spec in specs]

class BuiltInTaskAnalyzers:
    @staticmethod
    def research_task_analyzer() -> dict:
        return {"name": "research-swarm", "description": "Multi-agent research pipeline",
            "swarm_type": "research_analysis_synthesis", "agents": [
                {"name": "researcher", "description": "Research specialist", "system_prompt": "You are a researcher"},
                {"name": "analyst", "description": "Analysis specialist", "system_prompt": "You are an analyst"},
                {"name": "synthesizer", "description": "Synthesis specialist", "system_prompt": "You are a synthesizer"}]}

    @staticmethod
    def code_review_task_analyzer() -> dict:
        return {"name": "code-review-swarm", "description": "Multi-agent code review",
            "swarm_type": "council_of_judges", "agents": [
                {"name": "security", "description": "Security reviewer", "system_prompt": "Security expert"},
                {"name": "performance", "description": "Performance reviewer", "system_prompt": "Performance expert"},
                {"name": "quality", "description": "Quality reviewer", "system_prompt": "Quality expert"}]}

    @staticmethod
    def content_creation_task_analyzer() -> dict:
        return {"name": "content-swarm", "description": "Content creation pipeline",
            "swarm_type": "sequential", "agents": [
                {"name": "outliner", "description": "Outlining specialist", "system_prompt": "Outliner"},
                {"name": "writer", "description": "Writing specialist", "system_prompt": "Writer"},
                {"name": "editor", "description": "Editing specialist", "system_prompt": "Editor"}]}
