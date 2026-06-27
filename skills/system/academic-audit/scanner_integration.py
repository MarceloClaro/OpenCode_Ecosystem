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
from potentiality_estimator_v2 import PotentialityEstimatorV2
from cognitive_diversity_scanner import CognitiveDiversityScanner, ArtifactProfile
from epistemic_topology_mapper import EpistemicTopologyMapper, TopologicalPoint
from rupture_potential_index import RupturePotentialIndex, ResearchOpportunity


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

    def __init__(self, use_v2: bool = True):
        self.scanner = NoologicalScanner()
        self.estimator_v1 = EpistemologicalPotentialEstimator()
        self.estimator_v2 = PotentialityEstimatorV2() if use_v2 else None
        self.use_v2 = use_v2
        # SPEC-053/054/055 — Novos scanners epistêmicos
        self.cds = CognitiveDiversityScanner()
        self.etm = EpistemicTopologyMapper()
        self.rpi = RupturePotentialIndex()

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

        # 2. EPS — Oportunidades de Pesquisa (v2 se disponivel, senao v1)
        if self.use_v2 and self.estimator_v2 is not None:
            eps_result = self.estimator_v2.scan(
                noological_results=scan_results,
                teleological_results=getattr(self, '_teleological_cache', {}),
                evolutionary_results=getattr(self, '_evolutionary_cache', {}),
                dna_results=getattr(self, '_dna_cache', {}),
                social_impact_results=getattr(self, '_social_cache', {}),
            )
            opportunities = eps_result["opportunities"]
            self.estimator_v2.save_report(eps_result, scanner_dir / "oportunidades_pesquisa_v2.md")
            self.estimator_v2.save_json(eps_result, scanner_dir / "scanner_data_v2.json")
        else:
            opportunities = self.estimator_v1.estimate(scan_results)
            self.estimator_v1.save_report(opportunities, scanner_dir / "oportunidades_pesquisa.md")

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

        # ═══ NOVO: SPEC-053/054/055 — Análise Cognitiva Avançada ═══
        diversity_analysis = self._run_diversity_analysis(scan_results, domain)
        topology_analysis = self._run_topology_analysis(scan_results)
        rupture_analysis = self._run_rupture_analysis(eps_data, diversity_analysis)

        # Salvar relatórios adicionais
        self._save_diversity_report(diversity_analysis, scanner_dir)
        self._save_topology_report(topology_analysis, scanner_dir)
        self._save_rupture_report(rupture_analysis, scanner_dir)

        # Enriquecer eps_data com as novas análises
        eps_data["cognitive_diversity"] = diversity_analysis
        eps_data["epistemic_topology"] = topology_analysis
        eps_data["rupture_potential"] = rupture_analysis

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


    # ═══════════════════════════════════════════════════════════════════
    # MÉTODOS DOS NOVOS SCANNERS (SPEC-053/054/055)
    # ═══════════════════════════════════════════════════════════════════

    def _run_diversity_analysis(
        self, scan_results: dict[str, Any], domain: str
    ) -> dict[str, Any]:
        """
        SPEC-053: Analisa diversidade cognitiva dos artefatos.

        Cria perfis a partir das dimensões escaneadas e calcula
        o Índice de Homogeneidade (HI).
        """
        self.cds.clear()

        # Criar artefatos a partir das dimensões do scan
        dims = scan_results.get("dimensions", {})
        for dim_key, dim_data in dims.items():
            density = dim_data.get("density", 0.0) if isinstance(dim_data, dict) else 0.0
            profile = ArtifactProfile(
                artifact_id=f"dim_{dim_key}",
                text_preview=f"Artefato inferido da dimensao {dim_key} (domain={domain})",
                coverage_vector={dim_key: density},
            )
            self.cds.register_artifact(profile)

        result = self.cds.compute_homogeneity_index()
        return result

    def _run_topology_analysis(
        self, scan_results: dict[str, Any]
    ) -> dict[str, Any]:
        """
        SPEC-054: Mapeia topologia do espaço de conhecimento.

        Projeta dimensões epistemológicas em 2D e detecta
        ilhas, buracos e pontes.
        """
        self.etm.clear()

        dims = scan_results.get("dimensions", {})
        dim_names = sorted(dims.keys())

        # Construir vetor N-dimensional a partir das densidades
        for dim_key in dim_names:
            dim_data = dims[dim_key]
            density = dim_data.get("density", 0.0) if isinstance(dim_data, dict) else 0.0

            # Vetor de coordenadas: [densidade, cobertura, 1-densidade]
            coverage = dim_data.get("coverage", density) if isinstance(dim_data, dict) else density
            vec = [density, coverage, 1.0 - density]
            pt = TopologicalPoint(
                point_id=f"dim_{dim_key}",
                coordinates=vec,
                label=dim_key,
            )
            self.etm.add_point(pt)

        if self.etm.point_count() < 2:
            return {"error": "Pontos insuficientes para analise topologica",
                    "n_points": self.etm.point_count()}

        projection = self.etm.project(dimensions=2)
        islands = self.etm.detect_islands()
        holes = self.etm.detect_holes()
        bridges = self.etm.compute_bridge_potential()

        return {
            "projection": projection,
            "islands": islands,
            "holes": holes,
            "bridges": bridges,
            "n_points": self.etm.point_count(),
        }

    def _run_rupture_analysis(
        self, eps_data: dict[str, Any], diversity: dict[str, Any]
    ) -> dict[str, Any]:
        """
        SPEC-055: Calcula Índice de Potencial de Ruptura (RPI).

        Combina EPS das oportunidades com métricas de diversidade
        para gerar portfólio balanceado.
        """
        self.rpi.clear()

        opportunities = eps_data.get("opportunities", [])

        for i, opp_data in enumerate(opportunities[:20]):
            # Estimar DE, FT, RR, CO a partir dos dados disponiveis
            de = min(1.0, opp_data.get("cross_domain_impact", 5) / 10.0)
            ft = min(1.0, opp_data.get("theoretical_fertility", 5) / 10.0)
            rr = min(1.0, (opp_data.get("game_theoretic_value", 5) +
                          opp_data.get("cascade_impact", 3)) / 20.0)
            co = min(1.0, 1.0 - (opp_data.get("teleological_alignment", 5) / 10.0))
            eps = opp_data.get("eps", 50.0)

            opp = ResearchOpportunity(
                opportunity_id=f"opp_{i}_{opp_data.get('dimension', '?')}",
                label=f"{opp_data.get('dimension', '?')}: {opp_data.get('category', '?')}",
                epistemic_distance=de,
                fertility=ft,
                risk_reward=rr,
                cost_opportunity=co,
                eps_score=eps,
            )
            self.rpi.register_opportunity(opp)

        portfolio = self.rpi.compute_portfolio()
        return portfolio

    def _save_diversity_report(
        self, result: dict[str, Any], output_dir: Path
    ) -> None:
        """Salva relatório de diversidade cognitiva."""
        path = output_dir / "diversidade_cognitiva.md"
        hi = result.get("global_hi", "N/A")
        classification = result.get("classification", "unknown")
        is_echo = result.get("is_echo_chamber", False)

        lines = [
            "# Relatório de Diversidade Cognitiva (SPEC-053)",
            "",
            f"**Índice de Homogeneidade (HI):** {hi}",
            f"**Classificação:** {classification}",
            f"**Câmara de Eco:** {'SIM' if is_echo else 'NÃO'}",
            f"**Artefatos Analisados:** {result.get('n_artifacts', 0)}",
            "",
            "## Recomendações",
        ]
        for rec in result.get("recommendations", []):
            lines.append(f"- {rec}")

        lines.append(f"\n_Relatório gerado automaticamente pelo ScannerIntegration_")
        path.write_text("\n".join(lines), encoding="utf-8")

    def _save_topology_report(
        self, result: dict[str, Any], output_dir: Path
    ) -> None:
        """Salva relatório de topologia epistemológica."""
        path = output_dir / "topologia_epistemologica.md"
        lines = [
            "# Relatório de Topologia Epistemológica (SPEC-054)",
            "",
            f"**Pontos Mapeados:** {result.get('n_points', 0)}",
            f"**Ilhas Detectadas:** {len(result.get('islands', []))}",
            f"**Buracos Detectados:** {len(result.get('holes', []))}",
            f"**Pontes Identificadas:** {len(result.get('bridges', []))}",
            "",
        ]

        islands = result.get("islands", [])
        if islands:
            lines.append("## Ilhas Epistemológicas")
            for ilha in islands[:5]:
                lines.append(f"- {ilha.get('island_id')}: {ilha.get('size', 0)} pontos, "
                           f"II={ilha.get('isolation_index', 0):.3f}")

        holes = result.get("holes", [])
        if holes:
            lines.append("\n## Buracos Epistemológicos")
            for buraco in holes[:5]:
                lines.append(f"- {buraco.get('hole_id')}: BE={buraco.get('be_score', 0):.3f}, "
                           f"gap={buraco.get('gap', 0):.3f}")

        bridges = result.get("bridges", [])
        if bridges:
            lines.append("\n## Pontes Potenciais")
            for ponte in bridges[:5]:
                lines.append(f"- {ponte.get('point_id')}: PP={ponte.get('pp_score', 0):.3f}")

        lines.append(f"\n_Relatório gerado automaticamente pelo ScannerIntegration_")
        path.write_text("\n".join(lines), encoding="utf-8")

    def _save_rupture_report(
        self, result: dict[str, Any], output_dir: Path
    ) -> None:
        """Salva relatório de potencial de ruptura."""
        path = output_dir / "potencial_ruptura.md"

        if "error" in result:
            path.write_text(f"# Relatório de Potencial de Ruptura (SPEC-055)\n\nErro: {result['error']}",
                          encoding="utf-8")
            return

        lines = [
            "# Relatório de Potencial de Ruptura (SPEC-055)",
            "",
            f"**Oportunidades Analisadas:** {result.get('n_opportunities', 0)}",
            "",
            "## Distribuição por Quadrante",
        ]
        for q, count in result.get("quadrant_distribution", {}).items():
            lines.append(f"- {q}: {count}")

        lines.append("\n## Estratégia de Portfólio")
        strategy = result.get("portfolio_strategy", "")
        lines.append(strategy)

        opps = result.get("opportunities", [])
        if opps:
            lines.append("\n## Top 5 Oportunidades por RPI")
            for opp in opps[:5]:
                lines.append(f"- {opp.get('label', '?')}: RPI={opp.get('rpi_score', 0):.1f}, "
                           f"Quadrante={opp.get('quadrant', '?')}")

        lines.append(f"\n_Relatório gerado automaticamente pelo ScannerIntegration_")
        path.write_text("\n".join(lines), encoding="utf-8")


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
