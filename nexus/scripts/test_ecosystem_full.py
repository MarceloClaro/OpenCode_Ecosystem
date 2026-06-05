import unittest
import sys
import json
import os
import time
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

class TestEcosystemConfig(unittest.TestCase):
    def test_root_discovery(self):
        from ecosystem_config import ECO_ROOT, EVOLVE_DIR, SKILLS_DIR, NEXUS_DIR
        self.assertTrue(ECO_ROOT.exists())
        self.assertTrue(EVOLVE_DIR.exists())
        self.assertTrue(SKILLS_DIR.exists())
        self.assertTrue(NEXUS_DIR.exists())

    def test_state_paths(self):
        from ecosystem_config import MEMORY_PATH, STATE_PATH, HEALTH_PATH, OUTCOMES_PATH
        self.assertIn('.evolve', str(MEMORY_PATH))
        self.assertIn('.evolve', str(STATE_PATH))

    def test_pdf_watch_dirs(self):
        from ecosystem_config import PDF_WATCH_DIRS
        self.assertEqual(len(PDF_WATCH_DIRS), 3)


class TestNexusIntegrationFull(unittest.TestCase):
    def test_facade_initialization(self):
        from nexus_integration_full import NexusIntegrationFacade
        facade = NexusIntegrationFacade()
        result = facade.initialize()
        self.assertTrue(result)

    def test_facade_status(self):
        from nexus_integration_full import NexusIntegrationFacade
        facade = NexusIntegrationFacade()
        facade.initialize()
        status = facade.get_status()
        self.assertEqual(status['total_integrated'], 10)
        self.assertEqual(len(status['orphan_modules']), 4)
        self.assertEqual(len(status['micro_modules']), 5)
        self.assertTrue(status['mcp_router'])

    def test_orphan_modules_connected(self):
        from nexus_integration_full import NexusIntegrationFacade
        facade = NexusIntegrationFacade()
        facade.initialize()
        for name in ['agent_metamorphosis', 'domain_discovery', 'knowledge_graph', 'granular_sync']:
            self.assertIsNotNone(facade.get_orphan(name), f'{name} not connected')

    def test_micro_modules_connected(self):
        from nexus_integration_full import NexusIntegrationFacade
        facade = NexusIntegrationFacade()
        facade.initialize()
        for name in ['feedback', 'validation', 'reasoning', 'sync', 'integration']:
            self.assertIsNotNone(facade.get_micro(name), f'{name} not connected')

    def test_mcp_router_connected(self):
        from nexus_integration_full import NexusIntegrationFacade
        facade = NexusIntegrationFacade()
        facade.initialize()
        self.assertIsNotNone(facade.get_mcp_router())


class TestEvolutionLoopWithDocling(unittest.TestCase):
    def test_evolution_cycle(self):
        from evolution_loop import EvolutionLoopRunner
        runner = EvolutionLoopRunner()
        cycle = runner.run_cycle()
        self.assertIsNotNone(cycle.cycle_id)
        self.assertGreater(cycle.duration_ms, 0)

    def test_feedback_loop_outcomes(self):
        from evolution_loop import EvolutionLoopRunner
        runner = EvolutionLoopRunner()
        runner.run_cycle()
        self.assertGreater(len(runner.fb.outcomes), 0)

    def test_learnings_extracted(self):
        from evolution_loop import EvolutionLoopRunner
        runner = EvolutionLoopRunner()
        runner.run_cycle()
        self.assertGreater(len(runner.fb.learnings), 0)


class TestDoclingAdapter(unittest.TestCase):
    def test_adapter_init(self):
        from docling_adapter import DoclingAdapter
        adapter = DoclingAdapter()
        self.assertIsNotNone(adapter.converter)

    def test_skill_generator_init(self):
        from docling_adapter import DoclingSkillGenerator
        gen = DoclingSkillGenerator()
        self.assertTrue(gen.skills_dir.exists())

    def test_supported_formats(self):
        from docling_adapter import DoclingAdapter
        formats = DoclingAdapter.SUPPORTED_FORMATS
        self.assertIn('pdf', formats)
        self.assertIn('docx', formats)
        self.assertIn('xlsx', formats)

    def test_index_summary(self):
        from docling_adapter import DoclingAdapter
        adapter = DoclingAdapter()
        summary = adapter.get_index_summary()
        self.assertIn('total_processed', summary)
        self.assertIn('total_errors', summary)


class TestContextOffload(unittest.TestCase):
    def test_session_creation(self):
        from context_offload import ContextOffloadManager
        mgr = ContextOffloadManager()
        sid = mgr.create_session(project_id='test')
        self.assertIsNotNone(sid)

    def test_entry_addition(self):
        from context_offload import ContextOffloadManager
        mgr = ContextOffloadManager()
        mgr.create_session()
        eid = mgr.add_entry(content='test content', priority=10)
        self.assertIsNotNone(eid)

    def test_fingerprint(self):
        from context_offload import ContextOffloadManager
        mgr = ContextOffloadManager()
        mgr.create_session()
        mgr.add_entry(content='test term frequency analysis', priority=10)
        fp = mgr.create_behavioral_fingerprint()
        self.assertIn('term_frequency', fp)


class TestSocialAlgorithms(unittest.TestCase):
    def test_council_pattern(self):
        from social_algorithms import SocialAlgorithms, SocialAlgorithmType
        self.assertIsNotNone(SocialAlgorithmType.COUNCIL_OF_JUDGES)

    def test_debate_pattern(self):
        from social_algorithms import SocialAlgorithms, SocialAlgorithmType
        self.assertIsNotNone(SocialAlgorithmType.DEBATE_WITH_JUDGE)


class TestManusEvolveBridge(unittest.TestCase):
    def test_bridge_init(self):
        from manus_evolve_bridge import ManusEvolveBridge
        bridge = ManusEvolveBridge()
        self.assertIsNotNone(bridge)

    def test_combined_state(self):
        from manus_evolve_bridge import ManusEvolveBridge
        bridge = ManusEvolveBridge()
        state = bridge.get_combined_state()
        self.assertIn('manus', state)
        self.assertIn('evolution', state)
        self.assertIn('bridge_status', state)


class TestSyncOrchestrator(unittest.TestCase):
    def test_orchestrator_init(self):
        from sync_orchestrator import SyncOrchestrator
        orch = SyncOrchestrator()
        self.assertIsNotNone(orch)

    def test_component_discovery(self):
        from sync_orchestrator import ComponentDiscovery
        from ecosystem_config import ECO_ROOT
        disc = ComponentDiscovery(ECO_ROOT)
        skills = disc.discover_skills()
        self.assertIsInstance(skills, list)


class TestEndToEnd(unittest.TestCase):
    def test_full_ecosystem_flow(self):
        from ecosystem_config import ECO_ROOT
        from nexus_integration_full import NexusIntegrationFacade
        from evolution_loop import EvolutionLoopRunner
        from context_offload import ContextOffloadManager
        from manus_evolve_bridge import ManusEvolveBridge
        from docling_adapter import DoclingAdapter

        # 1. Initialize integrations
        facade = NexusIntegrationFacade()
        self.assertTrue(facade.initialize())

        # 2. Run evolution cycle
        runner = EvolutionLoopRunner()
        cycle = runner.run_cycle()
        self.assertGreater(cycle.health_before, 0)

        # 3. Context offload
        mgr = ContextOffloadManager()
        sid = mgr.create_session(project_id='ecosystem-test')
        mgr.add_entry(content='Full ecosystem test passed', priority=10)

        # 4. Bridge status
        bridge = ManusEvolveBridge()
        state = bridge.get_combined_state()
        self.assertTrue(state['bridge_status'] == 'active')

        # 5. Integration count
        status = facade.get_status()
        self.assertEqual(status['total_integrated'], 10)


if __name__ == '__main__':
    unittest.main()


class TestEdgeCases(unittest.TestCase):
    def test_evolution_cycle_error_handling(self):
        from evolution_loop import EvolutionLoopRunner
        runner = EvolutionLoopRunner()
        cycle = runner.run_cycle()
        self.assertIsNotNone(cycle.cycle_id)
        self.assertIn(cycle.phase, ['detect', 'diagnose', 'heal', 'learn', 'evolve', 'integrate'])

    def test_context_offload_compression(self):
        from context_offload import ContextOffloadManager
        mgr = ContextOffloadManager(max_context_size=100)
        mgr.create_session()
        mgr.add_entry(content='A' * 200, content_type='text', priority=3)
        self.assertTrue(mgr.sessions)

    def test_resume_consistency_no_fingerprint(self):
        from context_offload import ContextOffloadManager
        mgr = ContextOffloadManager()
        sid = mgr.create_session()
        result = mgr.check_resume_consistency(sid, 'test text')
        self.assertEqual(result['status'], 'no_fingerprint')

    def test_mcp_router_capabilities(self):
        from mcp_router import MCPCapability
        caps = list(MCPCapability)
        self.assertGreater(len(caps), 0)

    def test_granular_sync_operation(self):
        from granular_sync import OperationStatus, SyncBarrierType
        self.assertEqual(OperationStatus.PENDING.value, 'pending')
        self.assertEqual(SyncBarrierType.OPERATION.value, 'operation')

    def test_agent_metamorphosis_roles(self):
        from agent_metamorphosis import AgentRole
        roles = list(AgentRole)
        self.assertGreater(len(roles), 0)

    def test_domain_characteristics(self):
        from domain_discovery_engine import DomainCharacteristic
        chars = list(DomainCharacteristic)
        self.assertGreater(len(chars), 0)

    def test_knowledge_graph_relations(self):
        from knowledge_graphs import RelationType
        rels = list(RelationType)
        self.assertGreater(len(rels), 0)

    def test_micro_feedback_types(self):
        from micro_feedback_loop import FeedbackType
        types = list(FeedbackType)
        self.assertGreater(len(types), 0)

    def test_micro_validation_constraints(self):
        from micro_validation import ConstraintType
        types = list(ConstraintType)
        self.assertGreater(len(types), 0)

    def test_eco_root_is_portable(self):
        from ecosystem_config import ECO_ROOT
        self.assertIsInstance(ECO_ROOT, Path)
        self.assertTrue(ECO_ROOT.exists())

    def test_docling_index_persistence(self):
        from docling_adapter import DoclingAdapter
        adapter = DoclingAdapter()
        summary = adapter.get_index_summary()
        self.assertIsInstance(summary, dict)
        self.assertIn('total_processed', summary)

    def test_manus_state_file(self):
        from ecosystem_config import MANUS_STATE_PATH
        self.assertIn('.evolve', str(MANUS_STATE_PATH))

    def test_pdf_watch_dirs_exist_or_configured(self):
        from ecosystem_config import PDF_WATCH_DIRS
        self.assertEqual(len(PDF_WATCH_DIRS), 3)

    def test_nexus_integration_idempotent(self):
        from nexus_integration_full import NexusIntegrationFacade
        f1 = NexusIntegrationFacade()
        f1.initialize()
        f2 = NexusIntegrationFacade()
        f2.initialize()
        self.assertEqual(f1.get_status()['total_integrated'], f2.get_status()['total_integrated'])


class TestSyncOrchestratorFunctional(unittest.TestCase):
    """Testes funcionais do SyncOrchestrator - descuberta, scoring, healing."""

    def test_full_sync_execution(self):
        from sync_orchestrator import SyncOrchestrator
        orch = SyncOrchestrator()
        state = orch.run_full_sync()
        self.assertIsInstance(state.health_score, (int, float))
        self.assertGreater(state.total_components, 0)
        self.assertGreater(state.active_components, 0)
        self.assertIsNotNone(state.timestamp)

    def test_dynamic_scoring(self):
        from sync_orchestrator import DynamicScoringEngine
        from pathlib import Path
        test_path = Path('.evolve/test-dynamic-scores.json')
        engine = DynamicScoringEngine(path=test_path)
        engine.record_usage('test-component', success=True, response_ms=50)
        engine.record_usage('test-component', success=True, response_ms=30)
        engine.record_usage('test-component', success=False, response_ms=200)
        score = engine.get_score('test-component')
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 100)
        under = engine.get_underperforming(threshold=50.0)
        self.assertIsInstance(under, list)
        if test_path.exists():
            test_path.unlink()

    def test_auto_healing_diagnosis(self):
        from sync_orchestrator import AutoHealingEngine, SyncComponent
        engine = AutoHealingEngine()
        healthy = engine.assess(96)
        self.assertEqual(healthy, 'healthy')
        alert = engine.assess(72)
        self.assertEqual(alert, 'alert')
        critical = engine.assess(50)
        self.assertEqual(critical, 'critical')
        actions = engine.diagnose([], [], 96)
        self.assertIsInstance(actions, list)

    def test_conflict_detection(self):
        from sync_orchestrator import ConflictDetector, SyncComponent
        detector = ConflictDetector()
        mcps = [
            SyncComponent(name='playwright', component_type='mcp', status='active'),
            SyncComponent(name='chrome-devtools', component_type='mcp', status='active'),
        ]
        conflicts = detector.detect(mcps)
        self.assertIsInstance(conflicts, list)

    def test_cross_validation_affinity(self):
        from sync_orchestrator import CrossValidationEngine
        engine = CrossValidationEngine()
        aff = engine.compute_affinity('eslint', 'code-reviewer', 'mcp', 'agent')
        self.assertGreater(aff, 0)
        aff_zero = engine.compute_affinity('unknown-x', 'unknown-y', 'mcp', 'agent')
        self.assertEqual(aff_zero, 0.0)


class TestEvolutionLoopFunctional(unittest.TestCase):
    """Testes funcionais do EvolutionLoop - feedback, learnings, skill candidates."""

    def test_feedback_loop_record_outcome(self):
        from evolution_loop import FeedbackLoopEngine
        fb = FeedbackLoopEngine()
        initial = len(fb.outcomes)
        fb.record_outcome('test-comp', 'test-action', True, 85.0, 100.0, 'test context')
        self.assertEqual(len(fb.outcomes), initial + 1)
        self.assertTrue(fb.outcomes[-1].success)
        self.assertEqual(fb.outcomes[-1].component, 'test-comp')

    def test_feedback_loop_extract_learnings(self):
        from evolution_loop import FeedbackLoopEngine
        fb = FeedbackLoopEngine()
        for i in range(5):
            fb.record_outcome('comp-a', f'action-{i}', True, 80.0 + i, 50.0)
        learnings = fb.extract_learnings(min_confidence=0.5)
        self.assertIsInstance(learnings, list)

    def test_healing_recommendations(self):
        from evolution_loop import FeedbackLoopEngine
        fb = FeedbackLoopEngine()
        fb.record_outcome('weak-comp', 'fail-action', False, 20.0, 300.0, error='timeout')
        fb.record_outcome('weak-comp', 'fail-action', False, 15.0, 350.0, error='timeout')
        fb.record_outcome('weak-comp', 'fail-action', False, 10.0, 400.0, error='timeout')
        fb.extract_learnings()
        recs = fb.get_healing_recommendations()
        self.assertIsInstance(recs, list)

    def test_skill_generation_candidates(self):
        from evolution_loop import FeedbackLoopEngine
        fb = FeedbackLoopEngine()
        for i in range(4):
            fb.record_outcome('strong-comp', f'action-{i}', True, 95.0, 20.0)
        fb.extract_learnings()
        candidates = fb.get_skill_generation_candidates()
        self.assertIsInstance(candidates, list)

    def test_diagnosis_engine(self):
        from evolution_loop import FeedbackLoopEngine, SocialDiagnosisEngine
        fb = FeedbackLoopEngine()
        diag = SocialDiagnosisEngine(fb)
        result = diag.run_diagnosis('Test diagnosis')
        self.assertIn('analyses', result)
        self.assertIn('timestamp', result)

    def test_evolution_runner_status(self):
        from evolution_loop import EvolutionLoopRunner
        runner = EvolutionLoopRunner()
        status = runner.get_status()
        self.assertIn('feedback_loop', status)
        self.assertIn('learnings', status)
        self.assertIn('outcomes', status)


class TestMCPRouterFunctional(unittest.TestCase):
    """Testes funcionais do MCP Router - registro, roteamento, relatorios."""

    def test_register_and_route(self):
        from mcp_router import MCPRouter, MCPServer, MCPCapability, TaskDescriptor
        router = MCPRouter()
        router.register_mcp(MCPServer(
            id='mcp-fs', name='Filesystem MCP',
            capabilities=[MCPCapability.FILESYSTEM],
            endpoint='http://localhost:8001', max_concurrent_tasks=5
        ))
        task = TaskDescriptor(
            id='task-001', agent_id='A1', phase='Embedding',
            required_capabilities=[MCPCapability.FILESYSTEM], priority=3
        )
        decision = router.route_task(task)
        self.assertEqual(decision.mcp_server_id, 'mcp-fs')
        self.assertGreater(decision.confidence, 0)
        self.assertIsInstance(decision.rationale, str)

    def test_routing_with_load(self):
        from mcp_router import MCPRouter, MCPServer, MCPCapability, TaskDescriptor
        router = MCPRouter()
        router.register_mcp(MCPServer(
            id='mcp-1', name='Server 1',
            capabilities=[MCPCapability.FILESYSTEM],
            endpoint='http://localhost:8001', max_concurrent_tasks=5, health_score=0.9
        ))
        router.register_mcp(MCPServer(
            id='mcp-2', name='Server 2',
            capabilities=[MCPCapability.FILESYSTEM],
            endpoint='http://localhost:8002', max_concurrent_tasks=5, health_score=0.5
        ))
        task = TaskDescriptor(
            id='task-002', agent_id='A1', phase='Embedding',
            required_capabilities=[MCPCapability.FILESYSTEM], priority=3
        )
        decision = router.route_task(task)
        self.assertEqual(decision.mcp_server_id, 'mcp-1')

    def test_no_available_server_raises(self):
        from mcp_router import MCPRouter, MCPCapability, TaskDescriptor
        router = MCPRouter()
        task = TaskDescriptor(
            id='task-003', agent_id='A1', phase='Embedding',
            required_capabilities=[MCPCapability.DATABASE], priority=3
        )
        with self.assertRaises(RuntimeError):
            router.route_task(task)

    def test_routing_report(self):
        from mcp_router import MCPRouter, MCPServer, MCPCapability, TaskDescriptor
        router = MCPRouter()
        router.register_mcp(MCPServer(
            id='mcp-r', name='Report MCP',
            capabilities=[MCPCapability.MEMORY],
            endpoint='http://localhost:8003', max_concurrent_tasks=10
        ))
        for i in range(3):
            task = TaskDescriptor(
                id=f'task-r-{i}', agent_id='A4', phase='FeedForward',
                required_capabilities=[MCPCapability.MEMORY], priority=2
            )
            router.route_task(task)
        report = router.get_routing_report()
        self.assertEqual(report['total_routes'], 3)
        self.assertGreater(report['avg_confidence'], 0)

    def test_server_health_update(self):
        from mcp_router import MCPRouter, MCPServer, MCPCapability
        router = MCPRouter()
        router.register_mcp(MCPServer(
            id='mcp-h', name='Health MCP',
            capabilities=[MCPCapability.CODE_EXECUTION],
            endpoint='http://localhost:8004', max_concurrent_tasks=5
        ))
        router.update_server_health('mcp-h', 0.3)
        self.assertAlmostEqual(router.mcp_servers['mcp-h'].health_score, 0.3)
        router.update_server_load('mcp-h', 2)
        self.assertEqual(router.mcp_servers['mcp-h'].current_load, 2)


class TestKnowledgeGraphFunctional(unittest.TestCase):
    """Testes funcionais do KnowledgeGraph - entidades, relacoes, caminhos."""

    def test_add_entity_and_relation(self):
        from knowledge_graphs import KnowledgeGraph, Entity, EntityType, Relation, RelationType
        kg = KnowledgeGraph('test-kg')
        kg.add_entity(Entity('e1', 'Machine Learning', EntityType.CONCEPT, 'ML concept'))
        kg.add_entity(Entity('e2', 'Deep Learning', EntityType.CONCEPT, 'DL concept'))
        kg.add_relation(Relation('e2', 'e1', RelationType.SPECIALIZES))
        self.assertEqual(len(kg.entities), 2)
        self.assertEqual(len(kg.relations), 1)

    def test_search_entities(self):
        from knowledge_graphs import KnowledgeGraph, Entity, EntityType
        kg = KnowledgeGraph('test-search')
        kg.add_entity(Entity('n1', 'Neural Network', EntityType.ALGORITHM, 'NN'))
        kg.add_entity(Entity('n2', 'Decision Tree', EntityType.ALGORITHM, 'DT'))
        results = kg.search_entities('Neural')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, 'Neural Network')

    def test_find_shortest_path(self):
        from knowledge_graphs import KnowledgeGraph, Entity, EntityType, Relation, RelationType
        kg = KnowledgeGraph('test-path')
        kg.add_entity(Entity('a', 'A', EntityType.CONCEPT, 'Node A'))
        kg.add_entity(Entity('b', 'B', EntityType.CONCEPT, 'Node B'))
        kg.add_entity(Entity('c', 'C', EntityType.CONCEPT, 'Node C'))
        kg.add_relation(Relation('a', 'b', RelationType.RELATED_TO))
        kg.add_relation(Relation('b', 'c', RelationType.RELATED_TO))
        path = kg.find_shortest_path('a', 'c')
        self.assertIsNotNone(path)
        self.assertEqual(path, ['a', 'b', 'c'])

    def test_semantic_similarity(self):
        from knowledge_graphs import KnowledgeGraph, Entity, EntityType, Relation, RelationType
        kg = KnowledgeGraph('test-sim')
        kg.add_entity(Entity('x', 'X', EntityType.CONCEPT, 'X'))
        kg.add_entity(Entity('y', 'Y', EntityType.CONCEPT, 'Y'))
        kg.add_relation(Relation('x', 'y', RelationType.SIMILAR_TO))
        sim = kg.semantic_similarity('x', 'y')
        self.assertGreater(sim, 0)

    def test_find_communities(self):
        from knowledge_graphs import KnowledgeGraph, Entity, EntityType, Relation, RelationType
        kg = KnowledgeGraph('test-comm')
        for i in range(5):
            kg.add_entity(Entity(f'c{i}', f'Concept {i}', EntityType.CONCEPT, f'Desc {i}'))
        kg.add_relation(Relation('c0', 'c1', RelationType.RELATED_TO))
        kg.add_relation(Relation('c2', 'c3', RelationType.RELATED_TO))
        communities = kg.find_communities()
        self.assertIsInstance(communities, dict)

    def test_cs_knowledge_graph_init(self):
        from knowledge_graphs import ComputerScienceKG
        cs = ComputerScienceKG()
        self.assertGreater(len(cs.entities), 0)
        self.assertGreater(len(cs.relations), 0)


class TestGranularSyncFunctional(unittest.TestCase):
    """Testes funcionais do GranularSync - operacoes, barreiras, checkpoints."""

    def test_operation_lifecycle(self):
        from granular_sync import GranularSyncManager, OperationStatus
        mgr = GranularSyncManager()
        op = mgr.create_operation('op-1', 'Test', 'agent-1', 'test_type')
        self.assertEqual(op.status, OperationStatus.PENDING)
        mgr.start_operation('op-1')
        self.assertEqual(op.status, OperationStatus.IN_PROGRESS)
        mgr.checkpoint_operation('op-1', 'hash-abc')
        self.assertEqual(op.status, OperationStatus.CHECKPOINT)
        mgr.commit_operation('op-1', {'result': 'ok'})
        self.assertEqual(op.status, OperationStatus.COMMITTED)

    def test_barrier_readiness(self):
        from granular_sync import GranularSyncManager, SyncBarrierType
        mgr = GranularSyncManager()
        mgr.create_operation('op-b1', 'Phase1', 'agent-1', 'type1')
        mgr.create_operation('op-b2', 'Phase1', 'agent-1', 'type2')
        mgr.create_barrier('barrier-1', SyncBarrierType.PHASE, 'Phase1', ['op-b1', 'op-b2'])
        mgr.start_operation('op-b1')
        mgr.commit_operation('op-b1')
        mgr.start_operation('op-b2')
        mgr.commit_operation('op-b2')
        readiness = mgr.check_barrier_readiness('barrier-1')
        self.assertTrue(readiness['is_ready'])

    def test_operation_fail_and_rollback(self):
        from granular_sync import GranularSyncManager
        mgr = GranularSyncManager()
        mgr.create_operation('op-fail', 'Phase', 'agent-1', 'type')
        mgr.start_operation('op-fail')
        mgr.checkpoint_operation('op-fail', 'hash-1')
        mgr.rollback_operation('op-fail')
        self.assertEqual(mgr.operations['op-fail'].status.value, 'rolled_back')

    def test_dependency_checking(self):
        from granular_sync import GranularSyncManager, OperationDependency, OperationStatus
        mgr = GranularSyncManager()
        mgr.create_operation('dep-1', 'Phase', 'agent-1', 'type1')
        mgr.create_operation(
            'dep-2', 'Phase', 'agent-1', 'type2',
            dependencies=[OperationDependency('dep-2', 'dep-1', 'sequential')]
        )
        can_proceed = mgr.operations['dep-2'].can_proceed(mgr.operations)
        self.assertFalse(can_proceed)
        mgr.start_operation('dep-1')
        mgr.commit_operation('dep-1')
        can_proceed = mgr.operations['dep-2'].can_proceed(mgr.operations)
        self.assertTrue(can_proceed)


class TestPaginationAndRotation(unittest.TestCase):
    """Testes funcionais de paginacao e rotacao de dados."""

    def _make_fresh_fb(self):
        from evolution_loop import FeedbackLoopEngine
        fb = FeedbackLoopEngine()
        fb.outcomes = []
        fb.learnings = []
        return fb

    def test_outcomes_pagination(self):
        fb = self._make_fresh_fb()
        for i in range(25):
            fb.record_outcome('comp-'+str(i), 'action-'+str(i), True, 80.0, 30.0)
        page1 = fb.get_outcomes_paginated(page=1, page_size=10)
        self.assertEqual(page1['page'], 1)
        self.assertEqual(len(page1['outcomes']), 10)
        self.assertEqual(page1['total'], 25)
        self.assertEqual(page1['total_pages'], 3)
        self.assertTrue(page1['has_next'])
        self.assertFalse(page1['has_prev'])
        page3 = fb.get_outcomes_paginated(page=3, page_size=10)
        self.assertEqual(len(page3['outcomes']), 5)
        self.assertFalse(page3['has_next'])
        self.assertTrue(page3['has_prev'])

    def test_learnings_pagination(self):
        fb = self._make_fresh_fb()
        for i in range(15):
            fb.record_outcome('comp-a', 'action-'+str(i), True, 90.0, 20.0)
        fb.extract_learnings()
        page1 = fb.get_learnings_paginated(page=1, page_size=5)
        self.assertEqual(page1['page'], 1)
        self.assertTrue(page1['has_next'] or page1['total_pages'] == 1)

    def test_outcomes_rotation(self):
        fb = self._make_fresh_fb()
        for i in range(50):
            fb.record_outcome('comp-'+str(i), 'action-'+str(i), True, 80.0, 30.0)
        self.assertEqual(len(fb.outcomes), 50)
        removed = fb.rotate_outcomes(max_keep=20)
        self.assertEqual(removed, 30)
        self.assertEqual(len(fb.outcomes), 20)

    def test_learnings_rotation(self):
        fb = self._make_fresh_fb()
        for i in range(30):
            fb.record_outcome('comp-a', 'action-'+str(i), True, 90.0, 20.0)
        fb.extract_learnings()
        initial = len(fb.learnings)
        removed = fb.rotate_learnings(max_keep=5)
        self.assertEqual(removed, max(0, initial - 5))
        self.assertLessEqual(len(fb.learnings), 5)

    def test_state_file_rotation(self):
        from sync_orchestrator import SyncOrchestrator
        from ecosystem_config import STATE_PATH
        orch = SyncOrchestrator()
        state = orch.run_full_sync()
        orch.save_state(state)
        state_gz = STATE_PATH.with_suffix('.json.gz')
        self.assertTrue(state_gz.exists(), f'Gzip state file not found at {state_gz}')
        size_kb = state_gz.stat().st_size / 1024
        self.assertLess(size_kb, 50000, 'State file too large: %.0fKB' % size_kb)
