# Scanner Epistemológico Cognitivo (SPEC-053/054/055)

## Descrição
Três scanners complementares que estendem o pipeline de análise epistemológica:
- **SPEC-053 Cognitive Diversity Scanner**: Detecta câmaras de eco e homogeneidade cognitiva
- **SPEC-054 Epistemic Topology Mapper**: Projeta e mapeia o espaço de conhecimento em 2D
- **SPEC-055 Rupture Potential Index**: Calcula potencial de ruptura assimétrico (RPI)

## Como usar

### Cognitive Diversity Scanner
```python
from cognitive_diversity_scanner import CognitiveDiversityScanner, ArtifactProfile

cds = CognitiveDiversityScanner()
cds.register_artifact(ArtifactProfile(
    artifact_id="artigo_001",
    text_preview="Estudo sobre TCC para ansiedade",
    coverage_vector={"paradigmas": 0.8, "metodos": 0.6, "teorias": 0.4},
))
result = cds.compute_homogeneity_index()
print(f"HI: {result['global_hi']}, Eco: {result['is_echo_chamber']}")
```

### Epistemic Topology Mapper
```python
from epistemic_topology_mapper import EpistemicTopologyMapper, TopologicalPoint

etm = EpistemicTopologyMapper()
etm.add_point(TopologicalPoint("artigo_A", [0.8, 0.6, 0.4]))
etm.project(dimensions=2)
islands = etm.detect_islands()
holes = etm.detect_holes()
bridges = etm.compute_bridge_potential()
```

### Rupture Potential Index
```python
from rupture_potential_index import RupturePotentialIndex, ResearchOpportunity

rpi = RupturePotentialIndex()
rpi.register_opportunity(ResearchOpportunity(
    opportunity_id="OP-001",
    label="Novo paradigma em saude digital",
    epistemic_distance=0.8, fertility=0.7,
    risk_reward=0.6, cost_opportunity=0.3, eps_score=65.0,
))
result = rpi.compute("OP-001")
print(f"RPI: {result['rpi_score']}, Quadrante: {result['quadrant']}")
```

### Pipeline Integrado
```python
from scanner_integration import ScannerIntegration

integrator = ScannerIntegration()
report = integrator.scan_pipeline_output(
    pipeline="artigo",
    audit_trail=audit_trail,
    output_dir="pesquisas/meu_estudo/",
    domain="psicologia",
)
# report agora inclui:
# - cognitive_diversity (SPEC-053)
# - epistemic_topology (SPEC-054)
# - rupture_potential (SPEC-055)
```

## CTs
- Cognitive Diversity Scanner: 14/14
- Epistemic Topology Mapper: 14/14
- Rupture Potential Index: 14/14

## Dependências
- Python 3.11+
- `scanner_integration.py` (para pipeline completo)
- `potentiality_estimator_v2.py` (para integração RPI)

## Arquivos
- `cognitive_diversity_scanner.py` (457 linhas)
- `epistemic_topology_mapper.py` (675 linhas)
- `rupture_potential_index.py` (359 linhas)
