```text
 █▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀█
 █  ██████╗ ███████╗████████╗    ███████╗████████╗ █████╗ ██████╗ ████████╗   █
 █ ██╔════╝ ██╔════╝╚══██╔══╝    ██╔════╝╚══██╔══╝██╔══██╗██╔══██╗╚══██╔══╝   █
 █ ██║  ███╗█████╗     ██║       ███████╗   ██║   ███████║██████╔╝   ██║      █
 █ ██║   ██║██╔══╝     ██║       ╚════██║   ██║   ██╔══██║██╔══██╗   ██║      █
 █ ╚██████╔╝███████╗   ██║       ███████║   ██║   ██║  ██║██║  ██║   ██║      █
 █  ╚═════╝ ╚══════╝   ╚═╝       ╚══════╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝      █
 █                                                                            █
 █          INITIALIZATION DECRYPT PROTOCOL // ESTIMATED_BOOT: 10-15M         █
 █▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄█
```

### ⚡ [BOOT://TARGET_AUDIENCE] ── Para quem é este guia

Este guia destina-se a:
*   ⚡ **Pesquisadores Acadêmicos**: Que desejam gerar artigos com auditoria de qualidade (10 critérios CAPES) e debates multiagentes com verificadores simbólicos.
*   ⚡ **Desenvolvedores de IA**: Interessados em arquiteturas multiagentes, engenharia reversa automatizada e injeção dinâmica de servidores MCP.
*   ⚡ **Estudantes de Computação Quântica**: Que buscam experimentar com Variational Quantum Circuits (VQC) de 50 qubits, Quantum Machine Learning (QML) aplicado a imagens médicas e técnicas de mitigação de erros (ZNE/PEC).

Não é necessário conhecimento prévio do ecossistema. Este guia orientará desde a instalação até a primeira rodada operacional dos orquestradores.

---

### 🔌 [BOOT://PREREQUISITES] ── Requisitos do Sistema

Antes de iniciar, verifique se o seu terminal atende às seguintes especificações de grid:

| Componente | Versão Mínima | Observação / Função no Grid |
| :--- | :---: | :--- |
| **Node.js** | v22+ (LTS) | Runtime JavaScript para execução do OpenCode CLI |
| **Bun** | v1.3+ | Gerenciador de pacotes e runtime ultra-veloz do ecossistema |
| **Python** | 3.12+ | Runtime para agentes, scripts Nexus e simuladores quânticos |
| **OpenCode CLI** | 1.14+ | Interface de controle e console central do OpenCode |
| **OS Principal** | Windows 11 | Compatível nativamente via WSL2 (Ubuntu) |
| **Modelo Cloud** | `mimo-v2.5-pro` | Xiaomi MiMo API (1M contexto, Pay-as-you-go ou Token Plan) |
| **Modelo Local** | `qwen-coder-pro` | Ollama local — 100% offline, seguro e gratuito |

---

### 💾 [BOOT://DEPLOYMENT_STEP] ── Instalação Passo a Passo

#### 1. Clonar o Grid de Repositórios
```bash
git clone https://github.com/MarceloClaro/OpenCode_Ecosystem.git
cd OpenCode_Ecosystem
```

#### 2. Injetar Dependências Funcionais
O projeto utiliza o Bun para carregamento de alta velocidade. As dependências primárias cobrem `@opencode-ai/plugin` e `@types/bun`:
```bash
bun install
```

#### 3. Configurar e Validar OpenCode CLI
Certifique-se de que o CLI (versão 1.14+) esteja acessível no PATH do seu terminal:
```bash
opencode --version
# Saída esperada: 1.14.x ou superior
```

#### 4. Checar Modelos Ativos
Execute o CLI para verificar quais cérebros (locais e remotos) estão ativos no ecossistema:
```bash
opencode
/models
```
*(Isso retornará tanto os modelos em nuvem da Xiaomi MiMo quanto os modelos locais servidos via Ollama local).*

---

### 📋 [BOOT://INTEGRITY_CHECK] ── Comandos de Diagnóstico do Grid

Valide as versões instaladas no seu ambiente de execução:

| Comando de Varredura | Saída Mínima Esperada | Status |
| :--- | :---: | :---: |
| `node --version` | `v25.x.x` | 🟢 OK |
| `bun --version` | `1.3.x` | 🟢 OK |
| `python --version` | `Python 3.12.x` | 🟢 OK |
| `opencode --version` | `1.14.x` ou superior | 🟢 OK |

---

### 🕹️ [BOOT://OPERATIONAL_COMMANDS] ── Exemplos de Inicialização

#### 🚀 Exemplo 1: Gerar Artigo Acadêmico com Auditoria CAPES
```bash
/artigo
```
Este comando ativa o pipeline acadêmico distribuído:
1.  **SEEKER** — pesquisa autônoma e mineração em 10+ fontes científicas (arXiv, PubMed, OpenAlex, Semantic Scholar).
2.  **MASWOS** — 49 agentes especialistas rodando em 8 estágios síncronos de redação científica.
3.  **Banca** — 5 revisores e 4 orientadores virtuais em loop iterativo até atingir score de aprovação de 95/100.
4.  **AUTO_SCORE_QUALIS.py** — auditoria de 10 critérios CAPES.
5.  **Export** — Geração de LaTeX/PDF contendo 46 marcações de auditoria TSAC auditáveis.

**Saída**: Artigo de 35+ páginas ABNT estruturado com citações válidas e auditadas.

<div align="center">
  <img src="diagrams/academic-pipeline.svg" alt="Pipeline Acadêmico MASWOS" width="100%" style="max-width: 800px; border-radius: 8px; margin: 16px 0;"/>
</div>

#### 🚀 Exemplo 2: Engenharia Reversa de Sistemas Existentes
```bash
/reversa
```
Inicia o fluxo em cascata de 9 agentes especialistas em engenharia reversa e decomposição arquitetural:
```text
Scout ──> Archaeologist ──> Detective ──> Architect ──> Writer ──> Reviewer
                                            │
                                            └──> Visor ──> Data Master ──> Design System
```
**Saída**: 7 esquemas em formato SVG, mapas de dependências de código, ADRs e especificações técnicas de software (SDDs) gerados na pasta do projeto.

<div align="center">
  <img src="diagrams/agent-orchestration.svg" alt="Orquestração de Agentes" width="100%" style="max-width: 800px; border-radius: 8px; margin: 16px 0;"/>
</div>

#### 🚀 Exemplo 3: Modo Autônomo com Acesso Total a Ferramentas (MCPs)
```bash
/auto
```
Aciona o agente universal `openagent` com permissão total de leitura, escrita e execução em todos os 46 MCPs configurados, resolvendo missões complexas que demandam triangulação entre web crawling, refatoração de código local e consultas de dados estruturados.

---

### ☣️ [BOOT://TROUBLESHOOTING] ── Solução de Problemas do Grid

#### 1. Erro de Versão do Node.js
*   **Sintoma**: `Error: Unsupported Node.js version`
*   **Resolução**: Atualize o Node.js para v25+ (LTS). Use o `nvm` para atualização rápida:
    ```bash
    nvm install 25
    nvm use 25
    ```

#### 2. Modelos MiMo ou Ollama Indisponíveis
*   **Sintoma**: `Model not found` ao submeter prompts.
*   **Resolução**:
    *   Para **MiMo (Cloud)**: Valide a chave de API e a URL configuradas em `~/.config/opencode/opencode.json`.
    *   Para **Ollama (Local)**: Verifique se o daemon do Ollama está rodando localmente (`ollama serve`) e se o modelo foi baixado (`ollama run deepseek-r1:7b`).

#### 3. MCPs Não Inicializam ou Estão Inativos
*   **Sintoma**: Servidores MCP não respondem nas primeiras chamadas.
*   **Motivo**: Os MCPs usam **lazy init** (inicialização preguiçosa) para economizar recursos de startup da máquina. Eles só sobem na primeira requisição física que necessita da ferramenta.
*   **Resolução**: Execute um comando que demande explicitamente o MCP (ex: `/artigo` para buscas acadêmicas) e aguarde o spawn automático do processo em segundo plano.

#### 4. Erro ao Rodar `bun install`
*   **Sintoma**: Falha na instalação e links quebrados.
*   **Resolução**: Verifique se o Bun está atualizado (1.3+) e se você está executando o comando na mesma pasta onde está o arquivo `package.json`:
    ```bash
    bun --version
    ls package.json
    bun install
    ```

---

### 🗺️ [BOOT://NEXT_STEPS] ── Próximos Passos de Navegação

Explore a documentação detalhada para expandir seu controle sobre o grid:

| Código de Acesso | Documento de Destino | Descrição do Conteúdo |
| :--- | :--- | :--- |
| **SYS_DOC_001** | [README.md](README.md) | Visão geral cyberpunk e guias rápidos de demonstração |
| **SYS_DOC_002** | [PROJECTS.md](PROJECTS.md) | Painel didático de projetos organizados em Kanban |
| **SYS_DOC_003** | [TUTORIALS.md](TUTORIALS.md) | Tutoriais operacionais passo a passo |
| **SYS_DOC_004** | [GLOSSARY.md](GLOSSARY.md) | Glossário de arquitetura e conceitos do ecossistema |
| **SYS_DOC_005** | [CONTRIBUTING.md](CONTRIBUTING.md) | Diretrizes e padrões para desenvolvedores externos |
| **SYS_DOC_006** | [ROADMAP.md](ROADMAP.md) | Visão de metas e marcos de evolução futura |
| **SYS_DOC_007** | [AGENTS_PTBR.md](AGENTS_PTBR.md) | Detalhamento dos 125 agentes especialistas em PT-BR |

---

<div align="center">

**OpenCode Ecosystem v5.0** · Terminal de Controle de Documentação
`⚡ SYSTEM OVERWATCH ACTIVE ── GRID SECURED ⚡`

</div>
