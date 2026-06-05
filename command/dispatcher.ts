// SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL

/**
 * dispatcher.ts — Unified slash command dispatcher for OpenCode (v1.0)
 *
 * Carrega metadados dos 14 comandos markdown em command/ e fornece
 * registro centralizado com roteamento por nome.
 *
 * Uso:
 *   import { CommandDispatcher } from "./dispatcher"
 *   const dispatch = new CommandDispatcher(directory)
 *   const cmd = dispatch.find("reversa")
 *   console.log(cmd?.description)
 */
import { readFile, readdir } from "fs/promises"
import { join } from "path"

// ============================================================
// Types
// ============================================================

export interface CommandMeta {
  /** Nome do comando (sem /), ex: "reversa" */
  name: string
  /** Arquivo markdown de origem */
  sourceFile: string
  /** Descrição curta do comando */
  description: string
  /** Gatilhos que ativam este comando */
  triggers: string[]
  /** Se comando requer uma sessão nova */
  requiresNewSession: boolean
}

export interface DispatcherOptions {
  /** Diretório raiz onde está command/ */
  commandDir?: string
}

// ============================================================
// Command Registry
// ============================================================

const TRIGGER_MAP: Record<string, string[]> = {
  auto:         ["/auto", "auto", "autonomous"],
  commit:       ["/commit", "commit"],
  devcontainer: ["/devcontainer", "devcontainer"],
  evolve:       ["/evolve", "evolve", "evolution"],
  execute:      ["/execute", "execute"],
  plan:         ["/plan", "plan"],
  quantum:      ["/quantum", "quantum"],
  research:     ["/research", "research"],
  reversa:      ["/reversa", "reversa", "reverse engineering", "iniciar análise", "engenharia reversa"],
  review:       ["/review", "review"],
  ticket:       ["/ticket", "ticket"],
  workspaces:   ["/workspaces", "workspaces"],
  worktree:     ["/worktree", "worktree"],
  "ws-review":  ["/ws-review", "ws-review", "ws review"],
}

const NEW_SESSION_COMMANDS = new Set(["plan", "research", "execute"])

// ============================================================
// Frontmatter parser
// ============================================================

function parseFrontmatter(content: string): Record<string, string> {
  const meta: Record<string, string> = {}
  const match = content.match(/^---\n([\s\S]*?)\n---/)
  if (!match) return meta

  for (const line of match[1].split("\n")) {
    const idx = line.indexOf(": ")
    if (idx > 0) {
      const key = line.slice(0, idx).trim()
      const val = line.slice(idx + 2).trim()
      meta[key] = val
    }
  }
  return meta
}

// ============================================================
// Dispatcher
// ============================================================

export class CommandDispatcher {
  private commands: Map<string, CommandMeta> = new Map()
  private triggerIndex: Map<string, string> = new Map()
  private commandDir: string
  private loaded = false

  constructor(directory: string, options?: DispatcherOptions) {
    this.commandDir = options?.commandDir ?? join(directory, "command")
  }

  /** Carrega todos os comandos do diretório command/ */
  async load(): Promise<CommandMeta[]> {
    const files = await readdir(this.commandDir)
    const mdFiles = files.filter(f => f.endsWith(".md")).sort()

    for (const file of mdFiles) {
      const name = file.replace(/\.md$/, "")
      const content = await readFile(join(this.commandDir, file), "utf-8")
      const frontmatter = parseFrontmatter(content)
      const description = frontmatter["description"] || "N/A"
      const triggers = TRIGGER_MAP[name] || [`/${name}`, name]

      const meta: CommandMeta = {
        name,
        sourceFile: file,
        description,
        triggers,
        requiresNewSession: NEW_SESSION_COMMANDS.has(name),
      }

      this.commands.set(name, meta)
      for (const trigger of triggers) {
        this.triggerIndex.set(trigger.toLowerCase(), name)
      }
    }

    this.loaded = true
    return Array.from(this.commands.values())
  }

  /** Encontra um comando por nome, trigger, ou parte do texto */
  find(input: string): CommandMeta | undefined {
    if (!this.loaded) return undefined

    const normalized = input.toLowerCase().trim()

    // Try exact trigger match
    const cmdName = this.triggerIndex.get(normalized)
    if (cmdName) return this.commands.get(cmdName)

    // Try fuzzy: input contains trigger or vice versa
    for (const [trigger, name] of this.triggerIndex) {
      if (normalized.includes(trigger) || trigger.includes(normalized)) {
        return this.commands.get(name)
      }
    }

    return undefined
  }

  /** Lista todos os comandos registrados */
  list(): CommandMeta[] {
    return Array.from(this.commands.values())
  }

  /** Retorna contagem de comandos carregados */
  get count(): number {
    return this.commands.size
  }
}

// ============================================================
// Default instance factory
// ============================================================

let defaultDispatcher: CommandDispatcher | null = null

export async function getDispatcher(directory: string): Promise<CommandDispatcher> {
  if (!defaultDispatcher) {
    defaultDispatcher = new CommandDispatcher(directory)
    await defaultDispatcher.load()
  }
  return defaultDispatcher
}
