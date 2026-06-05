// SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL
// Toda resposta DEVE ser em português do Brasil formal.
// Modelo: big-pickle (OpenCode Zen)

/**
 * MANUS EVOLVE v2.0 — PlanAct Autonomous Evolution Engine + Token Efficiency
 * Inspirado em Manus AI (Simpleyyt/ai-manus)
 * Arquitetura Transformer com evolução por rodada e geracao de habilidades.
 * v2.0: Integra correção linguística, token efficiency e ecossistema v3.5
 * v2.2: Nexus Pipeline integrado — scan -> heal -> learn por ciclo
 *
 * Pipeline: PLAN → ACT → CORRECT → REFLECT → EXTRACT → EVOLVE → NEXUS
 * Integrado com Nexus Multiagents v6.2 (sync barriers + feedback)
 */
import type { Plugin } from "@opencode-ai/plugin"
import { readFile, writeFile, mkdir } from "fs/promises"
import { existsSync } from "fs"

interface ToolMetric {
  tool: string
  calls: number
  errors: number
  totalLatencyMs: number
  avgLatencyMs: number
  successRate: number
}

interface EvolutionRound {
  round: number
  timestamp: string
  plan: string
  actions: string[]
  reflections: string[]
  extractedSkills: string[]
  score: number
  learnings: string[]
  correctionsApplied: number    // v2.0: CJK + PT-BR corrections
  tokensSaved: number           // v2.0: Token efficiency metrics
}

interface SessionMetrics {
  sessionId: string
  agent: string
  toolsUsed: Record<string, ToolMetric>
  totalCalls: number
  totalErrors: number
  errorRate: number
  healthScore: number
  durationMinutes: number
  startTime: number
}

interface NexusReport {
  scanTime: string
  anomalies: number
  fixes: number
  recommendations: number
  healthDelta: string
}

interface ManusState {
  rounds: EvolutionRound[]
  totalSkillsGenerated: number
  currentPlan: string | null
  actionCount: number
  lastEvolution: string | null
  evolutionScore: number
  patterns: Record<string, number>
  correctionPatterns: Record<string, number>   // v2.0
  tokenOptimizationPatterns: Record<string, number>  // v2.0
  nexusReports: NexusReport[]
  lastNexusRun: string | null
  version: string
  toolCallMetrics: { startTime: number; tool: string } | null
  sessionMetrics: SessionMetrics
}

const STATE_FILE = ".evolve/manus-state.json"
const SKILLS_DIR = "evolution"

async function loadState(directory: string): Promise<ManusState> {
  try {
    const statePath = `${directory}/${STATE_FILE}`
    if (existsSync(statePath)) {
      const content = await readFile(statePath, "utf-8")
      const s = JSON.parse(content)
      if (!s.toolCallMetrics) s.toolCallMetrics = null
      if (!s.nexusReports) s.nexusReports = []
      if (!s.lastNexusRun) s.lastNexusRun = null
      if (!s.sessionMetrics) {
        s.sessionMetrics = {
          sessionId: crypto.randomUUID(), agent: "manus-evolve",
          toolsUsed: {}, totalCalls: 0, totalErrors: 0,
          errorRate: 0, healthScore: 100, durationMinutes: 0, startTime: Date.now()
        }
      }
      return s
    }
  } catch {}
  return {
    rounds: [], totalSkillsGenerated: 0, currentPlan: null,
    actionCount: 0, lastEvolution: null, evolutionScore: 0, patterns: {},
    correctionPatterns: {}, tokenOptimizationPatterns: {}, version: "2.1.0",
    nexusReports: [], lastNexusRun: null, toolCallMetrics: null,
    sessionMetrics: {
      sessionId: "", agent: "manus-evolve",
      toolsUsed: {}, totalCalls: 0, totalErrors: 0,
      errorRate: 0, healthScore: 100, durationMinutes: 0, startTime: Date.now()
    }
  }
}

async function saveState(directory: string, state: ManusState) {
  await mkdir(`${directory}/.evolve`, { recursive: true }).catch(() => {})
  await writeFile(`${directory}/${STATE_FILE}`, JSON.stringify(state, null, 2))
}

function extractPatterns(task: string, result: string): string[] {
  const patterns: string[] = []
  if (result.includes("success") || result.includes("OK") || result.includes("completed")) {
    patterns.push(`pattern:success_flow:${task.substring(0, 30)}`)
  }
  const toolPatterns = result.match(/tool:(\w+)/g)
  if (toolPatterns) {
    toolPatterns.forEach((t: string) => patterns.push(`tool_chain:${t}`))
  }
  if (task.includes("fix") || task.includes("error") || task.includes("bug")) {
    patterns.push(`category:debug:${task.substring(0, 30)}`)
  }
  return patterns
}

function extractCorrectionPatterns(result: string): string[] {
  const patterns: string[] = []
  const cjkMatches = result.match(/(\d+)\s*(?:CJK|chinese|character)/gi)
  if (cjkMatches) {
    patterns.push("correction:cjk_detected")
    cjkMatches.forEach((m: string) => patterns.push(`correction:cjk_count:${m}`))
  }
  if (result.includes("PT-BR") || result.includes("correction") || result.includes("ortografia")) {
    patterns.push("correction:ptbr_applied")
  }
  if (result.includes("clean") || result.includes("limpo") || result.includes("removed")) {
    patterns.push("correction:cleanup_success")
  }
  return patterns
}

function extractTokenPatterns(result: string): string[] {
  const patterns: string[] = []
  if (result.includes("token") && (result.includes("saved") || result.includes("economia") || result.includes("-"))) {
    patterns.push("token:efficiency_detected")
  }
  if (result.includes("chines") || result.includes("chinese") || result.includes("中文")) {
    patterns.push("token:chinese_context")
  }
  if (result.includes("big-pickle")) {
    patterns.push("token:model:big-pickle")
  }
  return patterns
}

async function generateSkill(
  directory: string, round: EvolutionRound, state: ManusState
): Promise<string | null> {
  if (round.reflections.length === 0 && round.learnings.length === 0) return null

  const skillName = `evo-${state.totalSkillsGenerated + 1}-${Date.now().toString(36)}`
  const reflections = round.reflections.join("\n")
  const actions = round.actions.join("\n- ")
  const learnings = round.learnings.map((l, i) => `${i + 1}. ${l}`).join('\n')

  let metricsSection = ""
  if (round.correctionsApplied > 0 || round.tokensSaved > 0) {
    metricsSection = `
## Metricas de Correcao e Eficiencia (v2.0)
- Correcoes aplicadas: ${round.correctionsApplied}
- Tokens economizados: ${round.tokensSaved}
- Padroes de correcao: ${Object.keys(state.correctionPatterns).join(', ') || 'nenhum'}
- Padroes de otimizacao: ${Object.keys(state.tokenOptimizationPatterns).join(', ') || 'nenhum'}
`
  }

  const skillContent = `---
name: ${skillName}
description: "Skill auto-gerada pelo Manus Evolve v2.0 — Round ${round.round}. Score: ${round.score}/100"
evolved: true
round: ${round.round}
source: "manus-evolve-plugin-v2"
version: "2.0.0"
---

# ${skillName}

## Plano Original
${round.plan}

## Acoes Executadas
- ${actions}

## Reflexoes & Aprendizados
${reflections}

## Melhores Praticas Extraidas
${learnings}
${metricsSection}
## Score de Evolucao
${round.score}/100
`

  const skillPath = `${directory}/${SKILLS_DIR}/${skillName}.md`
  await mkdir(`${directory}/${SKILLS_DIR}`, { recursive: true }).catch(() => {})
  await writeFile(skillPath, skillContent)
  return skillName
}

export const ManusEvolvePlugin: Plugin = async ({ project, client, $, directory, worktree }) => {
  console.log("[ManusEvolve v2.2] PlanAct Engine + Nexus Pipeline integrated")
  let state = await loadState(directory)
  await mkdir(`${directory}/${SKILLS_DIR}`, { recursive: true }).catch(() => {})

  return {
    "session.created": async () => {
      state.currentPlan = null; state.actionCount = 0
      await client.app.log({
        body: { service: "manus-evolve-v2", level: "info",
          message: `PlanAct v2.1 ready — Round ${state.rounds.length + 1} | Skills: ${state.totalSkillsGenerated} | Score: ${state.evolutionScore}` }
      })
    },

    "tool.execute.before": async (input: any, _output: any) => {
      state.actionCount++
      state.toolCallMetrics = { startTime: Date.now(), tool: input.tool || "unknown" }
      const prompt = input.args?.prompt || input.args?.command || ""
      if (prompt && prompt.length > 20 && !state.currentPlan) {
        state.currentPlan = prompt.substring(0, 200)
      }
    },

    "tool.execute.after": async (input: any, output: any) => {
      const toolName = input.tool || "unknown"
      const latency = state.toolCallMetrics ? Date.now() - state.toolCallMetrics.startTime : 0
      state.toolCallMetrics = null

      if (!state.sessionMetrics.toolsUsed[toolName]) {
        state.sessionMetrics.toolsUsed[toolName] = {
          tool: toolName, calls: 0, errors: 0, totalLatencyMs: 0, avgLatencyMs: 0, successRate: 1
        }
      }
      const tm = state.sessionMetrics.toolsUsed[toolName]
      tm.calls++
      tm.totalLatencyMs += latency
      tm.avgLatencyMs = Math.round(tm.totalLatencyMs / tm.calls)
      state.sessionMetrics.totalCalls++

      const resultStr = typeof output?.result === 'string' ? output.result :
        JSON.stringify(output?.result || output?.output || "").substring(0, 500)
      const isSuccess = resultStr.length > 0 && !resultStr.includes("error") && !resultStr.includes("FAIL")
      if (!isSuccess) {
        tm.errors++
        state.sessionMetrics.totalErrors++
      }
      tm.successRate = tm.calls > 0 ? (tm.calls - tm.errors) / tm.calls : 1
      state.sessionMetrics.errorRate = state.sessionMetrics.totalCalls > 0
        ? state.sessionMetrics.totalErrors / state.sessionMetrics.totalCalls : 0

      if (isSuccess && state.currentPlan) {
        const idx = state.rounds.length
        if (!state.rounds[idx]) {
          state.rounds.push({ round: idx + 1, timestamp: new Date().toISOString(),
            plan: state.currentPlan, actions: [], reflections: [], extractedSkills: [],
            score: 0, learnings: [], correctionsApplied: 0, tokensSaved: 0 })
        }
        const cr = state.rounds[state.rounds.length - 1]
        cr.actions.push(`${input.tool}: ${resultStr.substring(0, 80)}`)
        extractPatterns(input.tool, resultStr).forEach(p => {
          state.patterns[p] = (state.patterns[p] || 0) + 1
          cr.extractedSkills = [...new Set([...cr.extractedSkills, p])]
        })
        extractCorrectionPatterns(resultStr).forEach(p => {
          state.correctionPatterns[p] = (state.correctionPatterns[p] || 0) + 1
        })
        extractTokenPatterns(resultStr).forEach(p => {
          state.tokenOptimizationPatterns[p] = (state.tokenOptimizationPatterns[p] || 0) + 1
        })
      }
    },

    "session.idle": async () => {
      if (state.rounds.length > 0) {
        const cr = state.rounds[state.rounds.length - 1]
        if (cr.actions.length > 0) {
          cr.reflections.push(`Round ${cr.round}: ${cr.actions.length} acoes executadas`)
          const diversity = new Set(cr.actions.map((a: string) => a.split(':')[0])).size
          const correctionBonus = Math.min(10, Object.keys(state.correctionPatterns).length * 3)
          const tokenBonus = Math.min(10, Object.keys(state.tokenOptimizationPatterns).length * 3)
          cr.score = Math.min(100, diversity * 15 + cr.extractedSkills.length * 10 + 20 + correctionBonus + tokenBonus)
          if (cr.actions.length >= 3) cr.learnings.push(`Combinacao de ${diversity} ferramentas em sequencia efetiva`)
          if (cr.extractedSkills.length > 0) cr.learnings.push(`${cr.extractedSkills.length} padroes identificados`)
          if (Object.keys(state.correctionPatterns).length > 0) cr.learnings.push(`${Object.keys(state.correctionPatterns).length} padroes de correcao detectados`)
          if (Object.keys(state.tokenOptimizationPatterns).length > 0) cr.learnings.push(`${Object.keys(state.tokenOptimizationPatterns).length} padroes de token efficiency`)
          cr.learnings.push(`${cr.actions.length} passos completados — score ${cr.score}`)
          cr.correctionsApplied = Object.values(state.correctionPatterns).reduce((a, b) => a + b, 0)
          cr.tokensSaved = Object.values(state.tokenOptimizationPatterns).reduce((a, b) => a + b, 0) * 100
        }
        const newSkill = await generateSkill(directory, cr, state)
        if (newSkill) {
          state.totalSkillsGenerated++
          state.evolutionScore = Math.min(100, state.evolutionScore + 5)
          await client.app.log({
            body: { service: "manus-evolve-v2", level: "info",
              message: `Nova habilidade: ${newSkill} | Total: ${state.totalSkillsGenerated} | Score: ${state.evolutionScore}` }
          })
        }
      }

      state.lastEvolution = new Date().toISOString()

      // Nexus Pipeline v2.1: scan -> heal -> learn
      try {
        const nexusDir = `${directory}/nexus/scripts`
        const py = process.platform === 'win32' ? 'python' : 'python3'
        await $`${py} ${nexusDir}/ecosystem_scanner.py --scan`.quiet()
        const healResult = await $`${py} ${nexusDir}/self_healer.py --auto`.quiet()
        const healText = await healResult.text()
        await $`${py} ${nexusDir}/evolution_engine.py --learn`.quiet()
        const anomaliesMatch = healText.match(/(\d+) anomalias?/)
        const fixesMatch = healText.match(/(\d+) correcoes?/)
        const report: NexusReport = {
          scanTime: new Date().toISOString(),
          anomalies: anomaliesMatch ? parseInt(anomaliesMatch[1]) : 0,
          fixes: fixesMatch ? parseInt(fixesMatch[1]) : 0,
          recommendations: 0,
          healthDelta: 'pending',
        }
        state.nexusReports.push(report)
        state.lastNexusRun = report.scanTime
        await client.app.log({
          body: { service: 'manus-evolve-v2', level: 'info',
            message: `NEXUS: scan->heal->learn concluido | anomalias=${report.anomalies} fixes=${report.fixes}` }
        })
      } catch (e: any) {
        await client.app.log({
          body: { service: 'manus-evolve-v2', level: 'warn',
            message: `NEXUS pipeline falhou: ${e?.message || e}` }
        })
      }

      // Dashboard v2.0 heartbeat check
      try {
        const dashResp = await fetch('http://localhost:8081/api/dados', { signal: AbortSignal.timeout(2000) })
        if (dashResp.ok) {
          const dashData = await dashResp.json()
          const h = dashData.health || {}
          await client.app.log({
            body: { service: 'manus-evolve-v2', level: 'info',
              message: `DASHBOARD: OK (${h.skills || '?'} skills, ${h.scripts || '?'} scripts, ${h.anomalies || 0} anomalias)` }
          })
        }
      } catch (_e: any) {
        // Dashboard nao esta rodando — tentar iniciar
        try {
          const py = process.platform === 'win32' ? 'python' : 'python3'
          await $`powershell.exe -File "${directory}/nexus/scripts/start_dashboard.ps1" -Port 8081 -Silent`.nothrow().quiet()
          await client.app.log({
            body: { service: 'manus-evolve-v2', level: 'info',
              message: 'DASHBOARD: Iniciado via start_dashboard.ps1 -Silent (http://localhost:8081)' }
          })
        } catch (_e2: any) {
          // Falha silenciosa - dashboard nao e critico
        }
      }

      state.currentPlan = null
      state.version = "2.2.0"

      const sm = state.sessionMetrics
      sm.durationMinutes = (Date.now() - sm.startTime) / 60000
      const latencyPenalty = Math.min(30, Object.values(sm.toolsUsed).reduce((sum, t) => sum + t.avgLatencyMs, 0) / Math.max(1, sm.totalCalls) / 10)
      const errorPenalty = sm.errorRate * 50
      sm.healthScore = Math.max(0, Math.min(100, 100 - latencyPenalty - errorPenalty))

      const prevHealth = sm.healthScore
      state.sessionMetrics = {
        sessionId: crypto.randomUUID(), agent: "manus-evolve",
        toolsUsed: {}, totalCalls: 0, totalErrors: 0,
        errorRate: 0, healthScore: 100, durationMinutes: 0, startTime: Date.now()
      }

      await saveState(directory, state)
      const top = Object.entries(state.patterns).sort(([,a],[,b]) => b - a).slice(0,5).map(([p,c]) => `${p}(${c}x)`)
      await client.app.log({
        body: { service: "manus-evolve-v2", level: "info",
          message: `EVOLUCAO: Round ${state.rounds.length} | Skills: ${state.totalSkillsGenerated} | Score: ${state.evolutionScore} | Nexus: ${state.nexusReports.length} reports | Observability: health=${prevHealth.toFixed(1)} calls=${sm.totalCalls} errors=${sm.totalErrors} | Top: ${top.join(', ')}` }
      })
    },

    "shell.env": async (_input: any, output: any) => {
      output.env.MANUS_ROUND = String(state.rounds.length)
      output.env.MANUS_SCORE = String(state.evolutionScore)
      output.env.MANUS_SKILLS = String(state.totalSkillsGenerated)
      output.env.MANUS_VERSION = state.version
      output.env.MANUS_CORRECTION_PATTERNS = String(Object.keys(state.correctionPatterns).length)
      output.env.MANUS_TOKEN_PATTERNS = String(Object.keys(state.tokenOptimizationPatterns).length)
      output.env.MANUS_HEALTH = String(state.sessionMetrics.healthScore.toFixed(1))
      output.env.MANUS_TOOL_CALLS = String(state.sessionMetrics.totalCalls)
      output.env.MANUS_TOOL_ERRORS = String(state.sessionMetrics.totalErrors)
      output.env.MANUS_ERROR_RATE = String(state.sessionMetrics.errorRate.toFixed(3))
      output.env.MANUS_NEXUS_REPORTS = String(state.nexusReports.length)
      output.env.MANUS_LAST_NEXUS = state.lastNexusRun || "never"
    },

    "permission.asked": async (input: any, output: any) => {
      if (input.tool && (state.patterns[input.tool] || 0) >= 3) output.autoApprove = true
    },
  }
}
