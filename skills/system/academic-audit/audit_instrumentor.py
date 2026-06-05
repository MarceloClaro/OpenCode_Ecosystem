#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AuditInstrumentor v1.0 — Auto-Instrumentação de Pipelines
==========================================================
Wrapper que automaticamente registra todas as interações do
DataOrchestrator, SEEKER, MASWOS e PhD Auditor no sistema de
auditoria caixa branca.

Princípio: "Zero configuração — toda interação é registrada."

Uso:
  from audit_instrumentor import AuditInstrumentor
  orch = AuditInstrumentor.wrap(orchestrator)
  result = orch.query("PIB do Brasil")  # automaticamente logado!
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Callable

from interaction_logger import (
    InteractionLogger,
    RoutingInfo,
    TokenMetrics,
    get_logger,
)
from academic_audit_trail import AcademicAuditTrail
from token_economy_monitor import TokenEconomyMonitor

BRAZIL_TZ = timezone.utc


@dataclass
class InstrumentationConfig:
    """Configuração de auto-instrumentação."""
    log_queries: bool = True
    log_responses: bool = True
    log_decisions: bool = True
    log_errors: bool = True
    log_artifacts: bool = True
    track_tokens: bool = True
    paradigm: str = ""
    level: int = 2
    auto_tsac: bool = True


class AuditInstrumentor:
    """Instrumentador automático de pipelines.

    Wrapper que intercepta chamadas ao DataOrchestrator e pipelines
    para registrar automaticamente todas as interações.

    Uso:
      orch = DataOrchestrator()
      orch = AuditInstrumentor.wrap(orch, paradigm="Pragmatista")
      result = orch.query("PIB do Brasil")  # auto-logado!
    """

    def __init__(self, config: InstrumentationConfig | None = None) -> None:
        self.config = config or InstrumentationConfig()
        self.logger = get_logger()
        self.trail = AcademicAuditTrail()
        self.monitor = TokenEconomyMonitor(
            level=self.config.level,
            session_id=self.logger.session_id,
        )
        self._interaction_count = 0

        # Configurar sessão
        if self.config.paradigm:
            self.logger.set_paradigm(self.config.paradigm)
            self.trail.set_paradigm(self.config.paradigm)
        self.logger.set_level(self.config.level)

    @classmethod
    def wrap(
        cls,
        orchestrator: Any,
        paradigm: str = "Pragmatista (mista)",
        level: int = 2,
    ) -> Any:
        """Envolve um DataOrchestrator com auto-instrumentação.

        Args:
            orchestrator: Instância do DataOrchestrator
            paradigm: Paradigma epistemológico
            level: Nível de publicação (1/2/3)

        Returns:
            DataOrchestrator instrumentado (mesma interface)
        """
        instrumentor = cls(InstrumentationConfig(
            paradigm=paradigm, level=level,
        ))

        # Guarda referência ao query original
        original_query = orchestrator.query

        def instrumented_query(prompt: str, **kwargs: Any) -> Any:
            """Query instrumentada com logging automático."""
            return instrumentor._instrument_query(
                orchestrator, original_query, prompt, **kwargs
            )

        # Substitui método
        orchestrator.query = instrumented_query
        orchestrator._audit = instrumentor  # type: ignore[attr-defined]
        return orchestrator

    def _instrument_query(
        self,
        orch: Any,
        original_query: Callable[[str], Any],
        prompt: str,
        **kwargs: Any,
    ) -> Any:
        """Executa query com logging automático completo."""
        start_time = time.time()
        self._interaction_count += 1
        interaction_id = f"INT-{self._interaction_count:04d}"

        # Pré-execução: registrar query
        if self.config.log_queries:
            self.logger.log_query(
                query=prompt,
                pipeline_stage="DataOrchestrator",
            )

        # Executar query original
        error_msg = ""
        try:
            result = original_query(prompt, **kwargs)
        except Exception as e:
            error_msg = str(e)
            if self.config.log_errors:
                self.logger.log_error(
                    error_type=type(e).__name__,
                    message=error_msg,
                    stack_trace="",
                )
            raise

        # Pós-execução: registrar resultado
        elapsed_ms = int((time.time() - start_time) * 1000)

        # Extrair informações de roteamento do resultado
        routing = RoutingInfo(
            domain=getattr(result, "domain", "unknown"),
            source=getattr(result, "source", "unknown"),
            confidence=getattr(result, "confidence", 0.0),
        )

        # Estimar tokens (heurística: 1 token ≈ 4 chars em inglês, ajustado)
        input_chars = len(prompt)
        response_str = str(result.data)[:500] if hasattr(result, "data") else str(result)[:500]
        output_chars = len(response_str)

        tokens = TokenMetrics(
            estimated_input=input_chars // 3,  # ajuste para PT-BR
            estimated_output=output_chars // 3,
            level=self.config.level,
            efficiency_ratio=output_chars / max(1, input_chars),
        )

        # Registrar resposta
        if self.config.log_responses:
            self.logger.log_query(
                query=prompt,
                response_summary=response_str[:200],
                routing=routing,
                tokens=tokens,
                pipeline_stage="DataOrchestrator",
                decision_path=[f"domain={routing.domain}", f"source={routing.source}"],
            )

        # Registrar decisão de roteamento
        if self.config.log_decisions:
            self.logger.log_decision(
                decision=f"Roteado para {routing.source}",
                rationale=f"Domínio: {routing.domain}, Confiança: {routing.confidence:.0%}",
                context="DataOrchestrator.query",
            )

        # Monitor de tokens
        if self.config.track_tokens:
            self.monitor.record_usage(
                interaction_id=interaction_id,
                estimated_input=tokens.estimated_input,
                estimated_output=tokens.estimated_output,
                pipeline_stage="DataOrchestrator",
            )

        return result

    def record_evidence_link(
        self,
        paragraph_id: str,
        source: str,
        claim: str = "",
        source_type: str = "unknown",
    ) -> None:
        """Registra vínculo de evidência após query.

        Útil para chamar após cada busca acadêmica, vinculando
        automaticamente os resultados ao parágrafo correspondente.
        """
        self.trail.record_evidence(
            paragraph_id=paragraph_id,
            source=source,
            claim=claim,
            source_type=source_type,
        )
        if self.config.log_decisions:
            self.logger.log_decision(
                decision=f"Evidência: {source} → {paragraph_id}",
                rationale=claim,
                context="record_evidence_link",
            )

    def check_paragraph_tsac(self, paragraph_id: str, text: str) -> dict[str, Any]:
        """Verifica TSAC e registra parágrafo automaticamente."""
        self.trail.record_paragraph(paragraph_id, text)
        result = self.trail.run_tsac_check(paragraph_id)
        if self.config.log_decisions and not result["clean"]:
            self.logger.log_decision(
                decision=f"TSAC bloqueio: {paragraph_id}",
                rationale=f"{result['violations']} palavras banidas",
                context="tsac_check",
            )
        return result

    def generate_audit_report(self, format: str = "markdown") -> str:
        """Gera relatório completo de auditoria da sessão."""
        md = []
        md.append(self.trail.generate_audit_report(format))
        if format == "markdown":
            md.append("")
            md.append("---")
            md.append("")
            md.append(self.monitor.generate_markdown_report())
        return "\n".join(md)

    def close(self) -> dict[str, Any]:
        """Fecha sessão e salva todos os relatórios."""
        self.trail.save()
        self.monitor.save()
        summary = self.logger.close_session()
        return {
            "session_id": self.logger.session_id,
            "total_interactions": self._interaction_count,
            "audit_trail": str(self.trail.save()),
            "token_report": str(self.monitor.save()),
            "log_file": str(self.logger._log_file),
            **summary,
        }


# ── Decorator para funções de pipeline ──────────────────────────────────

def audit_traced(stage: str = ""):
    """Decorator que auto-instrumenta qualquer função de pipeline.

    Uso:
      @audit_traced("SEEKER.grounder")
      def search_papers(query: str) -> list:
          ...
    """
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            logger = get_logger()
            start = time.time()
            try:
                result = func(*args, **kwargs)
                elapsed = int((time.time() - start) * 1000)
                logger.log_query(
                    query=f"{stage}: {func.__name__}({args[:1]})",
                    response_summary=f"OK ({elapsed}ms)",
                    pipeline_stage=stage,
                )
                return result
            except Exception as e:
                logger.log_error(
                    error_type=type(e).__name__,
                    message=str(e),
                    stack_trace="",
                )
                raise
        return wrapper
    return decorator
