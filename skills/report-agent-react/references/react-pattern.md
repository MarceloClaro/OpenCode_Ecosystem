# Padrão ReACT + Reflection — Referência Detalhada

## O Ciclo ReACT

O padrão **ReACT (Reasoning + Acting)** permite que um agente de IA
raciocine e aja iterativamente, coletando informações antes de produzir
uma resposta final.

### Estrutura de cada turno

```
Thought: O que preciso descobrir? Qual informação está faltando?
Action: insight_forge(query="...") | panorama_search(query="...") | quick_search(query="...")
Observation: [Resultado da ferramenta]
[Repetir até informação suficiente]
Final Answer: [Conteúdo gerado]
```

### Exemplo prático

```
Thought: Preciso entender como a regulação de IA afetou as empresas
de tecnologia no cenário simulado.

Action: insight_forge(query="Impacto da regulação de IA em big techs")

Observation: Encontrados 15 fatos sobre reações de empresas...
- "Google anunciou conformidade com novas regras"
- "Startups de IA expressaram preocupação com custos"
- etc.

Thought: Ótimo, agora preciso de dados temporais...

Action: panorama_search(query="regulação IA timeline")

Observation: 8 fatos ativos, 3 históricos...

Thought: Informação suficiente. Vou gerar a seção.

Final Answer: [Conteúdo da seção em markdown]
```

## Reflexão em 3 Dimensões

### 1. Consistência (score 0-1)

Verifica:
- Contradições entre fatos citados
- Alinhamento com o contexto da simulação
- Coerência entre seções

### 2. Autocorreção

Ações:
- Remove conteúdo não suportado por dados
- Corrige imprecisões factuais
- Ajusta tom e escopo

### 3. Lacunas

Identifica:
- Perguntas do sumário não respondidas
- Dados mencionados mas não verificados
- Perspectivas não consideradas

## Boas Práticas

1. **Misturar ferramentas**: não use apenas uma estratégia de busca
2. **Mínimo 3 tool calls por seção**: garante profundidade
3. **Citar fatos literais**: use aspas para dados do grafo
4. **Refletir sempre**: nunca pule a fase de reflexão
