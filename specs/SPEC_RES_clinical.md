# SPEC_RES_clinical — Clinical Art Therapy v1.0

## API Contract (Synthetic — semantic-only skill)

### Skill: `clinical-art-therapy`

```python
@dataclass
class ProtocoloEtico:
    cep: str = ""       # Numero CAAE
    tcle: str = ""      # Texto do TCLE
    status: str = "rascunho"  # rascunho | submetido | aprovado

    def validar_tcle(self, texto: str) -> bool
        # True se len(texto) >= 100 (minimo para TCLE acessivel)

    def hash_consentimento(self, texto: str) -> str
        # MD5 deterministico para registro blockchain-like

@dataclass
class Participante:
    id: str
    idade: int
    tempo_grupo_meses: int
    diagnostico_familiar: str  # TEA | TDAH | ALTAS_HABILIDADES

    def elegivel(self) -> bool:
        return idade >= 18 and tempo_grupo_meses >= 3
           and diagnostico_familiar in ("TEA", "TDAH", "ALTAS_HABILIDADES")

@dataclass
class PipelineStage:
    nome: str
    concluido: bool = False
    artefatos: list[str] = field(default_factory=list)

    def validar(self) -> bool:
        return len(self.artefatos) > 0
```

### 8 Pipeline Stages:
1. Intake e Protocolo Etico (CNS 466/2012, 510/2016)
2. Codificacao Qualitativa Multiagente
3. Analise Visual (producao artistica)
4. Triangulacao Metodologica
5. Cora-Debate V1-V6 (verificacao interetapas)
6. PhD Auditor (rigor estatistico)
7. Relatorio Clinico
8. Exportacao ABNT / Publicacao

---

## CT-001: Participante Elegibilidade (Business Rule)
**Entrada**: Participantes com idade < 18, ou < 3 meses de grupo, ou diagnostico invalido
**Esperado**: `.elegivel() == False`; participante valido (idade >= 18, >= 3 meses, diagnostico valido) → `True`

## CT-002: Hash de Consentimento Deterministico (Privacy)
**Entrada**: Mesmo texto TCLE → `hash_consentimento()` duas vezes
**Esperado**: Hashes identicos (`len == 32`, MD5), uso blockchain-like para registro de consentimento

## CT-003: TCLE Tamanho Minimo (Ethics)
**Entrada**: `validar_tcle(texto_curto)` vs `validar_tcle(texto_longo >= 100)`
**Esperado**: Texto curto → `False`; texto >= 100 chars → `True`; conformidade CNS 466/2012

## CT-004: Pipeline Stage Validacao (Structural)
**Entrada**: `PipelineStage` com artefatos vs sem artefatos
**Esperado**: `.validar() == True` quando `len(artefatos) > 0`; `False` caso contrario
