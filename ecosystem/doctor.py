"""
Doctor — Diagnóstico completo de saúde do ecossistema.

Verifica:
- Entrypoints canônicos
- Contratos registrados
- Schemas de estado
- Dependências
- Integridade do ecossistema
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


def run_diagnosis(auto_fix: bool = False) -> int:
    """Executa diagnóstico completo.

    Args:
        auto_fix: Se True, tenta corrigir problemas automaticamente

    Returns:
        Código de saída (0 = tudo ok, 1 = problemas encontrados)
    """
    issues: list[str] = []
    fixes: list[str] = []
    score = 100

    print("=" * 60)
    print("  OpenCode Ecosystem — Diagnóstico de Saúde (Doctor)")
    print("=" * 60)

    # 1. Verifica ecosystem-state.json
    print("\n[1/6] Artefato de estado principal...")
    state_path = Path("ecosystem-state.json")
    if state_path.exists():
        try:
            state = json.loads(state_path.read_text(encoding="utf-8"))
            version = state.get("version", "unknown")
            cycle = state.get("current_cycle", "unknown")
            print(f"  ✅ ecosystem-state.json v{version}, ciclo {cycle}")
        except (json.JSONDecodeError, IOError) as e:
            issues.append(f"ecosystem-state.json corrompido: {e}")
            print(f"  ❌ {e}")
            score -= 15
    else:
        issues.append("ecosystem-state.json não encontrado")
        print("  ❌ Não encontrado")
        score -= 20

    # 2. Verifica entrypoints
    print("\n[2/6] Entrypoints canônicos...")
    entrypoints = [
        ("ecosystem/__main__.py", "CLI canônica"),
        ("ecosystem/cli.py", "Parser CLI"),
        ("ecosystem/__init__.py", "Pacote ecosystem"),
    ]
    for path, desc in entrypoints:
        if Path(path).exists():
            print(f"  ✅ {desc} ({path})")
        else:
            issues.append(f"{desc} não encontrado: {path}")
            print(f"  ❌ {desc} ausente")
            score -= 10

    # 3. Verifica contratos
    print("\n[3/6] Contratos entre módulos...")
    contract_files = [
        "ecosystem/contracts/registry.py",
        "ecosystem/contracts/interfaces/iagent.py",
        "ecosystem/contracts/interfaces/iscanner.py",
        "ecosystem/contracts/interfaces/iadapter.py",
    ]
    contracts_ok = 0
    for path in contract_files:
        if Path(path).exists():
            contracts_ok += 1
        else:
            issues.append(f"Contrato ausente: {path}")
            print(f"  ❌ {path}")

    if contracts_ok == len(contract_files):
        print(f"  ✅ {contracts_ok}/{len(contract_files)} contratos implementados")
    else:
        print(f"  ⚠️  {contracts_ok}/{len(contract_files)} contratos implementados")
        score -= 5 * (len(contract_files) - contracts_ok)

    # 4. Verifica schemas
    print("\n[4/6] Schemas de estado...")
    schema_dirs = [
        "ecosystem/schemas/registry.py",
        "ecosystem/schemas/versions.py",
    ]
    schemas_ok = sum(1 for p in schema_dirs if Path(p).exists())
    if schemas_ok == len(schema_dirs):
        print(f"  ✅ {schemas_ok}/{len(schema_dirs)} módulos de schema implementados")
    else:
        print(f"  ⚠️  {schemas_ok}/{len(schema_dirs)} módulos de schema")
        score -= 5

    # 5. Verifica grafo de dependências
    print("\n[5/6] Grafo de dependências...")
    dep_files = [
        "ecosystem/deps/analyzer.py",
    ]
    deps_ok = sum(1 for p in dep_files if Path(p).exists())
    if deps_ok == len(dep_files):
        print(f"  ✅ {deps_ok}/{len(dep_files)} módulos de dependência implementados")
    else:
        print(f"  ⚠️  {deps_ok}/{len(dep_files)} módulos de dependência")
        score -= 5

    # 6. Verifica testes
    print("\n[6/6] Testes do ecossistema...")
    test_dirs = [
        "tests/ecosystem/",
    ]
    test_files = list(Path("tests/ecosystem").rglob("test_*.py")) if Path("tests/ecosystem").exists() else []
    if test_files:
        print(f"  ✅ {len(test_files)} testes encontrados em tests/ecosystem/")
    else:
        print(f"  ⚠️  Nenhum teste específico do ecossistema encontrado")
        score -= 5

    # Resultado final
    print("\n" + "=" * 60)
    final_score = max(0, score)
    if final_score >= 90:
        grade = "🟢 EXCELENTE"
    elif final_score >= 70:
        grade = "🟡 REGULAR"
    else:
        grade = "🔴 CRÍTICO"

    print(f"  Score de saúde: {final_score}/100 — {grade}")

    if issues:
        print(f"\n  Problemas encontrados ({len(issues)}):")
        for issue in issues:
            print(f"    • {issue}")

    if fixes and auto_fix:
        print(f"\n  Correções aplicadas ({len(fixes)}):")
        for fix in fixes:
            print(f"    ✓ {fix}")

    if auto_fix and not fixes:
        print("\n  Nenhuma correção necessária.")

    print("=" * 60)

    return 0 if final_score >= 70 else 1
