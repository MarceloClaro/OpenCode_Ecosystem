#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ScannerIntegration v1.0 — Scanner Noológico em Toda Produção
==============================================================
Integra o Scanner Noológico (v1+v2+v3) em TODOS os pipelines
do OpenCode Ecosystem:
  - /artigo (MASWOS)  → auto-scan + EPS
  - /reversa          → scan de documentação
  - /evolve           → scan de evolução
  - @audit_traced     → decorator para qualquer função

Outputs para cada pipeline:
  1. Relatório de Cobertura (v2.0) — o que está ausente
  2. Relatório EPS (v3.0) — oportunidades priorizadas
  3. JSON estruturado para dashboards
  4. Integração com InteractionLogger (registro automático)
"""

import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import Any

BRAZIL_TZ = timezone.utc

# Localizar modulos
BASE = Path(__file__).parent.parent
sys.path.insert(0, str(BASE / "skills" / "system" / "academic-audit"))
sys.path.insert(0, str(BASE / "skills" / "system" / "reasoning-orchestrator"))

from noological_scanner import NoologicalScanner
from epistemological_potential import EpistemologicalPotentialEstimator


class ScannerIntegration:
    """Integração do Scanner Noológico em toda produção do ecossistema.

    Uso automático — basta chamar após qualquer pipeline:

        integrator = ScannerIntegration()
        report = integrator.scan_pipeline_output(
            pipeline="artigo",
            audit_trail=trail,
            output_dir="pesquisas/meu_artigo/"
        )
    """

    def __init__(self):
        self.scanner = NoologicalScanner()
        self.estimator = EpistemologicalPotentialEstimator()

    def scan_pipeline_output(
        self,
        pipeline: str,
        audit_trail: Any,
        output_dir: str | Path,
        domain: str = "",
    ) -> dict[str, Any]:
        """Executa scan completo em qualquer saída de pipeline.

        Args:
            pipeline: Nome do pipeline ("artigo", "reversa", "evolve", "estudo_de_caso")
            audit_trail: AcademicAuditTrail com parágrafos e evidências
            output_dir: Diretório para salvar relatórios
            domain: Domínio de pesquisa (psicologia, economia, computação, etc.)

        Returns:
            Dict com todos os resultados do scan
        """
        out = Path(output_dir)
        scanner_dir = out / "scanner_noológico"
        scanner_dir.mkdir(parents=True, exist_ok=True)

        # 1. Scan v2.0 — Cobertura Epistemológica
        scan_results = self.scanner.scan(audit_trail, research_domain=domain)
        self.scanner.save_report(scanner_dir / "cobertura_epistemologica.md")

        # 2. EPS v3.0 — Oportunidades de Pesquisa
        opportunities = self.estimator.estimate(scan_results)
        self.estimator.save_report(opportunities, scanner_dir / "oportunidades_pesquisa.md")

        # 3. JSON estruturado
        import json
        eps_data = {
            "pipeline": pipeline,
            "domain": domain,
            "timestamp": datetime.now(BRAZIL_TZ).isoformat(),
            "coverage": scan_results,
            "opportunities": [
                {
                    "rank": i+1,
                    "dimension": opp.dimension,
                    "category": opp.category,
                    "eps": opp.eps,
                    "grade": opp.grade,
                    "rationale": opp.rationale,
                    "suggested_method": opp.suggested_method,
                }
                for i, opp in enumerate(opportunities[:20])
            ],
            "summary": {
                "total_opportunities": len(opportunities),
                "discovery": sum(1 for o in opportunities if o.grade == "Discovery"),
                "promising": sum(1 for o in opportunities if o.grade == "Promising"),
                "exploratory": sum(1 for o in opportunities if o.grade == "Exploratory"),
                "marginal": sum(1 for o in opportunities if o.grade == "Marginal"),
                "coverage_pct": scan_results["overall_coverage_pct"],
                "completeness_grade": scan_results["completeness_grade"],
            },
        }
        (scanner_dir / "scanner_data.json").write_text(
            json.dumps(eps_data, indent=2, ensure_ascii=False), encoding="utf-8"
        )

        # 4. Registrar no InteractionLogger
        try:
            from interaction_logger import get_logger
            logger = get_logger()
            logger.log_artifact(
                "scanner_report",
                str(scanner_dir / "cobertura_epistemologica.md"),
                {"coverage_pct": scan_results["overall_coverage_pct"],
                 "discoveries": eps_data["summary"]["discovery"]}
            )
        except ImportError:
            pass

        return eps_data


# Decorator para auto-scan em qualquer função de pipeline
def auto_scan(pipeline_name: str = "", domain: str = ""):
    """Decorator que executa scan automático após qualquer pipeline.

    Uso:
        @auto_scan("artigo", "psicologia")
        def meu_pipeline(audit_trail):
            ...
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            # Executar scan se audit_trail estiver disponível
            audit_trail = kwargs.get("audit_trail") or (args[0] if args else None)
            if audit_trail and hasattr(audit_trail, "paragraphs"):
                try:
                    integrator = ScannerIntegration()
                    output_dir = kwargs.get("output_dir", "pesquisas/scanner_auto")
                    integrator.scan_pipeline_output(
                        pipeline=pipeline_name or func.__name__,
                        audit_trail=audit_trail,
                        output_dir=output_dir,
                        domain=domain,
                    )
                except Exception as e:
                    print(f"[auto_scan] Erro: {e}")
            return result
        return wrapper
    return decorator


# ── Quick test ──
if __name__ == "__main__":
    from academic_audit_trail import AcademicAuditTrail

    trail = AcademicAuditTrail()
    trail.record_paragraph("P01", "TCC eficaz para ansiedade com d=0.73.")
    trail.record_paragraph("P02", "Equilibrio de Nash na relacao terapeutica.")
    trail.record_paragraph("P03", "fMRI mostra reducao da amigdala pos-TCC.")

    integrator = ScannerIntegration()
    report = integrator.scan_pipeline_output(
        pipeline="teste",
        audit_trail=trail,
        output_dir="pesquisas/scanner_teste",
        domain="psicologia",
    )

    print(f"Pipeline: {report['pipeline']}")
    print(f"Coverage: {report['summary']['coverage_pct']}%")
    print(f"Oportunidades: {report['summary']['total_opportunities']}")
    print(f"  Discovery: {report['summary']['discovery']}")
    print(f"  Promising: {report['summary']['promising']}")
