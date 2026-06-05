# SPEC-09: CrossPlatformValidator (P3)

> Lacuna 9: Teste automatizado de portabilidade de skills entre plataformas

## Plataformas Alvo

| Plataforma | Skill Path | Comando de Invocacao |
|------------|-----------|---------------------|
| Claude Code | `.claude/skills/` | `claude` |
| Codex (OpenAI) | `.agents/skills/` ou `.codex/skills/` | `codex` |
| Antigravity (Google) | `.agents/skills/` | `antigravity` |

## Pipeline de Validacao

```
Skill (SKILL.md)
      │
      ▼
[1] Copia skill para cada plataforma
      │
      ├──► .claude/skills/<name>/SKILL.md
      ├──► .agents/skills/<name>/SKILL.md
      └──► .agents/skills/<name>/SKILL.md  (antigravity)
      │
      ▼
[2] Executa tarefa padrao em cada plataforma
      │
      ├──► Claude Code: "Execute a tarefa descrita na skill <name>"
      ├──► Codex: "Execute a tarefa descrita na skill <name>"
      └──► Antigravity: "Execute a tarefa descrita na skill <name>"
      │
      ▼
[3] Coleta saidas e compara
      │
      ▼
[4] Relatorio de portabilidade

Portability Score = (plataformas_compativeis / total_plataformas) * 100
```

## Criterios de Compatibilidade

| Criterio | Peso | Verificacao |
|----------|------|-------------|
| Estrutura de saida identica | 30% | diff JSON/YAML |
| Comportamento funcional identico | 40% | test suite comum |
| Tempo de execucao comparavel | 15% | ±20% entre plataformas |
| Tokens consumidos comparaveis | 10% | ±30% entre plataformas |
| Tratamento de erros consistente | 5% | mesmo tipo de erro nas 3 |

## Integracao com CI/CD

```yaml
# .github/workflows/cross-platform.yml
cross-platform-validation:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    - name: Validate all skills
      run: python swe-eval-v1/cross_platform/validator.py --all
    - name: Report
      run: python swe-eval-v1/cross_platform/report.py --format markdown
```
