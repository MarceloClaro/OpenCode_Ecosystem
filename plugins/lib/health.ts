// SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL
// Toda resposta DEVE ser em português do Brasil formal.
// Modelo: big-pickle (OpenCode Zen)

/**
 * health.ts — Plugin Health Check Runtime (v1.0)
 *
 * Fornece endpoint de health check para plugins OpenCode.
 * Pode ser usado via CLI ou integrado ao ecosystem-sync.
 *
 * Uso:
 *   bun run plugins/health.ts          # scan local
 *   bun run plugins/health.ts --watch  # watch mode (a cada 60s)
 */
import { readPluginState, type ComponentHealth, type HealthStatus } from "./interfaces"

interface HealthReport {
  timestamp: string
  overall: {
    status: HealthStatus
    score: number
    activeCount: number
    totalCount: number
  }
  components: ComponentHealth[]
  degraded: ComponentHealth[]
  offline: ComponentHealth[]
}

async function scanHealth(directory: string): Promise<HealthReport> {
  const evolveDir = directory + "/.evolve"
  const { readFile } = await import("fs/promises")

  let components: ComponentHealth[] = []
  try {
    const stateRaw = await readFile(evolveDir + "/ecosystem-state.json", "utf-8")
    const state = JSON.parse(stateRaw)
    components = [
      ...Object.values(state.mcps || {}),
      ...Object.values(state.agents || {}),
      ...Object.values(state.skills || {}),
      ...Object.values(state.plugins || {}),
      ...Object.values(state.commands || {}),
      ...Object.values(state.correctors || {}),
    ] as ComponentHealth[]
  } catch {
    // No state file yet — scan plugins directory
    const { readdir } = await import("fs/promises")
    const files = (await readdir(directory)).filter(f => f.endsWith(".ts") && f !== "interfaces.ts" && f !== "plugin.test.ts")
    components = files.map(f => ({
      name: f.replace(/\.ts$/, ""),
      type: "plugin" as const,
      status: "unknown" as HealthStatus,
      score: 0,
      lastCheck: null,
      errorCount: 0,
      latency: null,
    }))
  }

  const activeCount = components.filter(c => c.status === "active").length
  const degraded = components.filter(c => c.status === "degraded")
  const offline = components.filter(c => c.status === "offline" || c.status === "unknown")
  const avgScore = components.length > 0
    ? Math.round(components.reduce((s, c) => s + c.score, 0) / components.length)
    : 0

  let overallStatus: HealthStatus = "active"
  if (avgScore < 60 || offline.length > 0) overallStatus = "offline"
  else if (avgScore < 85 || degraded.length > 0) overallStatus = "degraded"

  return {
    timestamp: new Date().toISOString(),
    overall: {
      status: overallStatus,
      score: avgScore,
      activeCount,
      totalCount: components.length,
    },
    components,
    degraded,
    offline,
  }
}

// ============================================================
// CLI entry point
// ============================================================

if (import.meta.main) {
  const directory = process.argv[2] || import.meta.dir
  const watchMode = process.argv.includes("--watch")

  async function printReport() {
    const report = await scanHealth(directory)
    console.log("")
    console.log("=== Plugin Health Report ===")
    console.log("Timestamp: " + report.timestamp)
    console.log("Overall:   " + report.overall.status + " (" + report.overall.score + "/100)")
    console.log("Active:    " + report.overall.activeCount + "/" + report.overall.totalCount)
    console.log("")

    if (report.degraded.length > 0) {
      console.log("!! DEGRADED (" + report.degraded.length + "):")
      report.degraded.forEach(c => console.log("   - " + c.name + " (" + c.score + ")"))
      console.log("")
    }
    if (report.offline.length > 0) {
      console.log("!! OFFLINE (" + report.offline.length + "):")
      report.offline.forEach(c => console.log("   - " + c.name + " (" + c.score + ")"))
      console.log("")
    }
  }

  await printReport()

  if (watchMode) {
    console.log("Watch mode: re-checking every 60s...")
    setInterval(printReport, 60_000)
  }
}

export { scanHealth, type HealthReport }
