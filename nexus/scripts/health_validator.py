# -*- coding: utf-8 -*-
"""health_validator.py - Teste de validacao e saude do ecossistema."""

import sys
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.parent.resolve()
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from core import initialize_core
from core.config import settings
from core.container import Container

initialize_core()

sm = Container.instance().resolve('state_manager')

def separator(char="=", width=60):
    print(char * width)

def main():
    separator()
    print("  RELATORIO DE VALIDACAO E SAUDE DO ECOSISTEMA")
    separator()

    state = sm.get("ecosystem-state", default={})
    if not state:
        print("  ERRO: Nenhum estado encontrado. Rode sync_orchestrator --run primeiro.")
        return

    version = state.get("version", "?")
    timestamp = state.get("timestamp", "nunca")
    hs = state.get("health_score", 0)
    total = state.get("total_components", 0)
    active = state.get("active_components", 0)
    degraded = state.get("degraded_components", 0)
    offline = state.get("offline_components", 0)

    print(f"  Versao: {version}")
    print(f"  Timestamp: {timestamp}")
    print(f"  Health Score: {hs:.1f}/100")
    print(f"  Componentes: {total} total")
    print(f"    Ativos: {active}")
    print(f"    Degradados: {degraded}")
    print(f"    Offline: {offline}")

    cv = state.get("cross_validation_matrix", {})
    print(f"  Cross-Validation: {len(cv)} affinities")

    te = state.get("token_efficiency", {})
    print(f"  Token Efficiency:")
    cjk_status = "ATIVO" if te.get("cjk_corrector_active") else "INATIVO"
    hc = te.get("header_coverage", 0)
    econ = te.get("context_tokens_saved", 0)
    print(f"    Corretor CJK: {cjk_status}")
    print(f"    Header Coverage: {hc}%")
    print(f"    Economia contexto: ~{econ}%")

    cb = te.get("component_breakdown", {})
    if cb:
        print(f"  Breakdown:")
        for k, v in cb.items():
            print(f"    {k}: {v}")

    conflicts = state.get("conflicts", [])
    print(f"  Conflitos: {len(conflicts)}")

    recs = state.get("recommendations", [])
    print(f"  Recomendacoes ({len(recs)}):")
    for r in recs[:10]:
        print(f"    - {r}")

    heal = state.get("auto_healing_log", [])
    if heal:
        print(f"  Auto-Healing Log: {len(heal)} acoes")
        for h in heal[:5]:
            comp = h.get("component", "?")
            issue = h.get("issue", "?")
            print(f"    - {comp}: {issue}")

    healer_report = sm.get("self_healer:last_report", default={})
    if healer_report:
        separator()
        print("  SELF-HEALER ULTIMO RELATORIO:")
        totals = healer_report.get("totals", {})
        print(f"    CJK leaks: {totals.get('cjk', 0)}")
        print(f"    Frontmatter: {totals.get('frontmatter', 0)}")
        print(f"    Oversize: {totals.get('oversize', 0)}")
        print(f"    Syntax errors: {totals.get('syntax', 0)}")
        print(f"    Total anomalias: {totals.get('total', 0)}")

    healer_fix = sm.get("self_healer:last_fix", default={})
    if healer_fix:
        separator()
        print("  ULTIMA CORRECAO:")
        correcoes = healer_fix.get("correcoes", {})
        for k, v in correcoes.items():
            print(f"    {k}: {v}")

    hist = sm.get("self_healer:history", default=[])
    if hist and isinstance(hist, list) and len(hist) > 0:
        separator()
        print(f"  HISTORICO SELF-HEALER: {len(hist)} execucoes")
        last = hist[-1]
        lt = last.get("timestamp", "?")
        ltotal = last.get("total", 0)
        print(f"    Ultima: {lt} | total={ltotal}")

    ds = sm.get("dynamic-scores", default={})
    if ds:
        separator()
        print(f"  DYNAMIC SCORES: {len(ds)} componentes rastreados")
        under = [n for n, d in ds.items() if d.get("computed_score", 85) < 60]
        if under:
            print(f"    Underperforming (<60): {under[:5]}")
        else:
            print(f"    Todos acima de 60 - saudavel")

    state_path = settings.STATE_DIR / "ecosystem-state.json"
    if state_path.exists():
        separator()
        size_kb = state_path.stat().st_size / 1024
        print(f"  STATE PERSISTENTE: {size_kb:.1f}KB")
        print(f"  Path: {state_path}")

    separator()
    if hs >= 95:
        print("  STATUS: SAUDAVEL")
    elif hs >= 85:
        print("  STATUS: ATENCAO")
    elif hs >= 70:
        print("  STATUS: ALERTA")
    else:
        print("  STATUS: CRITICO")
    separator()

    valid = hs >= 95 and active > 0 and offline == 0 and cjk_status == "ATIVO"
    separator()
    if valid:
        print("  VALIDACAO: APROVADO - Ecossistema operacional e saudavel")
    else:
        issues = []
        if hs < 95:
            issues.append(f"health_score={hs:.1f} (esperado >= 95)")
        if active == 0:
            issues.append("nenhum componente ativo")
        if offline > 0:
            issues.append(f"{offline} componentes offline")
        if cjk_status != "ATIVO":
            issues.append("corretor CJK inativo")
        print(f"  VALIDACAO: REPROVADO - {', '.join(issues)}")
    separator()

if __name__ == "__main__":
    main()
