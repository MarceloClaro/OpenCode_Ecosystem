# Documentação do Sistema TDD Academico — Validação de SPECs da Meta-Avaliação DCA

## 1. Visão Geral

O **TDDAcademic** é um sistema de validação Test-Driven Development (TDD) para as 5 Especificações Técnicas (SPECs) extraídas da Meta-Avaliação do artigo *Dinâmica Caótica Aplicada à Arteterapia*. Ele implementa cada critério de aceitação como um teste automatizado, garantindo rastreabilidade formal entre recomendações, especificações e implementação.

### 1.1. Ciclo TDD

```
[RED]  → Escrever teste que falha (critério de aceitação)
[GREEN] → Implementar lógica mínima para passar
[REFACTOR] → Refatorar mantendo verdes (OOP)
[INTEGRATE] → Incorporar ao pipeline de qualidade
```

## 2. Arquitetura Orientada a Objetos

### 2.1. Diagrama de Classes

```
SpecValidator (ABC)
│   ├── spec_id: str (abstract)
│   ├── descricao: str (abstract)
│   ├── validar() → SpecReport (Template Method)
│   └── _executar_testes() → List[TestResult] (abstract)
│
├── PciValidator        (SPEC-PCI-001)
├── CodeValidator       (SPEC-CODE-001)
├── AntisymValidator    (SPEC-ANTISYM-001)
├── NarrValidator       (SPEC-NARR-001)
└── CoraValidator       (SPEC-CORA-001)

TestRunner (Composição)
│   └── criar_padrao() → TestRunner (Factory Method)
│   └── executar_todos() → List[SpecReport]

TestReport (Relatório)
│   ├── exibir() → stdout
│   ├── to_json(path) → JSON
│   └── to_markdown() → MD
```

### 2.2. Design Patterns Utilizados

| Padrão | Aplicação | Benefício |
|--------|-----------|-----------|
| **Template Method** | `SpecValidator.validar()` define esqueleto; `_executar_testes()` é implementado por cada subclasse | Reúso do fluxo de try/except/registro; cada validador só implementa a lógica específica |
| **Factory Method** | `TestRunner.criar_padrao()` instancia todos os validadores | Encapsulamento da criação; fácil adicionar novos validadores |
| **Strategy** | Cada validador é uma estratégia de verificação diferente | Polimorfismo permite trocar/estender validadores sem modificar o orquestrador |
| **Composite** | `TestRunner` compõe múltiplos `SpecValidator` | Tratamento uniforme de coleções de validadores |
| **Value Object** | `TestResult` e `SpecReport` são imutáveis | Imutabilidade garante consistência dos dados de teste |
| **Template Method + Hook** | `validar()` é o template; subclasses fornecem hooks via `_executar_testes()` | Inversão de controle (Hollywood Principle) |

### 2.3. Fluxo de Execução

```
TestRunner.criar_padrao()
    ↓
para cada validador:
    validador.validar()
        ↓
        para cada teste:
            try:
                func()        ← lógica do Acceptance Criterion
                → TestResult("PASS")
            except AssertionError:
                → TestResult("FAIL", erro)
            except Exception:
                → TestResult("ERROR", traceback)
        ↓
    retorna SpecReport(spec_id, resultados)
    ↓
TestReport(reports).exibir()  →  stdout
                 .to_json()   →  relatorio_tdd_specs.json
                 .to_markdown() → relatorio_tdd_specs.md
```

## 3. Validadores (SPECs)

### 3.1. SPEC-PCI-001: Calibração do Process Confidence Index

**Problema:** PCI bruto superestima confiança em artigos com simulações numéricas.

**Fórmula de calibração:**
```
PCI_calibrado = min(10, max(0, PCI_bruto × 0.062 × f_domínio + bônus_código + bônus_narração))
```

**Fatores de domínio:**
| Domínio | Fator |
|---------|-------|
| geral | 1.00 |
| geometria | 0.85 |
| numérico | 0.70 |

**Testes (5 CAs):**
| CA | Descrição | Entrada | Esperado |
|----|-----------|---------|----------|
| CA1 | PCI 95, geometria, 0 blocos | `calibrar(95, "geometria", 0)` | ≈5.01 |
| CA2 | PCI nunca > 10 | `calibrar(1000, *, 50, 0)` | ≤10.0 |
| CA3 | PCI nunca < 0 | `calibrar(-100)` | ≥0.0 |
| CA4 | Numérico penaliza mais que geral | `calibrar(p, "numerico") ≤ calibrar(p, "geral")` | True |
| CA5 | Bônus por código presente | `calibrar(100, *, 3) - calibrar(100, *, 0)` | ≈0.3 |

### 3.2. SPEC-CODE-001: Verificador de Obrigatoriedade de Código

**Problema:** Artigos que descrevem resultados numéricos sem disponibilizar código-fonte.

**Gatilhos de rejeição** (9 padrões regex): `código`, `simulação`, `RK45`, `Runge-Kutta`, `Euler-Maruyama`, `Monte Carlo`, `o código confirma`, `erro < 10...`, `resultado numérico`.

**Gatilhos de aviso** (5 padrões): `dados`, `dataset`, `amostra`, `gráfico mostra`, `figura mostra`.

**Testes (5 CAs):**
| CA | Descrição | Entrada | Esperado |
|----|-----------|---------|----------|
| CA1 | "Código Python com RK45" sem bloco | Gatilhos de rejeição ativos | rejeitado |
| CA2 | Texto matemático puro | Nenhum gatilho | aprovado |
| CA3 | Código em apêndice | `blocos=1` | aprovado |
| CA4 | 5 textos puramente matemáticos | Nenhum falso positivo | aprovado |
| CA5 | Mensagem aponta gatilho específico | Gatilho `\bRK45\b` identificado | len(gats)>0 |

### 3.3. SPEC-ANTISYM-001: Verificador de Antisimetria do Produto Exterior

**Problema:** O artigo Hénon-Heiles original continha erro de sinal no pullback `F^*(dx∧dy) = +b dx∧dy` quando deveria ser `-b dx∧dy`.

**Regras:**
- **AS-01:** `F^*(dx∧dy) = det(DF) dx∧dy`. Para Hénon, `det(DF) = -b`, logo `F^*(dx∧dy) = -b dx∧dy`.
- **AS-02:** `dx∧dx = 0` (forma quadrática nula por antisimetria).

**Testes (5 CAs):**
| CA | Descrição | Entrada | Esperado |
|----|-----------|---------|----------|
| CA1 | `F^*(dx∧dy) = b dx∧dy` (erro clássico) | Pullback com sinal positivo | inconsistente |
| CA2 | `F^*(dx∧dy) = -b dx∧dy` (correto) | Pullback com sinal negativo | ok |
| CA3 | Relações de comutação su(2) | `[J_i,J_j] = iℏε_{ijk}J_k` | ok |
| CA4 | `dx∧dx = dx∧dx` | Termo quadrático não simplificado | score < 0.5 |
| CA5 | `dx∧dy∧dz` | 3-forma válida | ok |

### 3.4. SPEC-NARR-001: Conversor de Narração para Demonstração

**Problema:** Uso excessivo de verbos narrativos ("obtém-se", "verifica-se", "é claro que") que mascaram a ausência de demonstração formal.

**Padrões detectados (N-01 a N-10):**

| ID | Padrão | Exemplo |
|----|--------|---------|
| N-01 | `\bobt[eé]m-se\b` | "obtém-se a equação" |
| N-02 | `\bverifica-se\b` | "verifica-se que" |
| N-03 | `\bdeve-se\b` | "deve-se ter" |
| N-04 | `\bpodemos\b` | "podemos escrever" |
| N-05 | `\bnota-se\b` | "nota-se que" |
| N-06 | `\bafirma-se\b` | "afirma-se que" |
| N-07 | `\b[ée] claro que\b` | "é claro que" |
| N-08 | `\bo c[óo]digo confirma\b` | "o código confirma" |
| N-09 | `\bsubstituindo, obt[eé]m-se\b` | "substituindo, obtém-se" |
| N-10 | `\bap[óo]s simplifica[cç][ãa]o\b` | "após simplificação" |

**Testes (5 CAs):**
| CA | Descrição | Resultado |
|----|-----------|-----------|
| CA1 | 100% dos padrões N-01 a N-10 são detectados em texto de teste | PASS |
| CA2 | "o código confirma" dispara N-08 | PASS |
| CA3 | 3 variações de "obtém-se" todas detectadas | PASS |
| CA4 | "é claro que" sempre dispara N-07 | PASS |
| CA5 | Taxa > 30% para texto narrativo; 0% para algébrico | PASS |

### 3.5. SPEC-CORA-001: Expansão do Escopo do Cora-Debate

**Problema:** O Cora-Debate original só verificava álgebra exterior (∧). Necessário expandir para álgebras de Lie (su(2), su(1,1), so(3), sl(2,R)).

**Assinaturas de álgebra suportadas:**

| Álgebra | Geradores | Padrão | Assinatura |
|---------|-----------|--------|------------|
| su(2) | J₁,J₂,J₃ | [J₁,J₂]=+J₃, [J₂,J₃]=+J₁, [J₃,J₁]=+J₂ | compacta |
| su(1,1) | J₀,J₁,J₂ | [J₁,J₂]=-J₀, [J₂,J₀]=+J₁, [J₀,J₁]=+J₂ | não-compacta |
| so(3) | L_x,L_y,L_z | [L_x,L_y]=+iℏL_z, ... | compacta |
| sl(2,R) | H,E,F | [H,E]=+2E, [H,F]=-2F, [E,F]=+H | split |

**Verificadores (V1-V6):**
- **V1:** Validação de forma diferencial (∧)
- **V2:** Verificação de sinal no pullback
- **V3:** Detecção de álgebra de Lie por padrão de comutadores
- **V4:** Validação de consistência contra assinatura conhecida
- **V5:** Sugestão de álgebra alternativa quando violação é consistente com outra assinatura
- **V6:** Verificação de conectivos lógicos ("logo", "portanto", "∴")

**Expressão regular flexível para detecção de comutadores:**
```
(?:\\?\[A,B\\?\]|\\?\{A,B\\?\})\s*=\s*([^\s,;]+)
```
Aceita: `[J1,J2]`, `\{J_1,J_2\}`, `{J1,J2}`, `[J_1,J_2]` (com/s sem LaTeX escaping, com/sem subscrito).

**Testes (5 CAs):**
| CA | Descrição | Resultado |
|----|-----------|-----------|
| CA1 | `{J1,J2}=+J0` em su(1,1) → inconsistente (deveria ser -J0) | PASS |
| CA2 | `[J1,J2]=+J3` em su(2) → ok | PASS |
| CA3 | `[H,E]=-2E` em sl(2,R) → inconsistente (deveria ser +2E) | PASS |
| CA4 | `[J1,J2]=+J3` em su(1,1) → sugere su(2) como alternativa | PASS |
| CA5 | Conectivos "Logo" e "Portanto" presentes | PASS |

## 4. Processo de Validação

### 4.1. Pipeline de Execução

```bash
python tdd_academic_validator.py
```

**Saídas geradas:**
| Arquivo | Formato | Conteúdo |
|---------|---------|----------|
| stdout | Texto | Resultado de cada teste + resumo |
| `relatorio_tdd_specs.json` | JSON | Dados completos para processamento posterior |
| `relatorio_tdd_specs.md` | Markdown | Relatório formatado para documentação |

### 4.2. Interpretação de Resultados

```
[PASS] → Critério de aceitação satisfeito
[FAIL] → Critério violado (AssertionError com mensagem)
[ERROR] → Exceção inesperada no teste (bug no validador)
```

**Taxa de aprovação por SPEC:**
- 100%: PCI-001, CODE-001, ANTISYM-001, NARR-001, CORA-001
- Global: 25/25 (100.0%)

### 4.3. Relação SPECs ↔ Recomendações do Artigo

| SPEC | Recomendação Artigo | Seção | Criticidade |
|------|-------------------|-------|-------------|
| PCI-001 | R1 (Calibração PCI) | §6.1 | Alta |
| CODE-001 | R2 (Código Obrigatório) | §6.2 | Alta |
| ANTISYM-001 | R3 (Erro Hénon-Heiles) | §6.3 | Crítica |
| NARR-001 | R4 (Narração→Demonstração) | §6.4 | Média |
| CORA-001 | R5 (Expansão Cora-Debate) | §6.5 | Alta |

## 5. Extensão do Sistema

### 5.1. Adicionar Nova SPEC

```python
class MinhaSpecValidator(SpecValidator):
    @property
    def spec_id(self) -> str:
        return "MINHA-001"
    
    @property
    def descricao(self) -> str:
        return "Descrição da minha SPEC"
    
    def _executar_testes(self) -> List[TestResult]:
        return [
            self._criar_teste("CA1", "Descrição do teste",
                lambda: self._minha_logica()),
        ]
    
    def _minha_logica(self):
        assert 1 + 1 == 2, "Matética básica falhou"
```

### 5.2. Registrar no TestRunner

```python
# Em TestRunner.criar_padrao():
return cls([
    PciValidator(),
    CodeValidator(),
    AntisymValidator(),
    NarrValidator(),
    CoraValidator(),
    MinhaSpecValidator(),  # <-- adicionar aqui
])
```

### 5.3. Novas Assinaturas de Álgebra (CORA-001)

```python
# Em CoraValidator._ALGEBRAS:
"e8": {
    "generators": [...],
    "pattern": {...},
    "signature": "exceptional"
}
```

## 6. Arquivos do Sistema

| Arquivo | Descrição |
|---------|-----------|
| `tdd_academic_validator.py` | Sistema TDD completo (arquitetura OOP) |
| `relatorio_tdd_specs.json` | Relatório de execução (JSON) |
| `relatorio_tdd_specs.md` | Relatório formatado (Markdown) |
| `lista_dca_completa_50_laudas.tex` | Documento LaTeX com meta-avaliação e SPECs |

## 7. Histórico de Versões

| Versão | Data | Alterações |
|--------|------|------------|
| 1.0 (procedural) | 2026-05-27 | Implementação inicial com funções avulsas, decorator `@test` |
| 2.0 (OOP) | 2026-05-27 | Refatoração completa: `SpecValidator` (ABC), 5 validadores concretos, `TestRunner`, `TestReport`, 3 design patterns |

### 7.1. Lições Aprendidas na Refatoração

1. **Regex flexível:** Comutadores LaTeX aceitam `\[`, `\{`, `[`, `{` com/sem escaping
2. **Normalização:** Subscritos `J_1` e `J1` precisam ser normalizados antes de comparação
3. **Sinal vs magnitude:** Violação de sinal é mais comum que violação de magnitude em álgebras de Lie
4. **Falsos positivos:** Texto matemático puro (Stokes, Laplace) não deve disparar CODE-001
5. **Pullback Hénon:** O erro clássico do artigo original (+b em vez de -b) é detectado por contexto (presença de `F^*`)
