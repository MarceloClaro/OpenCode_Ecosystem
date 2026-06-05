// SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL
// Toda resposta DEVE ser em português do Brasil formal.
// Modelo: big-pickle (OpenCode Zen)

/**
 * BERNSTEIN SYNC v1.0 — Multi-Agent Orchestration Plugin
 * Inspirado em Bernstein (GitHub Action multi-agent orchestrator)
 * Adaptado para OpenCode com cross-validation matrix + CI-fix engine.
 *
 * Pipeline: DECOMPOSE → SELECT → EXECUTE → VALIDATE → FIX → COMMIT
 * v1.0: Integração completa com ecosystem-sync v3.5 e manus-evolve v2.2
 */
import type { Plugin } from "@opencode-ai/plugin"
import { readFile, writeFile, mkdir } from "fs/promises"

interface BernsteinTask {
  id: string
  description: string
  status: "pending" | "executing" | "completed" | "failed" | "fixing"
  priority: number
  assignedAgents: string[]
  affinityScore: number
  attempts: number
  result?: string
  cost?: number
  startTime?: number
  endTime?: number
}

interface AgentConfig {
  name: string
  cli: "claude" | "codex" | "gemini" | "qwen"
  maxTokens: number
  timeout: number
  retryOnFailure: boolean
  affinityMCPs: string[]
}

interface EvidenceBundle {
  taskId: string
  timestamp: string
  tasksCompleted: number
  totalCost: number
  durationSeconds: number
  successRate: number
  logs: Record<string, string>
  testResults?: Record<string, any>
  costReport?: Record<string, any>
  fixLog?: string[]
}

interface BernsteinState {
  tasks: BernsteinTask[]
  currentTask: string | null
  status: "idle" | "decomposing" | "selecting" | "executing" | "validating" | "fixing" | "completed" | "failed"
  totalCost: number
  budget: number
  maxRetries: number
  cli: "claude" | "codex" | "gemini" | "qwen"
  evidenceBundles: EvidenceBundle[]
  currentRunId: string | null
  version: string
}

const STATE_FILE = ".evolve/bernstein-state.json"
const EVIDENCE_DIR = ".evidence"
const AGENTS_DIR = "agents"

const DEFAULT_AGENTS: AgentConfig[] = [
  { name: "ws-coder", cli: "claude", maxTokens: 8000, timeout: 120000, retryOnFailure: true, affinityMCPs: ["eslint", "diff", "code-runner", "sqlite"] },
  { name: "code-reviewer", cli: "claude", maxTokens: 4000, timeout: 60000, retryOnFailure: true, affinityMCPs: ["eslint", "diff", "github"] },
  { name: "debugger", cli: "claude", maxTokens: 6000, timeout: 90000, retryOnFailure: true, affinityMCPs: ["playwright", "chrome-devtools"] },
  { name: "git-manager", cli: "claude", maxTokens: 3000, timeout: 45000, retryOnFailure: false, affinityMCPs: ["github", "diff"] },
  { name: "test-engineer", cli: "claude", maxTokens: 5000, timeout: 75000, retryOnFailure: true, affinityMCPs: ["playwright", "code-runner"] },
  { name: "reversa-archaeologist", cli: "claude", maxTokens: 4000, timeout: 60000, retryOnFailure: false, affinityMCPs: ["filesystem", "diff", "sqlite"] },
  { name: "build-agent", cli: "claude", maxTokens: 6000, timeout: 90000, retryOnFailure: true, affinityMCPs: ["github", "eslint", "diff"] },
  { name: "openagent", cli: "claude", maxTokens: 10000, timeout: 180000, retryOnFailure: true, affinityMCPs: ["filesystem", "memory", "github", "websearch"] },
]

const MCP_AFFINITY: Record<string, string[]> = {
  "eslint": ["ws-coder", "code-reviewer", "build-agent"],
  "diff": ["ws-coder", "code-reviewer", "git-manager"],
  "code-runner": ["ws-coder", "test-engineer", "openagent"],
  "sqlite": ["ws-coder", "reversa-archaeologist"],
  "playwright": ["debugger", "test-engineer"],
  "chrome-devtools": ["debugger"],
  "github": ["git-manager", "build-agent", "openagent"],
  "filesystem": ["reversa-archaeologist", "openagent"],
  "memory": ["openagent"],
  "websearch": ["openagent"],
  "fetch": ["openagent"],
  "mem0-mcp": ["openagent"],
  "sequential-thinking": ["openagent", "ws-coder"],
}

function computeAffinity(task: string, agents: string[]): { agent: string; score: number }[] {
  const results: { agent: string; score: number }[] = []
  for (const agent of agents) {
    let score = 0.5
    const lc = agent.toLowerCase()
    if (lc.includes("code") || lc.includes("coder")) {
      if (task.match(/implement|build|create|write|add/i)) score = 0.85
      if (task.match(/fix|bug|error|patch/i)) score = 0.80
      if (task.match(/test|spec/i)) score = 0.75
    }
    if (lc.includes("review") || lc.includes("reviewer")) {
      if (task.match(/review|audit|check/i)) score = 0.90
      if (task.match(/pr|pull request/i)) score = 0.88
    }
    if (lc.includes("debug")) {
      if (task.match(/debug|fix|error|exception|fail/i)) score = 0.85
    }
    if (lc.includes("git")) {
      if (task.match(/commit|push|pull|branch|merge/i)) score = 0.90
      if (task.match(/fix-ci|ci|github/i)) score = 0.80
    }
    if (lc.includes("test")) {
      if (task.match(/test|spec|e2e|integration/i)) score = 0.88
    }
    if (lc.includes("build")) {
      if (task.match(/build|compile|package|deploy/i)) score = 0.85
      if (task.match(/fix-ci|ci|pipeline/i)) score = 0.78
    }
    if (lc.includes("openagent")) {
      score = 0.70
      if (task.match(/general|orchestrat|multi/i)) score = 0.92
    }
    results.push({ agent, score })
  }
  return results.sort((a, b) => b.score - a.score)
}

async function loadState(directory: string): Promise<BernsteinState> {
  try {
    const content = await readFile(`${directory}/${STATE_FILE}`, "utf-8")
    const s = JSON.parse(content)
    if (!s.evidenceBundles) s.evidenceBundles = []
    if (!s.currentRunId) s.currentRunId = null
    return s
  } catch { }
  return {
    tasks: [], currentTask: null, status: "idle",
    totalCost: 0, budget: 5.00, maxRetries: 3, cli: "claude",
    evidenceBundles: [], currentRunId: null, version: "1.0.0",
  }
}

async function saveState(directory: string, state: BernsteinState) {
  await mkdir(`${directory}/.evolve`, { recursive: true }).catch(() => {})
  await writeFile(`${directory}/${STATE_FILE}`, JSON.stringify(state, null, 2))
}

async function saveEvidence(directory: string, bundle: EvidenceBundle) {
  const base = `${directory}/${EVIDENCE_DIR}/${bundle.taskId}`
  await mkdir(`${base}/logs`, { recursive: true }).catch(() => {})
  await mkdir(`${base}/tests`, { recursive: true }).catch(() => {})
  await writeFile(`${base}/summary.json`, JSON.stringify({
    tasksCompleted: bundle.tasksCompleted,
    totalCost: bundle.totalCost,
    durationSeconds: bundle.durationSeconds,
    successRate: bundle.successRate,
    timestamp: bundle.timestamp,
  }, null, 2))
  await writeFile(`${base}/cost-report.json`, JSON.stringify(bundle.costReport || {}, null, 2))
  if (bundle.fixLog) {
    await writeFile(`${base}/fix-log.md`, bundle.fixLog.map(l => `- ${l}`).join("\n"))
  }
  for (const [name, log] of Object.entries(bundle.logs)) {
    await writeFile(`${base}/logs/${name}.log`, log)
  }
}

export const BernsteinSyncPlugin: Plugin = async ({ project, client, $, directory, worktree }) => {
  console.log("[Bernstein v1.0] Multi-Agent Orchestration initialized")
  let state = await loadState(directory)
  await mkdir(`${directory}/${EVIDENCE_DIR}`, { recursive: true }).catch(() => {})

  return {
    "session.created": async () => {
      state.status = "idle"
      state.currentTask = null
      state.totalCost = 0
      state.currentRunId = crypto.randomUUID()
      await saveState(directory, state)
      await client.app.log({
        body: {
          service: "bernstein-v1.0",
          level: "info",
          message: `Bernstein ready | Run: ${state.currentRunId} | Budget: $${state.budget} | CLI: ${state.cli} | Agents: ${DEFAULT_AGENTS.length}`,
        },
      })
    },

    "shell.env": async (_input: any, output: any) => {
      output.env.BERNSTEIN_RUN_ID = state.currentRunId || ""
      output.env.BERNSTEIN_STATUS = state.status
      output.env.BERNSTEIN_BUDGET = String(state.budget)
      output.env.BERNSTEIN_TOTAL_COST = String(state.totalCost.toFixed(4))
      output.env.BERNSTEIN_CLI = state.cli
      output.env.BERNSTEIN_MAX_RETRIES = String(state.maxRetries)
      output.env.BERNSTEIN_TASK_COUNT = String(state.tasks.length)
      output.env.BERNSTEIN_COMPLETED = String(state.tasks.filter(t => t.status === "completed").length)
      output.env.BERNSTEIN_VERSION = state.version
      output.env.BERNSTEIN_EVIDENCE_DIR = EVIDENCE_DIR
    },

    "tool.execute.before": async (input: any, _output: any) => {
      const toolName = input.tool || ""
      if (toolName === "bash" || toolName === "powershell") {
        const args = input.args?.command || input.args?._[0] || ""
        if (typeof args === "string" && args.includes("bernstein")) {
          state.status = "decomposing"
          await saveState(directory, state)
          await client.app.log({
            body: { service: "bernstein-v1.0", level: "info",
              message: `Task detected: ${args.substring(0, 80)}` }
          })
        }
      }
      if (toolName === "code-runner") {
        const isCIFix = (input.args?.code || "").includes("fix-ci") ||
                       (input.args?.code || "").includes("CI")
        if (isCIFix) {
          state.status = "fixing"
          await saveState(directory, state)
        }
      }
    },

    "tool.execute.after": async (input: any, output: any) => {
      const toolName = input.tool || ""
      if (toolName === "code-runner") {
        const result = typeof output?.result === "string" ? output.result : JSON.stringify(output?.result || "")
        if (state.status === "executing" || state.status === "fixing") {
          const completed = state.tasks.filter(t => t.status === "completed").length
          const total = state.tasks.length || 1
          const sr = completed / total
          state.totalCost += 0.05
          const bundle: EvidenceBundle = {
            taskId: state.currentRunId || "unknown",
            timestamp: new Date().toISOString(),
            tasksCompleted: completed,
            totalCost: state.totalCost,
            durationSeconds: 0,
            successRate: sr,
            logs: { "tool-execution": result.substring(0, 2000) },
          }
          if (state.totalCost > state.budget && state.budget > 0) {
            state.status = "failed"
            await client.app.log({
              body: { service: "bernstein-v1.0", level: "warn",
                message: `Budget exceeded: $${state.totalCost.toFixed(4)} > $${state.budget}` }
            })
          }
          state.evidenceBundles.push(bundle)
          if (state.status !== "failed") {
            state.status = "validating"
          }
          await saveState(directory, state)
        }
      }
      if (toolName === "github" && state.status === "fixing") {
        const result = typeof output?.result === "string" ? output.result : ""
        if (result.includes("logs") || result.includes("workflow")) {
          await client.app.log({
            body: { service: "bernstein-v1.0", level: "info",
              message: `CI logs downloaded, initiating fix sequence` }
          })
        }
      }
      if (toolName === "bash" && state.status === "validating") {
        state.status = "completed"
        await saveState(directory, state)
        const completed = state.tasks.filter(t => t.status === "completed").length
        await client.app.log({
          body: { service: "bernstein-v1.0", level: "info",
            message: `Bernstein run complete | Tasks: ${completed}/${state.tasks.length} | Cost: $${state.totalCost.toFixed(4)} | Status: ${state.status}` }
        })
      }
    },

    "session.idle": async () => {
      if (state.status === "idle" && state.tasks.length > 0) {
        const pending = state.tasks.filter(t => t.status === "pending")
        if (pending.length > 0) {
          state.status = "executing"
          const top = pending[0]
          top.status = "executing"
          top.startTime = Date.now()
          state.currentTask = top.id
          const agents = computeAffinity(top.description, DEFAULT_AGENTS.map(a => a.name))
          top.assignedAgents = agents.map(a => a.agent)
          top.affinityScore = agents[0]?.score || 0.5
          await client.app.log({
            body: { service: "bernstein-v1.0", level: "info",
              message: `Executing: ${top.id} | Agent: ${top.assignedAgents[0]} (affinity: ${top.affinityScore.toFixed(2)})` }
          })
          await saveState(directory, state)
        }
      }
      if (state.status === "completed" || state.status === "failed") {
        const bundles = state.evidenceBundles.filter(b => b.taskId === state.currentRunId)
        if (bundles.length > 0) {
          await saveEvidence(directory, bundles[bundles.length - 1])
          await client.app.log({
            body: { service: "bernstein-v1.0", level: "info",
              message: `Evidence bundle saved: ${EVIDENCE_DIR}/${state.currentRunId}` }
          })
        }
        const completed = state.tasks.filter(t => t.status === "completed").length
        await client.app.log({
          body: { service: "bernstein-v1.0", level: "info",
            message: `BERNSTEIN SUMMARY | Run: ${state.currentRunId} | Tasks: ${completed}/${state.tasks.length} | Cost: $${state.totalCost.toFixed(4)}/${state.budget > 0 ? '$' + state.budget : 'unlimited'} | Status: ${state.status}` }
        })
      }
    },
  }
}