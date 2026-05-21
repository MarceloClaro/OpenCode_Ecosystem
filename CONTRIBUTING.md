# Contribuindo para o OpenCode Ecosystem

Agradecemos o seu interesse em contribuir com o **OpenCode Ecosystem v4.2.1**. Este guia abrange o fluxo completo de contribuição — desde a configuração do ambiente até a submissão de Pull Requests — para todos os tipos de contribuição: agentes, skills, MCPs, correções e melhorias.

---

## Como Configurar o Ambiente de Desenvolvimento

1. **Fork e clone** o repositório:
   ```bash
   git clone https://github.com/<seu-usuario>/OpenCode_Ecosystem.git
   cd OpenCode_Ecosystem
   ```

2. **Instalar pré-requisitos** — consulte o [GETTING_STARTED.md](GETTING_STARTED.md) para instruções detalhadas:
   - Node.js v25+
   - Bun 1.3+
   - Python 3.12+
   - OpenCode CLI 1.14+

3. **Instalar dependências Node.js:**
   ```bash
   bun install
   ```

4. **Executar testes:**
   ```bash
   python -m pytest tests/ -v
   ```
   Referência de cobertura:
   - **88/88** testes DI passando (Fases 5-7)
   - **378/391** testes legado (13 falhas pré-existentes não relacionadas ao DI)

---

## Estrutura do Projeto

| Diretório | Função | Conteúdo |
|-----------|--------|----------|
| `agents/` | Definições de agentes | 125 agentes em arquivos `.md` (core 56 + criação 49 + SEEKER 12 + Reversa 7 + corretor 1) |
| `skills/` | Skills organizadas por categoria | 104 skills em 12 categorias com YAML frontmatter |
| `nexus/` | Orquestrador NMA v6.2 | 63 scripts Python — sync barriers, meta-orquestração, autocura |
| `quantum/` | Módulo de computação quântica | 81 arquivos — VQC 50 qubits, QML HAM10000, ZNE/PEC |
| `criador-artigo/` | Pipeline MASWOS | 49 agentes especializados para artigos Qualis A1 |
| `basis-research/` | SEEKER | 10 agentes de pesquisa + argument tree + 10+ fontes acadêmicas |
| `core/` | Infraestrutura central | Container DI com 11 serviços + bridge Python ⟷ TypeScript |
| `commands/` e `command/` | Comandos slash | 14 comandos registrados via CommandRegistry |
| `plugins/` | Plugins TypeScript | `manus-evolve.ts`, `ecosystem-sync.ts`, `bernstein-sync.ts` |
| `diagrams/` | Diagramas de arquitetura | 7 SVGs gerados pelo Reversa Framework |
| `evolution/` | Skills geradas pelo AutoEvolve | Skills criadas automaticamente pelos ciclos evo-1 a evo-8 |
| `.reversa/` | Artefatos de engenharia reversa | 67 artefatos — AST, UML, C4, ADRs, SDDs |

---

## Padrões de Código

### Python
- **Versão:** Python 3.12+
- **Docstrings:** obrigatórias em todas as funções públicas
- **Type hints:** encorajados, mas não obrigatórios
- **Estilo:** seguir o padrão existente no módulo que está sendo modificado
- **Testes:** executar `python -m pytest tests/ -v` antes e depois de alterações

### Skills
- Formato: YAML frontmatter + corpo Markdown
- Tamanho máximo: **2.500 bytes** por `SKILL.md` (progressive disclosure)
- Conteúdo estendido deve residir em `references/*.md`
- Referência: consulte `skills/SKILL_TEMPLATE.md` como modelo

### Agentes
- Cada agente é um arquivo `.md` em `agents/` seguindo o formato padrão
- Incluir descrição, capabilities e instruções de uso

### Saída e Idioma
- Toda saída ao usuário deve ser em **português brasileiro formal**
- **Zero tolerância** a caracteres CJK na saída — o `ptbr_corrector.py` deve ser executado antes de cada entrega
- Localização do corretor: `criador-artigo/banca/ptbr_corrector.py`

### Injeção de Dependência
- Novos componentes devem seguir o **Pattern A** (`from_container()` factory) quando possível
- Componentes existentes suportam o **Pattern B** (`container=` opcional no construtor)
- Compatibilidade retroativa: todos os construtores devem funcionar sem container

---

## Como Adicionar um Novo Agente

1. **Criar arquivo `.md`** em `agents/` seguindo o template dos agentes existentes
2. **Definir** nome, descrição, capabilities e instruções de uso
3. **Registrar no Container DI** se o agente requer integração com serviços core:
   ```python
   from core import Container
   container = Container.instance()
   container.register("meu_agente", MeuAgente.from_container(container))
   ```
4. **Testar integração** executando os testes do módulo relevante

---

## Como Adicionar uma Nova Skill

1. **Criar pasta** em `skills/<categoria>/` (ex.: `skills/research/minha-skill/`)
2. **Criar `SKILL.md`** com frontmatter YAML:
   ```yaml
   ---
   name: minha-skill
   category: research
   trigger: /minha-skill
   description: Descrição breve da skill
   version: 1.0.0
   ---
   ```
3. **Respeitar o limite de 2.500 bytes** no `SKILL.md`
4. **Adicionar `references/*.md`** para conteúdo estendido (progressive disclosure)
5. **Referenciar** `skills/SKILL_TEMPLATE.md` como modelo de estrutura

---

## Como Adicionar um Novo MCP Server

1. **Definir** a configuração do servidor em `opencode.json`:
   ```json
   {
     "mcpServers": {
       "meu-servidor": {
         "command": "node",
         "args": ["caminho/para/servidor.js"],
         "type": "stdio"
       }
     }
   }
   ```
2. **Implementar** o protocolo JSON-RPC (stdio para servidores locais, HTTP para remotos)
3. **Registrar no Container DI** se necessário:
   ```python
   container.register("mcp.meu-servidor", servidor_meta)
   ```
4. **Lazy init:** o servidor deve inicializar apenas na primeira chamada de ferramenta — não no startup do ecossistema

---

## Processo de Pull Request

1. **Criar branch** a partir de `main`:
   ```bash
   git checkout -b feature/minha-contribuicao
   ```
2. **Fazer alterações** seguindo os padrões de código descritos acima
3. **Executar testes:**
   ```bash
   python -m pytest tests/ -v
   ```
4. **Verificar** que não há caracteres CJK na saída:
   ```bash
   python criador-artigo/banca/ptbr_corrector.py
   ```
5. **Commitar** com mensagem clara e descritiva
6. **Submeter PR** com descrição detalhada do que foi alterado e por quê
7. **Aguardar review** dos maintainers

### Checklist do PR

- [ ] Testes passando (`python -m pytest tests/ -v`)
- [ ] Sem caracteres CJK na saída
- [ ] Documentação atualizada (se aplicável)
- [ ] Código segue os padrões existentes do módulo
- [ ] Compatibilidade retroativa mantida (se alterando APIs existentes)

---

## Código de Conduta

Ao contribuir com o OpenCode Ecosystem, comprometemo-nos com os seguintes princípios:

- **Respeito:** tratar todos os participantes com cortesia e consideração
- **Inclusão:** acolher contribuições independentemente de experiência, identidade ou origem
- **Foco técnico:** manter discussões centradas em aspectos técnicos e construtivos
- **Transparência:** documentar decisões e justificativas de forma clara
- **Qualidade:** priorizar código bem testado, documentado e compatível com a arquitetura existente

---

## Dúvidas

Abra uma [issue](https://github.com/MarceloClaro/OpenCode_Ecosystem/issues) no repositório. Estamos disponíveis para auxiliar.
