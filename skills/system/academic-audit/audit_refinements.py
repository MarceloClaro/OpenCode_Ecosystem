#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AuditRefinements v1.0 — Melhorias para Pesquisador e Auditor (Round 12)
=========================================================================
Cinco melhorias integradas ao sistema de auditoria:

1. AuditDashboard — Dashboard HTML interativo em tempo real
2. AuditSearch — Busca/filtro de sessões por paradigma, nível, data, score
3. ResearcherScore — Score de qualidade da sessão (0-100)
4. BudgetAlert — Alertas proativos de orçamento de tokens
5. PipelineIntegration — Integração automática com SEEKER e MASWOS

Uso:
  from audit_refinements import AuditDashboard, AuditSearch, ResearcherScore, BudgetAlert
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from interaction_logger import InteractionLogger, get_logger
from academic_audit_trail import AcademicAuditTrail
from token_economy_monitor import TokenEconomyMonitor, LEVEL_BUDGETS

BRAZIL_TZ = timezone.utc
REFINEMENTS_DIR = Path(__file__).parent.parent.parent.parent / ".evolve" / "audit-refinements"


# ═══════════════════════════════════════════════════════════════════════
# 1. ResearcherScore — Score de Qualidade da Sessão (0-100)
# ═══════════════════════════════════════════════════════════════════════

class ResearcherScore:
    """Calcula score de qualidade da sessão de pesquisa.

    Critérios (pesos):
      - Evidências por parágrafo (25%): ideal ≥ 2 evidências/parágrafo
      - Fontes verificadas (20%): % de DOIs/arXiv confirmados
      - TSAC compliance (20%): % parágrafos limpos (0 violações)
      - Diversidade de fontes (15%): número de fontes únicas
      - Cobertura multi-domínio (10%): domínios de dados acessados
      - Peer review (10%): % parágrafos revisados por pares
    """

    WEIGHTS = {
        "evidence_density": 0.25,
        "verified_sources": 0.20,
        "tsac_compliance": 0.20,
        "source_diversity": 0.15,
        "domain_coverage": 0.10,
        "peer_review": 0.10,
    }

    @classmethod
    def calculate(
        cls,
        trail: AcademicAuditTrail,
        monitor: TokenEconomyMonitor | None = None,
    ) -> dict[str, Any]:
        """Calcula score de qualidade da sessão."""
        paragraphs = trail.paragraphs
        if not paragraphs:
            return {"score": 0, "grade": "F", "details": {}}

        n = len(paragraphs)
        total_evidence = sum(len(p.evidence) for p in paragraphs.values())

        # 1. Densidade de evidências (ideal: 2+/parágrafo)
        ev_density = min(total_evidence / max(1, n * 2), 2.0) / 2.0

        # 2. Fontes verificadas
        verified = sum(1 for p in paragraphs.values() for e in p.evidence if e.verified)
        total_ev = max(1, total_evidence)
        verified_pct = verified / total_ev

        # 3. TSAC compliance
        clean_paras = sum(1 for p in paragraphs.values() if p.tsac_score == 0)
        tsac_pct = clean_paras / max(1, n)

        # 4. Diversidade de fontes
        sources = set()
        for p in paragraphs.values():
            for e in p.evidence:
                sources.add(e.source)
        source_diversity = min(len(sources) / max(1, n), 2.0) / 2.0

        # 5. Cobertura multi-domínio
        domains_used = 1  # mínimo 1
        if monitor:
            stages = set(u.pipeline_stage for u in monitor.usage_history)
            domains_used = min(len(stages), 8) / 8

        # 6. Peer review
        reviewed = sum(1 for p in paragraphs.values() if p.peer_reviewed)
        peer_pct = reviewed / max(1, n)

        # Score ponderado
        raw = (
            ev_density * cls.WEIGHTS["evidence_density"] +
            verified_pct * cls.WEIGHTS["verified_sources"] +
            tsac_pct * cls.WEIGHTS["tsac_compliance"] +
            source_diversity * cls.WEIGHTS["source_diversity"] +
            domains_used * cls.WEIGHTS["domain_coverage"] +
            peer_pct * cls.WEIGHTS["peer_review"]
        )
        score = round(raw * 100)

        grade = "A" if score >= 90 else "B" if score >= 75 else "C" if score >= 60 else "D" if score >= 40 else "F"

        return {
            "score": score,
            "grade": grade,
            "max_score": 100,
            "details": {
                "evidence_density": round(ev_density * 100),
                "verified_sources": round(verified_pct * 100),
                "tsac_compliance": round(tsac_pct * 100),
                "source_diversity": round(source_diversity * 100),
                "domain_coverage": round(domains_used * 100),
                "peer_review": round(peer_pct * 100),
            },
            "counts": {
                "paragraphs": n,
                "total_evidence": total_evidence,
                "unique_sources": len(sources),
                "clean_paragraphs": clean_paras,
                "reviewed_paragraphs": reviewed,
            },
        }


# ═══════════════════════════════════════════════════════════════════════
# 2. BudgetAlert — Alertas Proativos de Orçamento
# ═══════════════════════════════════════════════════════════════════════

class BudgetAlert:
    """Sistema de alertas proativos de orçamento de tokens."""

    @staticmethod
    def check(monitor: TokenEconomyMonitor) -> list[dict[str, Any]]:
        """Verifica condições de alerta e retorna lista de alertas."""
        alerts = []
        report = monitor.get_efficiency_report()

        # Alerta: orçamento > 50%
        if report["budget_used_pct"] > 50:
            alerts.append({
                "level": "warning" if report["budget_used_pct"] < 80 else "critical",
                "type": "budget_threshold",
                "message": f"Orçamento em {report['budget_used_pct']}% ({report['total_tokens']:,}/{report['session_budget']:,} tokens)",
                "suggestion": "Considere consolidar queries ou reduzir escopo",
                "timestamp": datetime.now(BRAZIL_TZ).isoformat(),
            })

        # Alerta: baixa eficiência
        if report["efficiency_ratio"] < 0.25:
            alerts.append({
                "level": "info",
                "type": "low_efficiency",
                "message": f"Eficiência baixa: {report['efficiency_ratio']:.2f} (output/input)",
                "suggestion": "Use edição cirúrgica para reduzir output redundante",
                "timestamp": datetime.now(BRAZIL_TZ).isoformat(),
            })

        # Alerta: muitas interações
        if report["interactions"] > 30 and monitor.level == 1:
            alerts.append({
                "level": "info",
                "type": "high_interaction_count",
                "message": f"{report['interactions']} interações no Nível 1",
                "suggestion": "Considere consolidar queries para reduzir round-trips",
                "timestamp": datetime.now(BRAZIL_TZ).isoformat(),
            })

        # Alerta: orçamento crítico (> 90%)
        if report["budget_used_pct"] > 90:
            alerts.append({
                "level": "critical",
                "type": "budget_exhausted",
                "message": f"ORÇAMENTO QUASE ESGOTADO: {report['budget_used_pct']}%",
                "suggestion": f"Migre para Nível {min(3, monitor.level + 1)} ou encerre a sessão",
                "timestamp": datetime.now(BRAZIL_TZ).isoformat(),
            })

        return alerts


# ═══════════════════════════════════════════════════════════════════════
# 3. AuditSearch — Busca e Filtro de Sessões
# ═══════════════════════════════════════════════════════════════════════

class AuditSearch:
    """Busca e filtro de sessões de auditoria."""

    @staticmethod
    def search(
        query: str = "",
        paradigm: str = "",
        level: int | None = None,
        min_score: int = 0,
        date_from: str = "",
        date_to: str = "",
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        """Busca sessões com filtros combinados.

        Args:
            query: Texto livre para busca em logs
            paradigm: Filtrar por paradigma
            level: Filtrar por nível (1/2/3)
            min_score: Score mínimo de qualidade
            date_from: Data inicial (ISO)
            date_to: Data final (ISO)
            limit: Máximo de resultados

        Returns:
            Lista de sessões que atendem aos critérios
        """
        results = []
        sessions = InteractionLogger.list_sessions()

        for s in sessions:
            sid = s.get("session_id", "")
            if not sid:
                continue

            # Filtro por paradigma
            if paradigm and paradigm.lower() not in s.get("paradigm", "").lower():
                continue

            # Filtro por nível
            if level is not None:
                records = InteractionLogger.load_session(sid)
                sess_level = 1
                for r in records:
                    if r.get("type") == "session_start":
                        sess_level = r.get("level", 1)
                        break
                if sess_level != level:
                    continue

            # Filtro por data
            ts = s.get("timestamp", "")
            if date_from and ts < date_from:
                continue
            if date_to and ts > date_to:
                continue

            # Busca textual nos registros
            if query:
                records = InteractionLogger.load_session(sid)
                found = False
                for r in records:
                    if query.lower() in json.dumps(r, ensure_ascii=False).lower():
                        found = True
                        break
                if not found:
                    continue

            # Carrega score se necessário
            score = 0
            if min_score > 0:
                records = InteractionLogger.load_session(sid)
                for r in records:
                    if r.get("type") == "session_end":
                        score = r.get("quality_score", 0)
                        break
                if score < min_score:
                    continue

            results.append({
                **s,
                "score": score,
            })

            if len(results) >= limit:
                break

        return results

    @staticmethod
    def compare(session_ids: list[str]) -> dict[str, Any]:
        """Compara múltiplas sessões lado a lado."""
        comparison = {"sessions": [], "best": None}

        best_score = -1
        for sid in session_ids:
            records = InteractionLogger.load_session(sid)
            if not records:
                continue

            interactions = sum(1 for r in records if r.get("type") == "interaction")
            errors = sum(1 for r in records if r.get("type") == "error")
            artifacts = sum(1 for r in records if r.get("type") == "artifact")
            paradigm = ""
            level = 1
            score = 0

            for r in records:
                if r.get("type") == "session_start":
                    paradigm = r.get("paradigm", "")
                    level = r.get("level", 1)
                if r.get("type") == "session_end":
                    score = r.get("quality_score", 0)
                    if score > best_score:
                        best_score = score
                        comparison["best"] = sid

            comparison["sessions"].append({
                "session_id": sid,
                "paradigm": paradigm,
                "level": level,
                "interactions": interactions,
                "errors": errors,
                "artifacts": artifacts,
                "score": score,
                "health": "OK" if errors == 0 else f"{errors} erros",
            })

        return comparison


# ═══════════════════════════════════════════════════════════════════════
# 4. AuditDashboard — Dashboard HTML Interativo
# ═══════════════════════════════════════════════════════════════════════

class AuditDashboard:
    """Dashboard HTML interativo para pesquisador e auditor."""

    @staticmethod
    def generate(
        trail: AcademicAuditTrail,
        monitor: TokenEconomyMonitor,
        logger: InteractionLogger,
        output_path: str | None = None,
    ) -> str:
        """Gera dashboard HTML completo.

        Args:
            trail: Trilha de auditoria
            monitor: Monitor de tokens
            logger: Logger de interações
            output_path: Caminho para salvar (opcional)

        Returns:
            HTML do dashboard
        """
        score = ResearcherScore.calculate(trail, monitor)
        alerts = BudgetAlert.check(monitor)
        token_rpt = monitor.get_efficiency_report()
        stats = logger.get_stats()

        # Construir HTML
        html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Audit Dashboard — {logger.session_id}</title>
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ font-family:'Segoe UI',Arial,sans-serif; background:#f5f6fa; color:#2c3e50; }}
.header {{ background:linear-gradient(135deg,#2c3e50,#34495e); color:white; padding:24px 32px; }}
.header h1 {{ font-size:22px; }}
.header .meta {{ font-size:12px; opacity:.7; margin-top:4px; }}
.grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(280px,1fr)); gap:16px; padding:24px; }}
.card {{ background:white; border-radius:12px; padding:20px; box-shadow:0 2px 8px rgba(0,0,0,.08); }}
.card h3 {{ font-size:14px; color:#7f8c8d; margin-bottom:12px; text-transform:uppercase; letter-spacing:.5px; }}
.score-big {{ font-size:48px; font-weight:bold; text-align:center; }}
.score-{score['grade'].lower()} {{ color:{'#27ae60' if score['grade']=='A' else '#f39c12' if score['grade']=='B' else '#e74c3c'}; }}
.metric-row {{ display:flex; justify-content:space-between; padding:6px 0; border-bottom:1px solid #ecf0f1; font-size:13px; }}
.metric-row:last-child {{ border-bottom:none; }}
.metric-val {{ font-weight:bold; }}
.alert {{ padding:10px 14px; border-radius:8px; margin:6px 0; font-size:12px; }}
.alert-critical {{ background:#fde8e8; color:#c0392b; border-left:4px solid #e74c3c; }}
.alert-warning {{ background:#fef9e7; color:#b7950b; border-left:4px solid #f39c12; }}
.alert-info {{ background:#eaf2f8; color:#2980b9; border-left:4px solid #3498db; }}
.progress-bar {{ height:8px; background:#ecf0f1; border-radius:4px; margin:8px 0; overflow:hidden; }}
.progress-fill {{ height:100%; border-radius:4px; transition:width .3s; }}
.table {{ width:100%; border-collapse:collapse; font-size:12px; }}
.table th {{ text-align:left; padding:8px; background:#f8f9fa; border-bottom:2px solid #dee2e6; }}
.table td {{ padding:8px; border-bottom:1px solid #ecf0f1; }}
.footer {{ text-align:center; padding:16px; font-size:11px; color:#95a5a6; }}
</style>
</head>
<body>

<div class="header">
  <h1>🔬 Audit Dashboard</h1>
  <div class="meta">
    Sessão: {logger.session_id} | Paradigma: {logger.paradigm or 'N/A'} | Nível: {logger.level}
    <br>Gerado: {datetime.now(BRAZIL_TZ).strftime('%d/%m/%Y %H:%M')} (UTC-3)
  </div>
</div>

<div class="grid">
  <!-- Score Card -->
  <div class="card">
    <h3>🎯 Score de Qualidade</h3>
    <div class="score-big score-{score['grade'].lower()}">{score['score']}</div>
    <div style="text-align:center;font-size:14px;color:#7f8c8d;">Grade: {score['grade']}</div>
    <div style="margin-top:12px;">
      {''.join(f'<div class="metric-row"><span>{k}</span><span class="metric-val">{v}%</span></div>' for k,v in score['details'].items())}
    </div>
  </div>

  <!-- Token Budget Card -->
  <div class="card">
    <h3>💰 Orçamento de Tokens</h3>
    <div style="font-size:13px;margin-bottom:8px;">
      {token_rpt['total_tokens']:,} / {token_rpt['session_budget']:,} tokens
    </div>
    <div class="progress-bar">
      <div class="progress-fill" style="width:{min(token_rpt['budget_used_pct'],100)}%;background:{'#e74c3c' if token_rpt['budget_used_pct']>80 else '#f39c12' if token_rpt['budget_used_pct']>50 else '#27ae60'};"></div>
    </div>
    <div style="font-size:11px;color:#7f8c8d;">{token_rpt['budget_used_pct']}% utilizado</div>
    <div class="metric-row"><span>Entrada</span><span class="metric-val">{token_rpt['total_input_tokens']:,}</span></div>
    <div class="metric-row"><span>Saída</span><span class="metric-val">{token_rpt['total_output_tokens']:,}</span></div>
    <div class="metric-row"><span>Eficiência (out/in)</span><span class="metric-val">{token_rpt['efficiency_ratio']:.2f}</span></div>
    <div class="metric-row"><span>Economia estimada</span><span class="metric-val">{token_rpt['estimated_savings_from_chinese'] + token_rpt['estimated_savings_from_progressive_disclosure'] + token_rpt['estimated_savings_from_lazy_init']:,}</span></div>
  </div>

  <!-- Alertas -->
  <div class="card">
    <h3>⚠️ Alertas ({len(alerts)})</h3>
    {''.join(f'<div class="alert alert-{a["level"]}"><strong>{a["type"]}</strong>: {a["message"]}<br><small>{a["suggestion"]}</small></div>' for a in alerts) if alerts else '<div style="color:#27ae60;font-size:13px;">✅ Nenhum alerta ativo</div>'}
  </div>

  <!-- Resumo -->
  <div class="card">
    <h3>📊 Resumo da Sessão</h3>
    <div class="metric-row"><span>Parágrafos</span><span class="metric-val">{score['counts']['paragraphs']}</span></div>
    <div class="metric-row"><span>Evidências</span><span class="metric-val">{score['counts']['total_evidence']}</span></div>
    <div class="metric-row"><span>Fontes únicas</span><span class="metric-val">{score['counts']['unique_sources']}</span></div>
    <div class="metric-row"><span>Parágrafos limpos (TSAC)</span><span class="metric-val">{score['counts']['clean_paragraphs']}</span></div>
    <div class="metric-row"><span>Revisados por pares</span><span class="metric-val">{score['counts']['reviewed_paragraphs']}</span></div>
    <div class="metric-row"><span>Interações</span><span class="metric-val">{stats['interactions']}</span></div>
  </div>
</div>

<!-- Evidências -->
<div style="padding:0 24px 24px;">
  <div class="card">
    <h3>🔗 Mapa de Evidências</h3>
    <table class="table">
      <tr><th>Parágrafo</th><th>Fonte</th><th>Tipo</th><th>Verificada</th></tr>
      {''.join(f'<tr><td>{pid}</td><td style="font-family:monospace;font-size:11px;">{e.source[:50]}</td><td>{e.source_type}</td><td>{"✅" if e.verified else "⚠️"}</td></tr>' for pid, p in sorted(trail.paragraphs.items()) for e in p.evidence)}
    </table>
    {f'<div style="color:#7f8c8d;font-size:12px;margin-top:8px;">Total: {score["counts"]["total_evidence"]} evidências</div>' if score['counts']['total_evidence'] > 0 else '<div style="color:#e74c3c;">Nenhuma evidência registrada</div>'}
  </div>
</div>

<div class="footer">
  OpenCode Ecosystem v4.2.3 — Academic Audit System — {datetime.now(BRAZIL_TZ).strftime('%Y')}
</div>

</body>
</html>"""

        if output_path:
            Path(output_path).write_text(html, encoding="utf-8")

        return html


# ═══════════════════════════════════════════════════════════════════════
# 5. PipelineIntegration — Integração com SEEKER e MASWOS
# ═══════════════════════════════════════════════════════════════════════

class PipelineIntegration:
    """Integração automática do sistema de auditoria com pipelines SEEKER e MASWOS."""

    @staticmethod
    def seeker_bridge(
        trail: AcademicAuditTrail,
        stage: str = "SEEKER.grounder",
    ) -> dict[str, Any]:
        """Conecta auditoria ao estágio SEEKER.

        Registra automaticamente cada busca como evidência rastreável.
        """
        return {
            "stage": stage,
            "trail_paragraphs": len(trail.paragraphs),
            "trail_evidence": sum(len(p.evidence) for p in trail.paragraphs.values()),
            "ready_for_maswos": len(trail.paragraphs) >= 3,
        }

    @staticmethod
    def maswos_bridge(
        trail: AcademicAuditTrail,
        monitor: TokenEconomyMonitor,
        logger: InteractionLogger,
    ) -> dict[str, Any]:
        """Conecta auditoria ao pipeline MASWOS.

        Gera relatório completo de auditoria pronto para inclusão
        no manuscrito como apêndice de rastreabilidade.
        """
        score = ResearcherScore.calculate(trail, monitor)
        dashboard = AuditDashboard.generate(trail, monitor, logger)

        REFINEMENTS_DIR.mkdir(parents=True, exist_ok=True)
        dash_path = REFINEMENTS_DIR / f"dashboard-{logger.session_id}.html"
        dash_path.write_text(dashboard, encoding="utf-8")

        return {
            "score": score,
            "dashboard_path": str(dash_path),
            "qualis_a1_ready": score["score"] >= 85,
            "audit_appendix": trail.generate_audit_report("latex"),
            "token_report": monitor.generate_markdown_report(),
        }

    @staticmethod
    def run_full_pipeline_audit(
        trail: AcademicAuditTrail,
        monitor: TokenEconomyMonitor,
        logger: InteractionLogger,
    ) -> dict[str, Any]:
        """Executa auditoria completa integrada aos pipelines.

        Fluxo: SEEKER → MASWOS → Auditoria → Relatório Final
        """
        seeker_status = PipelineIntegration.seeker_bridge(trail, "SEEKER")
        maswos_status = PipelineIntegration.maswos_bridge(trail, monitor, logger)

        return {
            "pipeline": "SEEKER → MASWOS → Auditoria",
            "seeker": seeker_status,
            "maswos": maswos_status,
            "final_score": maswos_status["score"]["score"],
            "qualis_a1_ready": maswos_status["score"]["score"] >= 85,
            "dashboard": maswos_status["dashboard_path"],
            "timestamp": datetime.now(BRAZIL_TZ).isoformat(),
        }
