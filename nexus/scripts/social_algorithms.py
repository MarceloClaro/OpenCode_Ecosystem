#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Social Algorithms Framework for Nexus Multi-Agent Orchestration
"""
import asyncio, logging, time
from enum import Enum
from typing import Any, Callable, Optional
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

class SocialAlgorithmType(Enum):
    CUSTOM = "custom"
    SEQUENTIAL = "sequential"
    CONCURRENT = "concurrent"
    HIERARCHICAL = "hierarchical"
    MESH = "mesh"
    ROUND_ROBIN = "round_robin"
    BROADCAST = "broadcast"
    RESEARCH_ANALYSIS_SYNTHESIS = "research_analysis_synthesis"
    DEBATE_WITH_JUDGE = "debate_with_judge"
    COUNCIL_OF_JUDGES = "council_of_judges"

@dataclass
class SocialAlgorithmResult:
    algorithm_name: str
    execution_time: float
    final_outputs: Any
    communication_log: list = field(default_factory=list)
    success: bool = True
    error: Optional[str] = None

class Agent:
    def __init__(self, name: str, run_fn: Callable):
        self.name = name
        self._run_fn = run_fn
    def run(self, task: str, **kwargs) -> Any:
        return self._run_fn(task, **kwargs)

class SocialAlgorithms:
    def __init__(self, name: str, agents: list, social_algorithm: Optional[Callable] = None,
                 algorithm_type: SocialAlgorithmType = SocialAlgorithmType.CUSTOM,
                 verbose: bool = False, max_execution_time: Optional[int] = None,
                 enable_communication_logging: bool = True):
        self.name = name
        self.agents = agents
        self.social_algorithm = social_algorithm
        self.algorithm_type = algorithm_type
        self.verbose = verbose
        self.max_execution_time = max_execution_time
        self.enable_communication_logging = enable_communication_logging
        self.communication_log = []

    def add_agent(self, agent: Agent) -> None:
        self.agents.append(agent)

    def remove_agent(self, agent_name: str) -> bool:
        for i, agent in enumerate(self.agents):
            if agent.name == agent_name:
                self.agents.pop(i)
                return True
        return False

    def run(self, task: str, algorithm_args: Optional[dict] = None, **kwargs) -> SocialAlgorithmResult:
        start_time = time.time()
        algorithm_args = algorithm_args or {}
        try:
            if self.social_algorithm:
                result = self.social_algorithm(self.agents, task, **algorithm_args, **kwargs)
            else:
                result = self._run_builtin(task, algorithm_args, **kwargs)
            execution_time = time.time() - start_time
            return SocialAlgorithmResult(algorithm_name=self.name, execution_time=execution_time,
                final_outputs=result, communication_log=self.communication_log.copy(), success=True)
        except Exception as e:
            execution_time = time.time() - start_time
            return SocialAlgorithmResult(algorithm_name=self.name, execution_time=execution_time,
                final_outputs=None, communication_log=self.communication_log.copy(), success=False, error=str(e))

    async def run_async(self, task: str, algorithm_args: Optional[dict] = None, **kwargs) -> SocialAlgorithmResult:
        start_time = time.time()
        algorithm_args = algorithm_args or {}
        try:
            if self.social_algorithm:
                if asyncio.iscoroutinefunction(self.social_algorithm):
                    result = await self.social_algorithm(self.agents, task, **algorithm_args, **kwargs)
                else:
                    result = await asyncio.to_thread(self.social_algorithm, self.agents, task, **algorithm_args, **kwargs)
            else:
                result = await self._run_builtin_async(task, algorithm_args, **kwargs)
            execution_time = time.time() - start_time
            return SocialAlgorithmResult(algorithm_name=self.name, execution_time=execution_time,
                final_outputs=result, communication_log=self.communication_log.copy(), success=True)
        except Exception as e:
            execution_time = time.time() - start_time
            return SocialAlgorithmResult(algorithm_name=self.name, execution_time=execution_time,
                final_outputs=None, communication_log=self.communication_log.copy(), success=False, error=str(e))

    def _log_communication(self, agent_name: str, action: str, result: Any) -> None:
        if self.enable_communication_logging:
            entry = {"timestamp": time.time(), "agent": agent_name, "action": action,
                     "result_summary": str(result)[:200] if result else None}
            self.communication_log.append(entry)
            if self.verbose:
                logger.info(f"[{agent_name}] {action}: {entry['result_summary']}")

    def _run_builtin(self, task: str, args: dict, **kwargs) -> Any:
        handlers = {
            SocialAlgorithmType.SEQUENTIAL: self._sequential,
            SocialAlgorithmType.CONCURRENT: self._concurrent,
            SocialAlgorithmType.HIERARCHICAL: self._hierarchical,
            SocialAlgorithmType.ROUND_ROBIN: self._round_robin,
            SocialAlgorithmType.BROADCAST: self._broadcast,
            SocialAlgorithmType.RESEARCH_ANALYSIS_SYNTHESIS: self._research_analysis_synthesis,
            SocialAlgorithmType.DEBATE_WITH_JUDGE: self._debate_with_judge,
            SocialAlgorithmType.COUNCIL_OF_JUDGES: self._council_of_judges,
        }
        handler = handlers.get(self.algorithm_type)
        if not handler:
            raise ValueError(f"Unknown algorithm type: {self.algorithm_type}")
        return handler(task, args, **kwargs)

    async def _run_builtin_async(self, task: str, args: dict, **kwargs) -> Any:
        handlers = {
            SocialAlgorithmType.SEQUENTIAL: self._sequential_async,
            SocialAlgorithmType.CONCURRENT: self._concurrent_async,
            SocialAlgorithmType.HIERARCHICAL: self._hierarchical_async,
            SocialAlgorithmType.ROUND_ROBIN: self._round_robin_async,
            SocialAlgorithmType.BROADCAST: self._broadcast_async,
        }
        handler = handlers.get(self.algorithm_type)
        if not handler:
            raise ValueError(f"Unknown algorithm type: {self.algorithm_type}")
        return await handler(task, args, **kwargs)

    def _sequential(self, task, args, **kwargs):
        results = []
        current = task
        for a in self.agents:
            self._log_communication(a.name, "sequential", None)
            r = a.run(current, **kwargs)
            results.append(r)
            current = str(r)
            self._log_communication(a.name, "completed", r)
        return results

    def _concurrent(self, task, args, **kwargs):
        results = []
        for a in self.agents:
            self._log_communication(a.name, "concurrent start", None)
        for a in self.agents:
            r = a.run(task, **kwargs)
            results.append({"agent": a.name, "result": r})
            self._log_communication(a.name, "completed", r)
        return results

    def _hierarchical(self, task, args, **kwargs):
        if not self.agents: return {}
        leader = self.agents[0]
        workers = self.agents[1:]
        lr = leader.run(f"Analyze and delegate: {task}", **kwargs)
        wr = []
        for w in workers:
            r = w.run(f"Execute based on: {lr}", **kwargs)
            wr.append({"agent": w.name, "result": r})
        return {"leader_result": lr, "worker_results": wr}

    def _round_robin(self, task, args, **kwargs):
        rounds = args.get("rounds", 3)
        results = []
        for rn in range(rounds):
            rr = []
            for a in self.agents:
                r = a.run(f"Round {rn+1}: {task}", **kwargs)
                rr.append({"agent": a.name, "result": r})
            results.append({"round": rn+1, "results": rr})
        return results

    def _broadcast(self, task, args, **kwargs):
        results = []
        for a in self.agents:
            r = a.run(task, **kwargs)
            results.append({"agent": a.name, "result": r})
        return results

    def _research_analysis_synthesis(self, task, args, **kwargs):
        if len(self.agents) < 3:
            raise ValueError("Need 3+ agents")
        r = self.agents[0].run(f"Research: {task}", **kwargs)
        a = self.agents[1].run(f"Analyze: {r}", **kwargs)
        s = self.agents[2].run(f"Synthesize: {r} + {a}", **kwargs)
        return {"research": r, "analysis": a, "synthesis": s}

    def _debate_with_judge(self, task, args, **kwargs):
        if len(self.agents) < 3:
            raise ValueError("Need 3+ agents")
        pro, con, judge = self.agents[0], self.agents[1], self.agents[2]
        rounds = args.get("rounds", 2)
        pa, ca = [], []
        for rn in range(rounds):
            pr = pro.run(f"Argue for (round {rn+1}): {task}", **kwargs)
            pa.append(pr)
            cr = con.run(f"Argue against (round {rn+1}): {task}", **kwargs)
            ca.append(cr)
        j = judge.run(f"Judge: {task}\nPro: {pa}\nCon: {ca}", **kwargs)
        return {"pro_arguments": pa, "con_arguments": ca, "judgment": j}

    def _council_of_judges(self, task, args, **kwargs):
        if len(self.agents) < 2:
            raise ValueError("Need 2+ agents")
        votes = []
        for ja in self.agents:
            v = ja.run(f"Vote on: {task}. APPROVE or REJECT.", **kwargs)
            votes.append({"judge": ja.name, "vote": v})
        ac = sum(1 for v in votes if "APPROVE" in str(v["vote"]).upper())
        rc = len(votes) - ac
        verdict = "APPROVED" if ac > rc else "REJECTED"
        return {"votes": votes, "approve_count": ac, "reject_count": rc, "verdict": verdict}

    async def _sequential_async(self, task, args, **kwargs):
        results = []
        current = task
        for a in self.agents:
            r = a.run(current, **kwargs)
            results.append(r)
            current = str(r)
        return results

    async def _concurrent_async(self, task, args, **kwargs):
        async def run_agent(agent):
            return {"agent": agent.name, "result": agent.run(task, **kwargs)}
        return await asyncio.gather(*[run_agent(a) for a in self.agents])

    async def _hierarchical_async(self, task, args, **kwargs):
        if not self.agents: return {}
        leader = self.agents[0]
        workers = self.agents[1:]
        lr = leader.run(f"Analyze: {task}", **kwargs)
        async def run_worker(w):
            return {"agent": w.name, "result": w.run(f"Execute: {lr}", **kwargs)}
        wr = await asyncio.gather(*[run_worker(w) for w in workers])
        return {"leader_result": lr, "worker_results": list(wr)}

    async def _round_robin_async(self, task, args, **kwargs):
        rounds = args.get("rounds", 3)
        results = []
        for rn in range(rounds):
            rr = []
            for a in self.agents:
                r = a.run(f"Round {rn+1}: {task}", **kwargs)
                rr.append({"agent": a.name, "result": r})
            results.append({"round": rn+1, "results": rr})
        return results

    async def _broadcast_async(self, task, args, **kwargs):
        async def run_agent(agent):
            return {"agent": agent.name, "result": agent.run(task, **kwargs)}
        return await asyncio.gather(*[run_agent(a) for a in self.agents])

    def get_communication_history(self) -> list:
        return self.communication_log.copy()
