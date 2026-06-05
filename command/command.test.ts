// SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL

/**
 * command.test.ts — Testes para o CommandDispatcher
 *
 * Uso: bun test command/command.test.ts
 */
import { describe, expect, test, beforeAll } from "bun:test"
import { CommandDispatcher } from "./dispatcher"

const COMMAND_DIR = import.meta.dir
let dispatcher: CommandDispatcher

beforeAll(async () => {
  dispatcher = new CommandDispatcher(COMMAND_DIR, { commandDir: COMMAND_DIR })
  await dispatcher.load()
})

// ============================================================
// Loading
// ============================================================

describe("CommandDispatcher.load()", () => {
  test("loads all 14 commands", () => {
    expect(dispatcher.count).toBe(14)
  })

  test("every command has a name and description", () => {
    for (const cmd of dispatcher.list()) {
      expect(cmd.name).toBeDefined()
      expect(cmd.name.length).toBeGreaterThan(0)
      expect(cmd.description).toBeDefined()
      expect(cmd.description.length).toBeGreaterThan(0)
    }
  })
})

// ============================================================
// Finding by exact trigger
// ============================================================

describe("CommandDispatcher.find()", () => {
  test("finds by slash prefix: /reversa", () => {
    const cmd = dispatcher.find("/reversa")
    expect(cmd).toBeDefined()
    expect(cmd!.name).toBe("reversa")
  })

  test("finds by name: reversa", () => {
    const cmd = dispatcher.find("reversa")
    expect(cmd).toBeDefined()
    expect(cmd!.name).toBe("reversa")
  })

  test("finds by alternate trigger: plan", () => {
    const cmd = dispatcher.find("/plan")
    expect(cmd).toBeDefined()
    expect(cmd!.name).toBe("plan")
  })

  test("finds quantum command", () => {
    const cmd = dispatcher.find("quantum")
    expect(cmd).toBeDefined()
    expect(cmd!.name).toBe("quantum")
  })

  test("finds auto command", () => {
    const cmd = dispatcher.find("auto")
    expect(cmd).toBeDefined()
    expect(cmd!.name).toBe("auto")
  })

  test("finds commit command", () => {
    const cmd = dispatcher.find("commit")
    expect(cmd).toBeDefined()
    expect(cmd!.name).toBe("commit")
  })

  test("finds execute command", () => {
    const cmd = dispatcher.find("/execute")
    expect(cmd).toBeDefined()
    expect(cmd!.name).toBe("execute")
  })
})

// ============================================================
// Fuzzy search
// ============================================================

describe("CommandDispatcher fuzzy search", () => {
  test("finds by partial: 'reverse' matches reversa", () => {
    const cmd = dispatcher.find("reverse")
    expect(cmd).toBeDefined()
    expect(cmd!.name).toBe("reversa")
  })

  test("finds by alternate: 'evolution' matches evolve", () => {
    const cmd = dispatcher.find("evolution")
    expect(cmd).toBeDefined()
    expect(cmd!.name).toBe("evolve")
  })
})

// ============================================================
// New session requirements
// ============================================================

describe("New session requirements", () => {
  test("plan requires new session", () => {
    const cmd = dispatcher.find("/plan")
    expect(cmd!.requiresNewSession).toBeTrue()
  })

  test("research requires new session", () => {
    const cmd = dispatcher.find("/research")
    expect(cmd!.requiresNewSession).toBeTrue()
  })

  test("reversa does not require new session", () => {
    const cmd = dispatcher.find("/reversa")
    expect(cmd!.requiresNewSession).toBeFalse()
  })

  test("commit does not require new session", () => {
    const cmd = dispatcher.find("/commit")
    expect(cmd!.requiresNewSession).toBeFalse()
  })
})

// ============================================================
// Not found
// ============================================================

describe("Not found", () => {
  test("returns undefined for unknown command", () => {
    const cmd = dispatcher.find("nonexistent-command-xyz")
    expect(cmd).toBeUndefined()
  })
})
