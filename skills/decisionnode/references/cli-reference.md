# DecisionNode — CLI Reference

## Inicialização

| Comando | Descrição |
|---------|-----------|
| `decide init` | Inicializar store no projeto atual |
| `decide setup` | Configurar Gemini API key |
| `decide config` | Ver/configurar configurações |

## Gerenciamento de Decisões

| Comando | Descrição |
|---------|-----------|
| `decide add` | Adicionar (modo interativo) |
| `decide add -s <scope> -d "<decision>"` | Adicionar inline |
| `decide add -s <scope> -d "<d>" -r "<r>" -c "<c>"` | Com rationale e constraints |
| `decide add --global -s <scope> -d "<d>"` | Decisão global (todos projetos) |
| `decide list` | Listar todas (inclui globais) |
| `decide list --status deprecated` | Listar apenas depreciadas |
| `decide get <id>` | Ver decisão específica |
| `decide search "<query>"` | Busca semântica |
| `decide edit <id>` | Editar (interativo) |
| `decide edit <id> -f` | Editar (sem confirmação global) |
| `decide deprecate <id>` | Soft-delete (reversível) |
| `decide activate <id>` | Reativar decisão depreciada |
| `decide delete <id>` | Remover permanentemente |
| `decide delete <id> -f` | Remover sem confirmação |
| `decide delete-scope "<scope>"` | Remover escopo inteiro |

## Dados

| Comando | Descrição |
|---------|-----------|
| `decide export <json\|md\|csv>` | Exportar decisões |
| `decide import <file.json>` | Importar de JSON |
| `decide check` | Mostrar decisões sem embedding |
| `decide embed` | Embedar decisões pendentes |
| `decide clean` | Remover vetores órfãos |
| `decide history` | Log de atividades |
| `decide projects` | Listar todos projetos |

## Visualização

| Comando | Descrição |
|---------|-----------|
| `decide ui` | Web UI (foreground) |
| `decide ui -d` | Web UI (background) |
| `decide ui stop` | Parar servidor |
| `decide ui status` | Status do servidor |

Docs completos: [decisionnode.dev/docs](https://decisionnode.dev/docs)
