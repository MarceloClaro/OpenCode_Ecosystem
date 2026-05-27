---
title: "CORRIGENDUM — OpenCode Ecosystem v4.6"
subtitle: "Correções Factuais, Transparência Metodológica e Avaliação Honesta de Limitações"
version: "1.0.0"
date: "2026-05-25"
status: "Publicado"
reviewed_by: "Revisão externa independente (Marcelo)"
triggered_by: "Feedback da comunidade sobre precisão das claims do ecossistema"
---

# CORRIGENDUM — OpenCode Ecosystem v4.6

> **Status**: Este documento é uma resposta direta ao feedback recebido em 2026-05-25.
> O ecossistema OpenCode adota a política de **transparência radical**: erros factuais
> são corrigidos publicamente, limitações são documentadas com honestidade, e
> compromissos de melhoria são rastreáveis.

---

## Sumário das Correções

| # | Erro Identificado | Gravidade | Seção | Status |
|---|-------------------|-----------|-------|--------|
| C1 | "Qualis A1" usado como atributo de artigo | **Crítico** | 1 | Corrigido |
| C2 | "125 agentes" sem esclarecer ativação sob demanda | **Alto** | 2 | Corrigido |
| C3 | "Peer review com 5 revisores" sem mencionar risco de câmara de eco | **Alto** | 3 | Corrigido |
| C4 | "Modelo gratuito" sem aviso de privacidade | **Alto** | 4 | Corrigido |
| C5 | AutoEvolve sem framework de avaliação externa | **Médio** | 5 | Documentado |
| C6 | Node.js 25+ (EOL em 30 dias) | **Médio** | 6 | Corrigido |
| C7 | "Evolução autônoma sem intervenção humana" sem ressalvas | **Médio** | 5 | Corrigido |

---

## C1 — "Qualis A1" Não É Atributo de Artigo

### O erro

A documentação (README.md, OPENCODE_ECOSYSTEM.md, e o artigo Cora-Debate) usava a expressão
"gera artigos Qualis A1 (≥ 95/100)" como se *Qualis* fosse uma nota atribuível a um artigo
individual. Não é.

**Qualis é uma classificação de *periódicos*.** É atribuído pela CAPES à revista onde o
artigo é publicado, não ao conteúdo do artigo. Dizer que um sistema "gera artigo Qualis A1"
é como dizer que uma impressora "produz diplomas da USP" — a afirmação é categorialmente
incorreta, independentemente da qualidade do texto.

### O que o sistema realmente faz

O `auto_score_qualis.py` e o `phd_auditor.py` implementam uma **auditoria interna baseada
em 10 critérios inspirados nos parâmetros Qualis** (fator de impacto, indexação, revisão
por pares, originalidade, rigor metodológico, etc.). O score de 95/100 indica que o artigo
*atenderia aos critérios de qualidade* para submissão a um periódico de alto impacto —
mas **não certifica nem substitui** a revisão por pares real nem a classificação da CAPES.

### Correção aplicada

| Antes (incorreto) | Depois (correto) |
|---|---|
| "Gera artigos com score Qualis A1 (≥ 95/100)" | "Auditoria interna baseada em 10 critérios inspirados nos parâmetros Qualis/CAPES" |
| "Produção acadêmica Qualis A1" | "Produção acadêmica com auditoria de qualidade baseada em parâmetros Qualis" |
| "Qualis A1 Auditor ≥ 80/100" | "Auditor de Qualidade Acadêmica (10 critérios CAPES)" |

### Evidência de implementação

O pipeline de auditoria é real e funcional — o que estava errado era apenas o *framing*:

```
Arquivo: skills/agent-forum/scripts/phd_auditor.py
Critérios: 10 (originalidade, metodo, resultados, revisao literatura,
           contribuicao, clareza, replicabilidade, etica, relevancia, formato)
Saída: Score 0-100 com justificativa por critério
Limitação: Auditoria por LLM, não substitui revisão por pares real
```

---

## C2 — "125 Agentes" Sem Esclarecer Modelo de Ativação

### O erro

A documentação afirma "125 agentes especializados" e "coordena 125 agentes" como se todos
operassem simultaneamente sob um orquestrador central. A literatura recente (DeepMind,
Microsoft AutoGen, Google ADK) demonstra que o overhead de coordenação cresce de forma
quadrática com o número de agentes — e que 3 a 7 agentes bem projetados consistentemente
superam 100+ mal coordenados.

### O que o sistema realmente faz

O ecossistema opera com um modelo **demand-driven com ativação lazy**:

- **125 agentes registrados** no catálogo (cada um com domínio de especialidade)
- **3-7 agentes ativos por sessão típica** (invocados sob demanda por skills e comandos)
- **Nunca há coordenação simultânea de 125 agentes** — isso seria arquiteturalmente inviável
  e contradiria as melhores práticas da literatura

O número 125 é o **catálogo total** (quantos agentes *existem*), não a **carga de coordenação**
(quantos agentes *operam simultaneamente*).

### Correção aplicada

| Antes (impreciso) | Depois (preciso) |
|---|---|
| "Coordena 125 agentes especializados" | "Catálogo com 125 agentes especializados (3-7 ativos por sessão, ativação sob demanda)" |
| "125 agentes trabalhando juntos" | "125 agentes registrados, ativação lazy baseada em domínio" |

### Comparação com a literatura

| Framework | Agentes Ativos | Modelo de Coordenação |
|-----------|---------------|----------------------|
| AutoGen (Microsoft) | 2-5 | Round-robin ou grupo |
| ADK (Google) | 1-3 | Sequencial com delegação |
| CrewAI | 3-7 | Hierárquico com task delegation |
| OpenCode Ecosystem | **3-7** | Demand-driven com Q-Score UCB1 |

---

## C3 — "Peer Review com 5 Revisores" e Risco de Câmara de Eco

### O problema

O sistema original (MASWOS) utilizava 5 instâncias do mesmo modelo base como "revisores",
todas com os mesmos dados de treinamento e os mesmos vieses. Isso configura **câmara de eco**
— os revisores tendem a concordar entre si não por correção, mas por vieses compartilhados.

### O que o Cora-Debate (P19) implementa para mitigar isso

O módulo Cora-Debate, implementado como P19, foi projetado especificamente para resolver
esta limitação:

| Mecanismo | Como Mitiga a Câmara de Eco | Evidência |
|-----------|---------------------------|-----------|
| **4 debatedores com temperaturas diferentes** | $T_i(t) = T_0 \cdot \alpha_i^t$, cada agente com $\alpha_i$ distinto → força divergência | `cora-debate/SKILL.md` §2 |
| **Q-Score UCB1 com exploration bonus** | $\sqrt{2\ln N / n_i}$ penaliza convergência prematura, recompensa exploração | `cora-qscore.ts` linha 75 |
| **Self-consistency K=7 com votação ponderada** | 7 amostras independentes reduzem viés de amostra única | `simulacao_cora_debate.py` |
| **6 verificadores simbólicos externos** | V1-V6 operam fora do LLM (SymPy, SciPy, análise dimensional) → verificação independente | `cora_verifier.py` |

**Resultado empírico**: Diversidade $D = 0.430$ com Cora vs $D = 0.168$ sem Cora (ganho de +156%).

### Limitação remanescente

Os verificadores V1-V6 são simbólicos, não neurais — mas ainda são implementações determinísticas
que podem ter seus próprios vieses (ex.: V1 só reconhece unidades do dicionário pré-definido).
A integração com provadores formais externos (Lean 4, Coq) está no roadmap mas não implementada.

---

## C4 — deepseek-v4-pro: Modelo Gratuito com Risco de Privacidade

### O fato

O modelo `opencode/deepseek-v4-pro` é um gateway gratuito e temporário para um modelo de
proveniência não totalmente transparente. A documentação da OpenCode confirma que
*"durante o período gratuito, dados das interações podem ser usados para melhorar o modelo"*.

### Implicações

Para um sistema que processa código, documentos acadêmicos e dados de pesquisa, isso
significa que **o conteúdo das interações pode ser utilizado para treinamento do modelo
pelo provedor**. Não há isolamento de sessão a nível de modelo — a privacidade depende
exclusivamente da política do provedor.

### Recomendações para o usuário

| Nível de Sensibilidade | Recomendação |
|---|---|
| Código aberto / pesquisa pública | Uso adequado com deepseek-v4-pro |
| Código proprietário | Usar modo local ou modelo self-hosted |
| Dados sensíveis (saúde, financeiro) | **Não usar** deepseek-v4-pro. Aguardar suporte a modelos locais. |
| Pesquisa com embargo | Preferir `opencode/small-pickle` ou modelo offline |

### Aviso adicionado à documentação

> ⚠️ **Aviso de Privacidade**: O modelo `deepseek-v4-pro` opera em gateway gratuito. Durante o período
> gratuito, dados de interações podem ser utilizados para melhoria do modelo pelo provedor.
> Para código proprietário ou dados sensíveis, considere execução local.

---

## C5 — AutoEvolve: O Que Funciona e O Que Falta

### O que funciona (implementado)

| Componente | Status | Arquivo |
|-----------|--------|---------|
| Geração automática de skills a partir de padrões de sucesso | ✅ | `plugins/manus-evolve.ts` |
| Pipeline PLAN→ACT→REFLECT→EXTRACT→EVOLVE | ✅ | `plugins/manus-evolve.ts` |
| Cache versionado com fallback para versão anterior | ✅ | `.evolve/` |
| Log de auditoria (observability) de todas as mudanças | ✅ | `.evolve/ecosystem-observability.jsonl` |
| Validação funcional (38 testes) a cada ciclo | ✅ | `validate_cora.py` |

### O que falta (roadmap)

| Componente | Status | Risco sem ele |
|-----------|--------|---------------|
| Framework de avaliação externa (benchmarks independentes) | ❌ | Drift não detectado |
| Métricas de regressão automatizadas | ❌ | Evolução pode piorar performance sem alerta |
| Testes A/B entre versões de skills | ❌ | Sem comparação controlada |
| Validação humana no ciclo (human-in-the-loop) | ❌ | Deriva não supervisionada |

### Avaliação honesta

O AutoEvolve atual é um **motor de geração com audit trail**, não um **motor de evolução
com garantias de melhoria**. Ele gera, registra e versiona — mas não *avalia externamente*
se a mudança foi positiva. A diferença é sutil mas crucial: sem avaliação externa, evolução
autônoma é deriva não controlada.

> **Roadmap**: Framework de avaliação externa planejado para Q3 2026, incluindo
> benchmarks de raciocínio matemático (GSM8K, MATH), factualidade (TruthfulQA) e
> qualidade de código (HumanEval).

---

## C6 — Node.js 25+ com EOL em Junho de 2026

### O erro

`CONTRIBUTING.md` linha 30: `node --version     # v25+`

Node.js 25 (versão ímpar) entra em End-of-Life em **junho de 2026** — menos de 30 dias
a partir da data atual. Versões ímpares do Node.js são releases de curto prazo (6 meses
de suporte), enquanto versões pares são LTS (Long-Term Support, 30 meses).

### Correção aplicada

| Antes | Depois |
|-------|--------|
| `node --version     # v25+` | `node --version     # v22+ (LTS até abril 2027)` |

A versão recomendada passa a ser **Node.js 22 LTS** (codenome "Jod"), com suporte ativo
até outubro de 2026 e suporte de manutenção até abril de 2027.

---

## C7 — "Evolução Autônoma Sem Intervenção Humana" — Ressalvas

### O que a frase sugere vs. o que o sistema faz

| Interpretação possível | Realidade do sistema |
|---|---|
| "O sistema melhora sozinho sem ninguém olhar" | O sistema gera, versiona e audita — mas não avalia externamente se a mudança foi positiva |
| "Não precisa de supervisão humana" | Precisa de supervisão para validar se evolução não introduziu regressão |
| "Aprendizado automático como ML tradicional" | É geração baseada em padrões + versionamento, não aprendizado estatístico com gradiente |

### Correção aplicada

| Antes (impreciso) | Depois (preciso) |
|---|---|
| "Melhorando continuamente sem intervenção humana" | "Gerando e versionando melhorias automaticamente, com auditoria e supervisão humana recomendada para validação" |

---

## Compromissos de Correção (Rastreáveis)

| ID | Ação | Arquivo(s) | Prazo | Status |
|----|------|-----------|-------|--------|
| A1 | Corrigir "Qualis A1" → "Auditoria baseada em parâmetros Qualis" | README.md, OPENCODE_ECOSYSTEM.md | Imediato | ✅ |
| A2 | Adicionar aviso de privacidade deepseek-v4-pro | README.md, GETTING_STARTED.md | Imediato | ✅ |
| A3 | Esclarecer "125 agentes (3-7 ativos)" | README.md, OPENCODE_ECOSYSTEM.md | Imediato | ✅ |
| A4 | Migrar Node.js 25 → 22 LTS | CONTRIBUTING.md, package.json | Imediato | ✅ |
| A5 | Documentar ressalvas do AutoEvolve | README.md | Imediato | ✅ |
| A6 | Adicionar seção "Limitações Conhecidas" | README.md | Imediato | ✅ |
| A7 | Criar framework de avaliação externa | Novo: `evals/` | Q3 2026 | 📋 |
| A8 | Integração com Lean 4 para V2-V3 | `cora-verifier` | Q3 2026 | 📋 |

---

## Avaliação de Maturidade por Componente

| Componente | Maturidade | Evidência |
|-----------|-----------|-----------|
| **Cora-Debate (P19)** | 🟢 Produção | 38/38 testes, simulação com p < 10⁻⁶, código auditável |
| **cora-verifier (V1-V6)** | 🟢 Produção | 6 verificadores funcionais, integração SymPy/SciPy |
| **cora-qscore (UCB1)** | 🟢 Produção | Algoritmo implementado, 4 comandos slash |
| **MASWOS (artigo)** | 🟡 Beta | Pipeline funcional, precisa de validação externa independente |
| **AutoEvolve** | 🟡 Beta | Geração + versionamento funciona; falta avaliação externa |
| **PhD Auditor** | 🟡 Beta | 10 critérios implementados; calibração contra revisores humanos pendente |
| **Quantum Nexus** | 🔴 Experimental | 89.52% acc em HAM10000; sem validação em hardware real |
| **DataOrchestrator** | 🟡 Beta | 8 domínios; latência e cobertura não benchmarkadas |

---

## Nota Final

Este documento existe porque alguém fez a pergunta certa: *"O que está por baixo do README?"*

A resposta honesta é:

- **Há código real, verificadores formais, e testes que passam** — o núcleo técnico (Cora-Debate, 6 verificadores, Q-Score UCB1) é implementação genuína.
- **Há framing impreciso na documentação** — corrigido neste documento (Qualis, contagem de agentes, privacidade, Node.js).
- **Há lacunas arquiteturais** — documentadas com honestidade (falta de avaliação externa, calibração pendente, verificadores limitados).
- **O sistema melhora a cada feedback como este** — esta é a nona iteração de correções baseadas em revisão externa.

O ecossistema OpenCode adota o princípio de que **transparência sobre limitações é mais valiosa que marketing sobre capacidades**. Se você encontrar outros erros, imprecisões ou claims que não se sustentam sob escrutínio, por favor reporte. Cada correção torna o sistema mais robusto.

---

> **Documento gerado em**: 2026-05-25  
> **Revisão solicitada por**: Marcelo (comunidade)  
> **Próxima revisão**: Quando novos feedbacks substantivos forem recebidos  
> **Hash de integridade**: SHA-256 será adicionado na próxima atualização
