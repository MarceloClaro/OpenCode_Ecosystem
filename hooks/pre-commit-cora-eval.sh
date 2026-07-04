#!/usr/bin/env bash
# CORA-Eval Pre-Commit Hook — D1-D26 + R31-R42
# Instalar: cp hooks/pre-commit-cora-eval.sh .git/hooks/pre-commit && chmod +x .git/hooks/pre-commit
set -e

VENV_PYTEST=".venv/bin/pytest"
if [ ! -f "$VENV_PYTEST" ]; then
    VENV_PYTEST="pytest"
fi

echo ""
echo "╔══════════════════════════════════════════════════════╗"
echo "║  🔬 CORA-Eval Pre-Commit (D1-D26 + R31-R42)          ║"
echo "╚══════════════════════════════════════════════════════╝"

# CORA-Eval: D1-D26 (261 CTs)
echo ""
echo "--- CORA-Eval D1-D26 ---"
$VENV_PYTEST tests/test_d*.py -q --tb=short --no-header

# Ecosystem Cycle Tests: R31-R42 (100+ CTs)
echo ""
echo "--- Ecosystem R31-R42 ---"
$VENV_PYTEST tests/test_r*_*.py -q --tb=short --no-header

echo ""
echo "✅ CORA-Eval + R31-R42: todos os CTs passando. Commit autorizado."
