# OpenCode Ecosystem

<div align="center">
  <img src="diagrams/architecture-overview.svg" alt="Arquitetura do Ecossistema OpenCode" width="800"/>
</div>

---

O **OpenCode Ecosystem** é uma arquitetura multiagente evolutiva desenhada para automatizar processos complexos de desenvolvimento, pesquisa acadêmica (Qualis A1) e engenharia de software no Windows (via WSL2). Integrado ao OpenCode (Antigravity), atua como um hub centralizado.

Atualmente na **v4.6.1**, o ecossistema orquestra:
- 🤖 **125 Agentes Especializados** catalogados
- 🔌 **41 Servidores MCP (Model Context Protocol)** configurados
- 🎯 **106 Skills Ativas** com foco em raciocínio avançado
- 🧠 **Nexus NMA v6.2 (Multi-Agent Framework)** com 120+ barreiras de sincronização
- 🧬 **Loop de Evolução Contínua** (AutoEvolve / Manus Evolve)

## 📖 Documentação Técnica Completa

A documentação exaustiva e de altíssimo nível da arquitetura encontra-se no arquivo central:
👉 **[OPENCODE_ECOSYSTEM.md](OPENCODE_ECOSYSTEM.md)**

Nele você encontrará:
- Integração e fluxo dos **18 Padrões MiroFish / BettaFish**
- Pipelines de Validação (PhD Auditor)
- Pipeline Acadêmico (MASWOS)
- Camada Universal de Dados (DataOrchestrator) e Ecosystem Hooks

---

## 🛠️ Como Instalar e Rodar no Windows / WSL

### 1. Pré-requisitos
Certifique-se de que o **WSL2 (Ubuntu)** esteja instalado no Windows.

### 2. Inicializando o Ecossistema
Abra o PowerShell como Administrador e execute:
```powershell
.\start_ecosystem.ps1
```
*(Ele cuidará de iniciar os serviços essenciais, como Ollama, atualizar os status do Git e iniciar o OpenCode).*

### 3. Executando Auditorias (TDD)
O repositório é orientado a testes. Para auditar o ecossistema e verificar a saúde dos MCPs no WSL:
```bash
./tests/test_environment.sh
```

---

## 📁 Estrutura do Repositório

- `agents/` — Definições e diretrizes de agentes autônomos (incluindo o orquestrador master `@marceloclaro`).
- `core/` e `nexus/` — Lógica do orquestrador NMA v6 e camada de Injeção de Dependências.
- `diagrams/` — Diagramas arquiteturais SVG auto-mantidos pelo Reversa Framework.
- `docs/` — Documentação complementar técnica (Software Design Document - SDD).
- `plugins/` — Plugins TypeScript do ecossistema integrados (ex: `manus-evolve`).
- `scripts/` — Scripts bash e python de automação.
- `skills/` — Repositório com as 104+ capacidades cognitivas categorizadas.
- `tests/` — Scripts de teste unitários e validação contínua (TDD).

---

> Desenvolvido no modelo de Governança Autônoma Assistida e mantido dinamicamente.
