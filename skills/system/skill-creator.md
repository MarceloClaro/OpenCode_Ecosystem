<!-- SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL -->
<!-- Toda resposta ao usuário DEVE ser em português do Brasil formal. -->
<!-- Contexto em chinês para eficiência de tokens. Responda em PT-BR formal. -->
<!-- Modelo: deepseek-v4-pro -->

---
name: skill-creator
description: Estrutura Padrão
version: 1.0.0
author: ecosystem
category: system
inspired_by: deer-flow 2.0 / opencode
compatibility: deepseek-v4-pro
migrated_at: 2026-05-07 06:10:30
---

# Skill Creator

# Estrutura Padrão
```
skill-name/
├── SKILL.md        (frontmatter + instruções)
├── README.md       (documentação)
├── scripts/        (Python/JS executáveis)
├── references/     (documentos de apoio)
└── templates/      (modelos reutilizáveis)
```

Scripts: `init_skill.py` (criar nova skill), `package_skill.py` (empacotar)

Source: opencode-skills-main/skill-creator

## Workflow

### Step 1: Identificar
Analise contexto e defina escopo.

### Step 2: Implementar
Aplique modificacoes.

### Step 3: Validar
Execute testes.

### Step 4: Documentar
Registre alteracoes.

## Best Practices

1. Backup antes de modificar
2. Validar com testes
3. Manter logs
4. Documentar decisoes
5. Seguir padroes

## Integration

| Component | Type | Connection |
|-----------|------|------------|
| sync_orchestrator | Script | Sincronizacao |
| memory | MCP | Contexto |
| filesystem | MCP | Arquivos |
