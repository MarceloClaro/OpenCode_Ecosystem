<!--
  SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL
  Toda resposta DEVE ser em português do Brasil formal.
  Contexto em chinês para eficiência de tokens (densidade +40%%).
  Modelo: deepseek-v4-pro (OpenCode Zen, 200K ctx, 128K out, gratuito)
-->

# TMA v5.0 MICRO - Guia de Raciocínio (38 Sub-tipos)

## 1. Categorias de Raciocínio

| Categoria | Sub-tipos | Uso Ideal |
|-----------|-----------|-----------|
| Dedutivo | 8 | Lógica formal, prova |
| Indutivo | 6 | Generalização, padrões |
| Causal | 5 | Relações causa-efeito |
| Contrafactual | 4 | Cenários hipotéticos |
| Bayesiano | 5 | Probabilidade, incerteza |
| Analógico | 4 | Comparação, transferência |
| Formal | 3 | Prova matemática |
| Abdutivo | 3 | Diagnóstico, explicação |

**Total: 38 Sub-tipos**

## 2. Raciocínio Dedutivo (8 Sub-tipos)

### 2.1 Modus Ponens
```
Premissa 1: Se A então B
Premissa 2: A é verdadeiro
Conclusão: B é verdadeiro

Exemplo:
  P1: Se o domínio é Física, então precisa de equações
  P2: O domínio é Física
  C: Precisa de equações
```

**Quando usar:** Aplicar regras conhecidas
**Confiança:** Alta (0.95+)
**Tempo:** Rápido (< 100ms)

### 2.2 Modus Tollens
```
Premissa 1: Se A então B
Premissa 2: B é falso
Conclusão: A é falso

Exemplo:
  P1: Se é um conceito válido, tem definição
  P2: Não tem definição
  C: Não é um conceito válido
```

**Quando usar:** Eliminar hipóteses
**Confiança:** Alta (0.95+)
**Tempo:** Rápido (< 100ms)

### 2.3 Silogismo
```
Premissa 1: Todos os A são B
Premissa 2: Todos os B são C
Conclusão: Todos os A são C

Exemplo:
  P1: Todos os conceitos têm definições
  P2: Todas as definições têm exemplos
  C: Todos os conceitos têm exemplos
```

**Quando usar:** Encadear relações
**Confiança:** Alta (0.90+)
**Tempo:** Médio (100-500ms)

### 2.4 Disjunção
```
Premissa 1: A ou B
Premissa 2: Não A
Conclusão: B

Exemplo:
  P1: O erro é de entrada ou lógica
  P2: Não é de entrada
  C: É de lógica
```

**Quando usar:** Eliminar alternativas
**Confiança:** Alta (0.85+)
**Tempo:** Rápido (< 100ms)

### 2.5 Conjunção
```
Premissa 1: A é verdadeiro
Premissa 2: B é verdadeiro
Conclusão: A e B são verdadeiros

Exemplo:
  P1: Conceito tem qualidade ≥ 0.7
  P2: Conceito tem definição
  C: Conceito é válido
```

**Quando usar:** Combinar condições
**Confiança:** Alta (0.90+)
**Tempo:** Rápido (< 100ms)

### 2.6 Negação
```
Premissa 1: Não (Não A)
Conclusão: A

Exemplo:
  P1: Não é verdade que não temos dados
  C: Temos dados
```

**Quando usar:** Simplificar negações
**Confiança:** Alta (0.95+)
**Tempo:** Rápido (< 50ms)

### 2.7 Quantificação
```
Premissa 1: Para todo X, P(X)
Premissa 2: X = x
Conclusão: P(x)

Exemplo:
  P1: Para todo conceito, tem qualidade
  P2: X = "energia"
  C: "energia" tem qualidade
```

**Quando usar:** Aplicar a casos específicos
**Confiança:** Alta (0.90+)
**Tempo:** Médio (100-300ms)

### 2.8 Identidade
```
Premissa 1: A = B
Premissa 2: P(A)
Conclusão: P(B)

Exemplo:
  P1: Conceito1 = Conceito2
  P2: Conceito1 é válido
  C: Conceito2 é válido
```

**Quando usar:** Substituir equivalentes
**Confiança:** Alta (0.95+)
**Tempo:** Rápido (< 100ms)

## 3. Raciocínio Indutivo (6 Sub-tipos)

### 3.1 Enumeração
```
Observação: A1, A2, A3, ... An têm propriedade P
Conclusão: Todos os A têm propriedade P

Exemplo:
  Obs: Conceito1, Conceito2, Conceito3 têm qualidade ≥ 0.7
  C: Todos os conceitos têm qualidade ≥ 0.7
```

**Quando usar:** Generalizar observações
**Confiança:** Média (0.60-0.80)
**Tempo:** Médio (500ms-2s)

### 3.2 Analogia
```
A é similar a B
A tem propriedade P
Conclusão: B provavelmente tem P

Exemplo:
  Física é similar a Química
  Física precisa de equações
  C: Química provavelmente precisa de equações
```

**Quando usar:** Transferir conhecimento
**Confiança:** Média (0.65-0.75)
**Tempo:** Médio (1-3s)

### 3.3 Generalização
```
Amostra S de população P tem propriedade Q
Conclusão: População P provavelmente tem Q

Exemplo:
  10% dos conceitos têm qualidade < 0.7
  C: Aproximadamente 10% dos conceitos têm qualidade < 0.7
```

**Quando usar:** Estimar propriedades
**Confiança:** Média (0.70-0.85)
**Tempo:** Médio (500ms-2s)

### 3.4 Abduction
```
Observação: O é verdadeiro
Explicação: E explicaria O
Conclusão: E é provavelmente verdadeiro

Exemplo:
  Obs: Conceitos têm qualidade alta
  Exp: Extrator é de alta qualidade
  C: Extrator é provavelmente de alta qualidade
```

**Quando usar:** Diagnóstico, explicação
**Confiança:** Média (0.60-0.75)
**Tempo:** Médio (1-3s)

### 3.5 Causal
```
A precede B regularmente
Conclusão: A causa B

Exemplo:
  Melhor entrada → Melhor saída
  C: Qualidade de entrada causa qualidade de saída
```

**Quando usar:** Identificar causas
**Confiança:** Média (0.65-0.80)
**Tempo:** Médio (2-5s)

### 3.6 Probabilístico
```
P(A) = 0.8, P(B|A) = 0.9
Conclusão: P(A e B) ≈ 0.72

Exemplo:
  P(conceito válido) = 0.85
  P(tem definição | válido) = 0.95
  C: P(válido e tem definição) ≈ 0.81
```

**Quando usar:** Combinar probabilidades
**Confiança:** Alta (0.85-0.95)
**Tempo:** Rápido (100-500ms)

## 4. Raciocínio Causal (5 Sub-tipos)

### 4.1 Causal Direto
```
A causa B diretamente
A → B

Exemplo:
  Qualidade de entrada → Qualidade de conceitos
```

**Quando usar:** Relações diretas
**Confiança:** Média (0.70-0.85)
**Tempo:** Médio (1-2s)

### 4.2 Causal Indireto
```
A causa B através de C
A → C → B

Exemplo:
  Qualidade entrada → Melhor processamento → Melhor saída
```

**Quando usar:** Cadeias causais
**Confiança:** Média (0.60-0.75)
**Tempo:** Médio (2-5s)

### 4.3 Causa Comum
```
A e B são causados por C
A ← C → B

Exemplo:
  Conceitos e relações são extraídos de texto
```

**Quando usar:** Identificar fatores comuns
**Confiança:** Média (0.65-0.80)
**Tempo:** Médio (2-4s)

### 4.4 Confundidor
```
A e B correlacionam mas não causam
A ← Z → B

Exemplo:
  Tempo de execução e qualidade correlacionam
  Ambos causados por complexidade
```

**Quando usar:** Evitar causalidade falsa
**Confiança:** Média (0.70-0.85)
**Tempo:** Médio (2-5s)

### 4.5 Mediador
```
A causa B através de M
A → M → B

Exemplo:
  Entrada → Processamento → Saída
```

**Quando usar:** Identificar mecanismos
**Confiança:** Média (0.65-0.80)
**Tempo:** Médio (2-5s)

## 5. Raciocínio Contrafactual (4 Sub-tipos)

### 5.1 Contrafactual Simples
```
Se X fosse diferente, Y seria diferente
Contra: X ≠ X' → Y ≠ Y'

Exemplo:
  Se entrada fosse melhor, saída seria melhor
```

**Quando usar:** Análise de impacto
**Confiança:** Baixa (0.50-0.70)
**Tempo:** Longo (5-10s)

### 5.2 Contrafactual Condicional
```
Se X fosse diferente E Z fosse igual, Y seria diferente
Contra: (X ≠ X' ∧ Z = Z) → Y ≠ Y'

Exemplo:
  Se entrada fosse melhor E algoritmo igual, saída seria melhor
```

**Quando usar:** Análise controlada
**Confiança:** Baixa (0.55-0.70)
**Tempo:** Longo (5-15s)

### 5.3 Contrafactual Múltiplo
```
Múltiplos cenários contrafactuais
Contra: ∀i (X ≠ X'_i → Y ≠ Y'_i)

Exemplo:
  Se entrada fosse melhor, saída seria melhor
  Se algoritmo fosse melhor, saída seria melhor
  Se tempo fosse maior, saída seria melhor
```

**Quando usar:** Análise multidimensional
**Confiança:** Baixa (0.50-0.65)
**Tempo:** Longo (10-30s)

### 5.4 Contrafactual Iterativo
```
Aplicar contrafactual recursivamente
Contra: Contra(Contra(X))

Exemplo:
  Se entrada fosse melhor, então se algoritmo fosse melhor, saída seria muito melhor
```

**Quando usar:** Análise profunda
**Confiança:** Muito Baixa (0.40-0.60)
**Tempo:** Muito Longo (30-60s)

## 6. Raciocínio Bayesiano (5 Sub-tipos)

### 6.1 Prior
```
P(H) = probabilidade inicial

Exemplo:
  P(conceito é válido) = 0.7
```

**Quando usar:** Inicializar probabilidades
**Confiança:** Média (0.70-0.85)
**Tempo:** Rápido (< 100ms)

### 6.2 Likelihood
```
P(E|H) = probabilidade de evidência dado hipótese

Exemplo:
  P(tem definição | conceito válido) = 0.95
```

**Quando usar:** Avaliar evidência
**Confiança:** Média (0.75-0.90)
**Tempo:** Rápido (100-300ms)

### 6.3 Posterior
```
P(H|E) = P(E|H) * P(H) / P(E)

Exemplo:
  P(conceito válido | tem definição) = 0.98
```

**Quando usar:** Atualizar crença
**Confiança:** Alta (0.85-0.95)
**Tempo:** Médio (100-500ms)

### 6.4 Atualização
```
Atualizar posterior com nova evidência
P(H|E1,E2) = P(E2|H,E1) * P(H|E1) / P(E2|E1)

Exemplo:
  Atualizar P(válido) com nova evidência
```

**Quando usar:** Incorporar feedback
**Confiança:** Alta (0.80-0.95)
**Tempo:** Médio (200-1000ms)

### 6.5 Inferência
```
Inferir valor mais provável
H_best = argmax P(H|E)

Exemplo:
  Melhor hipótese = conceito é válido
```

**Quando usar:** Tomar decisão
**Confiança:** Alta (0.85-0.95)
**Tempo:** Médio (100-500ms)

## 7. Raciocínio Analógico (4 Sub-tipos)

### 7.1 Estrutural
```
A e B têm estrutura similar
Conclusão: Propriedades similares

Exemplo:
  Física e Química têm estrutura similar
  Conclusão: Ambas precisam de equações
```

**Quando usar:** Transferência estrutural
**Confiança:** Média (0.65-0.80)
**Tempo:** Médio (2-5s)

### 7.2 Funcional
```
A e B têm função similar
Conclusão: Propriedades similares

Exemplo:
  Conceito1 e Conceito2 têm função similar
  Conclusão: Ambos têm qualidade similar
```

**Quando usar:** Transferência funcional
**Confiança:** Média (0.70-0.85)
**Tempo:** Médio (1-3s)

### 7.3 Processual
```
A e B têm processo similar
Conclusão: Resultados similares

Exemplo:
  Extração de conceitos e relações têm processo similar
  Conclusão: Ambas têm qualidade similar
```

**Quando usar:** Transferência processual
**Confiança:** Média (0.65-0.80)
**Tempo:** Médio (2-5s)

### 7.4 Relacional
```
A e B têm relações similares
Conclusão: Propriedades similares

Exemplo:
  Conceito1 relaciona-se com Relação1 como Conceito2 com Relação2
  Conclusão: Propriedades similares
```

**Quando usar:** Transferência relacional
**Confiança:** Média (0.60-0.75)
**Tempo:** Médio (3-7s)

## 8. Raciocínio Formal (3 Sub-tipos)

### 8.1 Prova Direta
```
Provar P através de sequência de passos lógicos
P1 → P2 → ... → P

Exemplo:
  Conceito tem qualidade ≥ 0.7
  Qualidade ≥ 0.7 → válido
  Portanto: Conceito é válido
```

**Quando usar:** Prova rigorosa
**Confiança:** Muito Alta (0.95+)
**Tempo:** Médio (500ms-2s)

### 8.2 Prova por Contradição
```
Assumir Não P e derivar contradição
¬P → Contradição → P

Exemplo:
  Assumir conceito não é válido
  Mas tem qualidade ≥ 0.7
  Contradição → Conceito é válido
```

**Quando usar:** Prova indireta
**Confiança:** Muito Alta (0.95+)
**Tempo:** Médio (1-3s)

### 8.3 Prova por Indução
```
Provar para caso base e passo indutivo
P(1) ∧ (P(n) → P(n+1)) → ∀n P(n)

Exemplo:
  Conceito1 é válido
  Se Conceiton é válido, Conceiton+1 é válido
  Portanto: Todos os conceitos são válidos
```

**Quando usar:** Prova recursiva
**Confiança:** Muito Alta (0.95+)
**Tempo:** Médio (2-5s)

## 9. Raciocínio Abdutivo (3 Sub-tipos)

### 9.1 Melhor Explicação
```
Qual explicação melhor explica observação?
E_best = argmax Qualidade(E|O)

Exemplo:
  Obs: Conceitos têm qualidade alta
  Exp1: Extrator é bom
  Exp2: Entrada é boa
  E_best: Extrator é bom
```

**Quando usar:** Diagnóstico
**Confiança:** Média (0.65-0.80)
**Tempo:** Médio (2-5s)

### 9.2 Diagnóstico
```
Qual problema causa sintomas?
P_best = argmax P(Sintomas|Problema)

Exemplo:
  Sintomas: Saída ruim
  Problema1: Entrada ruim
  Problema2: Algoritmo ruim
  P_best: Entrada ruim
```

**Quando usar:** Troubleshooting
**Confiança:** Média (0.60-0.75)
**Tempo:** Médio (3-7s)

### 9.3 Reconstrução
```
Reconstruir evento passado
E = argmax P(Evidência|Evento)

Exemplo:
  Evidência: Conceitos com qualidade baixa
  Evento: Entrada ruim no passado
```

**Quando usar:** Análise histórica
**Confiança:** Média (0.55-0.70)
**Tempo:** Médio (5-10s)

## 10. Seleção Automática de Raciocínio

### Algoritmo de Scoring

```python
def select_reasoning_type(characteristics: Dict) -> str:
    scores = {}
    
    # Dedutivo: quando temos regras claras
    if characteristics["has_rules"]:
        scores["deductive"] = 0.95
    
    # Indutivo: quando temos padrões
    if characteristics["has_patterns"]:
        scores["inductive"] = 0.85
    
    # Causal: quando temos relações
    if characteristics["has_relations"]:
        scores["causal"] = 0.80
    
    # Bayesiano: quando temos incerteza
    if characteristics["uncertainty"] > 0.3:
        scores["bayesian"] = 0.90
    
    # Contrafactual: quando precisamos explorar
    if characteristics["exploration_needed"]:
        scores["counterfactual"] = 0.70
    
    # Analógico: quando temos similaridade
    if characteristics["similarity"] > 0.7:
        scores["analogical"] = 0.75
    
    # Formal: quando precisamos rigor
    if characteristics["rigor_required"]:
        scores["formal"] = 0.95
    
    # Abdutivo: quando precisamos diagnóstico
    if characteristics["diagnosis_needed"]:
        scores["abductive"] = 0.85
    
    return max(scores, key=scores.get)
```

---

**Versão:** 5.0 MICRO | **Status:** Production Ready | **Total Sub-tipos:** 38
