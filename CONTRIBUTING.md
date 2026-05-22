# Guia para Contribuidores — OpenCode Ecosystem v4.2.1

Agradecemos o seu interesse em contribuir com o OpenCode Ecosystem. Este guia descreve os procedimentos para configurar o ambiente, entender a estrutura do projeto e submeter contribuições de qualidade.

---

## Como Configurar o Ambiente

### 1. Fork e Clone

```bash
# Fork o repositório no GitHub, depois clone:
git clone https://github.com/<seu-usuario>/OpenCode_Ecosystem.git
cd OpenCode_Ecosystem
```

### 2. Instalar Dependências

```bash
# Dependências Node.js / TypeScript (plugins e OpenCode CLI)
bun install

# Dependências Python (agentes, Nexus, módulo quântico)
pip install -r requirements.txt  # se disponível
```

### 3. Verificar Ambiente

```bash
node --version     # v25+
bun --version      # 1.3+
python --version   # 3.12+
opencode --version # 1.14+
```

### 4. Executar Testes

O ecossistema possui 88/88 testes de DI (Fases 5–7) e 378/391 testes legado:

```bash
python -m pytest tests/ -v
```

---

## Estrutura do Projeto

| Diretório | Função | Arquivos Principais |
|-----------|--------|-------------------|
| `agents/` | 125 agentes especializados em Markdown | Definições de agentes (core 56 + criação 49 + SEEKER 12 + Reversa 7 + corretor 1) |
| `skills/` | 104 skills com progressive disclosure | `SKILL.md` (≤2.500B) + `references/*.md` |
| `nexus/` | Orquestrador multiagente Nexus NMA v6.2 | 63 scripts Python, `sync_orchestrator.py`, `self_healer.py` |
| `quantum/` | Módulo de computação quântica | 81 arquivos: VQC, QML, ZNE/PEC |
| `criador-artigo/` | Pipeline MASWOS — 49 agentes para artigos Qualis A1 | Agentes A00–A45, templates, referências |
| `basis-research/` | SEEKER — pesquisa científica autônoma | 10 agentes Python, argument tree engine |
| `core/` | Infraestrutura core do ecossistema | Container DI, managers, bridges |
| `commands/` | Definições de comandos slash | Markdown com frontmatter YAML |
| `command/` | Implementação de comandos | 14 arquivos `.md` para `CommandRegistry` |
| `plugins/` | Plugins TypeScript | `manus-evolve.ts`, `ecosystem-sync.ts`, `bernstein-sync.ts` |
| `diagrams/` | 10 SVGs de arquitetura | Gerados automaticamente pelo Reversa Framework |
| `evolution/` | Skills geradas automaticamente pelo AutoEvolve | Output do ciclo PLAN→ACT→REFLECT→EXTRACT→EVOLVE |
| `.reversa/` | Artefatos de engenharia reversa | `DI_MIGRATION.md`, ADRs, SDDs |

---

## Padrões de Código

### Python

- **Versão mínima:** Python 3.12+
- **Docstrings:** obrigatórias em todas as funções e classes públicas
- **Type hints:** fortemente recomendados
- **Estilo:** seguir as convenções existentes no módulo que está sendo editado
- **Testes:** todo código novo deve incluir testes unitários

### Skills (YAML/Markdown)

- Cada `SKILL.md` deve conter **no máximo 2.500 bytes** (frontmatter YAML + conteúdo resumido)
- Conteúdo estendido deve residir em `references/*.md` (progressive disclosure)
- Frontmatter YAML obrigatório com campos: `name`, `description`, `trigger`, `version`

### Idioma

- **Toda documentação e output ao usuário:** português brasileiro formal
- **Zero CJK:** nenhum caractere chinês, japonês ou coreano deve aparecer em arquivos de saída
- **Variáveis, paths e código:** manter na língua original (inglês)
- Executar `criador-artigo/banca/ptbr_corrector.py` antes de submeter documentação

### TypeScript/JavaScript

- Compatível com Bun 1.3+
- Seguir padrões dos plugins existentes em `plugins/`

---

## Como Adicionar Novo Agente

1. **Criar arquivo** em `agents/` com o nome do agente (ex: `agents/meu-agente.md`)
2. **Definir o agente** seguindo o template dos agentes existentes (frontmatter YAML + instruções)
3. **Registrar no Container DI** se o agente necessitar de serviços do ecossistema:
   ```python
   from core import Container
   container = Container.instance()
   # Utilizar container.resolve("service_name") para acessar serviços
   ```
4. **Documentar** o agente no `AGENTS_PTBR.md` com estatísticas atualizadas

---

## Como Adicionar Nova Skill

1. **Criar diretório** em `skills/<categoria>/` (ex: `skills/research/minha-skill/`)
2. **Criar `SKILL.md`** com frontmatter YAML (máximo 2.500 bytes):
   ```yaml
   ---
   name: minha-skill
   description: Descrição concisa da skill
   trigger: /minha-skill
   version: 1.0.0
   category: research
   ---
   ```
3. **Criar `references/*.md`** para conteúdo estendido (progressive disclosure)
4. **Verificar tamanho:** `wc -c skills/<categoria>/minha-skill/SKILL.md` deve retornar ≤ 2.500

---

## Como Adicionar Novo MCP

1. **Definir configuração** em `opencode.json`:
   ```json
   {
     "mcpServers": {
       "meu-mcp": {
         "command": "npx",
         "args": ["-y", "@meu-pacote/mcp-server"],
         "env": {}
       }
     }
   }
   ```
2. **Protocolo:** implementar JSON-RPC sobre stdio (local) ou HTTP (remoto)
3. **Registrar no DI** se necessário:
   ```python
   # O MCP será descoberto automaticamente via lazy init
   # Registrar no Container apenas se houver integração com outros serviços
   ```
4. **Lazy init:** os MCPs inicializam automaticamente na primeira chamada de ferramenta — não é necessário código de inicialização explícito
5. **Documentar** o novo MCP no README.md na seção "MCP Servers"

---

## Pull Request

### Processo

1. **Criar branch** a partir de `main`:
   ```bash
   git checkout -b feature/minha-contribuicao
   ```
2. **Implementar alterações** seguindo os padrões de código descritos acima
3. **Executar testes:**
   ```bash
   python -m pytest tests/ -v
   ```
4. **Verificar CJK** (se alterou documentação):
   ```bash
   python criador-artigo/banca/ptbr_corrector.py
   ```
5. **Commit** com mensagem descritiva em português ou inglês
6. **Submeter PR** com descrição clara do que foi alterado e por quê

### Checklist do PR

- [ ] Testes passando (`python -m pytest tests/ -v`)
- [ ] Sem caracteres CJK em arquivos de saída
- [ ] Skills dentro do limite de 2.500B
- [ ] Documentação atualizada (se aplicável)
- [ ] Código segue os padrões do módulo editado

---

## Dúvidas?

Abra uma issue no repositório. Toda contribuição é bem-vinda.

---

<div align="center">

**OpenCode Ecosystem v4.2.1** · Guia para Contribuidores

</div>
