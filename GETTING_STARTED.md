# Primeiros Passos — OpenCode Ecosystem v4.2.1

Bem-vindo ao **OpenCode Ecosystem**, uma plataforma de inteligência artificial multiagente, autônoma e evolutiva, integrada ao OpenCode CLI. Este guia o conduzirá desde a instalação até a execução dos primeiros comandos.

---

## Para quem é este guia

| Perfil | Objetivo |
|--------|----------|
| **Pesquisador acadêmico** | Gerar artigos com score Qualis A1 (≥ 95/100) utilizando peer-review simulado com 49 agentes |
| **Desenvolvedor** | Executar engenharia reversa de sistemas, explorar a arquitetura multiagente e contribuir com novos agentes, skills ou MCPs |
| **Estudante de computação quântica** | Realizar experimentos QML com até 50 qubits (VQC, HAM10000, ZNE/PEC) |
| **Estudante ou entusiasta de IA** | Compreender e explorar um ecossistema com 125 agentes, 40 MCPs e 104 skills |

---

## Pré-requisitos

| Requisito | Versão mínima | Instalação |
|-----------|:------------:|------------|
| **Node.js** | v25+ | [nodejs.org/download](https://nodejs.org/en/download/) |
| **Bun** | 1.3+ | [bun.sh](https://bun.sh/) — `curl -fsSL https://bun.sh/install \| bash` |
| **Python** | 3.12+ | [python.org/downloads](https://www.python.org/downloads/) |
| **OpenCode CLI** | 1.14+ | [github.com/nicepkg/opencode](https://github.com/nicepkg/opencode) — `npm i -g @anthropic-ai/opencode` |
| **Sistema operacional** | Windows 11 | Sistema principal de desenvolvimento. Linux e macOS são compatíveis, porém não oficialmente testados |
| **Modelo** | big-pickle | Gratuito — OpenCode Zen, 200K tokens de contexto, 128K tokens de saída. Configurado automaticamente pelo OpenCode CLI |

---

## Instalação Passo-a-Passo

### 1. Clonar o repositório

```bash
git clone https://github.com/MarceloClaro/OpenCode_Ecosystem.git
cd OpenCode_Ecosystem
```

### 2. Instalar dependências Node.js

O `package.json` declara as dependências `@opencode-ai/plugin` e `@types/bun`. Instale-as com o Bun:

```bash
bun install
```

### 3. Configurar o OpenCode CLI

Após instalar o OpenCode CLI globalmente, configure o workspace:

```bash
opencode init
```

O workspace padrão será criado em `~/.config/opencode` (Linux/macOS) ou `C:\Users\<usuario>\.config\opencode` (Windows).

### 4. Verificar o modelo big-pickle

O modelo `opencode/big-pickle` é gratuito e deve estar disponível automaticamente. Verifique com:

```bash
opencode models
```

Confirme que `big-pickle` aparece na lista com 200K de contexto e 128K de saída.

---

## Comandos de Verificação

Execute os comandos abaixo para confirmar que todos os pré-requisitos estão corretamente instalados:

| Comando | Saída esperada |
|---------|---------------|
| `node --version` | `v25.x.x` |
| `bun --version` | `1.3.x` |
| `python --version` | `Python 3.12.x` |
| `opencode --version` | `1.14.x` |

Se algum comando retornar erro ou versão inferior à mínima, consulte a seção [Solução de Problemas Comuns](#solução-de-problemas-comuns).

---

## Primeiros Passos — 3 Exemplos Simples

### Exemplo 1: Gerar um artigo acadêmico

```
/artigo
```

**O que acontece:**
1. O comando aciona o pipeline **MASWOS** (Multi-Agent Scientific Writing and Orchestration System)
2. O **SEEKER** realiza pesquisa autônoma em 10+ fontes acadêmicas (arXiv, PubMed, OpenAlex, CORE, Semantic Scholar)
3. **49 agentes especializados** (A00–A45 + scheduler) executam 8 estágios: pesquisa → estrutura → escrita → formatação ABNT → revisão por banca de 5 → correção por 4 orientadores doutores → scoring → exportação LaTeX/PDF
4. O **manus-evolve** aprende padrões de sucesso e gera novas skills em `evolution/`
5. Resultado: artigo com score **≥ 95/100** segundo critérios Qualis A1 da CAPES

### Exemplo 2: Executar engenharia reversa

```
/reversa
```

**O que acontece:**
1. O **Reversa Framework v1.2.22** aciona um pipeline de **9 agentes especializados**:
   - `scout` → mapeia superfície do sistema (`surface.json`, `modules.json`)
   - `archaeologist` → analisa AST e dependências
   - `detective` → gera UML e fluxos de domínio
   - `architect` → produz diagramas C4 e ADRs
   - `writer` → gera 12 SDDs (Software Design Documents)
   - `reviewer`, `visor`, `data-master`, `design-system` → refinam e validam
2. Resultado: **67 artefatos** com confiança **100/100**

### Exemplo 3: Explorar o ecossistema

```
/auto
```

**O que acontece:**
1. O comando aciona o **openagent** juntamente com todos os MCPs disponíveis (40 registrados, 17 ativos)
2. O sistema opera em modo autônomo, utilizando busca (DuckDuckGo, GitHub, Context7), execução de código, análise de PDF, raciocínio sequencial e memória
3. Os MCPs inicializam sob demanda (**lazy init**) — apenas os servidores necessários para cada tarefa são carregados na primeira chamada

---

## Outros Comandos Úteis

| Comando | Descrição |
|---------|-----------|
| `/quantum` | Executa experimentos de computação quântica (VQC 50 qubits, QML HAM10000) |
| `/evolve` | Aciona o AutoEvolve: PLAN → ACT → REFLECT → EXTRACT → EVOLVE |
| `/plan` | Utiliza a skill `writing-plans` com o MCP `sequential-thinking` |

---

## Próximos Passos

| Documento | Descrição |
|-----------|-----------|
| [README.md](README.md) | Documentação técnica completa do ecossistema |
| [TUTORIALS.md](TUTORIALS.md) | Tutoriais práticos detalhados *(em breve)* |
| [GLOSSARY.md](GLOSSARY.md) | Glossário de termos técnicos *(em breve)* |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Guia para contribuidores |
| [ROADMAP.md](ROADMAP.md) | Visão futura do projeto |
| [AGENTS_PTBR.md](AGENTS_PTBR.md) | Documentação de agentes em português brasileiro *(em breve)* |

---

## Solução de Problemas Comuns

### Erro de versão do Node.js

**Sintoma:** `node --version` retorna versão inferior a 25.

**Solução:** Atualize o Node.js para a versão 25+ via [nodejs.org/download](https://nodejs.org/en/download/) ou utilize um gerenciador de versões:

```bash
# Com nvm (Linux/macOS)
nvm install 25
nvm use 25

# Com Volta (recomendado para Windows)
volta install node@25
```

### Python não encontrado

**Sintoma:** `python --version` retorna erro "command not found".

**Solução:**
1. Verifique se o Python 3.12+ está instalado: [python.org/downloads](https://www.python.org/downloads/)
2. No Windows, durante a instalação, marque a opção **"Add Python to PATH"**
3. No Linux, utilize `python3 --version` (o comando pode ser `python3` em vez de `python`)

### Modelo big-pickle não disponível

**Sintoma:** O modelo `big-pickle` não aparece ao executar `opencode models`.

**Solução:**
1. Verifique se o OpenCode CLI está na versão 1.14+: `opencode --version`
2. Atualize o CLI: `npm update -g @anthropic-ai/opencode`
3. O modelo `big-pickle` (OpenCode Zen) é gratuito e não requer chave de API

### MCPs não inicializando

**Sintoma:** Ferramentas MCP não respondem ou retornam erro de conexão.

**Solução:**
1. Os MCPs utilizam **lazy init** — só inicializam na primeira chamada de ferramenta. Aguarde a primeira execução
2. Verifique o arquivo `opencode.json` na raiz do projeto para confirmar as configurações dos servidores
3. Para MCPs locais (38 de 40), confirme que as dependências do servidor estão instaladas
4. Execute `/auto` para forçar a inicialização de todos os MCPs disponíveis

### Erro ao executar `bun install`

**Sintoma:** Falha na instalação das dependências Node.js.

**Solução:**
1. Confirme que o Bun está na versão 1.3+: `bun --version`
2. Limpe o cache e reinstale: `bun install --force`
3. Se necessário, remova `node_modules/` e `bun.lockb` antes de reinstalar

---

<div align="center">

**OpenCode Ecosystem v4.2.1** — Primeiros Passos

*Dúvidas? Abra uma issue no [repositório](https://github.com/MarceloClaro/OpenCode_Ecosystem/issues).*

</div>
