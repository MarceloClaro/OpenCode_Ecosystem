import type { Plugin } from "@opencode-ai/plugin"
import { readdir, writeFile, mkdir } from "fs/promises"
import { join } from "path"

export const AutoDiscoveryPlugin: Plugin = async ({ project, client, $, directory, worktree }) => {
  const discoveryPath = ".evolve/discoveries.json"
  
  const discover = async () => {
    const skillsDir = join(directory, "skills")
    const agentsDir = join(directory, "agents")
    
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
    
    await mkdir(`${directory}/.evolve`, { recursive: true }).catch(() => {})
    await writeFile(join(directory, discoveryPath), JSON.stringify(discoveries, null, 2), "utf-8")
  }

  await discover()
  // Run discovery periodically in background
  const interval = setInterval(discover, 600_000)
  console.log("[auto-discovery] Iniciado — scan a cada 10min")

  return {
    "session.idle": async () => {
      await discover()
    }
  }
}
