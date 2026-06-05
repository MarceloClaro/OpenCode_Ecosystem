<!-- SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL -->
<!-- Toda resposta ao usuário DEVE ser em português do Brasil formal. -->
<!-- Contexto em chinês para eficiência de tokens. Responda em PT-BR formal. -->
<!-- Modelo: deepseek-v4-pro -->

---
name: preferencias-usuario-escrita-academica
description: Formatação e Pontuação
version: 1.0.0
author: ecosystem
category: research
inspired_by: deer-flow 2.0 / opencode
compatibility: deepseek-v4-pro
migrated_at: 2026-05-07 06:10:30
---

# Preferencias Usuario Escrita Academica

# Formatação e Pontuação

- **Travessão (—):** Absolutamente proibido. Use vírgulas, parênteses ou reescreva a frase.
- **Ponto e Vírgula (;):** Deve ser evitado completamente.
- **Dois Pontos (:):** Use apenas em listas formais ou citações diretas.
- **Estrutura de Frases:** Não inicie parágrafos com "além disso", "contudo", "portanto". Máximo 25 palavras por frase.
- **Negrito:** Use apenas para o termo definido na primeira frase. Nunca para enfatizar palavras no meio do texto.
- **Variação Elegante Excessiva:** Não use múltiplos sinônimos para o mesmo conceito em parágrafos consecutivos. Clareza supera variedade. Repita o termo mais preciso quando necessário.

## Workflow

### Step 1: Definir escopo
Identifique tema, fontes e criterios.

### Step 2: Coletar dados
Utilize ferramentas de busca.

### Step 3: Analisar
Processe dados, identifique padroes.

### Step 4: Gerar output
Produza resultado final.

## Best Practices

1. Citar fontes verificaveis (DOIs, URLs)
2. Cruzar informacoes de 2+ fontes
3. Manter registro de buscas
4. Validar dados antes do output
5. Saida em PT-BR formal

## Integration

| Component | Type | Connection |
|-----------|------|------------|
| scihub | MCP | Download artigos |
| websearch | MCP | Busca web |
| context7 | MCP | Documentacao |
