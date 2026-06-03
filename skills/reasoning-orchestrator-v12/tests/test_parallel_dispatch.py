#!/usr/bin/env python
# =====================================================================
# TESTES — ParallelDispatch Intra-Fase (Ciclo 1)
# =====================================================================
# TDD: Escrever testes ANTES da implementação.
# Pipeline: RED (falha) → GREEN (passa) → REFACTOR (otimiza)
# =====================================================================
import sys, os, time, json
import unittest
from concurrent.futures import ThreadPoolExecutor, as_completed

# Path setup for v12
V12_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "agents")
V11_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                         "..", "reasoning-orchestrator-v11", "agents")
sys.path.insert(0, V12_PATH)
sys.path.insert(0, V11_PATH)

# Import v11 base classes (reused)
from framework import ReasoningAgent, ReasoningResult, REASONING_REGISTRY


# =====================================================================
# AGENT DUMMY PARA TESTES
# =====================================================================

class _DummyTestAgent(ReasoningAgent):
    """Agente ReasoningAgent concreto para testes de paralelismo.
    
    Dorme por sleep_time segundos e retorna um resultado dummy.
    """
    def __init__(self, agent_id: str, reasoning_type: str,
                 category: str, sleep_time: float = 0.1):
        super().__init__(agent_id, reasoning_type, category)
        self._sleep = sleep_time
    
    def reason(self, ctx: dict) -> ReasoningResult:
        time.sleep(self._sleep)
        return ReasoningResult(
            agent_id=self.agent_id,
            reasoning_type=self.reasoning_type,
            category=self.category,
            conclusion=f"Done in {self._sleep}s",
            confidence=0.9 - self._sleep * 0.1,
        )
    
    def get_dependencies(self) -> list:
        return []
    
    def validate_dependencies(self, ctx: dict) -> bool:
        return True


# =====================================================================
# TEST PARALLEL DISPATCH
# =====================================================================

class TestParallelDispatchBase(unittest.TestCase):
    """Testes base para ParallelDispatch (falham até implementação)."""
    
    def setUp(self):
        """Configura ambiente de teste."""
        # Importa após path estar configurado
        try:
            from parallel_dispatch import ParallelDispatch
            from orchestrator_v12 import ParallelOrchestrator
            self.ParallelDispatch = ParallelDispatch
            self.ParallelOrchestrator = ParallelOrchestrator
            self.HAS_V12 = True
        except ImportError:
            self.HAS_V12 = False
        
        self.sample_problem = {
            "id": "TEST-001",
            "description": "Prove that sqrt(2) is irrational",
            "domain": "mathematics",
            "structure": {"type": "number_theory"},
            "claimed_answer": set(),
        }
    
    # -----------------------------------------------------------------
    # TEST 1.1: ParallelDispatch existe e pode ser instanciado
    # -----------------------------------------------------------------
    def test_parallel_dispatch_exists(self):
        """C1-T1: ParallelDispatch deve ser importável e instanciável."""
        if not self.HAS_V12:
            self.skipTest("ParallelDispatch não implementado ainda")
        dispatcher = self.ParallelDispatch()
        self.assertIsNotNone(dispatcher)
        self.assertTrue(hasattr(dispatcher, "dispatch_phase"))
    
    # -----------------------------------------------------------------
    # TEST 1.2: Dispatch executa agentes em paralelo
    # -----------------------------------------------------------------
    def test_dispatch_parallel_execution(self):
        """C1-T2: Agentes de uma fase devem executar em paralelo."""
        if not self.HAS_V12:
            self.skipTest("ParallelDispatch não implementado ainda")
        dispatcher = self.ParallelDispatch()
        
        # Criar 3 agentes dummy com tempos diferentes
        agents = self._create_test_agents([0.2, 0.3, 0.1])
        
        start = time.time()
        results = dispatcher.dispatch_phase(
            agents=agents,
            context={"problem": self.sample_problem, "agent_results": {}},
            max_workers=3
        )
        elapsed = time.time() - start
        
        # Paralelo com 3 workers: tempo deve ser ~max(0.2, 0.3, 0.1) = ~0.3s
        # Sequencial seria ~0.2+0.3+0.1 = ~0.6s
        self.assertLess(elapsed, 0.5, 
                       f"Tempo paralelo ({elapsed:.3f}s) deve ser < soma sequencial (~0.6s)")
        self.assertEqual(len(results), 3, "Deve ter 3 resultados")
    
    # -----------------------------------------------------------------
    # TEST 1.3: Todos os resultados são coletados
    # -----------------------------------------------------------------
    def test_all_results_collected(self):
        """C1-T3: Todos os agentes devem ter seus resultados coletados."""
        if not self.HAS_V12:
            self.skipTest("ParallelDispatch não implementado ainda")
        dispatcher = self.ParallelDispatch()
        agents = self._create_test_agents([0.1, 0.1, 0.1])
        
        results = dispatcher.dispatch_phase(
            agents=agents,
            context={"problem": self.sample_problem, "agent_results": {}},
        )
        
        agent_ids = [a.agent_id for a in agents]
        for aid in agent_ids:
            self.assertIn(aid, results, f"Resultado para {aid} deve existir")
    
    # -----------------------------------------------------------------
    # TEST 1.4: Falha de um agente não aborta os outros
    # -----------------------------------------------------------------
    def test_failure_isolation(self):
        """C1-T4: Falha em um agente não deve abortar execução dos outros."""
        if not self.HAS_V12:
            self.skipTest("ParallelDispatch não implementado ainda")
        dispatcher = self.ParallelDispatch()
        
        class FailingAgent(ReasoningAgent):
            def __init__(self):
                super().__init__("failing-agent", "R01", "I")
            def reason(self, ctx):
                raise RuntimeError("Falha intencional")
            def get_dependencies(self):
                return []
            def validate_dependencies(self, ctx):
                return True
        
        class WorkingAgent(ReasoningAgent):
            def __init__(self):
                super().__init__("working-agent", "R02", "I")
            def reason(self, ctx):
                return ReasoningResult(
                    agent_id="working-agent",
                    reasoning_type="R02",
                    category="I",
                    conclusion="OK",
                    confidence=0.95,
                )
            def get_dependencies(self):
                return []
            def validate_dependencies(self, ctx):
                return True
        
        agents = [FailingAgent(), WorkingAgent()]
        results = dispatcher.dispatch_phase(
            agents=agents,
            context={"problem": self.sample_problem, "agent_results": {}},
        )
        
        self.assertIn("working-agent", results)
        self.assertEqual(results["working-agent"].result.confidence, 0.95)
        # O agente que falhou pode não estar em results (depende da implementação)
    
    # -----------------------------------------------------------------
    # TEST 1.5: Timeout é respeitado
    # -----------------------------------------------------------------
    def test_agent_timeout(self):
        """C1-T5: Agente que excede timeout deve ser interrompido."""
        if not self.HAS_V12:
            self.skipTest("ParallelDispatch não implementado ainda")
        dispatcher = self.ParallelDispatch()
        
        class SlowAgent(ReasoningAgent):
            def __init__(self):
                super().__init__("slow-agent", "R01", "I")
            def reason(self, ctx):
                time.sleep(5)  # Muito lento
                return ReasoningResult(
                    agent_id="slow-agent",
                    reasoning_type="R01",
                    category="I",
                    conclusion="Too late",
                    confidence=0.5,
                )
            def get_dependencies(self):
                return []
            def validate_dependencies(self, ctx):
                return True
        
        agents = [SlowAgent()]
        start = time.time()
        results = dispatcher.dispatch_phase(
            agents=agents,
            context={"problem": self.sample_problem, "agent_results": {}},
            timeout_per_agent=1.0  # 1 segundo de timeout
        )
        elapsed = time.time() - start
        
        self.assertLess(elapsed, 3.0, 
                       f"Timeout deve evitar execução longa ({elapsed:.2f}s)")
    
    # -----------------------------------------------------------------
    # TEST 1.6: Métricas de paralelismo são reportadas
    # -----------------------------------------------------------------
    def test_parallel_metrics_reported(self):
        """C1-T6: ParallelResult deve incluir métricas de tempo e thread."""
        if not self.HAS_V12:
            self.skipTest("ParallelDispatch não implementado ainda")
        dispatcher = self.ParallelDispatch()
        agents = self._create_test_agents([0.1, 0.1])
        
        results = dispatcher.dispatch_phase(
            agents=agents,
            context={"problem": self.sample_problem, "agent_results": {}},
        )
        
        for aid, pr in results.items():
            self.assertGreater(pr.elapsed_ms, 0, 
                              f"{aid}: elapsed_ms deve ser > 0")
            self.assertIsInstance(pr.thread_id, int,
                                 f"{aid}: thread_id deve ser int")
            self.assertIsNotNone(pr.result,
                                f"{aid}: result não deve ser None")
    
    # -----------------------------------------------------------------
    # TEST 1.7: Dependências são validadas antes da execução
    # -----------------------------------------------------------------
    def test_dependency_validation(self):
        """C1-T7: Agentes com dependências insatisfeitas devem ser pulados."""
        if not self.HAS_V12:
            self.skipTest("ParallelDispatch não implementado ainda")
        dispatcher = self.ParallelDispatch()
        
        class DependentAgent(ReasoningAgent):
            def __init__(self):
                super().__init__("dependent", "R02", "I")
            def reason(self, ctx):
                return ReasoningResult(...)
            def get_dependencies(self):
                return ["some-prerequisite"]
            def validate_dependencies(self, ctx):
                return "some-prerequisite" in ctx.get("agent_results", {})
        
        agent = DependentAgent()
        results = dispatcher.dispatch_phase(
            agents=[agent],
            context={"problem": self.sample_problem, "agent_results": {}},
        )
        # Dependência insatisfeita → agente deve ter status "skipped"
        self.assertIn("dependent", results,
                      "Agente skipped deve aparecer nos resultados")
        self.assertEqual(results["dependent"].status, "skipped",
                         "Agente com dependência insatisfeita deve ter status=skipped")
        self.assertIsNone(results["dependent"].result,
                          "Agente skipped não deve ter resultado")
    
    # =================================================================
    # HELPERS
    # =================================================================
    
    def _create_test_agents(self, sleep_times: list[float]) -> list:
        """Cria agentes dummy que dormem por tempos especificados."""
        agents = []
        for i, t in enumerate(sleep_times):
            agent = _DummyTestAgent(
                agent_id=f'test-agent-{i}',
                reasoning_type=f'R{i+1:02d}',
                category='I',
                sleep_time=t,
            )
            agents.append(agent)
        return agents


# =====================================================================
# TEST PARALLEL ORCHESTRATOR v12
# =====================================================================

class TestParallelOrchestrator(unittest.TestCase):
    """Testes de integração do ParallelOrchestrator v12."""
    
    def setUp(self):
        try:
            from orchestrator_v12 import ParallelOrchestrator
            self.Orchestrator = ParallelOrchestrator
            self.HAS_V12 = True
        except ImportError:
            self.HAS_V12 = False
    
    def test_orchestrator_creation(self):
        """C1-T8: ParallelOrchestrator deve ser criado com configurações default."""
        if not self.HAS_V12:
            self.skipTest("ParallelOrchestrator não implementado")
        orch = self.Orchestrator()
        self.assertIsNotNone(orch)
        self.assertEqual(orch.config.intra_phase_workers, 2)  # Standard mode default
    
    def test_orchestrator_solve_returns_report(self):
        """C1-T9: solve() deve retornar SolutionReport com PCI."""
        if not self.HAS_V12:
            self.skipTest("ParallelOrchestrator não implementado")
        orch = self.Orchestrator()
        report = orch.solve("Prove that sqrt(2) is irrational")
        self.assertIsNotNone(report)
        self.assertTrue(hasattr(report, 'pci'))
        self.assertGreaterEqual(report.pci, 0)
    
    def test_mode_configuration(self):
        """C1-T10: Modos Express/Standard/Magnum devem configurar paralelismo."""
        if not self.HAS_V12:
            self.skipTest("ParallelOrchestrator não implementado")
        orch = self.Orchestrator()
        
        express = orch.configure_mode("express")
        self.assertEqual(express.intra_phase_workers, 1)
        
        standard = orch.configure_mode("standard")
        self.assertEqual(standard.intra_phase_workers, 2)
        
        magnum = orch.configure_mode("magnum")
        self.assertEqual(magnum.intra_phase_workers, 4)


if __name__ == "__main__":
    unittest.main(verbosity=2)
