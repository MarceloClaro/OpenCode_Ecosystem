# SPEC-04: Context Grounding / API Hallucination Detection (P1)

> Lacuna 4: Extensao do Cora-Debate V6 para detectar APIs inventadas e violacoes arquiteturais

## Arquitetura

```
context_grounding/
├── __init__.py
├── api_validator.py        # Validador de imports vs dependencias reais
├── architecture_checker.py # Verificador de aderencia a decisoes DecisionNode
├── grounding_scorer.py     # Score de grounding (0-100) por arquivo
├── cora_v6_extension.py    # Extensao do verificador V6 do Cora-Debate
├── package_indexer.py      # Indexador de package.json/requirements.txt
└── hallucination_report.py # Relatorio de APIs potencialmente alucinadas
```

## Tipos de Alucinacao Detectados

| Tipo | Descricao | Exemplo |
|------|-----------|---------|
| API_IMPORT | Import de modulo nao listado em dependencias | `import magic_lib` sem `magic_lib` no requirements.txt |
| API_METHOD | Chamada de metodo que nao existe na versao instalada | `os.nonexistent()` |
| API_SIGNATURE | Assinatura errada (params faltando/trocados) | `requests.get(url, method="POST")` |
| ARCH_VIOLATION | Violacao de decisao arquitetural registrada | Usar SQL direto quando DecisionNode define Repository Pattern |
| CONSTRAINT_IGNORE | Ignorar restricao documentada | Upload sem validacao de tipo quando spec exige |
| CONTEXT_BLIND | Agente ignorou arquivo/documento relevante | Spec menciona `.env.template`, agente leu `.env` |

## Integracao com Cora-Debate V6

```python
# Extensao do verificador V6 existente
class CoraV6GroundingExtension:
    """Adiciona verificacao de grounding ao Cora-Debate V6."""
    
    def verify(self, agent_output: dict, context: dict) -> GroundingReport:
        imports = self.api_validator.check_imports(
            code=agent_output["code"],
            dependencies=context["dependencies"]
        )
        violations = self.architecture_checker.check(
            code=agent_output["code"],
            decisions=context["architectural_decisions"]
        )
        score = self.grounding_scorer.calculate(
            imports_valid=imports.valid_count,
            imports_total=imports.total_count,
            arch_violations=len(violations)
        )
        return GroundingReport(
            score=score,
            hallucinations=imports.invalid_imports,
            arch_violations=violations,
            passed=score >= 80
        )
```

## Metrica de Grounding

```
grounding_score = (
    (imports_valid / imports_total) * 40 +
    (1 - arch_violations / max_violations) * 30 +
    (files_referenced / files_should_reference) * 20 +
    (constraints_respected / constraints_total) * 10
)

>= 90: Excelente -- agente usou contexto correto
70-89: Bom -- pequenas divergencias
50-69: Regular -- requer revisao humana
< 50:  Ruim -- provavel alucinacao, BLOQUEIA
```
