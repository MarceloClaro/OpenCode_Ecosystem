// Plugin: auto-discovery v1.0
// Descobre automaticamente novas skills, MCPs e agentes no ecossistema
import type { Plugin } from "@opencode-ai/plugin"
import { readdir, writeFile, mkdir } from "fs/promises"
import { join } from "path"

export const plugin: Plugin = {
  id: "auto-discovery",
  name: "Auto Discovery Engine",
  version: "1.0.0",
  description: "Descobre automaticamente novos componentes no ecossistema",

  async init(ctx) {
    const discoveryPath = ".evolve/discoveries.json"
    
    const discover = async () => {
      const skillsDir = join(process.cwd(), "skills")
      const agentsDir = join(process.cwd(), "agents")
      
      let skillsCount = 0
      let agentsCount = 0
      
      try {
        const skillFiles = await readdir(skillsDir, { recursive: true })
        skillsCount = skillFiles.filter(f => f.endsWith("SKILL.md")).length
      } catch {}
      
      try {
        const agentFiles = await readdir(agentsDir)
        agentsCount = agentFiles.filter(f => f.endsWith(".md")).length
      } catch {}

      const discoveries = {
        timestamp: new Date().toISOString(),
        skills_found: skillsCount,
        agents_found: agentsCount,
        new_since_last: 0,
      }
      
      await mkdir(".evolve", { recursive: true })
      await writeFile(discoveryPath, JSON.stringify(discoveries, null, 2), "utf-8")
    }

    await discover()
    setInterval(discover, 600_000)
    console.log("[auto-discovery] Iniciado — scan a cada 10min")
  },
}
