// =====================================================================
// CORA Q-SCORE PLUGIN v1.0
// Algoritmo UCB1 para selecao adaptativa de debatedores no Cora-Debate
// =====================================================================
// Integracao: skill cora-debate (P19) + reasoning-orchestrator + agent-forum
// Dependencia: @opencode-ai/plugin
// =====================================================================
import type { Plugin } from "@opencode-ai/plugin"
import { readFile, writeFile, mkdir } from "fs/promises"
import { join } from "path"

// ---------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------

interface QScoreEntry {
  agent_id: string
  mean_reward: number    // v_i: recompensa media do agente i
  samples: number        // n_i: numero de vezes que o agente foi selecionado
  total_reward: number   // soma acumulada de recompensas
  last_selected: string | null  // ISO timestamp
  domain_scores: Record<string, { mean: number; samples: number }>
}

interface QScoreState {
  total_samples: number  // N: numero total de selecoes
  agents: Record<string, QScoreEntry>
  version: string
  last_updated: string
}

interface DebateContext {
  domain: string
  topic: string
  active_verifiers: string[]
  k_self_consistency: number
  temperature_initial: number
  alpha_annealing: number
}

interface AgentRecommendation {
  agent_id: string
  q_score: number
  exploitation_term: number   // v_i
  exploration_term: number    // sqrt(2 ln N / n_i)
  reason: string
}

// ---------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------

const QSCORE_STATE_FILE = ".evolve/cora-qscore-state.json"
const QSCORE_LOG_FILE = ".evolve/cora-qscore-audit.jsonl"
const PLUGIN_VERSION = "1.0.0"

// ---------------------------------------------------------------------
// Core UCB1 Algorithm
// ---------------------------------------------------------------------

/**
 * Calcula Q-Score UCB1 para um agente.
 *
 * Formula: Q_i(N) = v_i + sqrt(2 * ln(N) / n_i)
 *
 * Onde:
 *   v_i = recompensa media do agente i (exploitation)
 *   N   = numero total de amostras
 *   n_i = numero de vezes que o agente i foi selecionado (exploration)
 *
 * Exploration bonus decai com sqrt(ln N / n_i), favorecendo agentes
 * pouco testados quando N e grande e n_i e pequeno.
 */
function computeQScore(entry: QScoreEntry, totalSamples: number): number {
  if (entry.samples === 0) return Infinity  // nunca testado -> prioridade maxima
  const exploitation = entry.mean_reward
  const exploration = Math.sqrt((2 * Math.log(totalSamples)) / entry.samples)
  return exploitation + exploration
}

/**
 * Calcula Q-Score com ponderacao por dominio.
 * Agentes com bom desempenho no dominio atual recebem bonus.
 */
function computeDomainQScore(
  entry: QScoreEntry,
  totalSamples: number,
  domain: string
): number {
  const base = computeQScore(entry, totalSamples)
  const domainStats = entry.domain_scores[domain]
  if (domainStats && domainStats.samples > 0) {
    const domainBonus = domainStats.mean * 0.15  // +15% bonus por expertise no dominio
    return base + domainBonus
  }
  return base
}

// ---------------------------------------------------------------------
// State Management
// ---------------------------------------------------------------------

async function loadState(): Promise<QScoreState> {
  try {
    const raw = await readFile(QSCORE_STATE_FILE, "utf-8")
    return JSON.parse(raw) as QScoreState
  } catch {
    return {
      total_samples: 0,
      agents: {},
      version: PLUGIN_VERSION,
      last_updated: new Date().toISOString(),
    }
  }
}

async function saveState(state: QScoreState): Promise<void> {
  state.last_updated = new Date().toISOString()
  state.version = PLUGIN_VERSION
  await mkdir(".evolve", { recursive: true })
  await writeFile(QSCORE_STATE_FILE, JSON.stringify(state, null, 2), "utf-8")
}

async function auditLog(entry: Record<string, unknown>): Promise<void> {
  const line = JSON.stringify({ ...entry, timestamp: new Date().toISOString() })
  await writeFile(QSCORE_LOG_FILE, line + "\n", "utf-8")
}

// ---------------------------------------------------------------------
// Agent Operations
// ---------------------------------------------------------------------

/**
 * Registra um novo agente no sistema Q-Score.
 */
async function registerAgent(agentId: string, initialReward: number = 0.5): Promise<void> {
  const state = await loadState()
  if (!state.agents[agentId]) {
    state.agents[agentId] = {
      agent_id: agentId,
      mean_reward: initialReward,
      samples: 1,
      total_reward: initialReward,
      last_selected: null,
      domain_scores: {},
    }
    state.total_samples += 1
    await saveState(state)
    await auditLog({ action: "register_agent", agent_id: agentId, initial_reward: initialReward })
  }
}

/**
 * Atualiza o Q-Score de um agente apos uma rodada de debate.
 *
 * @param agentId - ID do agente
 * @param reward - Recompensa: 1.0 se verificacao passou, 0.0 se falhou, 0.5 se incerto
 * @param domain - Dominio do debate (algebra, physics, statistics, demonstrations)
 */
async function updateReward(agentId: string, reward: number, domain: string): Promise<void> {
  const state = await loadState()
  const agent = state.agents[agentId]
  if (!agent) {
    await registerAgent(agentId, reward)
    return
  }
  // Atualizar metricas globais
  agent.samples += 1
  agent.total_reward += reward
  agent.mean_reward = agent.total_reward / agent.samples
  agent.last_selected = new Date().toISOString()
  state.total_samples += 1
  // Atualizar metricas por dominio
  if (!agent.domain_scores[domain]) {
    agent.domain_scores[domain] = { mean: 0, samples: 0 }
  }
  const ds = agent.domain_scores[domain]
  ds.samples += 1
  ds.mean = (ds.mean * (ds.samples - 1) + reward) / ds.samples
  await saveState(state)
  await auditLog({
    action: "update_reward", agent_id: agentId, reward, domain,
    new_mean: agent.mean_reward, samples: agent.samples,
  })
}

/**
 * Seleciona o melhor agente para a proxima rodada usando UCB1.
 * Retorna recomendacao com explicacao dos termos.
 */
async function selectAgent(domain: string, excludeAgentIds: string[] = []): Promise<AgentRecommendation | null> {
  const state = await loadState()
  const candidates = Object.entries(state.agents)
    .filter(([id]) => !excludeAgentIds.includes(id))
  if (candidates.length === 0) return null
  let bestAgent: AgentRecommendation | null = null
  let bestScore = -Infinity
  for (const [id, entry] of candidates) {
    const qScore = computeDomainQScore(entry, state.total_samples, domain)
    if (qScore > bestScore) {
      bestScore = qScore
      const exploitation = entry.mean_reward
      const exploration = entry.samples > 0
        ? Math.sqrt((2 * Math.log(state.total_samples)) / entry.samples)
        : Infinity
      bestAgent = {
        agent_id: id,
        q_score: qScore,
        exploitation_term: exploitation,
        exploration_term: exploration,
        reason: exploration > exploitation
          ? `exploracao (n_i=${entry.samples}, bonus=${exploration.toFixed(3)})`
          : `exploitacao (v_i=${exploitation.toFixed(3)}, samples=${entry.samples})`,
      }
    }
  }
  return bestAgent
}

/**
 * Retorna ranking completo de agentes ordenado por Q-Score.
 */
async function getRanking(domain?: string): Promise<AgentRecommendation[]> {
  const state = await loadState()
  const ranking: AgentRecommendation[] = []
  for (const [id, entry] of Object.entries(state.agents)) {
    const qScore = domain
      ? computeDomainQScore(entry, state.total_samples, domain)
      : computeQScore(entry, state.total_samples)
    ranking.push({
      agent_id: id,
      q_score: qScore,
      exploitation_term: entry.mean_reward,
      exploration_term: entry.samples > 0
        ? Math.sqrt((2 * Math.log(state.total_samples)) / entry.samples)
        : Infinity,
      reason: `n_i=${entry.samples}, v_i=${entry.mean_reward.toFixed(4)}`,
    })
  }
  ranking.sort((a, b) => b.q_score - a.q_score)
  return ranking
}

/**
 * Reseta todos os Q-Scores (util para novo dominio ou apos recalibracao).
 */
async function resetScores(domain?: string): Promise<void> {
  const state = await loadState()
  if (domain) {
    for (const agent of Object.values(state.agents)) {
      if (agent.domain_scores[domain]) {
        delete agent.domain_scores[domain]
      }
    }
  } else {
    state.agents = {}
    state.total_samples = 0
  }
  await saveState(state)
  await auditLog({ action: "reset_scores", domain: domain || "ALL" })
}

// ---------------------------------------------------------------------
// Plugin Entry Point
// ---------------------------------------------------------------------

const coraQScorePlugin: Plugin = {
  id: "cora-qscore",
  name: "Cora Q-Score UCB1",
  version: PLUGIN_VERSION,
  description: "Motor de selecao adaptativa de debatedores usando algoritmo UCB1 (Upper Confidence Bound 1). Implementa exploration-exploitation para o pipeline Cora-Debate (P19).",

  async onInit() {
    const state = await loadState()
    console.log(`[CORA-QSCORE] v${PLUGIN_VERSION} inicializado | ${Object.keys(state.agents).length} agentes registrados | N=${state.total_samples} amostras`)
  },

  async onShutdown() {
    console.log("[CORA-QSCORE] Finalizado. Estado persistido em", QSCORE_STATE_FILE)
  },

  // Expor funcoes como comandos para o ecossistema
  commands: {
    "/cora-score": {
      description: "Exibe Q-Score de todos os debatedores",
      async handler(args: string[]) {
        const domain = args[0] || undefined
        const ranking = await getRanking(domain)
        const lines = ["# Q-Score Ranking (UCB1)", ""]
        lines.push("| Agente | Q-Score | v_i (exploit) | sqrt(2lnN/n_i) (explore) | Samples |")
        lines.push("|--------|---------|---------------|---------------------------|---------|")
        for (const r of ranking) {
          lines.push(`| ${r.agent_id} | ${r.q_score.toFixed(4)} | ${r.exploitation_term.toFixed(4)} | ${r.exploration_term.toFixed(4)} | - |`)
        }
        return lines.join("\n")
      },
    },
    "/cora-select": {
      description: "Seleciona melhor agente para dominio usando UCB1",
      async handler(args: string[]) {
        const domain = args[0] || "general"
        const recommendation = await selectAgent(domain)
        if (!recommendation) return "Nenhum agente registrado."
        return [
          `# Agente Selecionado: ${recommendation.agent_id}`,
          `- Q-Score: ${recommendation.q_score.toFixed(4)}`,
          `- Criterio: ${recommendation.reason}`,
        ].join("\n")
      },
    },
    "/cora-reward": {
      description: "Registra recompensa para um agente: /cora-reward <agent_id> <reward> <domain>",
      async handler(args: string[]) {
        if (args.length < 3) return "Uso: /cora-reward <agent_id> <reward> <domain>"
        const [agentId, rewardStr, domain] = args
        const reward = parseFloat(rewardStr)
        if (isNaN(reward) || reward < 0 || reward > 1) return "Reward deve ser entre 0 e 1"
        await updateReward(agentId, reward, domain)
        return `Recompensa registrada: ${agentId} += ${reward} (dominio: ${domain})`
      },
    },
    "/cora-reset": {
      description: "Reseta Q-Scores: /cora-reset [dominio]",
      async handler(args: string[]) {
        await resetScores(args[0] || undefined)
        return args[0] ? `Q-Scores resetados para dominio: ${args[0]}` : "Todos Q-Scores resetados."
      },
    },
  },
}

export default coraQScorePlugin
