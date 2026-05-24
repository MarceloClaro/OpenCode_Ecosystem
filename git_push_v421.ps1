# Script para atualizar o repositório GitHub com as mudanças da v4.2.1
Write-Host "Iniciando processo de atualização do Git..." -ForegroundColor Cyan

# Adicionando os arquivos modificados
Write-Host "Adicionando arquivos modificados..."
git add diagrams/self-healing.svg
git add diagrams/rag-strategies.svg
git add diagrams/mirofish-phd-auditor.svg
git add diagrams/mcp-architecture.svg
git add diagrams/architecture-overview.svg
git add diagrams/agent-orchestration.svg
git add diagrams/academic-pipeline.svg
git add diagrams/classification-taxonomy.svg
git add diagrams/architectural-patterns.svg
git add diagrams/subsystem-classification.svg
git add README.md
git add PROJECTS.md
git add criador-artigo/ECOSYSTEM_BRIDGE.md
git add OPENCODE_ECOSYSTEM.md
git add GETTING_STARTED.md
git add CONTRIBUTING.md
git add ROADMAP.md
git add GLOSSARY.md
git add AGENTS.md
git add AGENTS_PTBR.md
git add TUTORIALS.md

# Adicionando os agentes corrigidos
git add agents/architect.md
git add agents/debugger.md
git add agents/docs-writer.md
git add agents/optimizer.md
git add agents/security-auditor.md
git add agents/quantum-nexus-phd.md

# Verificando o status local
Write-Host "Status do repositório local:" -ForegroundColor Yellow
git status

# Commit
$commitMessage = "docs: unifica diagramas SVG e estabiliza arquivos de documentação para v4.2.1"
Write-Host "Realizando commit: $commitMessage" -ForegroundColor Green
git commit -m $commitMessage

# Push
Write-Host "Enviando alterações para o GitHub..." -ForegroundColor Green
git push origin main

Write-Host "Processo concluído com sucesso!" -ForegroundColor Cyan
