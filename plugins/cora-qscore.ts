// =====================================================================
// CORA Q-SCORE PLUGIN v1.0
// Algoritmo UCB1 para selecao adaptativa de debatedores no Cora-Debate
// =====================================================================
import type { Plugin } from "@opencode-ai/plugin"
import { readFile, writeFile, mkdir } from "fs/promises"
import { join } from "path"

interface QScoreEntry {
  agent_id: string
  mean_reward: number
  samples: number
  total_reward: number
  last_selected: string | null
  domain_scores: Record<string, { mean: number; samples: number }>
}

interface QScoreState {
  total_samples: number
  agents: Record<string, QScoreEntry>
  version: string
  last_updated: string
}

interface AgentRecommendation {
  agent_id: string
  q_score: number
  exploitation_term: number
  exploration_term: number
  reason: string
}

const QSCORE_STATE_FILE = ".evolve/cora-qscore-state.json"
const QSCORE_LOG_FILE = ".evolve/cora-qscore-audit.jsonl"
const PLUGIN_VERSION = "1.0.0"

function computeQScore(entry: QScoreEntry, totalSamples: number): number {
  if (entry.samples === 0) return Infinity
  const exploitation = entry.mean_reward
  const exploration = Math.sqrt((2 * Math.log(totalSamples)) / entry.samples)
  return exploitation + exploration
}

function computeDomainQScore(entry: QScoreEntry, totalSamples: number, domain: string): number {
  const base = computeQScore(entry, totalSamples)
  const domainStats = entry.domain_scores[domain]
  if (domainStats && domainStats.samples > 0) {
    const domainBonus = domainStats.mean * 0.15
    return base + domainBonus
  }
  return base
}

async function loadState(directory: string): Promise<QScoreState> {
  try {
    const raw = await readFile(join(directory, QSCORE_STATE_FILE), "utf-8")
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

async function saveState(directory: string, state: QScoreState): Promise<void> {
  state.last_updated = new Date().toISOString()
  state.version = PLUGIN_VERSION
  await mkdir(join(directory, ".evolve"), { recursive: true }).catch(() => {})
  await writeFile(join(directory, QSCORE_STATE_FILE), JSON.stringify(state, null, 2), "utf-8")
}

async function auditLog(directory: string, entry: Record<string, unknown>): Promise<void> {
  const line = JSON.stringify({ ...entry, timestamp: new Date().toISOString() }) + "\n"
  await writeFile(join(directory, QSCORE_LOG_FILE), line, { flag: "a" }).catch(() => {})
}

async function registerAgent(directory: string, agentId: string, initialReward: number = 0.5): Promise<void> {
  const state = await loadState(directory)
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
    await saveState(directory, state)
    await auditLog(directory, { action: "register_agent", agent_id: agentId, initial_reward: initialReward })
  }
}

async function updateReward(directory: string, agentId: string, reward: number, domain: string): Promise<void> {
  const state = await loadState(directory)
  const agent = state.agents[agentId]
  if (!agent) {
    await registerAgent(directory, agentId, reward)
    return
  }
  agent.samples += 1
  agent.total_reward += reward
  agent.mean_reward = agent.total_reward / agent.samples
  agent.last_selected = new Date().toISOString()
  state.total_samples += 1
  if (!agent.domain_scores[domain]) {
    agent.domain_scores[domain] = { mean: 0, samples: 0 }
  }
  const ds = agent.domain_scores[domain]
  ds.samples += 1
  ds.mean = (ds.mean * (ds.samples - 1) + reward) / ds.samples
  await saveState(directory, state)
  await auditLog(directory, {
    action: "update_reward", agent_id: agentId, reward, domain,
    new_mean: agent.mean_reward, samples: agent.samples,
  })
}

async function selectAgent(directory: string, domain: string, excludeAgentIds: string[] = []): Promise<AgentRecommendation | null> {
  const state = await loadState(directory)
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

async function getRanking(directory: string, domain?: string): Promise<AgentRecommendation[]> {
  const state = await loadState(directory)
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

async function resetScores(directory: string, domain?: string): Promise<void> {
  const state = await loadState(directory)
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
  await saveState(directory, state)
  await auditLog(directory, { action: "reset_scores", domain: domain || "ALL" })
}

export const CoraQScorePlugin: Plugin = async ({ project, client, $, directory, worktree }) => {
  const state = await loadState(directory)
  console.log(`[CORA-QSCORE] v${PLUGIN_VERSION} inicializado | ${Object.keys(state.agents).length} agentes registrados | N=${state.total_samples} amostras`)

  return {
    "session.idle": async () => {
      console.log("[CORA-QSCORE] Finalizado. Estado persistido em", QSCORE_STATE_FILE)
    }
  }
}
