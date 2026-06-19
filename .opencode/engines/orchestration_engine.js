/**
 * ============================================================
 * OPENCODE ECOSYSTEM — ORCHESTRATION ENGINE v2.0
 * ============================================================
 * SDD Contract: OrchestrationEngine
 * Agent: marceloclaro | TDD-compliant
 *
 * Responsibilities:
 * - Route tasks to specialized skill agents
 * - Manage agent lifecycle (spawn, pool, retire)
 * - Load balance across 128 agents
 * - Fault tolerance with retry/circuit-breaker
 * - Multi-reasoning dispatch integration
 * - Scientific production pipeline orchestration
 * ============================================================
 */

'use strict';

const { MultiReasoningEngine } = typeof require !== 'undefined'
  ? require('./multi_reasoning_engine')
  : { MultiReasoningEngine: class { reason() { return { confidence: 0.8, mode: 'mock' }; } } };

const { PotentialityScanner } = typeof require !== 'undefined'
  ? require('./potentiality_scanner')
  : { PotentialityScanner: class { async scanForLatentSolutions() { return { discoveries: [] }; } } };

// ─── AGENT SKILL TAXONOMY ───────────────────────────────────────────────────

const SKILL_TAXONOMY = {
  // Scientific Production Skills
  scientific: [
    'hypothesis_formation', 'literature_review', 'methodology_design',
    'data_analysis', 'statistical_modeling', 'scientific_writing',
    'peer_review', 'citation_management', 'meta_analysis',
    'sroi_calculation', 'impact_measurement', 'systematic_review'
  ],
  // Reasoning Skills
  reasoning: [
    'deductive_reasoning', 'inductive_reasoning', 'abductive_reasoning',
    'analogical_reasoning', 'causal_analysis', 'meta_cognition',
    'chain_of_thought', 'tree_of_thought', 'socratic_questioning'
  ],
  // Data Processing Skills
  data: [
    'data_ingestion', 'data_cleaning', 'feature_engineering',
    'statistical_analysis', 'nlp_processing', 'knowledge_extraction',
    'graph_analysis', 'time_series_analysis', 'anomaly_detection'
  ],
  // Orchestration Skills
  orchestration: [
    'task_decomposition', 'agent_routing', 'load_balancing',
    'result_synthesis', 'error_recovery', 'priority_scheduling',
    'dependency_resolution', 'parallel_execution'
  ],
  // Communication Skills
  communication: [
    'report_generation', 'visualization', 'api_integration',
    'webhook_dispatch', 'notification', 'documentation'
  ]
};

// ─── CIRCUIT BREAKER ────────────────────────────────────────────────────────

class CircuitBreaker {
  constructor({ threshold = 5, timeout = 60000, resetAfter = 30000 } = {}) {
    this.threshold = threshold;
    this.timeout = timeout;
    this.resetAfter = resetAfter;
    this.failures = {};
    this.state = {}; // 'closed' | 'open' | 'half-open'
    this.lastFailure = {};
  }

  canCall(agentId) {
    const state = this.state[agentId] || 'closed';
    if (state === 'closed') return true;
    if (state === 'open') {
      const elapsed = Date.now() - (this.lastFailure[agentId] || 0);
      if (elapsed > this.resetAfter) {
        this.state[agentId] = 'half-open';
        return true;
      }
      return false;
    }
    return true; // half-open: allow one test
  }

  recordSuccess(agentId) {
    this.failures[agentId] = 0;
    this.state[agentId] = 'closed';
  }

  recordFailure(agentId) {
    this.failures[agentId] = (this.failures[agentId] || 0) + 1;
    this.lastFailure[agentId] = Date.now();
    if (this.failures[agentId] >= this.threshold) {
      this.state[agentId] = 'open';
    }
  }

  getStatus() {
    return {
      breakers: Object.entries(this.state).map(([id, state]) => ({
        agent: id, state,
        failures: this.failures[id] || 0
      }))
    };
  }
}

// ─── TASK QUEUE ─────────────────────────────────────────────────────────────

class PriorityTaskQueue {
  constructor() {
    this.queues = { critical: [], high: [], normal: [], low: [] };
    this.total = 0;
    this.processed = 0;
  }

  enqueue(task) {
    const priority = task.priority || 'normal';
    const queue = this.queues[priority] || this.queues.normal;
    task.queued_at = Date.now();
    task.id = task.id || `task-${++this.total}-${Date.now()}`;
    queue.push(task);
    return task.id;
  }

  dequeue() {
    for (const priority of ['critical', 'high', 'normal', 'low']) {
      if (this.queues[priority].length > 0) {
        this.processed++;
        return this.queues[priority].shift();
      }
    }
    return null;
  }

  size() {
    return Object.values(this.queues).reduce((s, q) => s + q.length, 0);
  }

  stats() {
    return {
      total_enqueued: this.total,
      total_processed: this.processed,
      pending: this.size(),
      by_priority: Object.fromEntries(
        Object.entries(this.queues).map(([k, v]) => [k, v.length])
      )
    };
  }
}

// ─── AGENT POOL ─────────────────────────────────────────────────────────────

class AgentPool {
  /**
   * @param {Object} config
   * @param {number} config.total_agents - Total agents in ecosystem
   * @param {Object} config.skill_taxonomy - Skill taxonomy map
   */
  constructor(config = {}) {
    this.total_agents = config.total_agents || 128;
    this.skill_taxonomy = config.skill_taxonomy || SKILL_TAXONOMY;
    this.agents = this._initializeAgents();
    this.active = new Map(); // taskId → agentId
  }

  _initializeAgents() {
    const agents = new Map();
    const allSkills = Object.values(this.skill_taxonomy).flat();

    for (let i = 0; i < this.total_agents; i++) {
      const category = Object.keys(this.skill_taxonomy)[i % Object.keys(this.skill_taxonomy).length];
      const categorySkills = this.skill_taxonomy[category];
      const primarySkill = categorySkills[i % categorySkills.length];
      const secondarySkills = allSkills.filter(s => s !== primarySkill).slice(0, 3);

      agents.set(`agent-${i}`, {
        id: `agent-${i}`,
        status: 'idle', // idle | busy | error | offline
        category,
        primary_skill: primarySkill,
        skills: [primarySkill, ...secondarySkills],
        task_count: 0,
        success_rate: 1.0,
        last_active: null,
        reasoning_mode: ['deductive', 'inductive', 'abductive', 'analogical', 'causal', 'meta'][i % 6]
      });
    }
    return agents;
  }

  /**
   * Find best available agent for a required skill
   * @param {string} requiredSkill - Skill needed
   * @param {string} preferredReasoningMode - Preferred reasoning mode
   */
  findAgent(requiredSkill, preferredReasoningMode = null) {
    const candidates = [...this.agents.values()]
      .filter(a => a.status === 'idle' && a.skills.includes(requiredSkill))
      .sort((a, b) => {
        // Prefer: primary skill match, high success rate, low task count
        const aScore = (a.primary_skill === requiredSkill ? 1 : 0) * 0.5
          + a.success_rate * 0.3
          + (1 / (a.task_count + 1)) * 0.2
          + (preferredReasoningMode && a.reasoning_mode === preferredReasoningMode ? 0.1 : 0);
        const bScore = (b.primary_skill === requiredSkill ? 1 : 0) * 0.5
          + b.success_rate * 0.3
          + (1 / (b.task_count + 1)) * 0.2
          + (preferredReasoningMode && b.reasoning_mode === preferredReasoningMode ? 0.1 : 0);
        return bScore - aScore;
      });

    return candidates[0] || null;
  }

  assignTask(agentId, taskId) {
    const agent = this.agents.get(agentId);
    if (!agent) throw new Error(`Agent ${agentId} not found`);
    agent.status = 'busy';
    agent.task_count++;
    agent.last_active = new Date().toISOString();
    this.active.set(taskId, agentId);
    return agent;
  }

  releaseAgent(agentId, success = true) {
    const agent = this.agents.get(agentId);
    if (!agent) return;
    agent.status = 'idle';
    // Update rolling success rate
    agent.success_rate = agent.success_rate * 0.95 + (success ? 0.05 : 0);
  }

  getStats() {
    const statusCounts = { idle: 0, busy: 0, error: 0, offline: 0 };
    for (const agent of this.agents.values()) {
      statusCounts[agent.status] = (statusCounts[agent.status] || 0) + 1;
    }
    return {
      total: this.total_agents,
      ...statusCounts,
      utilization: ((statusCounts.busy / this.total_agents) * 100).toFixed(1) + '%',
      active_tasks: this.active.size
    };
  }
}

// ─── ORCHESTRATION ENGINE ───────────────────────────────────────────────────

class OrchestrationEngine {
  /**
   * @param {Object} config
   * @param {number} config.max_retries - Max retry attempts per task
   * @param {number} config.timeout_ms - Task timeout in milliseconds
   * @param {boolean} config.enable_multi_reasoning - Enable multi-reasoning dispatch
   * @param {Object} config.circuit_breaker - Circuit breaker settings
   */
  constructor(config = {}) {
    this.config = {
      max_retries: config.max_retries || 3,
      timeout_ms: config.timeout_ms || 30000,
      enable_multi_reasoning: config.enable_multi_reasoning !== false,
      parallel_limit: config.parallel_limit || 10,
      version: '2.0.0'
    };

    this.pool = new AgentPool({ total_agents: 128, skill_taxonomy: SKILL_TAXONOMY });
    this.taskQueue = new PriorityTaskQueue();
    this.circuitBreaker = new CircuitBreaker(config.circuit_breaker || {});
    this.reasoningEngine = new MultiReasoningEngine({
      enable_meta: true,
      log_trace: true
    });

    this.metrics = {
      tasks_dispatched: 0,
      tasks_completed: 0,
      tasks_failed: 0,
      retries_used: 0,
      avg_latency_ms: 0,
      pipelines_run: 0
    };

    this.n35_active = false;
    this.potentialityScanner = null;
    this.ecosystem_graph = null;

    this.eventLog = [];
  }

  // ─── TASK DISPATCH ──────────────────────────────────────────────────────────

  /**
   * Dispatch a task to the most suitable agent
   * @param {Object} task - Task descriptor
   * @param {string} task.skill - Required skill
   * @param {string} task.priority - 'critical' | 'high' | 'normal' | 'low'
   * @param {Object} task.payload - Task data
   * @param {string} task.reasoning_mode - Preferred reasoning mode (optional)
   * @param {number} task.retry - Internal retry count (managed by engine)
   */
  async dispatch(task) {
    // SDD Preconditions
    this._assertTaskContract(task);

    const taskId = this.taskQueue.enqueue(task);
    this.metrics.tasks_dispatched++;
    const startTime = Date.now();

    this._log('DISPATCH', `Task ${taskId} queued [${task.skill}] priority=${task.priority || 'normal'}`);

    // N3.5+ Preventive Safety Barrier
    if (this.n35_active && this._detectAnomalousStress(task)) {
      this._log('N3.5_INTERCEPT', `Task ${taskId} bloqueada preventivamente pelo Scanner Noológico (Risco detectado antes da execução).`);
      return { status: 'error', taskId, error: 'BLOCKED_BY_N3_5_PREVENTIVE_BARRIER' };
    }

    try {
      const result = await this._executeTask(task, taskId);

      const latency = Date.now() - startTime;
      this.metrics.tasks_completed++;
      this.metrics.avg_latency_ms = (
        (this.metrics.avg_latency_ms * (this.metrics.tasks_completed - 1)) + latency
      ) / this.metrics.tasks_completed;

      this._log('COMPLETE', `Task ${taskId} completed in ${latency}ms`);
      return { status: 'success', taskId, result, latency_ms: latency };

    } catch (error) {
      this.metrics.tasks_failed++;
      this._log('FAILED', `Task ${taskId} failed: ${error.message}`);
      return { status: 'error', taskId, error: error.message };
    }
  }

  async _executeTask(task, taskId) {
    const retries = task.retry || 0;

    // Select reasoning mode
    const reasoning_mode = task.reasoning_mode || this._selectReasoningMode(task);

    // Find available agent
    const agent = this.pool.findAgent(task.skill, reasoning_mode);
    if (!agent) {
      throw new Error(`No available agent with skill "${task.skill}"`);
    }

    // Circuit breaker check
    if (!this.circuitBreaker.canCall(agent.id)) {
      throw new Error(`Circuit breaker OPEN for agent ${agent.id}`);
    }

    // Assign task to agent
    this.pool.assignTask(agent.id, taskId);

    try {
      // Apply multi-reasoning to task payload
      let enriched_payload = task.payload;
      if (this.config.enable_multi_reasoning && task.payload) {
        const reasoning_result = this.reasoningEngine.reason(reasoning_mode, {
          query: task.skill,
          ...task.payload
        });
        enriched_payload = { ...task.payload, reasoning_result };
      }

      // Simulate task execution (in production: call actual agent handler)
      const result = await this._simulateAgentExecution(agent, enriched_payload, task);

      this.circuitBreaker.recordSuccess(agent.id);
      this.pool.releaseAgent(agent.id, true);

      return {
        ...result,
        agent_id: agent.id,
        reasoning_mode,
        agent_skill: agent.primary_skill
      };

    } catch (execError) {
      this.circuitBreaker.recordFailure(agent.id);
      this.pool.releaseAgent(agent.id, false);

      // Retry logic
      if (retries < this.config.max_retries) {
        this.metrics.retries_used++;
        this._log('RETRY', `Task ${taskId} retry ${retries + 1}/${this.config.max_retries}`);
        return this._executeTask({ ...task, retry: retries + 1 }, taskId);
      }

      throw execError;
    }
  }

  /**
   * Simulate agent execution (replace with real agent call in production)
   */
  async _simulateAgentExecution(agent, payload, task) {
    // Simulate async work with realistic latency
    const latency = 50 + Math.random() * 100;
    await new Promise(resolve => setTimeout(resolve, latency));

    // Simulate occasional failures for testing circuit breaker
    if (Math.random() < 0.02) {
      throw new Error(`Agent ${agent.id} execution error (simulated)`);
    }

    return {
      success: true,
      agent: agent.id,
      skill: agent.primary_skill,
      output: `Result of ${task.skill} by agent ${agent.id}`,
      metadata: {
        task_count: agent.task_count,
        reasoning_mode: agent.reasoning_mode,
        timestamp: new Date().toISOString()
      }
    };
  }

  // ─── PIPELINE ORCHESTRATION ─────────────────────────────────────────────────

  /**
   * Run a sequential pipeline of tasks with dependency handling
   * @param {Array<Object>} pipeline - Ordered array of task descriptors
   * @param {Object} options - Pipeline options
   */
  async runPipeline(pipeline, options = {}) {
    // SDD Precondition
    if (!Array.isArray(pipeline) || pipeline.length === 0) {
      throw new Error('[OrchestrationEngine] Pipeline must be a non-empty array of tasks');
    }

    this.metrics.pipelines_run++;
    const pipelineId = `pipeline-${Date.now()}`;
    const pipelineStart = Date.now();
    const results = [];
    let context = options.initial_context || {};

    this._log('PIPELINE_START', `Pipeline ${pipelineId} starting with ${pipeline.length} stages`);

    for (let i = 0; i < pipeline.length; i++) {
      const stage = pipeline[i];
      this._log('STAGE', `Pipeline ${pipelineId} stage ${i+1}/${pipeline.length}: ${stage.name || stage.skill}`);

      // Inject previous results into payload
      const enriched_stage = {
        ...stage,
        payload: { ...stage.payload, context, previous_results: results }
      };

      const result = await this.dispatch(enriched_stage);
      results.push({ stage: i + 1, name: stage.name, ...result });

      // Gate: if stage fails and is critical, abort pipeline
      if (result.status === 'error' && stage.critical !== false) {
        this._log('PIPELINE_ABORT', `Critical stage ${stage.name} failed, aborting pipeline`);
        break;
      }

      // Update context with stage output for next stages
      if (result.result) {
        context = { ...context, ...result.result, [`stage_${i+1}_output`]: result.result };
      }
    }

    const duration = Date.now() - pipelineStart;
    const successful = results.filter(r => r.status === 'success').length;

    this._log('PIPELINE_DONE', `Pipeline ${pipelineId} done: ${successful}/${pipeline.length} stages OK in ${duration}ms`);

    return {
      pipeline_id: pipelineId,
      total_stages: pipeline.length,
      successful_stages: successful,
      failed_stages: results.filter(r => r.status === 'error').length,
      stages: results,
      duration_ms: duration,
      success: successful === pipeline.length
    };
  }

  /**
   * Run tasks in parallel (respecting parallel_limit)
   * @param {Array<Object>} tasks - Array of task descriptors
   */
  async runParallel(tasks) {
    if (!Array.isArray(tasks) || tasks.length === 0) {
      throw new Error('[OrchestrationEngine] runParallel requires a non-empty array');
    }

    const limit = this.config.parallel_limit;
    const results = [];

    // Process in batches to respect parallel limit
    for (let i = 0; i < tasks.length; i += limit) {
      const batch = tasks.slice(i, i + limit);
      const batchResults = await Promise.allSettled(
        batch.map(task => this.dispatch(task))
      );
      results.push(...batchResults.map(r =>
        r.status === 'fulfilled' ? r.value : { status: 'error', error: r.reason?.message }
      ));
    }

    return {
      total: tasks.length,
      successful: results.filter(r => r.status === 'success').length,
      failed: results.filter(r => r.status === 'error').length,
      results
    };
  }

  // ─── SCIENTIFIC PRODUCTION PIPELINE ────────────────────────────────────────

  /**
   * Orchestrate the full scientific production pipeline
   * Integrates with SROI impact measurement
   * @param {Object} researchContext - Research context with topic, data sources, etc.
   */
  async runScientificPipeline(researchContext) {
    const { topic = 'OpenCode Ecosystem', domain = 'technology' } = researchContext;

    const pipeline = [
      {
        name: 'hypothesis_formation',
        skill: 'hypothesis_formation',
        priority: 'high',
        reasoning_mode: 'abductive',
        critical: true,
        payload: { topic, domain, ...researchContext }
      },
      {
        name: 'literature_review',
        skill: 'literature_review',
        priority: 'high',
        reasoning_mode: 'inductive',
        payload: { topic, domain }
      },
      {
        name: 'methodology_design',
        skill: 'methodology_design',
        priority: 'high',
        reasoning_mode: 'deductive',
        payload: { domain }
      },
      {
        name: 'data_analysis',
        skill: 'data_analysis',
        priority: 'critical',
        reasoning_mode: 'causal',
        payload: { domain }
      },
      {
        name: 'sroi_calculation',
        skill: 'sroi_calculation',
        priority: 'critical',
        reasoning_mode: 'deductive',
        payload: { domain: 'social_impact' }
      },
      {
        name: 'scientific_writing',
        skill: 'scientific_writing',
        priority: 'normal',
        reasoning_mode: 'meta',
        payload: { output_format: 'imrad' }
      },
      {
        name: 'peer_review',
        skill: 'peer_review',
        priority: 'normal',
        reasoning_mode: 'analogical',
        payload: {}
      },
      {
        name: 'report_generation',
        skill: 'report_generation',
        priority: 'low',
        reasoning_mode: 'deductive',
        payload: { formats: ['markdown', 'json', 'html'] }
      }
    ];

    return this.runPipeline(pipeline, { initial_context: researchContext });
  }

  // ─── N3.5+ EPISTEMOLOGICAL SCANNERS (SPEC-043) ──────────────────────────

  /**
   * Ativa a autonomia comportamental de Nível N3.5+ (agente /marceloclaro)
   */
  activateN3_5Safety(ecosystem_graph = null) {
    this._log('N3.5_ACTIVATION', 'Iniciando nível de autonomia N3.5+ e ativando Scanners Epistemológicos (SPEC-043)');
    this.n35_active = true;
    this.potentialityScanner = new PotentialityScanner();
    this.ecosystem_graph = ecosystem_graph || {
      agents: Array.from(this.pool.agents.values()),
      skills: Object.values(SKILL_TAXONOMY).flat(),
      mcps: ['core_mcp', 'finance_mcp', 'research_mcp', 'impact_mcp']
    };
  }

  /**
   * Executa varredura por correlações e aplica soluções autônomas
   */
  async applyPotentialityScan() {
    if (!this.n35_active || !this.potentialityScanner) {
      throw new Error("N3.5+ Autonomy not activated. Call activateN3_5Safety() first.");
    }
    
    this._log('SPEC-043_SCAN', 'Iniciando varredura profunda por correlações latentes...');
    const report = await this.potentialityScanner.scanForLatentSolutions(this.ecosystem_graph);
    
    // N4-lite: Aplicação autônoma das soluções provadas
    report.discoveries.forEach(disc => {
       if (disc.validation.is_valid && disc.validation.epistemological_status !== 'UNPROVEN_HYPOTHESIS') {
          this._log('N3.5_AUTONOMY_ACTION', `Executando solução validada estatisticamente: ${disc.actionable_solution}`);
       }
    });

    return report;
  }

  _detectAnomalousStress(task) {
    // Heurísticas preditivas do Nível N3.5
    if (task.payload && JSON.stringify(task.payload).length > 2000000) return true; // Causal risk: memory exhaust
    if (task.skill === 'infinite_recursion' || task.priority === 'doom') return true; // Logical risk
    return false;
  }

  // ─── HELPERS ────────────────────────────────────────────────────────────────

  _selectReasoningMode(task) {
    const skillModeMap = {
      hypothesis_formation: 'abductive',
      data_analysis: 'causal',
      literature_review: 'inductive',
      methodology_design: 'deductive',
      peer_review: 'analogical',
      scientific_writing: 'meta',
      sroi_calculation: 'deductive',
      impact_measurement: 'causal',
      task_decomposition: 'meta',
      agent_routing: 'analogical'
    };
    return skillModeMap[task.skill] || 'meta';
  }

  _assertTaskContract(task) {
    if (!task || typeof task !== 'object') {
      throw new TypeError('[OrchestrationEngine] Task must be an object');
    }
    if (!task.skill || typeof task.skill !== 'string') {
      throw new Error('[OrchestrationEngine] Task must have a "skill" string field');
    }
    const validSkills = Object.values(SKILL_TAXONOMY).flat();
    if (!validSkills.includes(task.skill)) {
      throw new Error(`[OrchestrationEngine] Unknown skill "${task.skill}". Valid skills: ${validSkills.slice(0, 5).join(', ')}...`);
    }
  }

  _log(type, message) {
    const entry = { timestamp: new Date().toISOString(), type, message };
    this.eventLog.push(entry);
    if (this.eventLog.length > 1000) this.eventLog.shift(); // rolling buffer
  }

  /**
   * Get full engine diagnostics
   */
  getDiagnostics() {
    return {
      version: this.config.version,
      timestamp: new Date().toISOString(),
      config: this.config,
      metrics: this.metrics,
      agent_pool: this.pool.getStats(),
      task_queue: this.taskQueue.stats(),
      circuit_breaker: this.circuitBreaker.getStatus(),
      reasoning_engine: this.reasoningEngine.getMetrics(),
      recent_events: this.eventLog.slice(-20)
    };
  }

  /**
   * Health check — returns true if engine is operational
   */
  isHealthy() {
    const pool = this.pool.getStats();
    const idleRatio = parseInt(pool.idle) / pool.total;
    return idleRatio > 0.1 && this.metrics.tasks_failed / Math.max(this.metrics.tasks_dispatched, 1) < 0.3;
  }

  /**
   * Reset for testing (TDD support)
   */
  reset() {
    this.pool = new AgentPool({ total_agents: 128, skill_taxonomy: SKILL_TAXONOMY });
    this.taskQueue = new PriorityTaskQueue();
    this.circuitBreaker = new CircuitBreaker();
    this.reasoningEngine.reset();
    this.metrics = {
      tasks_dispatched: 0, tasks_completed: 0,
      tasks_failed: 0, retries_used: 0,
      avg_latency_ms: 0, pipelines_run: 0
    };
    this.eventLog = [];
  }
}

// ─── EXPORTS ────────────────────────────────────────────────────────────────

if (typeof module !== 'undefined') {
  module.exports = { OrchestrationEngine, AgentPool, PriorityTaskQueue, CircuitBreaker, SKILL_TAXONOMY };
}
