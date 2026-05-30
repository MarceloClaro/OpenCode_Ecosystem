---
name: progressive-disclosure-design
description: "Design de skills com progressive disclosure: entrypoint magro (<2.5kt), carregamento sob demanda de aprofundamentos, token budget controlado. Inspirado em samber/cc-skills e agent-skills.io."
---

# Progressive Disclosure Design para Skills OpenCode

## Principios

Skills do ecossistema OpenCode seguem o principio de **progressive disclosure**: o SKILL.md e um entrypoint magro que carrega apenas o essencial no contexto, com referencias a arquivos secundarios para aprofundamento sob demanda.

## Token Budget

| Componente | Limite | Descricao |
|-----------|--------|-----------|
| `description` (frontmatter) | ~100 tokens | Gatilho de ativacao - deve conter palavras-chave precisas |
| `SKILL.md` (entrypoint) | 1.000 - 2.500 tokens | Instrucoes essenciais, estrutura, referencias |
| Diretorio completo | < 10.000 tokens | SKILL.md + arquivos secundarios |
| Skills carregadas simultaneas | 2 - 4 | Mantem contexto < 10kt total carregado |

## Estrutura Recomendada

```
skills/<categoria>/<skill-name>/
  SKILL.md                  # Entrypoint (<2.5kt)
  references/               # Aprofundamentos (carga sob demanda)
    methodology.md
    examples.md
    troubleshooting.md
  templates/                # Templates (carga quando solicitado)
    template-1.md
```

## Regras de Design

1. **SKILL.md e o unico arquivo carregado automaticamente** - todo o resto e sob demanda
2. **Use paths relativos** - `[Metodologia](./references/methodology.md)` - o modelo carrega quando relevante
3. **Frontmatter description e o gatilho principal** - ajuste fino por palavras-chave para ativacao precisa
4. **Skills atomicas** - uma skill, um dominio. Skills complexas usam sub-skills ou referencias
5. **Dependencias explicitas** - se uma skill depende de outra, declare no frontmatter com `depends_on: [skill-name]`
6. **Token budget rigido** - descriptions ~100t, SKILL.md 1k-2.5kt, total <10kt

## Template SKILL.md

```yaml
---
name: my-skill-name
description: "Descricao precisa em ~100 tokens para ativacao correta. Inclua palavras-chave do dominio."
depends_on: []
---
# My Skill Name

## Visao Geral
<contexto essencial - 2-3 paragrafos>

## Quando Usar
- <criterio 1>
- <criterio 2>

## Workflow
1. <passo 1>
2. <passo 2>

## Referencias
- [Aprofundamento 1](./references/deep-dive-1.md)
- [Template X](./templates/template-x.md)

## Regras Criticas
- <regra 1>
- <regra 2>
```

## Metricas de Qualidade

| Indicador | Alvo | Medicao |
|-----------|------|---------|
| SKILL.md tokens | < 2.500 | Contagem de tokens do modelo |
| Description tokens | ~100 | Frontmatter YAML description |
| Taxa de ativacao | > 80% | Proporcao de ativacoes corretas vs. total |
| Tokens carregados por sessao | < 10.000 | Soma de todos os SKILL.md carregados |
| Dependencias circulares | 0 | Verificacao em sync |
