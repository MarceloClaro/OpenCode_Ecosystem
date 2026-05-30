# Relatorio TDD — Validacao de SPECs

**Data:** 2026-05-27 22:50
**Total:** 25 | **PASS:** 25 | **FAIL:** 0 | **Taxa:** 100.0%

## Resultados por SPEC

| SPEC | Pass/Fail | Taxa |
|------|-----------|------|
| PCI-001 | 5/5 | 100% |
| CODE-001 | 5/5 | 100% |
| ANTISYM-001 | 5/5 | 100% |
| NARR-001 | 5/5 | 100% |
| CORA-001 | 5/5 | 100% |

## Detalhamento

### PCI-001

- [+] CA1: PCI bruto 95, geometria, 0 blocos -> aprox. 5.01
- [+] CA2: PCI calibrado nunca ultrapassa 10.0
- [+] CA3: PCI calibrado nunca eh negativo
- [+] CA4: Dominio 'numerico' sempre penaliza mais que 'geral'
- [+] CA5: Bonus por codigo so se bloco REAL existe

### CODE-001

- [+] CA1: Frase 'Codigo Python com RK45 confirma' sem bloco -> rejeitado
- [+] CA2: Solucao puramente analitica sem gatilhos -> aprovado
- [+] CA3: Codigo em arquivo externo -> aprovado
- [+] CA4: Falso positivo zero para texto matematico puro
- [+] CA5: Mensagem de rejeicao aponta o gatilho

### ANTISYM-001

- [+] CA1: Detecta +b dx^dy onde deveria ser -b dx^dy
- [+] CA2: Nao dispara falso positivo para pulback correto
- [+] CA3: Nao dispara falso positivo para su(2)
- [+] CA4: Pontuacao < 0.5 dispara alerta
- [+] CA5: Zero falso positivo em n-formas com n>1

### NARR-001

- [+] CA1: 100% dos padroes N-01 a N-10 sao detectados
- [+] CA2: 'o codigo confirma' sem bloco -> pendente
- [+] CA3: Expressoes 'obtem-se' viaveis
- [+] CA4: 'e claro que' sempre dispara verificacao
- [+] CA5: Taxa de narracao calculada corretamente

### CORA-001

- [+] CA1: V4 detecta {J1,J2}=+J0 em contexto su(1,1)
- [+] CA2: V4 aceita [J1,J2]=+J3 em contexto su(2)
- [+] CA3: V4 rejeita [H,E]=-2E onde deveria ser +2E (sl2r)
- [+] CA4: V5 sugere algebra alternativa correta quando violacao e consistente com outra algebra
- [+] CA5: V6 verifica conectivos logicos
