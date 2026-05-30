# SYNC_MANIFEST.md — Clone Identico Autonomo
## OpenCode Ecosystem ↔ Antiprojeto UFC
### Gerado: 2026-05-30T12:16:06.918977
### Arquivos espelhados: 2091
### Erros: 0

## Proposito
Este manifesto prova que o ecossistema OpenCode e o projeto Antiprojeto UFC
sao clones identicos. Se qualquer um for deletado, o outro contem TODOS os
artefatos necessarios para reconstruir o par.

## Como verificar
```bash
python sync_mirror.py --dry-run   # Verifica sem alterar
python sync_mirror.py             # Executa espelhamento
```

## Executar TDD em qualquer lado
```bash
# No projeto
cd artigo/evaluations/tests
python -m pytest test_anticircularidade.py test_domain_shift_camada1b.py test_d1_matematica.py test_d2_fisica.py test_d9_metodologia.py -v

# No ecossistema (clone identico)
cd tests
python -m pytest test_anticircularidade.py test_domain_shift_camada1b.py test_d1_matematica.py test_d2_fisica.py test_d9_metodologia.py -v
```

## Sumario de Artefatos Espelhados

| Categoria | Arquivos | Direcao |
|-----------|----------|---------|
| Specs | 9 | projeto → eco |
| TDD Suites | 5 suites, 58 CTs | projeto → eco |
| Orchestration | 13 specs | projeto → eco |
| Skills | 67 SKILL.md | eco → projeto |
| Plugins | 5 plugins | eco → projeto |
| Quantum | 146 arquivos | eco → projeto |
| Nexus | 488 arquivos | eco → projeto |
| Evolve State | ~15 JSONs | bidirecional |
| Config | opencode.json, .menu_registry | bidirecional |
| Artigos | LaTeX + PDFs | projeto → eco |
| Dados | templates, figuras, dados_entrada | projeto → eco |

## Hash de Verificacao
- Script: c12e0268ab077af03c1b4e15327bf75a
- Timestamp: 2026-05-30T12:16:06.920695
