// Plugin: event-aggregator v1.0
// Agrega eventos do ecossistema para analise e alertas
import type { Plugin } from "@opencode-ai/plugin"
import { writeFile, mkdir } from "fs/promises"

interface EcosystemEvent {
  type: string
  timestamp: string
  component: string
  status: string
}

export const plugin: Plugin = {
  id: "event-aggregator",
  name: "Event Aggregator",
  version: "1.0.0",
  description: "Agrega eventos do ecossistema para analise unificada",

  async init(ctx) {
    const logPath = ".evolve/events.jsonl"
    await mkdir(".evolve", { recursive: true })

    const log = async (event: EcosystemEvent) => {
      const line = JSON.stringify(event) + "\n"
      await writeFile(logPath, line, { flag: "a" }).catch(() => {})
    }

    // Log inicial
    await log({ type: "plugin_init", timestamp: new Date().toISOString(), component: "event-aggregator", status: "active" })
    console.log("[event-aggregator] Iniciado — agregando eventos do ecossistema")
  },
}
