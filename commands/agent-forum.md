# /agent-forum — Debate Multiagente com Moderador LLM

Comando para iniciar, gerenciar e concluir debates multiagente.

## Subcomandos

### `/agent-forum open <topic> [agents] [buffer_size] [language]`

Abre uma nova sessão de debate.

| Parâmetro    | Descrição                                | Obrigatório |
|--------------|------------------------------------------|-------------|
| topic        | Tópico central do debate                 | Sim         |
| agents       | Agentes participantes (separados por vírgula) | Não (padrão: "Scout,Analyst,Reviewer") |
| buffer_size  | Speeches por rodada antes do moderador   | Não (padrão: 5) |
| language     | Idioma das respostas                     | Não (padrão: pt-BR) |
| model        | Modelo LLM do moderador                  | Não (padrão: gpt-4) |

Exemplo:
```
/agent-forum open "Impacto da IA na educação" "Analytics,Ethics,Pedagogy"
```

### `/agent-forum publish <source> <content> [confidence] [stance]`

Agente publica um discurso no fórum ativo.

| Parâmetro  | Descrição                                  | Obrigatório |
|------------|--------------------------------------------|-------------|
| source     | Nome do agente                             | Sim         |
| content    | Texto do discurso (entre aspas)            | Sim         |
| confidence | Nível de confiança 0.0-1.0                 | Não (padrão: 0.5) |
| stance     | Posição: neutral, supportive, opposing     | Não (padrão: neutral) |

Exemplo:
```
/agent-forum publish Analytics "Dados mostram 40% de adoção em 2026" 0.8 supportive
```

### `/agent-forum conclude`

Força a conclusão da sessão atual e gera relatório final.

### `/agent-forum report`

Exibe o relatório JSON completo da sessão atual.

### `/agent-forum status`

Exibe o estado atual da sessão (estágio, total de discursos, agentes).

### `/agent-forum transcript`

Exibe o histórico completo de discursos da sessão atual.

### `/agent-forum close`

Fecha a sessão atual sem gerar relatório final.

## Exemplos

```
# Abrir debate
/agent-forum open "Regulamentação de IA no Brasil" "Legal,Tech,Ethics" 3

# Agentes publicam
/agent-forum publish Legal "Marco Legal da IA aprovado no Senado" 0.9 supportive
/agent-forum publish Tech "Desafios de implementação técnica persistem" 0.7 opposing

# Ver estado
/agent-forum status

# Concluir e obter relatório
/agent-forum conclude
/agent-forum report
```

## Retorno

O comando retorna JSON com:
- `status`: "ok" ou "error"
- `operation`: nome da operação
- `data`: dados da operação (discursos, estado, relatório)
- `error`: mensagem de erro (se aplicável)
