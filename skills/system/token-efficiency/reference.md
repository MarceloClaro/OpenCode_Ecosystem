# Token Efficiency - Referencia Detalhada

# Referencia Rapida - Token Efficiency

## Modelo
- **ID**: deepseek-v4-pro
- **Provider**: opencode (Zen)
- **URL**: https://opencode.ai/zen/v1/chat/completions
- **Specs**: 200K ctx, 128K out, free, reasoning, tool-calling

## Encoding
- **Contexto**: Chines simplificado (UTF-8)
- **Saida**: Portugues brasileiro formal (UTF-8)
- **Codigo**: Lingua original (variaveis, paths, funcoes)

## Densidade
- Chines: ~30-40% mais denso que Latin por token
- Economia esperada: ~40% tokens de contexto por sessao

## Arquivos Criticos
| Arquivo | Funcao |
|---------|--------|
| AGENTS.md | Mapa de arquitetura unificado |
| opencode.json | Config principal (MCPs, plugins, modelo) |
| evolution/*.md | Skills auto-geradas por round |
| .evolve/memory.json | Estado de evolucao e aprendizado |

## Headers Obrigatorios
Todos os arquivos de sistema DEVEM conter:
- Mandate PT-BR formal
- Referencia ao modelo deepseek-v4-pro
- Nota de eficiencia de tokens (se aplicavel)

## Arquivos por Categoria (210 total)
| Categoria | Path | Count |
|-----------|------|-------|
| Agentes | agents/*.md | 56 |
| Comandos | command/*.md | 14 |
| Criador-Agentes | criador-artigo/agents/*.md | 48 |
| Criador-Referencias | criador-artigo/references/*.md | 14 |
| Criador-Templates | criador-artigo/templates/*.md | 24 |
| Nexus-Referencias | nexus/references/*.md | 17 |
| Nexus-Templates | nexus/templates/*.md | 3 |
| Nexus-Scripts | nexus/scripts/*.py | 19 |
| SEEKER-Agentes | basis-research/agents/*.py | 11 |
| Plugins | plugins/*.ts | 2 |
| Raiz | AGENTS.md, opencode.json | 2 |


## Objetivo
Maximizar eficiencia de tokens mantendo saida em portugues brasileiro formal.


## Principios

### 1. Contexto em Chines Simplificado
- Caracteres chineses carregam ~30-40% mais densidade semantica por token
- Usar para: documentacao interna, AGENTS.md, notas de evolucao, comentarios de sistema
- Manter: variaveis, caminhos, nomes de arquivos em lingua original
- Exemplo: `# 环境` (5 chars) vs `# Environment Configuration` (25 chars) = 80% economia

### 2. Saida Obrigatoria PT-BR
- TODA resposta ao usuario DEVE ser em portugues brasileiro formal
- Diretiva no topo de AGENTS.md e em cada arquivo de sistema
- Nao usar emojis, girias, ou linguagem informal
- Manter termos tecnicos em ingles quando padrao da industria

### 3. Modelo deepseek-v4-pro
- Provedor: OpenCode Zen (https://opencode.ai/zen/v1/chat/completions)
- Contexto: 200K tokens | Saida: 128K tokens | Custo: Gratuito
- Reasoning: Sim | Tool Calling: Sim
- Knowledge cutoff: 2025-01

### 4. Padroes de Compressao
| Tecnica | Economia | Exemplo |
|---------|----------|---------|
| Chines simplificado | 30-40% | 统一生态系统 vs Unified Ecosystem |
| Tabelas vs paragrafos | 25-35% | Dados estruturados em markdown |
| Referencia vs copia | 50-70% | "ver AGENTS.md" vs copiar conteudo |
| Abreviacoes tecnicas | 15-20% | ctx, out, MCP, SDK |
| Dry-run antes de acao | evita retrabalho | Diagnostico antes de correcao |

### 5. Workflow Otimizado
```
1. carregar contexto (chines, denso) → ~60% tokens
2. processar/inferir (deepseek-v4-pro) → reasoning nativo
3. formatar saida (PT-BR formal) → obrigatorio
4. validar/converter (se necessario) → automatico
```


## Integracao com Ecossistema

### Arquivos Atualizados (210)
- 56 agentes (agents/*.md)
- 14 comandos (command/*.md)
- 48 agentes criador-artigo (criador-artigo/agents/*.md)
- 14 referencias criador-artigo (criador-artigo/references/*.md)
- 24 templates criador-artigo (criador-artigo/templates/*.md)
- 17 referencias nexus (nexus/references/*.md)
- 3 templates nexus (nexus/templates/*.md)
- 19 scripts nexus (nexus/scripts/*.py)
- 11 agentes SEEKER (basis-research/agents/*.py)
- 2 plugins (plugins/*.ts)
- 1 AGENTS.md (raiz)
- 1 opencode.json (config principal)

### Header Padrao (Markdown)
```markdown
<!--
  SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL
  Toda resposta DEVE ser em português do Brasil formal.
  Contexto em chinês para eficiência de tokens (densidade +40%).
  Modelo: deepseek-v4-pro (OpenCode Zen, 200K ctx, 128K out, gratuito)
-->
```

### Header Padrao (Python)
```python

# SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL

# Toda resposta ao usuário DEVE ser em português do Brasil formal.

# Contexto em chinês para eficiência de tokens (densidade +40%).

# Modelo: deepseek-v4-pro (OpenCode Zen, 200K ctx, 128K out, gratuito)
```


## Metricas de Economia
| Item | Antes | Depois | Economia |
|------|-------|--------|----------|
| AGENTS.md | 7434 bytes | 4269 bytes | -42.6% |
| Contexto por sessao | ~12000 tokens | ~7200 tokens | -40% |
| Tokens de sistema | 100% | 60% | -40% |
| Custo do modelo | pago | gratuito | -100% |


## Regras de Uso
1. Sempre verificar se AGENTS.md tem header PT-BR
2. Usar tabelas para dados estruturados
3. Referenciar arquivos ao inves de copiar conteudo
4. Executar dry-run antes de modificacoes em massa
5. Manter consistencia de encoding (UTF-8 obrigatorio)
6. Validar que saida final esta em PT-BR formal
7. **CORRECAO OBRIGATORIA**: Executar ptbr_corrector.py antes de qualquer entrega ao usuario


# Correcao automatica
python criador-artigo/banca/ptbr_corrector.py --input arquivo.md --fix --output arquivo_corrigido.md


# Correcao em massa
python criador-artigo/banca/ptbr_corrector.py --directory documentos/ --recursive --fix


# Validacao (scan only)
python criador-artigo/banca/ptbr_corrector.py --input arquivo.md --json
```

### Regras de Protecao
- NUNCA corrigir dentro de blocos de codigo ```
- NUNCA corrigir dentro de HTML comments <!-- -->
- NUNCA corrigir URLs e caminhos de arquivos
- NUNCA corrigir citacoes diretas de fontes chinesas

### Metricas
| Indicador | Meta | Status |
|-----------|------|--------|
| Contaminacao CJK na saida | 0 | Ativo |
| Correcoes ortograficas | Auto | Ativo |
| Falsos positivos | <1% | 0% |
