// SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL
// Toda resposta DEVE ser em português do Brasil formal.
// Modelo: big-pickle (OpenCode Zen)

/**
 * interfaces.ts — Shared type definitions for OpenCode plugins (v1.0)
 *
 * Extraído do ecossistema Reversa, consolida interfaces comuns entre
 * EcosystemSync v3.5 e ManusEvolve v2.2.
 *
 * Uso: import type { PluginManifest, ComponentHealth, ... } from "./interfaces"
 */
import type { Plugin } from "@opencode-ai/plugin"

// ============================================================
// Plugin Manifest
// ============================================================

export interface PluginManifest {
  name: string
  version: string
  author?: string
  description: string
  hooks: string[]
  dependencies: string[]
}

// ============================================================
// Component Health (EcosystemSync origin)
// ============================================================

export type ComponentType = "mcp" | "skill" | "agent" | "plugin" | "command" | "corrector"
export type HealthStatus = "active" | "degraded" | "offline" | "unknown"

export interface ComponentHealth {
  name: string
  type: ComponentType
  status: HealthStatus
  score: number
  lastCheck: string | null
  errorCount: number
  latency: number | null
  category?: string
}

export function scoreToStatus(score: number): HealthStatus {
  if (score >= 90) return "active"
  if (score >= 60) return "degraded"
  if (score > 0) return "offline"
  return "unknown"
}

// ============================================================
// Token Efficiency (cross-plugin concern)
// ============================================================

export interface TokenEfficiencyState {
  contextEncoding: "chinese-simplified"
  outputLanguage: "pt-br-formal"
  model: string
  modelProvider: string
  contextTokensSaved: number
  filesWithHeader: number
  totalSystemFiles: number
  headerCoverage: number
  cjkCorrectorActive: boolean
}

// ============================================================
// Tool Metrics (ManusEvolve origin)
// ============================================================

export interface ToolMetric {
  tool: string
  calls: number
  errors: number
  totalLatencyMs: number
  avgLatencyMs: number
  successRate: number
}

export interface SessionMetrics {
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

export function createSessionMetrics(agent: string): SessionMetrics {
  return {
    sessionId: crypto.randomUUID(),
    agent,
    toolsUsed: {},
    totalCalls: 0,
    totalErrors: 0,
    errorRate: 0,
    healthScore: 100,
    durationMinutes: 0,
    startTime: Date.now(),
  }
}

// ============================================================
// Evolution Round (ManusEvolve origin)
// ============================================================

export interface EvolutionRound {
  round: number
  timestamp: string
  plan: string
  actions: string[]
  reflections: string[]
  extractedSkills: string[]
  score: number
  learnings: string[]
  correctionsApplied: number
  tokensSaved: number
}

// ============================================================
// Cross-Validation (EcosystemSync origin)
// ============================================================

export interface CrossValidationEntry {
  source: string
  target: string
  affinity: number
  updatedAt: string
}

// ============================================================
// Plugin State I/O helpers
// ============================================================

const EVOLVE_DIR = ".evolve"

/** Default mkdir+writeFile for plugin state */
export async function writePluginState<T>(
  directory: string,
  filename: string,
  state: T,
): Promise<void> {
  const path = directory + "/" + EVOLVE_DIR + "/" + filename
  const { mkdir, writeFile } = await import("fs/promises")
  await mkdir(directory + "/" + EVOLVE_DIR, { recursive: true }).catch(() => {})
  await writeFile(path, JSON.stringify(state, null, 2))
}

/** Default readFile+parse for plugin state */
export async function readPluginState<T>(directory: string, filename: string, fallback: T): Promise<T> {
  try {
    const { readFile } = await import("fs/promises")
    const content = await readFile(directory + "/" + EVOLVE_DIR + "/" + filename, "utf-8")
    return JSON.parse(content) as T
  } catch {
    return fallback
  }
}

// ============================================================
// Observability
// ============================================================

export interface ObservabilityEntry {
  timestamp: string
  event: string
  [key: string]: unknown
}

export async function logObservability(
  directory: string,
  event: string,
  data: Record<string, unknown>,
): Promise<void> {
  const entry: ObservabilityEntry = {
    timestamp: new Date().toISOString(),
    event,
    ...data,
  }
  try {
    const { mkdir, writeFile } = await import("fs/promises")
    await mkdir(directory + "/" + EVOLVE_DIR, { recursive: true }).catch(() => {})
    await writeFile(
      directory + "/" + EVOLVE_DIR + "/ecosystem-observability.jsonl",
      JSON.stringify(entry) + "\n",
      { flag: "a" },
    )
  } catch (err: any) {
    console.error("[interfaces] Observability log error: " + err.message)
  }
}
