// SAÃDA OBRIGATÃ“RIA: PORTUGUÃŠS BRASILEIRO FORMAL

/**
 * plugin.test.ts â€” Testes unitÃ¡rios para plugins OpenCode
 *
 * Pipeline: import interfaces => mock Plugin context => test each hook
 *
 * Uso: bun test plugins/plugin.test.ts
 */
import { describe, expect, test, mock } from "bun:test"
import {
  scoreToStatus,
  createSessionMetrics,
  writePluginState,
} from "./interfaces"

// ============================================================
// Mocks
// ============================================================

const mockDirectory = import.meta.dir

const mockPluginContext = () => ({
  project: { name: "test-project" },
  client: {
    app: {
      log: mock(async (_msg: any) => {}),
    },
  },
  directory: mockDirectory,
  worktree: { name: "main" },
} as any)

// ============================================================
// interfaces.ts
// ============================================================

describe("interfaces.ts", () => {
  test("scoreToStatus: active >= 90", () => {
    expect(scoreToStatus(100)).toBe("active")
    expect(scoreToStatus(90)).toBe("active")
  })

  test("scoreToStatus: degraded 60-89", () => {
    expect(scoreToStatus(89)).toBe("degraded")
    expect(scoreToStatus(60)).toBe("degraded")
  })

  test("scoreToStatus: offline 1-59", () => {
    expect(scoreToStatus(59)).toBe("offline")
    expect(scoreToStatus(1)).toBe("offline")
  })

  test("scoreToStatus: unknown 0", () => {
    expect(scoreToStatus(0)).toBe("unknown")
  })

  test("createSessionMetrics: generates UUID", () => {
    const sm = createSessionMetrics("test-agent")
    expect(sm.agent).toBe("test-agent")
    expect(sm.sessionId).toBeDefined()
    expect(sm.sessionId.length).toBeGreaterThan(0)
    expect(sm.totalCalls).toBe(0)
    expect(sm.healthScore).toBe(100)
  })

  test("writePluginState: writes and reads back", async () => {
    const tmp = mockDirectory + "/../../temp/plugin-test-" + Date.now()
    const { mkdir } = await import("fs/promises")
    await mkdir(tmp, { recursive: true }).catch(() => {})

    const data = { hello: "world", count: 42 }
    await writePluginState(tmp, "test-state.json", data)

    const { readFile } = await import("fs/promises")
    const content = await readFile(tmp + "/.evolve/test-state.json", "utf-8")
    const parsed = JSON.parse(content)
    expect(parsed.hello).toBe("world")
    expect(parsed.count).toBe(42)
  })
})

// ============================================================
// EcosystemSyncPlugin -- unit tests
// ============================================================

describe("EcosystemSyncPlugin", () => {
  test("plugin module loads and exports", async () => {
    const mod = await import("./ecosystem-sync")
    expect(mod.EcosystemSyncPlugin).toBeDefined()
    expect(typeof mod.EcosystemSyncPlugin).toBe("function")
  })

  test("plugin factory returns hook object", async () => {
    const mod = await import("./ecosystem-sync")
    const ctx = mockPluginContext()
    const instance = await mod.EcosystemSyncPlugin(ctx as any)
    expect(instance).toBeDefined()
    expect(instance["session.created"]).toBeDefined()
    expect(instance["tool.execute.before"]).toBeDefined()
    expect(instance["tool.execute.after"]).toBeDefined()
    expect(instance["session.idle"]).toBeDefined()
    expect(instance["session.error"]).toBeDefined()
    expect(instance["shell.env"]).toBeDefined()
  })

  test("session.created runs without throwing", async () => {
    const mod = await import("./ecosystem-sync")
    const ctx = mockPluginContext()
    const instance = await mod.EcosystemSyncPlugin(ctx as any)
    await expect(instance["session.created"]()).resolves.toBeUndefined()
  })

  test("shell.env injects environment variables", async () => {
    const mod = await import("./ecosystem-sync")
    const ctx = mockPluginContext()
    const instance = await mod.EcosystemSyncPlugin(ctx as any)
    const output = { env: {} as Record<string, string> }
    await instance["shell.env"]({}, output)
    expect(output.env.ECOSYSTEM_HEALTH).toBeDefined()
    expect(output.env.ECOSYSTEM_VERSION).toBe("3.5.0")
    expect(output.env.ECOSYSTEM_CJK_CORRECTOR).toBeDefined()
  })
})

// ============================================================
// ManusEvolvePlugin -- unit tests
// ============================================================

describe("ManusEvolvePlugin", () => {
  test("plugin module loads and exports", async () => {
    const mod = await import("./manus-evolve")
    expect(mod.ManusEvolvePlugin).toBeDefined()
    expect(typeof mod.ManusEvolvePlugin).toBe("function")
  })

  test("plugin factory returns hook object", async () => {
    const mod = await import("./manus-evolve")
    const ctx = mockPluginContext()
    const instance = await mod.ManusEvolvePlugin(ctx as any)
    expect(instance).toBeDefined()
    expect(instance["session.created"]).toBeDefined()
    expect(instance["tool.execute.before"]).toBeDefined()
    expect(instance["tool.execute.after"]).toBeDefined()
    expect(instance["session.idle"]).toBeDefined()
    expect(instance["shell.env"]).toBeDefined()
    expect(instance["permission.asked"]).toBeDefined()
  })

  test("session.created runs without throwing", async () => {
    const mod = await import("./manus-evolve")
    const ctx = mockPluginContext()
    const instance = await mod.ManusEvolvePlugin(ctx as any)
    await expect(instance["session.created"]()).resolves.toBeUndefined()
  })

  test("session.idle: no crash with zero rounds", async () => {
    const mod = await import("./manus-evolve")
    const ctx = mockPluginContext()
    const instance = await mod.ManusEvolvePlugin(ctx as any)
    await expect(instance["session.idle"]()).resolves.toBeUndefined()
  })
})
