/**
 * ============================================================
 * OPENCODE ECOSYSTEM — TDD TEST SUITE
 * ============================================================
 * Tests: MultiReasoningEngine + OrchestrationEngine + ScientificProductionAgent
 * Pattern: TDD (Test-Driven Development) — Red → Green → Refactor
 * Agent: marceloclaro | No external dependencies
 *
 * Run: node .opencode/tests/run_tests.js
 * ============================================================
 */

'use strict';

// ─── MINIMAL TEST RUNNER ─────────────────────────────────────────────────────

class TestRunner {
  constructor(suiteName) {
    this.suiteName = suiteName;
    this.tests = [];
    this.passed = 0;
    this.failed = 0;
    this.errors = [];
  }

  test(name, fn) {
    this.tests.push({ name, fn });
  }

  async run() {
    console.log(`\n${'═'.repeat(60)}`);
    console.log(`📋 TEST SUITE: ${this.suiteName}`);
    console.log('═'.repeat(60));

    for (const { name, fn } of this.tests) {
      try {
        await fn();
        this.passed++;
        console.log(`  ✅ ${name}`);
      } catch (err) {
        this.failed++;
        this.errors.push({ test: name, error: err.message });
        console.log(`  ❌ ${name}`);
        console.log(`     Error: ${err.message}`);
      }
    }

    console.log(`\n  Results: ${this.passed}/${this.tests.length} passed`);
    if (this.failed > 0) {
      console.log(`  Failed tests:`);
      this.errors.forEach(e => console.log(`    - ${e.test}: ${e.error}`));
    }

    return { passed: this.passed, failed: this.failed, total: this.tests.length };
  }
}

// ─── ASSERTION HELPERS ──────────────────────────────────────────────────────

function assert(condition, message) {
  if (!condition) throw new Error(message || 'Assertion failed');
}

function assertEqual(actual, expected, message) {
  if (actual !== expected) {
    throw new Error(message || `Expected ${JSON.stringify(expected)}, got ${JSON.stringify(actual)}`);
  }
}

function assertApprox(actual, expected, tolerance = 0.01, message) {
  if (Math.abs(actual - expected) > tolerance) {
    throw new Error(message || `Expected ~${expected} ± ${tolerance}, got ${actual}`);
  }
}

function assertThrows(fn, errorPattern, message) {
  let threw = false;
  try { fn(); } catch (e) {
    threw = true;
    if (errorPattern && !e.message.includes(errorPattern)) {
      throw new Error(`Expected error matching "${errorPattern}", got: "${e.message}"`);
    }
  }
  if (!threw) throw new Error(message || 'Expected function to throw but it did not');
}

function assertType(value, type, message) {
  if (typeof value !== type) {
    throw new Error(message || `Expected type ${type}, got ${typeof value}`);
  }
}

function assertInRange(value, min, max, message) {
  if (value < min || value > max) {
    throw new Error(message || `Expected value in [${min}, ${max}], got ${value}`);
  }
}

function assertHasKeys(obj, keys, message) {
  const missing = keys.filter(k => !(k in obj));
  if (missing.length > 0) {
    throw new Error(message || `Object missing required keys: ${missing.join(', ')}`);
  }
}

// ─── LOAD ENGINES ───────────────────────────────────────────────────────────

const path = require('path');
const BASE = path.join(__dirname, '..');

const { MultiReasoningEngine, REASONING_MODES } = require(path.join(BASE, 'engines', 'multi_reasoning_engine'));
const { OrchestrationEngine, AgentPool, PriorityTaskQueue, CircuitBreaker, SKILL_TAXONOMY } = require(path.join(BASE, 'engines', 'orchestration_engine'));
const { ScientificProductionAgent, QualityGate, CitationManager, QUALITY_GATES } = require(path.join(BASE, 'engines', 'scientific_production_agent'));

// ═══════════════════════════════════════════════════════════════
// SUITE 1: MULTI-REASONING ENGINE
// ═══════════════════════════════════════════════════════════════

const reasoningSuite = new TestRunner('MultiReasoningEngine');

reasoningSuite.test('MRE-01: Engine instantiates with default config', () => {
  const engine = new MultiReasoningEngine();
  assert(engine !== null, 'Engine should be instantiated');
  assertHasKeys(engine.config, ['max_reasoning_chain', 'enable_meta', 'global_confidence_threshold']);
  assertEqual(engine.config.version, '2.0.0', 'Should have version 2.0.0');
});

reasoningSuite.test('MRE-02: Deductive reasoning returns valid result', () => {
  const engine = new MultiReasoningEngine();
  const result = engine.reason('deductive', {
    premises: ['SROI > 1.0', 'investment = 50000'],
    rules: [
      { name: 'positive_impact', condition: p => p.includes('SROI'), conclude: p => 'Positive social impact', confidence: 0.9 }
    ]
  });

  assertHasKeys(result, ['mode', 'confidence', 'conclusions', 'trace', 'reasoning_path']);
  assertEqual(result.mode, 'deductive', 'Mode should be deductive');
  assertInRange(result.confidence, 0, 1, 'Confidence must be 0-1');
  assert(Array.isArray(result.conclusions), 'Conclusions must be an array');
  assert(result.conclusions.length > 0, 'Should have at least one conclusion');
});

reasoningSuite.test('MRE-03: Inductive reasoning detects patterns correctly', () => {
  const engine = new MultiReasoningEngine();
  const observations = [
    { pattern: 'open_source', value: 1 },
    { pattern: 'open_source', value: 2 },
    { pattern: 'open_source', value: 3 },
    { pattern: 'closed_source', value: 1 }
  ];

  const result = engine.reason('inductive', { observations, min_support: 0.5 });
  assertEqual(result.mode, 'inductive');
  assert(result.generalizations.length > 0, 'Should find at least one pattern');
  // 'open_source' appears 3/4 = 75% > 50% threshold
  const openSourceGen = result.generalizations.find(g => JSON.stringify(g.pattern).includes('open_source'));
  assert(openSourceGen, 'Should detect open_source pattern');
  assert(openSourceGen.support >= 0.5, 'Support should be >= 0.5');
});

reasoningSuite.test('MRE-04: Abductive reasoning selects best explanation', () => {
  const engine = new MultiReasoningEngine();
  const result = engine.reason('abductive', {
    observation: 'SROI ratio is 1.39x, below sector average',
    hypotheses: [
      { name: 'insufficient_scale', explanatory_power: 0.9, prior: 0.7, simplicity: 0.8 },
      { name: 'measurement_error', explanatory_power: 0.3, prior: 0.2, simplicity: 0.9 },
      { name: 'domain_mismatch', explanatory_power: 0.5, prior: 0.4, simplicity: 0.6 }
    ]
  });

  assertEqual(result.mode, 'abductive');
  assert(result.best_explanation, 'Should select best explanation');
  assertEqual(result.best_explanation.name, 'insufficient_scale', 'Should select highest-scored hypothesis');
  assertInRange(result.confidence, 0, 1, 'Confidence must be 0-1');
});

reasoningSuite.test('MRE-05: Analogical reasoning computes Jaccard similarity correctly', () => {
  const engine = new MultiReasoningEngine();
  const result = engine.reason('analogical', {
    target: { name: 'OpenCode', features: ['open_source', 'autonomous_agents', 'skills'] },
    cases: [
      { name: 'Linux', features: ['open_source', 'community', 'tools'], solution: 'community governance', similarity: 0 },
      { name: 'LangChain', features: ['open_source', 'autonomous_agents', 'chains'], solution: 'modular agent chains', similarity: 0 }
    ]
  });

  assertEqual(result.mode, 'analogical');
  assert(result.best_analog, 'Should find best analog');
  // LangChain shares 2/4 features with OpenCode = 0.5; Linux shares 1/5 = 0.2
  assert(result.best_analog.name === 'LangChain', 'LangChain should be most similar');
});

reasoningSuite.test('MRE-06: Causal reasoning traces effect chains', () => {
  const engine = new MultiReasoningEngine();
  const result = engine.reason('causal', {
    causal_graph: [
      { cause: 'more_agents', effect: 'more_skills', strength: 0.9, mechanism: 'capability_expansion', confounders: [] },
      { cause: 'more_skills', effect: 'higher_sroi', strength: 0.8, mechanism: 'value_generation', confounders: ['market_conditions'] }
    ]
  });

  assertEqual(result.mode, 'causal');
  assert(result.effects.length === 2, 'Should have 2 causal effects');
  assertInRange(result.confidence, 0, 1, 'Confidence must be 0-1');
  // Confounder penalty: strength 0.8 - 0.05 = 0.75 for second edge
  const higherSroi = result.effects.find(e => e.effect === 'higher_sroi');
  assert(higherSroi, 'Should have higher_sroi effect');
  assertApprox(higherSroi.strength, 0.75, 0.01, 'Should apply confounder penalty');
});

reasoningSuite.test('MRE-07: Meta reasoning selects optimal mode from query', () => {
  const engine = new MultiReasoningEngine();
  const result = engine.reason('meta', {
    query: 'Find best explanation for the low SROI',
    available_data: { sroi: 1.39 }
  });

  assertEqual(result.mode, 'meta');
  assert(result.selected_mode, 'Should select a reasoning mode');
  // Query contains 'explanation' → should select abductive
  assertEqual(result.selected_mode, 'abductive', 'Query about explanation should select abductive');
});

reasoningSuite.test('MRE-08: Chain reasoning executes sequential modes', () => {
  const engine = new MultiReasoningEngine();
  const chain = [
    { mode: 'inductive', context: { observations: [{ pattern: 'growth' }, { pattern: 'growth' }], min_support: 0.5 } },
    { mode: 'deductive', context: { premises: ['growth detected'], rules: [{ name: 'scale', condition: () => true, conclude: () => 'scale_up', confidence: 0.85 }] } }
  ];

  const result = engine.chainReason(chain);
  assert(result.type === 'chain', 'Result should be type chain');
  assertEqual(result.steps.length, 2, 'Should have 2 steps');
  assertInRange(result.overall_confidence, 0, 1, 'Overall confidence must be 0-1');
  assert(result.reasoning_chain.includes('→'), 'Should show reasoning chain');
});

reasoningSuite.test('MRE-09: Ensemble reasoning combines multiple modes', () => {
  const engine = new MultiReasoningEngine();
  const result = engine.ensembleReason(
    ['deductive', 'inductive'],
    { premises: ['P1'], rules: [], observations: [{ pattern: 'A' }, { pattern: 'A' }], min_support: 0.5 },
    'weighted_avg'
  );

  assert(result.ensemble_results, 'Should have ensemble results');
  assertEqual(result.ensemble_results.length, 2, 'Should have results from 2 modes');
  assertInRange(result.confidence, 0, 1, 'Confidence must be 0-1');
});

reasoningSuite.test('MRE-10: SDD Precondition — invalid mode throws error', () => {
  const engine = new MultiReasoningEngine();
  assertThrows(
    () => engine.reason('invalid_mode', {}),
    'Unknown reasoning mode',
    'Should throw for invalid mode'
  );
});

reasoningSuite.test('MRE-11: SDD Precondition — null context throws error', () => {
  const engine = new MultiReasoningEngine();
  assertThrows(
    () => engine.reason('deductive', null),
    'Precondition violated',
    'Should throw for null context'
  );
});

reasoningSuite.test('MRE-12: Chain exceeding max length throws error', () => {
  const engine = new MultiReasoningEngine({ max_reasoning_chain: 3 });
  const longChain = [1, 2, 3, 4].map(i => ({ mode: 'deductive', context: { premises: [`P${i}`], rules: [] } }));
  assertThrows(
    () => engine.chainReason(longChain),
    'exceeds max',
    'Should throw for chain exceeding max length'
  );
});

reasoningSuite.test('MRE-13: Metrics track usage correctly', () => {
  const engine = new MultiReasoningEngine();
  engine.reason('deductive', { premises: ['P1'], rules: [] });
  engine.reason('inductive', { observations: [{ pattern: 'A' }], min_support: 0.3 });
  engine.reason('deductive', { premises: ['P2'], rules: [] });

  const metrics = engine.getMetrics();
  assertEqual(metrics.total_invocations, 3, 'Should track 3 invocations');
  assertEqual(metrics.mode_usage.deductive, 2, 'Deductive used 2 times');
  assertEqual(metrics.mode_usage.inductive, 1, 'Inductive used 1 time');
});

reasoningSuite.test('MRE-14: Reset clears state completely', () => {
  const engine = new MultiReasoningEngine();
  engine.reason('deductive', { premises: ['P1'], rules: [] });
  engine.reset();

  const metrics = engine.getMetrics();
  assertEqual(metrics.total_invocations, 0, 'After reset, invocations should be 0');
  assertEqual(engine.history.length, 0, 'After reset, history should be empty');
});

reasoningSuite.test('MRE-15: All 6 reasoning modes are registered', () => {
  const modes = Object.keys(REASONING_MODES);
  assert(modes.length === 6, `Expected 6 modes, got ${modes.length}`);
  ['deductive', 'inductive', 'abductive', 'analogical', 'causal', 'meta'].forEach(mode => {
    assert(modes.includes(mode), `Mode "${mode}" should be registered`);
  });
});

// ═══════════════════════════════════════════════════════════════
// SUITE 2: ORCHESTRATION ENGINE
// ═══════════════════════════════════════════════════════════════

const orchestrationSuite = new TestRunner('OrchestrationEngine');

orchestrationSuite.test('ORCH-01: Engine instantiates with 128 agents', () => {
  const engine = new OrchestrationEngine();
  const stats = engine.pool.getStats();
  assertEqual(stats.total, 128, 'Should have 128 agents');
  assertEqual(engine.config.version, '2.0.0');
});

orchestrationSuite.test('ORCH-02: AgentPool initializes all agents as idle', () => {
  const pool = new AgentPool({ total_agents: 128, skill_taxonomy: SKILL_TAXONOMY });
  const stats = pool.getStats();
  assertEqual(stats.idle, 128, 'All agents should start idle');
  assertEqual(stats.busy, 0, 'No agents should start busy');
});

orchestrationSuite.test('ORCH-03: AgentPool finds agent with required skill', () => {
  const pool = new AgentPool({ total_agents: 128, skill_taxonomy: SKILL_TAXONOMY });
  const agent = pool.findAgent('hypothesis_formation');
  assert(agent !== null, 'Should find an agent');
  assert(agent.skills.includes('hypothesis_formation'), 'Agent should have the required skill');
});

orchestrationSuite.test('ORCH-04: AgentPool marks agent as busy on assignment', () => {
  const pool = new AgentPool({ total_agents: 128, skill_taxonomy: SKILL_TAXONOMY });
  const agent = pool.findAgent('data_analysis');
  pool.assignTask(agent.id, 'test-task-1');
  assertEqual(agent.status, 'busy', 'Agent should be marked as busy');
});

orchestrationSuite.test('ORCH-05: AgentPool releases agent after task', () => {
  const pool = new AgentPool({ total_agents: 128, skill_taxonomy: SKILL_TAXONOMY });
  const agent = pool.findAgent('data_analysis');
  pool.assignTask(agent.id, 'test-task-2');
  pool.releaseAgent(agent.id, true);
  assertEqual(agent.status, 'idle', 'Agent should be released back to idle');
});

orchestrationSuite.test('ORCH-06: PriorityTaskQueue respects priority order', () => {
  const queue = new PriorityTaskQueue();
  queue.enqueue({ skill: 'data_analysis', priority: 'low' });
  queue.enqueue({ skill: 'hypothesis_formation', priority: 'critical' });
  queue.enqueue({ skill: 'literature_review', priority: 'normal' });

  const first = queue.dequeue();
  assert(first.priority === 'critical', 'Critical task should dequeue first');
  const second = queue.dequeue();
  assert(second.priority === 'normal', 'Normal task should dequeue second');
  const third = queue.dequeue();
  assert(third.priority === 'low', 'Low priority task should dequeue last');
});

orchestrationSuite.test('ORCH-07: CircuitBreaker opens after threshold failures', () => {
  const cb = new CircuitBreaker({ threshold: 3 });
  assert(cb.canCall('agent-1'), 'Should allow calls initially');
  cb.recordFailure('agent-1');
  cb.recordFailure('agent-1');
  cb.recordFailure('agent-1');
  assert(!cb.canCall('agent-1'), 'Circuit breaker should be OPEN after 3 failures');
});

orchestrationSuite.test('ORCH-08: CircuitBreaker closes after success', () => {
  const cb = new CircuitBreaker({ threshold: 2 });
  cb.recordFailure('agent-2');
  cb.recordFailure('agent-2');
  // Force half-open
  cb.lastFailure['agent-2'] = Date.now() - 60000;
  cb.state['agent-2'] = 'half-open';
  assert(cb.canCall('agent-2'), 'Should allow test call in half-open');
  cb.recordSuccess('agent-2');
  assertEqual(cb.state['agent-2'], 'closed', 'Should close after success');
});

orchestrationSuite.test('ORCH-09: SDD Contract — invalid task throws', () => {
  const engine = new OrchestrationEngine();
  assertThrows(
    () => engine._assertTaskContract({ skill: 'invalid_skill_xyz' }),
    'Unknown skill',
    'Should throw for unknown skill'
  );
});

orchestrationSuite.test('ORCH-10: SDD Contract — missing skill throws', () => {
  const engine = new OrchestrationEngine();
  assertThrows(
    () => engine._assertTaskContract({}),
    'must have a "skill"',
    'Should throw for missing skill'
  );
});

orchestrationSuite.test('ORCH-11: Task dispatch returns success structure', async () => {
  const engine = new OrchestrationEngine();
  const result = await engine.dispatch({
    skill: 'data_analysis',
    priority: 'normal',
    payload: { data: 'test' }
  });

  assertHasKeys(result, ['status', 'taskId', 'latency_ms']);
  assertEqual(result.status, 'success', 'Should succeed');
  assert(result.latency_ms >= 0, 'Should have latency measurement');
  assert(typeof result.taskId === 'string', 'Task ID should be a string');
});

orchestrationSuite.test('ORCH-12: Reasoning mode auto-selected by skill', () => {
  const engine = new OrchestrationEngine();
  const mode = engine._selectReasoningMode({ skill: 'hypothesis_formation' });
  assertEqual(mode, 'abductive', 'hypothesis_formation should use abductive reasoning');

  const mode2 = engine._selectReasoningMode({ skill: 'data_analysis' });
  assertEqual(mode2, 'causal', 'data_analysis should use causal reasoning');
});

orchestrationSuite.test('ORCH-13: Pipeline runs all stages sequentially', async () => {
  const engine = new OrchestrationEngine();
  const pipeline = [
    { name: 'stage1', skill: 'hypothesis_formation', priority: 'high', payload: {} },
    { name: 'stage2', skill: 'data_analysis', priority: 'normal', payload: {} }
  ];

  const result = await engine.runPipeline(pipeline);
  assertHasKeys(result, ['pipeline_id', 'total_stages', 'successful_stages', 'stages', 'duration_ms']);
  assertEqual(result.total_stages, 2, 'Should have 2 stages');
  assert(result.duration_ms >= 0, 'Should have duration');
});

orchestrationSuite.test('ORCH-14: Engine metrics track completed tasks', async () => {
  const engine = new OrchestrationEngine();
  await engine.dispatch({ skill: 'scientific_writing', priority: 'normal', payload: {} });
  await engine.dispatch({ skill: 'peer_review', priority: 'normal', payload: {} });

  assertEqual(engine.metrics.tasks_dispatched, 2, 'Should track 2 dispatched tasks');
  assert(engine.metrics.tasks_completed >= 1, 'Should track completed tasks');
});

orchestrationSuite.test('ORCH-15: Diagnostics returns complete health report', () => {
  const engine = new OrchestrationEngine();
  const diag = engine.getDiagnostics();

  assertHasKeys(diag, ['version', 'timestamp', 'metrics', 'agent_pool', 'task_queue', 'circuit_breaker', 'reasoning_engine']);
  assertHasKeys(diag.agent_pool, ['total', 'idle', 'busy', 'utilization']);
  assertEqual(diag.agent_pool.total, 128);
});

orchestrationSuite.test('ORCH-16: isHealthy returns true for fresh engine', () => {
  const engine = new OrchestrationEngine();
  assert(engine.isHealthy() === true, 'Fresh engine should be healthy');
});

orchestrationSuite.test('ORCH-17: Reset clears all engine state', async () => {
  const engine = new OrchestrationEngine();
  await engine.dispatch({ skill: 'data_analysis', priority: 'normal', payload: {} });
  engine.reset();

  assertEqual(engine.metrics.tasks_dispatched, 0, 'After reset, metrics should be 0');
  assertEqual(engine.eventLog.length, 0, 'After reset, event log should be empty');
});

// ═══════════════════════════════════════════════════════════════
// SUITE 3: SCIENTIFIC PRODUCTION AGENT
// ═══════════════════════════════════════════════════════════════

const scientificSuite = new TestRunner('ScientificProductionAgent');

scientificSuite.test('SCI-01: Agent instantiates with correct defaults', () => {
  const agent = new ScientificProductionAgent({ agent_id: 'marceloclaro' });
  assertEqual(agent.agent_id, 'marceloclaro');
  assert(agent.citationManager instanceof CitationManager, 'Should have CitationManager');
  assert(Object.keys(QUALITY_GATES).length >= 5, 'Should have at least 5 quality gates');
});

scientificSuite.test('SCI-02: CitationManager seeds base citations on init', () => {
  const agent = new ScientificProductionAgent();
  assert(agent.citationManager.citations.size >= 5, 'Should have at least 5 seed citations');
  const validation = agent.citationManager.validate();
  assert(validation.valid === true, 'All seed citations should be valid');
});

scientificSuite.test('SCI-03: CitationManager formats ABNT correctly', () => {
  const cm = new CitationManager();
  cm.addCitation({ id: 'test1', author: 'SILVA, J.', title: 'Teste ABNT', year: 2024, journal: 'Rev. Bras.', volume: '1', number: '2', pages: '10-20' });
  const formatted = cm.getFormatted('test1', 'ABNT');
  assert(formatted.includes('SILVA, J.'), 'ABNT must include author');
  assert(formatted.includes('2024'), 'ABNT must include year');
  assert(formatted.includes('Teste ABNT'), 'ABNT must include title');
});

scientificSuite.test('SCI-04: Hypothesis formation passes quality gate', () => {
  const agent = new ScientificProductionAgent({ strict_gates: false });
  const result = agent.formHypothesis({ topic: 'OpenCode Ecosystem', domain: 'technology' });

  assertHasKeys(result, ['artifact', 'quality']);
  assert(result.artifact.research_question.length > 20, 'Should have research question');
  assert(result.artifact.hypothesis.length > 10, 'Should have hypothesis');
  assert(result.artifact.is_falsifiable === true, 'Hypothesis must be falsifiable');
  assertInRange(result.quality.score, 0, 1, 'Quality score must be 0-1');
});

scientificSuite.test('SCI-05: Literature review generates sufficient references', () => {
  const agent = new ScientificProductionAgent({ strict_gates: false });
  agent.formHypothesis({ topic: 'OpenCode', domain: 'technology' });
  const result = agent.conductLiteratureReview(agent.pipeline_state.hypothesis);

  assert(result.artifact.references.length >= 5, 'Should have at least 5 references');
  assert(result.artifact.gap_analysis.length > 20, 'Should have gap analysis');
  assert(result.artifact.keywords.length >= 3, 'Should have at least 3 keywords');
  assert(result.quality.passed, `Literature review should pass quality gate: ${result.quality.summary}`);
});

scientificSuite.test('SCI-06: Methodology design passes quality gate', () => {
  const agent = new ScientificProductionAgent({ strict_gates: false });
  const result = agent.designMethodology({});

  assert(result.artifact.research_design.length > 5, 'Should have research design');
  assert(Array.isArray(result.artifact.data_collection), 'Data collection must be array');
  assert(Array.isArray(result.artifact.analysis_method), 'Analysis method must be array');
  assert(result.quality.passed, 'Methodology should pass quality gate');
});

scientificSuite.test('SCI-07: Data analysis integrates SROI data correctly', () => {
  const agent = new ScientificProductionAgent({ strict_gates: false });
  const result = agent.analyzeData({
    sroi: { sroi_ratio: 1.39, net_social_value: 69265, investment: 50000,
             rating: { level: 'POSITIVO' } },
    ecosystem: { agents: 128, skills: 155, mcps: 46, health_score: 96 }
  });

  const qd = result.artifact.quantitative_data;
  assertEqual(qd.sroi_ratio, 1.39, 'SROI ratio should be 1.39');
  assertEqual(qd.users_reached, 19200, 'Users reached = 128 * 150');
  assertEqual(qd.skills_available, 155, 'Skills should be 155');
  assert(result.artifact.research_question_addressed === true, 'Should address research question');
  assert(result.quality.passed, 'Results should pass quality gate');
});

scientificSuite.test('SCI-08: Quality gate evaluates scoring correctly', () => {
  const gate = QUALITY_GATES.hypothesis;
  const goodArtifact = {
    research_question: 'What is the SROI of OpenCode ecosystem over 24 months?',
    hypothesis: 'If skills increase, SROI will increase proportionally',
    variables: { dependent: ['SROI'], independent: ['skills'] },
    is_falsifiable: true,
    domain: 'technology'
  };

  const result = gate.evaluate(goodArtifact);
  assert(result.passed, 'Good artifact should pass hypothesis gate');
  assertInRange(result.score, 0.7, 1.0, 'Score should be >= 0.7 to pass');
});

scientificSuite.test('SCI-09: Quality gate rejects insufficient artifact', () => {
  const gate = QUALITY_GATES.hypothesis;
  const badArtifact = {
    research_question: 'OK?', // too short
    hypothesis: null, // missing
    domain: 'technology'
  };

  const result = gate.evaluate(badArtifact);
  assert(!result.passed, 'Insufficient artifact should fail quality gate');
  assert(result.score < 0.7, 'Score should be below passing threshold');
});

scientificSuite.test('SCI-10: Peer review runs 3 reviewers and aggregates', () => {
  const agent = new ScientificProductionAgent({ strict_gates: false });
  // Run earlier stages first to populate state
  agent.formHypothesis({ topic: 'OpenCode', domain: 'technology' });
  agent.conductLiteratureReview(agent.pipeline_state.hypothesis);
  agent.designMethodology(agent.pipeline_state.literature);
  agent.analyzeData({});
  agent.writeScientificPaper({ topic: 'OpenCode', agent: 'marceloclaro' });

  const result = agent.runPeerReview(agent.pipeline_state.paper);

  assert(result.artifact.reviewers.length === 3, 'Should have 3 reviewers');
  assertInRange(result.artifact.originality_score, 0, 1, 'Originality must be 0-1');
  assertInRange(result.artifact.methodology_soundness, 0, 1, 'Soundness must be 0-1');
  assert(['ACCEPT', 'MINOR_REVISION', 'MAJOR_REVISION'].includes(result.artifact.decision), 'Should have valid decision');
});

scientificSuite.test('SCI-11: Full pipeline completes all 6 stages', async () => {
  const agent = new ScientificProductionAgent({ strict_gates: false });
  const result = await agent.runFullPipeline({
    topic: 'OpenCode Ecosystem',
    domain: 'technology',
    agent: 'marceloclaro',
    impact_data: {
      sroi: { sroi_ratio: 1.39, net_social_value: 69265, investment: 50000, rating: { level: 'POSITIVO' } },
      ecosystem: { agents: 128, skills: 155, mcps: 46, health_score: 96 }
    }
  });

  assertHasKeys(result, ['pipeline_id', 'successful_stages', 'total_stages', 'quality_reports', 'metrics']);
  assertEqual(result.total_stages, 6, 'Should have 6 stages');
  assert(result.successful_stages >= 4, `At least 4 stages should pass, got ${result.successful_stages}`);
  assert(result.metrics.papers_produced === 1, 'Should produce 1 paper');
});

scientificSuite.test('SCI-12: Reset clears pipeline state completely', async () => {
  const agent = new ScientificProductionAgent({ strict_gates: false });
  agent.formHypothesis({ topic: 'Test', domain: 'technology' });
  agent.reset();

  assertEqual(Object.keys(agent.pipeline_state).length, 0, 'Pipeline state should be empty after reset');
  assertEqual(agent.quality_reports.length, 0, 'Quality reports should be empty after reset');
  assertEqual(agent.metrics.papers_produced, 0, 'Papers produced should be 0 after reset');
});

// ═══════════════════════════════════════════════════════════════
// INTEGRATION TESTS
// ═══════════════════════════════════════════════════════════════

const integrationSuite = new TestRunner('Integration: SROI + Reasoning + Orchestration');

integrationSuite.test('INT-01: MultiReasoning integrates into OrchestrationEngine dispatch', async () => {
  const engine = new OrchestrationEngine({ enable_multi_reasoning: true });
  const result = await engine.dispatch({
    skill: 'impact_measurement',
    priority: 'high',
    reasoning_mode: 'causal',
    payload: {
      causal_graph: [
        { cause: 'open_access', effect: 'digital_inclusion', strength: 0.8, mechanism: 'accessibility', confounders: [] }
      ]
    }
  });

  assertEqual(result.status, 'success', 'SROI+reasoning dispatch should succeed');
  assert(result.result.reasoning_mode, 'Result should include reasoning mode');
});

integrationSuite.test('INT-02: Scientific pipeline uses causal reasoning for data analysis', async () => {
  const reasoning = new MultiReasoningEngine({ enable_meta: true });
  const result = reasoning.reason('causal', {
    causal_graph: [
      { cause: 'agents_128', effect: 'users_19200', strength: 0.85, mechanism: 'agent_user_ratio_150x', confounders: [] },
      { cause: 'skills_155', effect: 'knowledge_transfer', strength: 0.78, mechanism: 'skill_distribution', confounders: ['access_barriers'] }
    ]
  });

  assertEqual(result.mode, 'causal');
  assertEqual(result.effects.length, 2);
  assertInRange(result.confidence, 0.5, 1.0);
});

integrationSuite.test('INT-03: Full ecosystem pipeline — orchestration + scientific production', async () => {
  const orchestrator = new OrchestrationEngine();
  const scientist = new ScientificProductionAgent({ strict_gates: false });

  // Run orchestrator scientific pipeline
  const orchResult = await orchestrator.runScientificPipeline({
    topic: 'OpenCode Ecosystem',
    domain: 'technology'
  });

  // Run scientific agent pipeline
  const sciResult = await scientist.runFullPipeline({
    topic: 'OpenCode Ecosystem',
    domain: 'technology',
    agent: 'marceloclaro',
    impact_data: { sroi: { sroi_ratio: 1.39, net_social_value: 69265, investment: 50000, rating: { level: 'POSITIVO' } }, ecosystem: { agents: 128, skills: 155, mcps: 46, health_score: 96 } }
  });

  assert(orchResult.pipeline_id, 'Orchestration pipeline should have ID');
  assert(sciResult.pipeline_id, 'Scientific pipeline should have ID');
  assert(sciResult.successful_stages >= 4, 'Scientific pipeline should pass most stages');

  // Verify both systems tracked work
  assert(orchestrator.metrics.tasks_dispatched >= 8, 'Orchestrator should dispatch at least 8 tasks');
  assert(scientist.metrics.papers_produced === 1, 'Scientist should produce 1 paper');
});

integrationSuite.test('INT-04: SROI data flows correctly through reasoning chain', () => {
  const engine = new MultiReasoningEngine();
  const chain = [
    {
      mode: 'causal',
      context: {
        causal_graph: [
          { cause: 'investment_50000', effect: 'social_value_69265', strength: 0.85, mechanism: 'sroi_1.39x', confounders: [] }
        ]
      }
    },
    {
      mode: 'deductive',
      context: {
        premises: ['SROI = 1.39x', 'investment > 0'],
        rules: [
          { name: 'positive_sroi', condition: p => p.includes('SROI'), conclude: () => 'Impact is POSITIVO', confidence: 0.90 }
        ]
      }
    }
  ];

  const result = engine.chainReason(chain);
  assertEqual(result.steps.length, 2);
  assert(result.steps[1].conclusions.length > 0, 'Deductive conclusions should be non-empty');
  assertInRange(result.overall_confidence, 0.5, 1.0, 'Overall confidence should be reasonable');
});

// ═══════════════════════════════════════════════════════════════
// TEST RUNNER ENTRY POINT
// ═══════════════════════════════════════════════════════════════

async function runAllTests() {
  const suites = [reasoningSuite, orchestrationSuite, scientificSuite, integrationSuite];
  const allResults = [];
  let totalPassed = 0;
  let totalFailed = 0;

  console.log('\n' + '╔' + '═'.repeat(58) + '╗');
  console.log('║  OPENCODE TDD TEST SUITE — marceloclaro              ║');
  console.log('║  TDD (Red→Green→Refactor) + SDD Contracts            ║');
  console.log('╚' + '═'.repeat(58) + '╝');

  for (const suite of suites) {
    const result = await suite.run();
    allResults.push(result);
    totalPassed += result.passed;
    totalFailed += result.failed;
  }

  console.log('\n' + '═'.repeat(60));
  console.log('🏁 TOTAL RESULTS:');
  console.log(`   ✅ Passed: ${totalPassed}`);
  console.log(`   ❌ Failed: ${totalFailed}`);
  console.log(`   📊 Total:  ${totalPassed + totalFailed}`);
  console.log(`   🎯 Rate:   ${((totalPassed / (totalPassed + totalFailed)) * 100).toFixed(1)}%`);

  if (totalFailed === 0) {
    console.log('\n  🎉 ALL TESTS PASSED — Green phase achieved!');
  } else {
    console.log('\n  ⚠️  Some tests failed — Red phase detected, refactor needed');
  }
  console.log('═'.repeat(60));

  return { passed: totalPassed, failed: totalFailed, total: totalPassed + totalFailed };
}

// Auto-run if called directly
if (require.main === module) {
  runAllTests().catch(console.error);
}

module.exports = { runAllTests, TestRunner, assert, assertEqual, assertThrows };
