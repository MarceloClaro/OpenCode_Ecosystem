<!--
  SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL
  Toda resposta DEVE ser em português do Brasil formal.
  Contexto em chinês para eficiência de tokens (densidade +40%%).
  Modelo: deepseek-v4-pro (OpenCode Zen, 200K ctx, 128K out, gratuito)
-->

# Arquitetura MCP Transformadora

## Visão Geral

A integração de **Model Context Protocol (MCP)** com o TMA permite que agentes acessem capacidades especializadas de forma dinâmica e escalável. MCPs funcionam como "extensões de contexto" que fornecem ferramentas, dados e APIs sem aumentar o tamanho do prompt.

## Camadas da Arquitetura MCP

```
┌─────────────────────────────────────────┐
│  Camada de Aplicação (TMA Agents)       │
│  A1-A8 com especialização dinâmica      │
└────────────┬────────────────────────────┘
             │
┌────────────▼────────────────────────────┐
│  Camada de Roteamento (MCP Router)      │
│  - Descoberta de capacidades            │
│  - Seleção inteligente de MCP           │
│  - Balanceamento de carga               │
│  - Fallback e retry automático          │
└────────────┬────────────────────────────┘
             │
┌────────────▼────────────────────────────┐
│  Camada de Protocolos MCP               │
│  - Filesystem MCP                       │
│  - Web Search MCP                       │
│  - Database MCP                         │
│  - Code Execution MCP                   │
│  - LLM Inference MCP                    │
│  - Memory/State MCP                     │
│  - Custom MCPs (extensível)             │
└────────────┬────────────────────────────┘
             │
┌────────────▼────────────────────────────┐
│  Camada de Recursos                     │
│  - Sistemas de arquivos                 │
│  - Bancos de dados                      │
│  - APIs externas                        │
│  - Serviços de computação               │
└─────────────────────────────────────────┘
```

## Tipos de MCP

### 1. **Filesystem MCP** (A1, A5)
Acesso a arquivos e diretórios para:
- Leitura de requisitos e documentação
- Escrita de artefatos (código, testes, relatórios)
- Navegação de estrutura de projeto

**Operações:**
- `read_file(path)` → conteúdo
- `write_file(path, content)` → sucesso
- `list_directory(path)` → arquivos
- `create_directory(path)` → sucesso

### 2. **Web Search MCP** (A2, A3)
Busca e análise de informações da web para:
- Pesquisa de padrões de design
- Verificação de compatibilidade de bibliotecas
- Análise de tendências tecnológicas

**Operações:**
- `search(query, limit)` → resultados
- `get_page(url)` → conteúdo HTML
- `extract_metadata(url)` → metadados

### 3. **Database MCP** (A4, A6)
Acesso a bancos de dados para:
- Consultas de dados de teste
- Validação de integridade
- Geração de fixtures

**Operações:**
- `query(sql)` → resultados
- `execute(sql)` → status
- `transaction_begin()` → ID
- `transaction_commit(id)` → sucesso

### 4. **Code Execution MCP** (A4, A8)
Execução segura de código para:
- Testes unitários
- Validação de sintaxe
- Análise estática

**Operações:**
- `execute_python(code, timeout)` → output
- `execute_shell(cmd, timeout)` → output
- `lint_code(code, language)` → issues

### 5. **LLM Inference MCP** (A2, A3, A8)
Inferência de modelos para:
- Análise de impacto
- Mediação de consenso
- Otimização evolutiva

**Operações:**
- `infer(prompt, model, temperature)` → resposta
- `batch_infer(prompts)` → respostas
- `stream_infer(prompt)` → generator

### 6. **Memory/State MCP** (A7, A8)
Gerenciamento de estado persistente para:
- Armazenamento de contexto entre fases
- Histórico de decisões
- Métricas evolutivas

**Operações:**
- `store(key, value)` → sucesso
- `retrieve(key)` → valor
- `delete(key)` → sucesso
- `list_keys(prefix)` → chaves

## Estratégia de Roteamento Inteligente

O **MCP Router** implementa seleção inteligente baseada em:

### 1. **Matching de Capacidades**
```
Tarefa: "Gerar testes unitários"
Requer: [CODE_EXECUTION, FILESYSTEM]
Candidatos: [MCP-A4, MCP-A6, MCP-Custom]
Seleção: MCP-A4 (especializado em execução)
```

### 2. **Scoring Multi-Critério**
- **Health Score** (40%): Disponibilidade e confiabilidade
- **Load Factor** (30%): Capacidade de processamento
- **Specialization Alignment** (20%): Alinhamento com papel do agente
- **Priority Boost** (10%): Prioridade da tarefa

### 3. **Fallback Automático**
```
Tentativa 1: MCP-A4 (indisponível)
  ↓
Tentativa 2: MCP-A6 (sobrecarga)
  ↓
Tentativa 3: MCP-Custom (sucesso)
```

## Granularidade de Sincronização com MCPs

### Sem MCP (Fase-Level)
```
Embedding → Attention → Feed-Forward → ...
```

### Com MCP (Operation-Level)
```
Embedding:
  ├─ op-embed-001: Requirement Analysis (MCP-Filesystem)
  ├─ op-embed-002: Domain Modeling (MCP-LLM)
  └─ [SYNC BARRIER] ← Consenso entre A1 e A2

Attention:
  ├─ op-attention-001: Impact Analysis (MCP-Web)
  ├─ op-attention-002: Risk Assessment (MCP-LLM)
  └─ [SYNC BARRIER] ← Mediação A3
```

## Padrões de Integração MCP

### 1. **Request-Response**
```python
# Simples e síncrono
result = mcp_router.route_task(task)
mcp_server.execute(result.mcp_server_id, task)
```

### 2. **Streaming**
```python
# Para operações longas
for chunk in mcp_server.stream(task):
    process_chunk(chunk)
    checkpoint()
```

### 3. **Batch Processing**
```python
# Múltiplas operações em paralelo
tasks = [task1, task2, task3]
results = mcp_router.batch_route(tasks)
```

### 4. **Conditional Routing**
```python
# Roteamento baseado em resultado anterior
if result.status == "success":
    next_task = create_next_task(result)
    route_task(next_task)
```

## Segurança e Isolamento

### 1. **Sandboxing**
- Code Execution MCP roda em container isolado
- Timeout obrigatório para todas as operações
- Limite de recursos (CPU, memória, disco)

### 2. **Autenticação**
- Cada MCP requer credenciais específicas
- Tokens armazenados em Memory MCP (encriptado)
- Auditoria de acesso

### 3. **Rate Limiting**
- Por MCP: máximo de requisições/segundo
- Por agente: quota de uso
- Por operação: timeout e retry limits

## Exemplo: Pipeline Embedding com MCPs

```
Tarefa: Mapear requisitos de novo módulo

1. A1 inicia Embedding
   ├─ Lê requisitos: Filesystem MCP
   ├─ Busca padrões similares: Web Search MCP
   └─ Gera modelo de domínio: LLM Inference MCP

2. [Checkpoint] Salva artefatos em Memory MCP

3. A2 inicia Attention
   ├─ Analisa impacto: LLM Inference MCP
   ├─ Valida compatibilidade: Code Execution MCP
   └─ Registra riscos: Database MCP

4. [Sync Barrier] Consenso entre A1 e A2

5. A3 inicia mediação se conflitos
   ├─ Propõe soluções: LLM Inference MCP
   └─ Registra decisão: Memory MCP

6. A4 inicia Feed-Forward
   ├─ Gera código: LLM Inference MCP
   ├─ Executa testes: Code Execution MCP
   └─ Salva artefatos: Filesystem MCP
```

## Métricas de Performance

### Por MCP
- Taxa de sucesso
- Latência média
- Throughput (ops/segundo)
- Taxa de erro

### Por Agente
- Operações completadas
- Taxa de retry
- Tempo médio por fase
- Fitness score

### Por Tarefa
- Tempo total
- Número de MCPs utilizados
- Checkpoints criados
- Rollbacks necessários

## Extensibilidade

### Criar Custom MCP
```python
class CustomMCP:
    def __init__(self, name, capabilities):
        self.name = name
        self.capabilities = capabilities
    
    def execute(self, operation):
        # Implementar lógica específica
        pass
    
    def health_check(self):
        # Verificar disponibilidade
        pass
```

### Registrar no Router
```python
custom_mcp = CustomMCP("mcp-custom", [CAPABILITY.CUSTOM])
router.register_mcp(custom_mcp)
```

## Referências
- MCP Specification: https://modelcontextprotocol.io
- TMA Pipeline: `references/arquitetura_transformer.md`
- Granular Sync: `references/evolucao_granular.md`
