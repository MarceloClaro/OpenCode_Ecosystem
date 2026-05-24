# 🎯 Estratégias de Economia de Tokens (OpenCode Ecosystem)

O OpenCode Ecosystem foi especificamente projetado para minimizar o consumo de tokens através de múltiplas estratégias de otimização. O Manus deve seguir estas 7 estratégias para garantir a máxima eficiência no uso de tokens:

## 1. Contexto em Chinês (+40% Densidade)
O sistema armazena contexto interno em chinês, que tem 40% mais densidade informacional que português ou inglês, mas o output ao usuário é sempre em PT-BR formal. Isso significa que a mesma quantidade de informação cabe em menos tokens.

## 2. Progressive Disclosure
Cada skill tem um arquivo `SKILL.md` com máximo de 2.500 bytes, enquanto o conteúdo detalhado reside em `references/*.md`. Isso reduz drasticamente o contexto carregado inicialmente.

## 3. Edição Cirúrgica
O princípio central da skill `edicao-cirurgica` é retornar apenas o delta - o bloco que mudou, nunca reescrever o artefato inteiro. Isso preserva contexto e reduz consumo de tokens.

## 4. Sistema de 3 Níveis de Publicação
O ecossistema adapta o uso de tokens ao objetivo:

| Nível | Agentes | Economia de Tokens |
| :--- | :--- | :--- |
| Nível 1 (Magnum/Tese/Qualis A1) | 43 agentes | Nenhuma economia (rigor máximo) |
| Nível 2 (Standard Paper/Q1-Q2) | ~20 agentes | Eficiência de tempo exigida |
| Nível 3 (Short Communication) | Max 10 agentes | Pipeline expresso, economia máxima |

## 5. MCP Lazy Init
Servidores MCP do tipo local auto-iniciam apenas na primeira chamada de ferramenta, sem overhead de inicialização.

## 6. Modelo Gratuito com Contexto Gigante (OpenCode Zen)
O sistema usa o modelo `big-pickle` (OpenCode Zen) que é gratuito e oferece:
- 200K tokens de contexto
- 128K tokens de saída

## 7. Skill Específica de Token Efficiency
Existe uma skill dedicada `token-efficiency` que gerencia otimização de tokens.

## 📊 Comparativo de Consumo

| Cenário | Consumo de Tokens |
| :--- | :--- |
| Uso via CLI direto (scripts Python) | 0 tokens (execução local) |
| Uso via agente IA | ~500-1.000 tokens (contexto da skill) |
| Artigo completo Nível 1 | Alto (sem economia, rigor máximo) |
| Artigo completo Nível 2 | Médio (~20 agentes) |
| Artigo completo Nível 3 | Baixo (max 10 agentes) |

## 💡 Conclusão

O OpenCode Ecosystem não gasta muitos tokens quando comparado com abordagens convencionais porque:

- Usa chinês para contexto interno (+40% densidade)
- Implementa progressive disclosure (SKILL.md ≤ 2.500B)
- Usa edição cirúrgica (apenas delta)
- Adapta o número de agentes ao objetivo
- Usa modelo gratuito com 200K contexto
- MCPs iniciam sob demanda (lazy init)

Para uso via CLI direto, o consumo é zero tokens. Para uso via agente IA, o consumo é otimizado pelas estratégias acima.
