<!-- SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL -->
<!-- Toda resposta ao usuário DEVE ser em português do Brasil formal. -->
<!-- Contexto em chinês para eficiência de tokens. Responda em PT-BR formal. -->
<!-- Modelo: deepseek-v4-pro -->

---
name: video-creator
description: 1. Gera/obtém imagens
version: 1.0.0
author: ecosystem
category: content
inspired_by: deer-flow 2.0 / opencode
compatibility: deepseek-v4-pro
migrated_at: 2026-05-07 06:10:30
---

# Video Creator

# Fluxo
1. Gera/obtém imagens
2. Gera áudio TTS por cena
3. Divide cenas com `scene_splitter.py`
4. Compõe vídeo final com `video_maker.py`

Source: opencode-skills-main/video-creator

## Workflow

### Step 1: Planejar
Defina estrutura e publico-alvo.

### Step 2: Criar
Produza conteudo base.

### Step 3: Revisar
Aplique correcoes.

### Step 4: Exportar
Gere output final.

## Best Practices

1. Tom de voz consistente
2. Revisar gramatica
3. Formatacao Markdown
4. Incluir frontmatter
5. PT-BR formal

## Integration

| Component | Type | Connection |
|-----------|------|------------|
| websearch | MCP | Pesquisa |
| pdf | Tool | Extracao PDF |
| ptbr_corrector | Tool | Correcao |
