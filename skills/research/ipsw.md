<!-- SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL -->
<!-- Toda resposta ao usuário DEVE ser em português do Brasil formal. -->
<!-- Contexto em chinês para eficiência de tokens. Responda em PT-BR formal. -->
<!-- Modelo: deepseek-v4-pro -->

---
name: ipsw
description: Core Commands
version: 1.0.0
author: ecosystem
category: research
inspired_by: deer-flow 2.0 / opencode
compatibility: deepseek-v4-pro
migrated_at: 2026-05-07 06:10:30
---

# Ipsw

# Core Commands
- **Firmware:** `ipsw download ipsw --device <ID> --latest`
- **DSC:** `ipsw dyld a2s|symaddr|disass|xref|dump|str|extract`
- **Kernel:** `ipsw kernel kexts|extract|syscall`
- **Entitlements:** `ipsw ent --sqlite ent.db --key "com.apple.*"`
- **Class Dump:** `ipsw class-dump|swift-dump`
- **Sandbox:** `ipsw sb list|dec|opts|graph|query`
- **Diff:** `ipsw diff old.ipsw new.ipsw --output ./diff/`
- **Symbolicate:** `ipsw symbolicate panic.ips firmware.ipsw`

More: https://github.com/blacktop/ipsw-skill

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
