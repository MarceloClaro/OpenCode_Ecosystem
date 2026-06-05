import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))
from core import initialize_core
from core.container import Container
from datetime import datetime

initialize_core()
sm = Container.instance().resolve('state_manager')

concepts = sm.get("zrm:concepts_extracted", {})
citations = sm.get("zrm:citations", [])
methodologies = sm.get("zrm:methodologies", [])
arguments = sm.get("zrm:arguments", [])

eco_state = sm.get("ecosystem-state", {})

print("=" * 70)
print("  RELATORIO CONSOLIDADO: PESQUISA ZRM + ECOSSISTEMA OPENCODE")
print(f"  Gerado: {datetime.now().isoformat()}")
print("=" * 70)

print(f"\n  ECOSYSTEM HEALTH: {eco_state.get('health_score', 'N/A')}/100")
print(f"  Componentes ativos: {eco_state.get('active_components', 'N/A')}")

print("\n" + "-" * 70)
print("  1. FRAMEWORK METODOLOGICO EXTRAIDO DO ZRM")
print("-" * 70)
cc = concepts.get("core_concepts", {})
for k, v in cc.items():
    print(f"\n  [{k}]")
    print(f"    {v}")

print("\n" + "-" * 70)
print(f"  2. BASE DE CITACOES ({len(citations)} referencias)")
print("-" * 70)
for c in sorted(citations, key=lambda x: x["year"]):
    yr = c["year"]
    t = c["type"].upper()
    title = c["title"]
    authors = ", ".join(c["authors"][:3])
    doi = c.get("doi", "")
    cites = c.get("citations", "")
    kw = ", ".join(c["keywords"][:3])
    rel = c.get("relevance", "")
    print(f"\n  [{yr}] [{t}] {title}")
    print(f"    Autores: {authors}")
    if doi: print(f"    DOI: {doi}")
    if cites: print(f"    Citacoes: {cites}")
    print(f"    Keywords: {kw}")
    print(f"    Relevancia: {rel}")

print("\n" + "-" * 70)
print(f"  3. METODOLOGIAS REFINADAS POR Z ({len(methodologies)} metodos)")
print("-" * 70)
for m in methodologies:
    print(f"\n  [{m['id']}]")
    print(f"    Conceito ZRM: {m['zrm_concept']}")
    print(f"    Ref ZRM: {m['zrm_ref']}")
    print(f"    Argumento: {m['argument'][:200]}...")
    print(f"    Solucao Pratica: {m['practical_solution']}")
    print(f"    Ferramentas: {', '.join(m['tools'])}")
    print(f"    Dominios: {', '.join(m['domain_applications'][:3])}")

print("\n" + "-" * 70)
print(f"  4. ARGUMENTOS COM CITACOES ({len(arguments)} teses)")
print("-" * 70)
for a in arguments:
    print(f"\n  [{a['id']}]")
    print(f"    TESE: {a['claim']}")
    print(f"    Premissas:")
    for p in a['premises']:
        print(f"      - {p[:150]}")
    print(f"    Conclusao: {a['conclusion'][:200]}...")
    print(f"    Citacoes: {', '.join(a['citations'])}")

print("\n" + "=" * 70)
print("  RESUMO EXECUTIVO")
print("=" * 70)
print(f"""
  Base de pesquisa construida sobre o ecossistema OpenCode v4.0
  (Health Score: {eco_state.get('health_score', 0):.1f}/100, 
  {eco_state.get('active_components', 0)} componentes ativos).

  RECURSOS PRODUZIDOS:
    {len(concepts.get('core_concepts', {}))} conceitos extraidos do ZRM (Spivey 1992)
    {len(citations)} citacoes academicas com DOIs
    {len(methodologies)} metodologias refinadas por Z com ferramentas e dominios
    {len(arguments)} argumentos estruturados com premissas, conclusoes e contra-argumentos
    Tudo armazenado no SQLite state_manager (key: 'zrm:*')

  PROXIMOS PASSOS:
    1. Executar /artigo para gerar artigo Qualis A1 baseado nesta pesquisa
    2. Usar ptbr_corrector.py para garantir saida 100%% PT-BR
    3. Expandir base com mais artigos especificos de cada dominio
    4. Integrar com SEEKER para busca profunda em arXiv, Semantic Scholar
""")

print("=" * 70)
print("  Base de dados: SQLite (.evolve/state.db)")
print("  Chaves: zrm:concepts_extracted, zrm:citations,")
print("          zrm:methodologies, zrm:arguments")
print("=" * 70)
