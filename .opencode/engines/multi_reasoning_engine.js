/**
 * ============================================================
 * OPENCODE ECOSYSTEM — MULTI-REASONING ENGINE
 * ============================================================
 * SDD Contract: MultiReasoningEngine v2.0
 * Agent: marceloclaro | TDD-compliant
 *
 * Implements 6 reasoning modes with confidence scoring,
 * chain-of-thought tracing, fallback logic, and
 * meta-cognitive self-evaluation.
 *
 * Modes: deductive | inductive | abductive | analogical | causal | meta
 * ============================================================
 */

'use strict';

// ─── REASONING MODE REGISTRY ───────────────────────────────────────────────

const REASONING_MODES = {

  /**
   * DEDUCTIVE: From general rules to specific conclusions
   * If P then Q; P → Q
   */
  deductive: {
    id: 'deductive',
    description: 'Derives specific conclusions from general premises using formal logic',
    confidence_threshold: 0.85,
    triggers: ['rule-based', 'logical', 'mathematical', 'formal', 'proof'],
    fallback_mode: 'inductive',
    chain_template: ['Premise', 'Sub-premise', 'Inference', 'Conclusion', 'Validation'],

    apply(context) {
      const { premises = [], rules = [] } = context;
      const conclusions = [];
      const trace = [];

      for (const rule of rules) {
        for (const premise of premises) {
          if (rule.condition(premise)) {
            const conclusion = rule.conclude(premise);
            conclusions.push(conclusion);
            trace.push({
              step: 'deductive_inference',
              rule: rule.name,
              premise: premise,
              conclusion,
              confidence: rule.confidence || 0.90
            });
          }
        }
      }

      return {
        mode: 'deductive',
        conclusions,
        trace,
        confidence: conclusions.length > 0
          ? trace.reduce((s, t) => s + t.confidence, 0) / trace.length
          : 0,
        reasoning_path: trace.map(t => `[${t.rule}] ${t.premise} → ${t.conclusion}`).join('\n')
      };
    }
  },

  /**
   * INDUCTIVE: From specific observations to general patterns
   * Pattern recognition and generalization
   */
  inductive: {
    id: 'inductive',
    description: 'Generalizes patterns from specific observations',
    confidence_threshold: 0.70,
    triggers: ['pattern', 'trend', 'data', 'observation', 'empirical', 'statistical'],
    fallback_mode: 'abductive',
    chain_template: ['Observations', 'Pattern Detection', 'Hypothesis', 'Generalization', 'Confidence'],

    apply(context) {
      const { observations = [], min_support = 0.6 } = context;
      const patterns = {};
      const trace = [];

      // Frequency analysis
      for (const obs of observations) {
        const key = JSON.stringify(obs.pattern || obs);
        patterns[key] = (patterns[key] || 0) + 1;
      }

      const total = observations.length || 1;
      const generalizations = Object.entries(patterns)
        .filter(([, count]) => count / total >= min_support)
        .map(([pattern, count]) => {
          const support = count / total;
          trace.push({ step: 'pattern_found', pattern, support, count });
          return { pattern: JSON.parse(pattern), support, count };
        });

      const confidence = generalizations.length > 0
        ? generalizations.reduce((s, g) => s + g.support, 0) / generalizations.length
        : 0;

      return {
        mode: 'inductive',
        generalizations,
        trace,
        confidence,
        reasoning_path: generalizations.map(g =>
          `Observed ${g.count}x (support=${(g.support*100).toFixed(1)}%): ${JSON.stringify(g.pattern)}`
        ).join('\n')
      };
    }
  },

  /**
   * ABDUCTIVE: Best explanation for observations (inference to best explanation)
   */
  abductive: {
    id: 'abductive',
    description: 'Finds the most probable explanation for a set of observations',
    confidence_threshold: 0.65,
    triggers: ['explain', 'why', 'cause', 'hypothesis', 'best-fit', 'diagnosis'],
    fallback_mode: 'analogical',
    chain_template: ['Observation', 'Possible Explanations', 'Scoring', 'Best Explanation', 'Verification'],

    apply(context) {
      const { observation, hypotheses = [] } = context;
      const trace = [];

      // Score each hypothesis by how well it explains the observation
      const scored = hypotheses.map(hyp => {
        const explanatory_power = hyp.explanatory_power || 0.5;
        const prior_probability = hyp.prior || 0.5;
        const simplicity = hyp.simplicity || 0.5;
        // Weighted score (simplified Bayesian-like)
        const score = (explanatory_power * 0.5) + (prior_probability * 0.3) + (simplicity * 0.2);

        trace.push({
          step: 'hypothesis_scoring',
          hypothesis: hyp.name,
          explanatory_power,
          prior_probability,
          simplicity,
          score
        });

        return { ...hyp, score };
      }).sort((a, b) => b.score - a.score);

      const best = scored[0];
      const confidence = best ? best.score : 0;

      return {
        mode: 'abductive',
        best_explanation: best,
        alternatives: scored.slice(1),
        trace,
        confidence,
        reasoning_path: scored.map((h, i) =>
          `[${i === 0 ? 'BEST' : `#${i+1}`}] ${h.name}: score=${h.score.toFixed(3)}`
        ).join('\n')
      };
    }
  },

  /**
   * ANALOGICAL: Reasoning by structural similarity to known cases
   */
  analogical: {
    id: 'analogical',
    description: 'Maps solutions from structurally similar domains',
    confidence_threshold: 0.60,
    triggers: ['similar', 'like', 'analogy', 'case-based', 'comparison', 'precedent'],
    fallback_mode: 'causal',
    chain_template: ['Source Domain', 'Target Domain', 'Structure Mapping', 'Inference Transfer', 'Validity Check'],

    apply(context) {
      const { target, cases = [] } = context;
      const trace = [];

      // Compute similarity between target and each case
      const ranked = cases.map(caseItem => {
        const similarity = this._computeSimilarity(target, caseItem);
        trace.push({
          step: 'similarity_computation',
          case: caseItem.name,
          target_features: target.features || [],
          case_features: caseItem.features || [],
          similarity
        });
        return { ...caseItem, similarity };
      }).sort((a, b) => b.similarity - a.similarity);

      const best_analog = ranked[0];
      const confidence = best_analog
        ? best_analog.similarity * (best_analog.domain_overlap || 0.7)
        : 0;

      return {
        mode: 'analogical',
        best_analog,
        ranked_cases: ranked,
        inferred_solution: best_analog
          ? `Apply ${best_analog.name} solution: ${best_analog.solution}`
          : null,
        trace,
        confidence,
        reasoning_path: ranked.slice(0, 3).map(c =>
          `Analog: ${c.name} (similarity=${(c.similarity*100).toFixed(0)}%) → ${c.solution}`
        ).join('\n')
      };
    },

    _computeSimilarity(target, caseItem) {
      const tf = new Set(target.features || []);
      const cf = new Set(caseItem.features || []);
      const intersection = [...tf].filter(f => cf.has(f)).length;
      const union = new Set([...tf, ...cf]).size;
      return union > 0 ? intersection / union : 0;
    }
  },

  /**
   * CAUSAL: Reasoning through cause-effect chains (Pearl's causality)
   */
  causal: {
    id: 'causal',
    description: 'Models cause-effect chains and counterfactuals (Pearl model)',
    confidence_threshold: 0.75,
    triggers: ['cause', 'effect', 'impact', 'intervention', 'counterfactual', 'mechanism'],
    fallback_mode: 'deductive',
    chain_template: ['Cause', 'Mechanism', 'Effect', 'Confounders', 'Counterfactual', 'Confidence'],

    apply(context) {
      const { causal_graph = [], intervention = null } = context;
      const trace = [];
      const effects = [];

      // Traverse causal graph
      for (const edge of causal_graph) {
        const { cause, effect, strength = 0.7, mechanism = 'unknown', confounders = [] } = edge;
        const confounder_penalty = confounders.length * 0.05;
        const adjusted_strength = Math.max(strength - confounder_penalty, 0);

        trace.push({
          step: 'causal_edge',
          cause, effect, mechanism,
          strength, confounders,
          adjusted_strength
        });

        if (!intervention || cause === intervention.variable) {
          effects.push({
            cause, effect, strength: adjusted_strength,
            counterfactual: `Without ${cause}: ${effect} would be ${intervention ? 'absent' : 'uncertain'}`
          });
        }
      }

      const confidence = effects.length > 0
        ? effects.reduce((s, e) => s + e.strength, 0) / effects.length
        : 0;

      return {
        mode: 'causal',
        effects,
        intervention_effects: intervention ? effects.filter(e => e.cause === intervention.variable) : [],
        trace,
        confidence,
        reasoning_path: effects.map(e =>
          `${e.cause} → ${e.effect} [strength=${(e.strength*100).toFixed(0)}%] | ${e.counterfactual}`
        ).join('\n')
      };
    }
  },

  /**
   * META: Reasoning about reasoning — self-monitoring and mode selection
   */
  meta: {
    id: 'meta',
    description: 'Meta-cognitive layer: selects optimal reasoning mode and monitors quality',
    confidence_threshold: 0.80,
    triggers: ['orchestrate', 'select-mode', 'evaluate', 'monitor', 'self-assess', 'quality'],
    fallback_mode: 'deductive',
    chain_template: ['Context Analysis', 'Mode Selection', 'Execution', 'Quality Evaluation', 'Refinement'],

    apply(context, engine) {
      const { query, available_data = {} } = context;
      const trace = [];

      // Analyze query to select best reasoning mode
      const mode_scores = {};
      for (const [modeId, mode] of Object.entries(REASONING_MODES)) {
        if (modeId === 'meta') continue;
        const trigger_matches = mode.triggers.filter(t =>
          (query || '').toLowerCase().includes(t)
        ).length;
        mode_scores[modeId] = trigger_matches / mode.triggers.length;
        trace.push({ step: 'mode_scoring', mode: modeId, score: mode_scores[modeId] });
      }

      const best_mode = Object.entries(mode_scores).sort((a, b) => b[1] - a[1])[0];
      const selected_mode = best_mode[1] > 0 ? best_mode[0] : 'deductive';

      trace.push({ step: 'mode_selected', mode: selected_mode, score: best_mode[1] });

      // Execute selected mode if engine provided
      let sub_result = null;
      if (engine && engine.reason) {
        sub_result = engine.reason(selected_mode, context);
      }

      return {
        mode: 'meta',
        selected_mode,
        mode_scores,
        sub_result,
        trace,
        confidence: 0.85,
        reasoning_path: [
          `Query analyzed: "${query}"`,
          `Best mode selected: ${selected_mode} (score=${(best_mode[1]*100).toFixed(0)}%)`,
          sub_result ? `Sub-result confidence: ${(sub_result.confidence*100).toFixed(1)}%` : 'No sub-execution'
        ].join('\n')
      };
    }
  }
};

// ─── MULTI-REASONING ENGINE ─────────────────────────────────────────────────

class MultiReasoningEngine {
  /**
   * @param {Object} config - Engine configuration
   * @param {number} config.max_reasoning_chain - Max depth for chained reasoning
   * @param {boolean} config.enable_meta - Enable meta-cognitive layer
   * @param {number} config.global_confidence_threshold - Min confidence to accept result
   */
  constructor(config = {}) {
    this.config = {
      max_reasoning_chain: config.max_reasoning_chain || 5,
      enable_meta: config.enable_meta !== false,
      global_confidence_threshold: config.global_confidence_threshold || 0.55,
      log_trace: config.log_trace !== false,
      version: '2.0.0'
    };
    this.history = [];
    this.metrics = {
      total_invocations: 0,
      mode_usage: {},
      avg_confidence: 0,
      fallbacks_triggered: 0,
      chains_executed: 0
    };
  }

  /**
   * Primary reasoning entry point
   * @param {string} mode - Reasoning mode ID
   * @param {Object} context - Domain context
   * @returns {Object} Reasoning result with trace and confidence
   */
  reason(mode, context) {
    // Preconditions (SDD contract)
    this._assertPreconditions(mode, context);

    const modeImpl = REASONING_MODES[mode];
    if (!modeImpl) {
      throw new Error(`[MultiReasoningEngine] Unknown reasoning mode: "${mode}". Valid: ${Object.keys(REASONING_MODES).join(', ')}`);
    }

    this.metrics.total_invocations++;
    this.metrics.mode_usage[mode] = (this.metrics.mode_usage[mode] || 0) + 1;

    let result;
    try {
      result = mode === 'meta'
        ? modeImpl.apply(context, this)
        : modeImpl.apply(context);
    } catch (err) {
      result = this._handleFallback(mode, context, err);
    }

    // Postcondition: confidence must be a number 0-1
    this._assertPostconditions(result);

    // Update rolling average confidence
    this.metrics.avg_confidence = (
      (this.metrics.avg_confidence * (this.metrics.total_invocations - 1)) + result.confidence
    ) / this.metrics.total_invocations;

    // Store in history
    if (this.config.log_trace) {
      this.history.push({
        timestamp: new Date().toISOString(),
        mode,
        confidence: result.confidence,
        context_keys: Object.keys(context)
      });
    }

    return result;
  }

  /**
   * Chain multiple reasoning modes sequentially
   * Each mode's output feeds the next as context
   * @param {Array<{mode, context}>} chain - Array of {mode, context} objects
   */
  chainReason(chain) {
    if (!Array.isArray(chain) || chain.length === 0) {
      throw new Error('[MultiReasoningEngine] chainReason requires a non-empty array');
    }
    if (chain.length > this.config.max_reasoning_chain) {
      throw new Error(`[MultiReasoningEngine] Chain length ${chain.length} exceeds max ${this.config.max_reasoning_chain}`);
    }

    this.metrics.chains_executed++;
    let accumulated_context = {};
    const results = [];

    for (const step of chain) {
      const merged_context = { ...accumulated_context, ...step.context };
      const result = this.reason(step.mode, merged_context);
      results.push(result);

      // Feed output as context for next step
      accumulated_context = {
        ...merged_context,
        previous_mode: step.mode,
        previous_confidence: result.confidence,
        previous_conclusions: result.conclusions || result.generalizations || result.effects || [],
        previous_reasoning_path: result.reasoning_path
      };
    }

    const overall_confidence = results.reduce((s, r) => s + r.confidence, 0) / results.length;

    return {
      type: 'chain',
      steps: results,
      overall_confidence,
      reasoning_chain: results.map(r => `[${r.mode.toUpperCase()}] conf=${(r.confidence*100).toFixed(1)}%`).join(' → '),
      final_result: results[results.length - 1]
    };
  }

  /**
   * Ensemble reasoning: run multiple modes in parallel, combine results
   * @param {Array<string>} modes - Array of mode IDs to run
   * @param {Object} context - Shared context
   * @param {string} combination - 'weighted_avg' | 'majority_vote' | 'highest_confidence'
   */
  ensembleReason(modes, context, combination = 'weighted_avg') {
    const results = modes.map(mode => {
      try {
        return this.reason(mode, context);
      } catch {
        return { mode, confidence: 0, reasoning_path: 'Failed', conclusions: [] };
      }
    });

    let combined;
    switch (combination) {
      case 'highest_confidence':
        combined = results.sort((a, b) => b.confidence - a.confidence)[0];
        break;

      case 'majority_vote': {
        const votes = {};
        results.forEach(r => {
          const key = JSON.stringify(r.conclusions || r.generalizations || []);
          votes[key] = (votes[key] || 0) + 1;
        });
        const winner = Object.entries(votes).sort((a, b) => b[1] - a[1])[0];
        combined = results.find(r => JSON.stringify(r.conclusions || []) === winner[0]);
        break;
      }

      default: { // weighted_avg
        const total_conf = results.reduce((s, r) => s + r.confidence, 0) || 1;
        combined = {
          mode: 'ensemble',
          combination,
          modes_used: modes,
          confidence: total_conf / results.length,
          results,
          reasoning_path: results.map(r =>
            `${r.mode}: conf=${(r.confidence*100).toFixed(1)}%`
          ).join('\n')
        };
      }
    }

    return { ...combined, ensemble_results: results };
  }

  /**
   * Auto-select best reasoning mode based on context analysis
   * @param {Object} context - Context with query and available_data
   */
  autoReason(context) {
    return this.reason('meta', context);
  }

  // ─── SDD CONTRACT ENFORCEMENT ──────────────────────────────────────────────

  _assertPreconditions(mode, context) {
    if (typeof mode !== 'string' || mode.length === 0) {
      throw new TypeError('[MultiReasoningEngine] Precondition violated: mode must be a non-empty string');
    }
    if (typeof context !== 'object' || context === null) {
      throw new TypeError('[MultiReasoningEngine] Precondition violated: context must be a non-null object');
    }
  }

  _assertPostconditions(result) {
    if (typeof result !== 'object' || result === null) {
      throw new TypeError('[MultiReasoningEngine] Postcondition violated: result must be an object');
    }
    if (typeof result.confidence !== 'number' || result.confidence < 0 || result.confidence > 1) {
      throw new RangeError(`[MultiReasoningEngine] Postcondition violated: confidence must be 0-1, got ${result.confidence}`);
    }
    if (!result.mode) {
      throw new Error('[MultiReasoningEngine] Postcondition violated: result must have mode field');
    }
  }

  _handleFallback(mode, context, originalError) {
    const modeImpl = REASONING_MODES[mode];
    const fallback = modeImpl ? modeImpl.fallback_mode : 'deductive';
    this.metrics.fallbacks_triggered++;

    console.warn(`[MultiReasoningEngine] Mode "${mode}" failed (${originalError.message}), falling back to "${fallback}"`);

    try {
      const result = REASONING_MODES[fallback].apply(context);
      return { ...result, fallback_from: mode, fallback_reason: originalError.message };
    } catch (fallbackError) {
      // Last resort: return empty deductive result
      return {
        mode: 'deductive',
        confidence: 0,
        conclusions: [],
        trace: [],
        reasoning_path: `All reasoning failed. Original: ${originalError.message}. Fallback: ${fallbackError.message}`,
        error: true
      };
    }
  }

  /**
   * Get engine health metrics
   */
  getMetrics() {
    return {
      ...this.metrics,
      modes_available: Object.keys(REASONING_MODES),
      history_size: this.history.length,
      config: this.config,
      timestamp: new Date().toISOString()
    };
  }

  /**
   * Reset engine state (for testing — TDD support)
   */
  reset() {
    this.history = [];
    this.metrics = {
      total_invocations: 0,
      mode_usage: {},
      avg_confidence: 0,
      fallbacks_triggered: 0,
      chains_executed: 0
    };
  }
}

// ─── EXPORTS ────────────────────────────────────────────────────────────────

if (typeof module !== 'undefined') {
  module.exports = { MultiReasoningEngine, REASONING_MODES };
}
