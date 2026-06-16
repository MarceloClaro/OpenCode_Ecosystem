import type { Plugin } from "@opencode-ai/plugin"
import { writeFile, mkdir } from "fs/promises"
import { join } from "path"

interface EcosystemEvent {
  type: string
  timestamp: string
  component: string
  status: string
}

export const EventAggregatorPlugin: Plugin = async ({ project, client, $, directory, worktree }) => {
  const logPath = ".evolve/events.jsonl"
  await mkdir(`${directory}/.evolve`, { recursive: true }).catch(() => {})

  const log = async (event: EcosystemEvent) => {
    const line = JSON.stringify(event) + "
"
    await writeFile(join(directory, logPath), line, { flag: "a" }).catch(() => {})
  }

  await log({ type: "plugin_init", timestamp: new Date().toISOString(), component: "event-aggregator", status: "active" })
  console.log("[event-aggregator] Iniciado — agregando eventos do ecossistema")

  return {
    "session.idle": async () => {
      await log({ type: "session_idle", timestamp: new Date().toISOString(), component: "event-aggregator", status: "active" })
    }
  }
}
