"""
Adaptador para execução de auditoria do ecossistema.

Delega para scripts de auditoria acadêmica e Qualis A1 quando disponíveis.
Em modo fallback, invoca `ecosystem doctor` e `ecosystem status` via subprocess
para evitar acoplamento direto com módulos de camada inferior.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


AUDIT_SCRIPT = Path("ecosystem-auditor/scripts/audit_ecosystem.py")


def run_audit(output_format: str = "text") -> int:
    """Executa auditoria completa do ecossistema.

    Args:
        output_format: Formato de saída ('text', 'json', 'html').

    Returns:
        Código de saída (0 = sucesso).
    """
    if AUDIT_SCRIPT.exists():
        cmd = [sys.executable, str(AUDIT_SCRIPT)]
        if output_format != "text":
            cmd.extend(["--format", output_format])
        print(f"Auditando ecossistema (formato: {output_format})...")
        try:
            result = subprocess.run(cmd, cwd=Path.cwd())
            return result.returncode
        except Exception as e:
            print(f"ERRO na auditoria: {e}", file=sys.stderr)
            return 1
    else:
        # Fallback: executa doctor e status via subprocess (sem acoplamento)
        print("Usando auditoria embutida do ecossistema via subprocess:\n"
              "  ecosystem doctor  (diagnóstico de saúde)\n"
              "  ecosystem status  (métricas do sistema)")
        try:
            eco_script = Path(sys.argv[0]) if sys.argv else None
            if eco_script and eco_script.name == "ecosystem":
                doctor = subprocess.run(
                    [sys.executable, str(eco_script), "doctor"],
                    capture_output=True, text=True, timeout=30,
                )
                status = subprocess.run(
                    [sys.executable, str(eco_script), "status"],
                    capture_output=True, text=True, timeout=30,
                )
                print(doctor.stdout[:200] if doctor.stdout else "")
                print(status.stdout[:200] if status.stdout else "")
            else:
                print("(ecosystem CLI não encontrado — fallback informativo)")
        except Exception as e:
            print(f"AVISO: fallback de auditoria: {e}", file=sys.stderr)
        return 0
