# Tutoriais — OpenCode Ecosystem v4.2.1

> Tutoriais práticos com passo-a-passo para as principais funcionalidades do ecossistema.

**Pré-requisito:** ambiente configurado conforme o [GETTING_STARTED.md](GETTING_STARTED.md).

---

## Tutorial 1: Gerar Artigo Acadêmico Qualis A1

### Objetivo

Produzir um artigo acadêmico completo, com score ≥ 95/100 segundo critérios Qualis A1 da CAPES, utilizando o pipeline MASWOS com 49 agentes especializados.

### Comando

```
/artigo
```

### Pipeline Detalhado

O comando `/artigo` aciona a seguinte sequência automatizada:

```
┌─────────────────────────────────────────────────────────────────┐
│  SEEKER (pesquisa em 10+ fontes acadêmicas)                     │
│  ├── arXiv, PubMed, OpenAlex, CORE, Semantic Scholar            │
│  └── Argument Tree Engine: cada afirmação → evidência rastreável│
│                              ↓                                   │
│  MASWOS — 49 agentes em 8 estágios:                             │
│  S01. Pesquisa autônoma (SEEKER)                                │
│  S02. Definição de estrutura, hipóteses e metodologia           │
│  S03. Redação com vocabulário anti-IA (87 termos proibidos)     │
│  S04. Formatação ABNT NBR 6023, LaTeX, figuras e tabelas       │
│  S05. Banca de revisão — 5 revisores especializados             │
│  S06. Orientação — 4 doutores com feedback iterativo            │
│  S07. AUTO_SCORE_QUALIS.py (10 critérios ponderados)            │
│       └── Score < 95? → loopback para S06 (iteração)            │
│  S08. Exportação LaTeX/PDF com 46 anotações TSAC auditáveis     │
│                              ↓                                   │
│  Corretor CJK (ptbr_corrector.py)                               │
│  PhD Auditor (Nash + Bonferroni + Qualis)                       │
│  Manus Evolve (aprende padrões → gera novas skills)             │
└─────────────────────────────────────────────────────────────────┘
```

### Passo-a-Passo

1. **Iniciar o OpenCode CLI** no diretório do ecossistema:
   ```bash
   cd OpenCode_Ecosystem
   opencode
   ```

2. **Executar o comando** no prompt do OpenCode:
   ```
   /artigo
   ```

3. **Definir o tema** quando solicitado. O SEEKER iniciará a pesquisa autônoma em 10+ fontes acadêmicas.

4. **Aguardar o pipeline.** Os 49 agentes executarão os 8 estágios automaticamente. O processo inclui:
   - Pesquisa e coleta de referências
   - Redação multiagente com estilo anti-IA
   - Revisão por banca simulada (5 revisores)
   - Orientação por 4 doutores virtuais
   - Avaliação automática via `AUTO_SCORE_QUALIS.py`
   - Iteração até score ≥ 95/100

5. **Verificar o output.** O artigo final será gerado em formato LaTeX/PDF.

### Output Esperado

- Artigo de **35+ páginas** em formato ABNT
- **46 citações** com anotações TSAC auditáveis
- Score Qualis A1: **≥ 95/100**
- Formato: LaTeX e PDF
- Métricas de execução: Board Score 86,5 → 92,7 (+7,1%), Auto Score 74 → 95 (+28,4%)

### Dica

O pipeline executa iterações automáticas (loopback) até atingir o score mínimo. Quanto mais específico o tema, mais focada será a pesquisa do SEEKER.

---

## Tutorial 2: Executar Pipeline Quântico

### Objetivo

Realizar experimentos de computação quântica aplicada, incluindo VQC de 50 qubits, QML em dados médicos e mitigação de erros quânticos.

### Comando

```
/quantum
```

### Pipeline Detalhado

```
┌─────────────────────────────────────────────────────────┐
│  quantum-nexus-phd (orquestrador quântico)              │
│  ├── code-runner (execução de scripts Python/Rust)      │
│  ├── pdf (geração de relatórios)                        │
│  └── sequential-thinking (raciocínio estruturado)       │
│                              ↓                           │
│  Módulos disponíveis:                                    │
│  ├── VQC 50-qubit MPS (Matrix Product State)            │
│  ├── QML HAM10000 (classificação médica, 7 classes)     │
│  ├── ZNE (Zero Noise Extrapolation, 5 níveis)           │
│  ├── PEC (Probabilistic Error Cancellation)             │
│  └── Grad-CAM (interpretabilidade)                      │
└─────────────────────────────────────────────────────────┘
```

### Passo-a-Passo

1. **Iniciar o OpenCode CLI:**
   ```bash
   cd OpenCode_Ecosystem
   opencode
   ```

2. **Executar o comando:**
   ```
   /quantum
   ```

3. **Selecionar o experimento** quando solicitado. Opções disponíveis:

   | Experimento | Descrição | Resultado Esperado |
   |------------|-----------|-------------------|
   | VQC 50-qubit | Variational Quantum Classifier com MPS | 90,54% ± 0,58% (5-fold CV) |
   | QML HAM10000 | Classificação de 10.015 imagens dermatológicas | 89,52% acurácia |
   | ZNE | Zero Noise Extrapolation (5 níveis: 1,0×–3,0×) | E_zero_noise: 0,771 |
   | PEC | Probabilistic Error Cancellation (50 qubits) | 89,88% expected accuracy |

4. **Aguardar a execução.** O `code-runner` MCP executará os scripts Python/Rust do módulo `quantum/`.

5. **Verificar resultados.** Os outputs incluem métricas, gráficos e relatórios PDF.

### Parâmetros do VQC

| Parâmetro | Valor |
|-----------|:-----:|
| Qubits | 50 |
| Camadas | 6 |
| Parâmetros treináveis | 600 |
| Backend | MPS (Matrix Product State) |
| Bond dimension (χ) | 64 |

### Dica

O backend MPS reduz a memória necessária em **~10¹¹×** comparado ao Statevector, permitindo simulações de 50 qubits em hardware convencional.

---

## Tutorial 3: Engenharia Reversa de Sistemas

### Objetivo

Executar a análise completa de um sistema utilizando o pipeline de engenharia reversa com 9 agentes especializados, gerando diagramas de arquitetura, ADRs e SDDs.

### Comando

```
/reversa
```

### Pipeline Detalhado

```
┌─────────────────────────────────────────────────────────┐
│  Pipeline de 9 agentes — Reversa Framework v1.2.22      │
│                                                          │
│  Fase 1: reversa-scout                                   │
│     └── surface.json, modules.json                       │
│  Fase 2: reversa-archaeologist                           │
│     └── code-analysis/ (AST, deps)                       │
│  Fase 3: reversa-detective                               │
│     └── domain/ (UML, fluxos)                            │
│  Fase 4: reversa-architect                               │
│     └── architecture/ (C4, ADRs)                         │
│  Fase 5: reversa-writer                                  │
│     └── specs/ (12 SDDs)                                 │
│  Fases 6–9: reviewer → visor → data-master →            │
│             design-system                                │
│     └── 67 artefatos totais                              │
│                                                          │
│  MCPs utilizados: filesystem, diff, github               │
└─────────────────────────────────────────────────────────┘
```

### Passo-a-Passo

1. **Iniciar o OpenCode CLI:**
   ```bash
   cd OpenCode_Ecosystem
   opencode
   ```

2. **Executar o comando:**
   ```
   /reversa
   ```

3. **Indicar o alvo** da engenharia reversa (diretório ou repositório a ser analisado).

4. **Aguardar o pipeline.** Os 9 agentes executarão sequencialmente:
   - **Scout:** varredura superficial do sistema
   - **Archaeologist:** análise de código (AST, dependências)
   - **Detective:** mapeamento de domínio (UML, fluxos)
   - **Architect:** arquitetura (modelo C4, ADRs)
   - **Writer:** especificações (12 SDDs)
   - **Reviewer → Visor → Data Master → Design System:** revisão e consolidação

5. **Verificar artefatos gerados.** Os outputs são organizados em subdiretórios dentro de `.reversa/`.

### Output Esperado

| Artefato | Quantidade | Descrição |
|----------|:----------:|-----------|
| SVGs de arquitetura | 7 | Diagramas interativos vetoriais |
| ADRs | 12 | Architecture Decision Records |
| SDDs | 12 | Software Design Documents |
| Diagramas C4 | 3 | Context, Container, Component |
| Artefatos totais | 67 | Documentação completa do sistema |

**Confiança do pipeline:** 100/100

### Dica

O Reversa Framework gera os 7 SVGs automaticamente e mantém a documentação sincronizada com o código-fonte. Qualquer alteração no sistema pode ser re-analisada executando `/reversa` novamente.

---

## Tutorial 4: Configurar e Usar MCPs

### Objetivo

Entender como os servidores MCP (Model Context Protocol) funcionam no ecossistema, como configurá-los e como adicionar novos MCPs.

### Conceitos Fundamentais

**MCP (Model Context Protocol)** é um protocolo JSON-RPC criado pela Anthropic (2024) que padroniza a comunicação entre agentes de IA e servidores de contexto. No OpenCode Ecosystem:

- **40 servidores MCP** estão configurados (38 locais + 2 remotos)
- **Transporte:** stdio (local) ou HTTP (remoto)
- **Lazy init:** servidores só inicializam na primeira chamada de ferramenta

### Arquivo de Configuração: `opencode.json`

Os MCPs são definidos no arquivo `opencode.json` na raiz do projeto. Exemplo de configuração:

```json
{
  "mcpServers": {
    "websearch": {
      "command": "npx",
      "args": ["-y", "@anthropic/mcp-websearch"],
      "env": {}
    },
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@anthropic/mcp-filesystem", "/caminho/do/projeto"],
      "env": {}
    },
    "code-runner": {
      "command": "npx",
      "args": ["-y", "@anthropic/mcp-code-runner"],
      "env": {}
    }
  }
}
```

### Categorias de MCPs Disponíveis

| Categoria | MCPs | Função |
|-----------|------|--------|
| Busca | `websearch`, `gh_grep`, `context7`, `scihub` | Pesquisa web, GitHub, documentação, papers |
| Navegador | `playwright`, `chrome-devtools` | Automação de browser |
| Código | `eslint`, `diff`, `code-runner` | Linting, comparação, execução |
| Dados | `sqlite`, `fetch`, `pdf`, `time` | Banco de dados, HTTP, PDF, timestamp |
| Raciocínio | `sequential-thinking`, `memory` | Raciocínio estruturado, memória persistente |
| Infraestrutura | `filesystem`, `github` | Acesso ao sistema de arquivos e GitHub |

### Passo-a-Passo: Usar MCPs Existentes

1. **Os MCPs são ativados automaticamente** quando um comando os requisita:
   ```
   /artigo    → ativa: websearch, scihub, sequential-thinking, code-runner
   /reversa   → ativa: filesystem, diff, github
   /quantum   → ativa: code-runner, pdf, sequential-thinking
   /auto      → ativa: todos os 40 MCPs
   ```

2. **Verificar MCPs ativos** na sessão:
   - Os MCPs utilizam lazy init — só aparecem como ativos após a primeira chamada
   - O `mcp_router.py` (Nexus) gerencia o roteamento entre MCPs

### Passo-a-Passo: Adicionar Novo MCP

1. **Editar `opencode.json`** e adicionar a configuração do novo servidor:
   ```json
   {
     "mcpServers": {
       "meu-novo-mcp": {
         "command": "npx",
         "args": ["-y", "@meu-pacote/mcp-server"],
         "env": {
           "API_KEY": "sua-chave-se-necessario"
         }
       }
     }
   }
   ```

2. **Protocolo:** o servidor deve implementar JSON-RPC 2.0 sobre stdio (recomendado para local) ou HTTP (para servidores remotos).

3. **Testar a conexão** executando `/auto` para ativar todos os MCPs e verificar se o novo servidor inicializa corretamente.

4. **Registrar no Container DI** (opcional, para integração avançada):
   ```python
   from core import Container
   container = Container.instance()
   # O MCP será descoberto via lazy init automaticamente
   ```

5. **Documentar** o novo MCP na seção "MCP Servers" do README.md.

### Dica

O comando `/auto` ativa o agente `openagent` com acesso a **todos** os MCPs simultaneamente. Use-o para testar a integração de novos servidores sem precisar configurar comandos específicos.

---

## Próximos Passos

- Consulte o [GLOSSARY.md](GLOSSARY.md) para definições de termos técnicos
- Leia o [CONTRIBUTING.md](CONTRIBUTING.md) para contribuir com o projeto
- Veja o [ROADMAP.md](ROADMAP.md) para a visão futura do ecossistema
- Explore o [README.md](README.md) para a documentação técnica completa

---

<div align="center">

**OpenCode Ecosystem v4.2.1** · Tutoriais Práticos

</div>
