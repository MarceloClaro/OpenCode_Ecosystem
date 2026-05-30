---
name: multimodal-vision
description: "Skill de integração multimodal visão+texto para o ecossistema OpenCode. Permite análise de imagens, diagramas, gráficos, screenshots e raciocínio visual combinado com texto. Integra MCPs de visão, Image Specialist agent, baoyu-diagram e ferramentas de geração/edição visual."
version: 1.0.0
author: ecosystem
tags: [vision, multimodal, image, visual-reasoning, gpt-4o, gemini, claude-vision]
compatibility: deepseek-v4-pro, gpt-4o, gemini-2.5-pro
---

# Multimodal Vision — Integração Visão + Texto

## 1. Arquitetura do Pipeline de Visão

O ecossistema OpenCode suporta três modalidades principais de interação visão-linguagem. O **Vision Router** é o ponto de entrada que classifica a requisição e direciona ao pipeline correto.

```
User Input (text + optional image)
    │
    ▼
Vision Router (determina modalidade: text-only, image-analysis, visual-generation)
    │
    ├── Text-only ─────────────────────────────────────────────────┐
    │                                                              ▼
    │                                               Standard LLM pipeline
    │                                          (deepseek-v4-pro, gpt-4o, etc.)
    │
    ├── Image Analysis ───────► Vision MCP ──────► Extracted features ──────┐
    │                              │                    / description        │
    │                              ▼                                        ▼
    │                    Provider específico                   Downstream Reasoning
    │                    (GPT-4o / Gemini / Claude)            (reasoning-orchestrator,
    │                                                            cora-debate)
    │
    └── Visual Generation ────► Image Gen Tool ───────────────► SVG / PNG / WebP
                               (baoyu-imagine,
                                baoyu-diagram,
                                baoyu-infographic)
```

### 1.1 Componentes do Pipeline

| Componente | Função | Tecnologia |
|-----------|--------|------------|
| **Vision Router** | Classifica a entrada e seleciona pipeline | Classificação heurística (presença de attachment, palavra-chave) |
| **Vision MCP** | Media chamadas a APIs de visão | MCP server configurado em `opencode.json` |
| **Image Preprocessor** | Prepara imagem para consumo pela API | `baoyu-compress-image`, conversão de formato |
| **Extractor** | Extrai dados estruturados da resposta da API | Parsing de JSON, extração de bounding boxes, OCR cleaning |
| **Downstream Reasoner** | Alimenta informação visual para raciocínio textual | `reasoning-orchestrator`, `cora-debate` |
| **Image Generator** | Gera imagens a partir de texto + parâmetros | `baoyu-imagine`, `baoyu-diagram`, `baoyu-infographic` |

## 2. Configuração do Vision MCP

### 2.1 Provedores Suportados

| Provedor | Modelo | Janela de Contexto | Custo Relativo | Suporte a Ferramentas |
|----------|--------|--------------------|----------------|-----------------------|
| **OpenAI** | GPT-4o / GPT-4o-mini | 128K tokens | Médio | Nativo |
| **Google** | Gemini 2.5 Pro | 1M tokens | Alto | Nativo |
| **Anthropic** | Claude 3.5 Sonnet | 200K tokens | Alto | Nativo |

### 2.2 Configuração no `opencode.json`

Para habilitar o Vision MCP, adicione o seguinte bloco ao arquivo `opencode.json` do projeto:

```jsonc
{
  "mcpServers": {
    "vision": {
      "type": "api",
      "provider": "openai",   // "openai" | "google" | "anthropic"
      "model": "gpt-4o",
      "apiKey": "${VISION_API_KEY}",
      "maxTokens": 4096,
      "temperature": 0.2,
      "vision": {
        "enabled": true,
        "maxImageSize": 2048,        // pixels no lado maior
        "supportedFormats": ["png", "jpg", "webp", "svg"],
        "detail": "high",             // "high" | "low" | "auto"
        "compressionQuality": 85,    // 1-100, usado no pré-processamento
        "ephemeralStorage": true     // imagens não persistem
      }
    }
  }
}
```

### 2.3 Formatos de Imagem Suportados

| Formato | Recomendado para | Tamanho Máximo (pixels) | Modo de Cor |
|---------|-----------------|------------------------|-------------|
| PNG | Diagramas, gráficos, screenshots | 2048×2048 | RGBA |
| JPG/JPEG | Fotos, capturas de tela | 2048×2048 | RGB |
| WebP | Imagens da web, transferência otimizada | 2048×2048 | RGBA |
| SVG | Diagramas vetoriais, arquiteturas | N/A (convertido para PNG/WebP) | Vetorial |

### 2.4 Limites e Recomendações

- **Tamanho máximo do lado maior**: 2048 pixels (recomendado); APIs aceitam até 4096.
- **Tamanho máximo do arquivo**: 20 MB antes da compressão.
- **Recomendação de compressão**: Use `baoyu-compress-image` para reduzir para <5 MB com qualidade 85%.
- **Proporção**: Imagens muito alongadas (panorâmicas 4:1+) têm qualidade reduzida. Prefira recortes.

## 3. Pipeline de Análise de Imagem

### 3.1 Stage 1 — Pré-processamento

```
Imagem bruta
    │
    ▼
[Detecção de formato]
    ├── SVG? ──► Converter para PNG (resolução base 1024×1024)
    ├── PNG/JPG/WebP? ──► OK
    │
    ▼
[Redimensionamento] ──► baoyu-compress-image ──► max lado 2048px, qualidade 85%
    │
    ▼
[Validação] ──► Verificar integridade do arquivo
    │
    ▼
Imagem pré-processada
```

**Comandos úteis para pré-processamento:**

```bash
# Comprimir imagem com baoyu-compress-image
# (invocado via skill, aceita path + formato de saída)
# Saída: imagem.webp com qualidade 85%, lado maior ≤2048px
```

### 3.2 Stage 2 — Chamada à API de Visão

**Template de prompt estruturado para análise de imagem:**

```
Você é um analista visual do ecossistema OpenCode.
Analise a imagem fornecida e responda com:

1. TIPO_IMAGEM: [diagrama | gráfico | screenshot | foto | figura_cientifica | outro]
2. DESCRICAO_GERAL: (2-3 frases sobre o conteúdo)
3. DADOS_ESTRUTURADOS: (se aplicável, em JSON)
4. TEXTO_EXTRAIDO: (todo texto legível presente na imagem)
5. RELACOES_VISUAIS: (relações espaciais entre elementos)
6. ANOMALIAS: (inconsistências visuais, se houver)

Contexto adicional do usuário: {user_prompt}
```

### 3.3 Stage 3 — Pós-processamento

A resposta bruta da API de visão passa por um extrator que estrutura o resultado:

```jsonc
{
  "imageType": "diagram",
  "description": "Arquitetura de microsserviços com 4 serviços...",
  "structuredData": {
    "nodes": ["API Gateway", "Service A", "Service B", "Database"],
    "edges": [
      { "from": "API Gateway", "to": "Service A", "label": "HTTP" },
      { "from": "Service A", "to": "Database", "label": "SQL" }
    ]
  },
  "extractedText": "API Gateway\nService A\nService B\nDatabase",
  "spatialRelations": [
    { "element": "API Gateway", "position": "top", "relativeTo": "Service A" }
  ],
  "anomalies": []
}
```

### 3.4 Stage 4 — Integração com Raciocínio Downstream

Os dados extraídos da imagem são roteados para agentes de raciocínio:

| Tipo de Análise | Agente Downstream | Uso |
|-----------------|-------------------|-----|
| Diagrama de arquitetura | `reasoning-orchestrator` | Validar conformidade com ADRs |
| Gráfico de desempenho | `cora-debate` | Argumentar sobre trade-offs baseados em dados |
| Screenshot de UI | `fullstack-guardian` | Gerar código equivalente |
| Figura científica | `MASWOS pipeline` | Incluir como evidência em artigo |
| Log/stderr capturado | `debugging-wizard` | Correlacionar erro visual com stack trace |

## 4. Tipos de Raciocínio Visual (8 Novos Tipos)

Estes 8 tipos estendem o catálogo de 68+ tipos de raciocínio do ecossistema (ver `reasoning-orchestrator` e `reasoning-orchestrator-v11`).

| Código | Nome | Descrição | Gatilho de Ativação | Exemplo de Uso |
|--------|------|-----------|---------------------|----------------|
| **VR01** | Diagram Comprehension | Extrair significado de fluxogramas, diagramas de arquitetura, grafos | "entenda este diagrama", "explique esta arquitetura" | Analisar diagrama de deployment e extrair dependências entre serviços |
| **VR02** | Chart Numerical Reading | Ler valores precisos de gráficos de barra, linha, dispersão, pizza | "que valor está no eixo Y para X=10", "leia este gráfico" | Extrair precisamente valores de um gráfico de benchmark sem dados brutos |
| **VR03** | Visual Anomaly Detection | Identificar inconsistências visuais, erros em renders, artefatos | "há algo errado nesta imagem?", "detecte anomalias" | Encontrar elementos UI sobrepostos, bordas quebradas, texto cortado |
| **VR04** | Screenshot-to-Code | Converter screenshots de UI para código HTML/CSS/React | "transforme esta tela em código", "reproduza esta interface" | Gerar componente React fiel a um mockup do Figma |
| **VR05** | Figure-to-Description | Gerar alt-text detalhado e legendas para figuras científicas | "descreva esta figura para acessibilidade", "gere legenda" | Produzir descrição ABNT/NBR 6023 para figura de artigo Qualis A1 |
| **VR06** | Visual Relationship | Compreender relações espaciais (acima, abaixo, dentro, adjacente) | "o que está dentro de X?", "qual elemento está à direita" | Mapear hierarquia visual de uma interface |
| **VR07** | Gesture/Pose Recognition | Identificar poses humanas, gestos, expressões faciais | "que gesto esta pessoa está fazendo?", "descreva a expressão" | Analisar linguagem corporal em foto de apresentação |
| **VR08** | Multi-Image Comparison | Comparar e contrastar múltiplas imagens lado a lado | "compare estas duas imagens", "o que mudou entre A e B" | Detectar diferenças entre versões de UI (regressão visual) |

### 4.1 Tabela de Ativação Automática

O `Vision Router` utiliza heurísticas para ativar automaticamente o tipo de raciocínio visual:

```yaml
VR01_DiagramComprehension:
  triggers: [arquitetura, diagrama, flowchart, grafo, fluxo, pipeline, deployment]
  min_confidence: 0.7
VR02_ChartNumericalReading:
  triggers: [gráfico, chart, plot, benchmark, eixo, barra, linha, pizza, scatter]
  min_confidence: 0.75
VR03_VisualAnomalyDetection:
  triggers: [anomalia, bug visual, artefato, inconsistência, sobreposição, quebrado]
  min_confidence: 0.8
VR04_ScreenshotToCode:
  triggers: [screenshot, tela, interface, ui, mockup, figma, protótipo, código]
  min_confidence: 0.7
VR05_FigureToDescription:
  triggers: [figura, legenda, alt-text, acessibilidade, caption, descrição científica]
  min_confidence: 0.7
VR06_VisualRelationship:
  triggers: [acima, abaixo, dentro, adjacente, esquerda, direita, hierarquia visual]
  min_confidence: 0.75
VR07_GesturePoseRecognition:
  triggers: [gesto, pose, expressão, rosto, corpo, postura, linguagem corporal]
  min_confidence: 0.8
VR08_MultiImageComparison:
  triggers: [compare, diferença, diff, before/after, lado a lado, regressão, A/B]
  min_confidence: 0.7
```

## 5. Pipeline de Geração Visual

### 5.1 Composição de Requisições Texto + Imagem

O pipeline de geração visual combina entrada textual com parâmetros de estilo para produzir imagens em diferentes formatos.

```
Prompt do usuário + parâmetros de estilo
    │
    ▼
[Vision Router — modo geração]
    │
    ├── Diagrama/SVG ──► baoyu-diagram ──► SVG
    ├── Ilustração/Arte ──► baoyu-imagine ──► PNG/WebP
    ├── Infográfico/Dados ──► baoyu-infographic ──► PNG/SVG
    └── Cards sociais ──► baoyu-image-cards ──► PNG
```

### 5.2 Ferramentas de Geração

| Skill | Finalidade | Formatos de Saída | Provedores |
|-------|-----------|-------------------|------------|
| `baoyu-imagine` | Geração de imagem por prompt (text-to-image) | PNG, WebP, JPEG | OpenAI GPT Image 2, Google Gemini, Replicate, MiniMax, Seedream |
| `baoyu-diagram` | Diagramas vetoriais (arquitetura, fluxo, grafos) | SVG | Renderização local via template |
| `baoyu-infographic` | Infográficos densos com dados | PNG, SVG | 21 layouts × 22 estilos visuais |
| `baoyu-image-cards` | Cards para redes sociais | PNG | 12 estilos × 8 layouts |
| `baoyu-cover-image` | Capas de artigo | PNG | 5 dimensões × 11 paletas × 7 estilos |

### 5.3 Encadeamento (Chaining)

Para pipelines complexos que requerem análise visual seguida de geração:

```
[Análise]  Screenshot de UI existente
    │
    ▼
[VR04]     Screenshot-to-Code → código extraído
    │
    ▼
[Geração]  baoyu-diagram → diagrama SVG da arquitetura do código gerado
    │
    ▼
[Revisão]  VR01 Diagram Comprehension → valida o diagrama gerado
```

Este encadeamento é orquestrado pelo `synthesis-agent` ou pelo `agent-node-pipeline`.

## 6. Integração com Skills Existentes

### 6.1 Comando `/auto` para Análise de Imagem

O comando `/auto` detecta automaticamente a presença de anexos de imagem e invoca o Vision MCP:

```
/auto (analise esta imagem e explique a arquitetura)
  → Vision Router detecta attachment → VR01 Diagram Comprehension
  → Resposta: descrição textual + dados estruturados
```

### 6.2 Integração com `reasoning-orchestrator`

O `reasoning-orchestrator` (v11) pode receber saída do Vision MCP como premissa para raciocínio:

```
1. Image Analysis → [VR02] extrai valores do gráfico
2. Valores extraídos → alimentam reasoning-orchestrator como fatos
3. Reasoning orchestrator → aplica inductive/deductive reasoning sobre os dados
```

Configuração no reasoning-orchestrator para aceitar entrada visual:

```yaml
vision_input:
  enabled: true
  source: vision_mcp
  confidence_threshold: 0.75
  enrich_with: [description, structured_data, extracted_text]
```

### 6.3 Integração com o Pipeline MASWOS (Artigo Acadêmico)

O pipeline de criação de artigo (`criador-artigo`) pode utilizar análise visual para:

1. **Analisar figuras de referência** (VR05) → gerar legendas ABNT automáticas
2. **Comparar gráficos** (VR02) → extrair dados para discussão nos resultados
3. **Detectar anomalias** (VR03) → identificar problemas em figuras antes da submissão
4. **Gerar figuras** via `baoyu-infographic` → dados de simulação → gráfico Qualis-ready

Fluxo típico:

```
MASWOS pipeline
    │
    ├── Figure Analysis: VR05 → gera caption e descrição acessível
    ├── Data Extraction: VR02 → lê valores de gráfico de referência
    ├── Figure Generation: baoyu-infographic → cria gráfico para Results
    └── Quality Check: VR03 → valida resolução, proporção, cor
```

### 6.4 Integração com `baoyu-diagram` para Documentação

A skill `baoyu-diagram` pode ser invocada a partir de análise visual de um sistema legado:

```
Reversa Scout → screenshot de arquitetura → VR01 → descrição textual
  → baoyu-diagram → SVG reconstruído → docs/architecture.svg
```

### 6.5 Integração com `debugging-wizard`

Screenshots de erros podem ser analisados visualmente:

```
Captura de tela de erro → VR03 → detecção de anomalia visual
  → debugging-wizard → correlação com stack trace (texto extraído)
  → hipótese de diagnóstico → ROOT_CAUSE
```

## 7. Segurança

### 7.1 Privacidade de Imagens

- **Nunca** enviar imagens contendo dados sensíveis (documentos pessoais, telas com PII, fotos de rostos sem consentimento) para APIs de visão externas sem confirmação explícita do usuário.
- O campo `ephemeralStorage: true` na configuração do Vision MCP garante que as imagens **não são armazenadas** pelo provedor após o processamento.
- Para ambientes com restrição de dados, configurar um proxy local ou utilizar modelos locais (via Ollama, llama.cpp com LLaVA).

### 7.2 Política de Retenção

| Aspecto | Padrão | Configurável |
|---------|--------|-------------|
| Armazenamento no provedor | Efêmero (não retido após resposta) | `ephemeralStorage` |
| Cache local de imagens | Limpo após sessão | `cacheDir` + TTL |
| Logs contendo descrições | Apenas texto extraído, sem imagem | `logLevel` |

### 7.3 Limites e Rate Limiting

- **Tamanho da imagem**: Máximo 20 MB por requisição (pré-processamento reduz para <5 MB).
- **Rate limit**: 60 requisições/minuto (OpenAI Tier 1), ajustável por provedor.
- **Custo**: Visão custa ~2-3× o custo de texto puro (tokenização de imagem). Use `detail: "low"` para tarefas que não exigem precisão visual.
- **Timeout**: 30 segundos por chamada de análise de imagem.

### 7.4 Mitigação de Riscos

| Risco | Mitigação |
|-------|-----------|
| Vazamento de PII via OCR | Filtragem pós-processamento: regex para CPF, RG, e-mail |
| Imagem corrompida | Validação de integridade no Stage 1 (checksum + header magic bytes) |
| Alucinação visual (descrição incorreta) | Múltiplas chamadas com self-consistency K=3 |
| Custo excessivo | Modo `detail: "low"` + limite de tokens por chamada |
| Ataque de prompt injection via imagem | Sanitização de texto extraído antes de alimentar downstream |

### 7.5 Configuração de Segurança Recomendada

```jsonc
{
  "vision": {
    "privacy": {
      "requireConsent": true,
      "allowedDomains": ["localhost", "*.trusted-source.com"],
      "blockedPatterns": ["cpf", "rg", "passport", "credit_card"],
      "autoRedact": true
    },
    "rateLimit": {
      "requestsPerMinute": 60,
      "burstSize": 10,
      "cooldownSeconds": 5
    },
    "costControl": {
      "defaultDetail": "auto",
      "maxImagesPerRequest": 5,
      "budgetAlert": "usd_10.00"
    }
  }
}
```

## 8. Exemplos de Uso

### 8.1 Análise de Diagrama de Arquitetura

```
Usuário: "/auto (entenda este diagrama de arquitetura)"
  + attachment: diagrama.png

Pipeline:
  1. Vision Router → detecta "diagrama" + imagem → VR01
  2. Pré-processamento → redimensiona para 2048px
  3. Vision MCP → GPT-4o com prompt VR01
  4. Extração → nodes, edges, relações
  5. Saída → descrição + grafo de dependências
```

### 8.2 Geração de Alt-Text para Artigo Científico

```
Usuário: "gere legenda ABNT para esta figura do artigo"
  + attachment: figura_cientifica.png

Pipeline:
  1. Vision Router → VR05 Figure-to-Description
  2. Image Analysis → descrição detalhada + termos técnicos
  3. Pós-processamento → formata como legenda ABNT (NBR 6023)
  4. Saída → "Figura 1 — Diagrama de blocos do sistema proposto..."
```

### 8.3 Screenshot-to-Code

```
Usuário: "reproduza esta tela em React com Tailwind"
  + attachment: screenshot.png

Pipeline:
  1. Vision Router → VR04 Screenshot-to-Code
  2. Análise → extrai layout, cores, tipografia, elementos
  3. Geração → código React + Tailwind + story
  4. Output → componente funcional + preview
```

### 8.4 Comparação de Versões (Regressão Visual)

```
Usuário: "compare a versão antiga com a nova e aponte diferenças"
  + attachment: antes.png, depois.png

Pipeline:
  1. Vision Router → VR08 Multi-Image Comparison
  2. Análise → detecção de diferenças pixel a pixel + semânticas
  3. Relatório → lista de mudanças: movidas, adicionadas, removidas
  4. Saída → diff visual anotado + sumário textual
```

## 9. Extensibilidade

### 9.1 Adicionar Novo Provedor de Visão

Para adicionar um novo provedor de visão (ex.: Amazon Bedrock, Mistral Pixtral, Anthropic Claude 4):

1. Adicionar entrada em `opencode.json` → `mcpServers.vision.provider`
2. Implementar adapter no Vision MCP seguindo a interface:

```typescript
interface VisionProviderAdapter {
  analyze(params: VisionParams): Promise<VisionResponse>;
  // VisionParams: { image, prompt, detail?, maxTokens?, temperature? }
  // VisionResponse: { description, structuredData?, extractedText?, confidence }
}
```

3. Registrar no Vision Router como novo handler.

### 9.2 Adicionar Novo Tipo de Raciocínio Visual

Para estender o catálogo VR (ex.: VR09 — Document Layout Analysis):

1. Adicionar entrada na tabela de tipos (seção 4)
2. Criar trigger no Vision Router
3. Definir template de prompt específico
4. Registrar no `reasoning-orchestrator` como novo reasoning type

## 10. Referências

- **[reasoning-orchestrator-v11](./skill/../reasoning-orchestrator-v11/SKILL.md)** — Integração com pipeline de raciocínio
- **[baoyu-imagine](./skill/../baoyu-skills/skills/baoyu-imagine/SKILL.md)** — Geração de imagem por prompt
- **[baoyu-diagram](./skill/../baoyu-skills/skills/baoyu-diagram/SKILL.md)** — Geração de diagramas SVG
- **[baoyu-infographic](./skill/../baoyu-skills/skills/baoyu-infographic/SKILL.md)** — Geração de infográficos
- **[baoyu-compress-image](./skill/../baoyu-skills/skills/baoyu-compress-image/SKILL.md)** — Compressão e pré-processamento de imagem
- **[baoyu-image-cards](./skill/../baoyu-skills/skills/baoyu-image-cards/SKILL.md)** — Geração de cards para redes sociais
- **[cora-debate](./skill/../cora-debate/SKILL.md)** — Debate multiagente com verificação simbólica
- **[agent-node-pipeline](./skill/../agent-node-pipeline/SKILL.md)** — Pipeline de processamento com nós tipados
- **OpenAI Vision API**: https://platform.openai.com/docs/guides/vision
- **Google Gemini Vision**: https://ai.google.dev/gemini-api/docs/vision
- **Anthropic Claude Vision**: https://docs.anthropic.com/en/docs/build-with-claude/vision
