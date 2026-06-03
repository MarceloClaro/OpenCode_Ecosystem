"""
TDD tests for Agent Forum — Debate multiagente com moderador LLM.
CT-1: test_init — inicializacao de Forum, AgentSpeech, ModeratorSpeech
CT-2: test_session_lifecycle — open_session → publish → conclude
CT-3: test_game_theory — run_game_theory_analysis e describe_strategies
CT-4: test_available — Forum sem LLM (modo offline/demo)
"""

import os
import sys
import pytest

SCRIPT_DIR = os.path.join(os.path.dirname(__file__), "..", "scripts")
sys.path.insert(0, SCRIPT_DIR)

from moderator import (
    Forum, AgentSpeech, ModeratorSpeech,
    ForumModerator, ForumMonitor, SessionConfig,
    MemoryChannel, DebateStage, ModeratorMode,
)


class TestAgentForum:

    def test_init(self):
        forum = Forum(
            agents=["QueryEngine", "MediaEngine"],
            debate_profile="LOGICO_RIGOROSO",
            language="pt-BR",
        )
        assert len(forum.agents) == 2
        assert forum.debate_profile == "LOGICO_RIGOROSO"
        assert forum.stage == DebateStage.IDLE
        assert forum.is_active is False
        assert isinstance(forum._channel, MemoryChannel)

    def test_session_lifecycle(self):
        forum = Forum(
            agents=["AgenteA", "AgenteB"],
            debate_profile="ESTRATEGISTA",
            language="pt-BR",
        )

        opening = forum.open_session("Teste de debate")
        assert forum.stage == DebateStage.OPEN
        assert forum.is_active is True
        assert isinstance(opening, ModeratorSpeech)
        assert "Teste de debate" in opening.content

        speech = forum.publish(
            "AgenteA",
            "Dados mostram tendencia de alta no setor.",
            confidence=0.85,
            stance="Apoio",
        )
        assert isinstance(speech, AgentSpeech)
        assert speech.source == "AgenteA"
        assert speech.confidence == 0.85

        conclusion = forum.conclude()
        assert forum.stage == DebateStage.CLOSED
        assert isinstance(conclusion, ModeratorSpeech)

        report = forum.get_json_report()
        assert report["topic"] == "Teste de debate"
        assert report["stage"] == "closed"
        assert report["total_speeches"] >= 1

    def test_game_theory(self):
        forum = Forum(
            agents=["P1", "P2"],
            debate_profile="ESTRATEGISTA",
            language="pt-BR",
        )
        forum.open_session("Analisar cooperacao")

        analysis = forum.run_game_theory_analysis()
        assert "prisoners_dilemma" in analysis
        pd = analysis["prisoners_dilemma"]
        assert "nash_equilibria" in pd or "insight" in pd

        strategies = forum.describe_strategies()
        assert strategies["total"] == 38
        assert "categorias" in strategies
        assert "perfis_predefinidos" in strategies

    def test_available(self):
        forum = Forum(agents=["Solo"], language="pt-BR")
        forum.open_session("Sessao offline")

        speech = forum.publish("Solo", "Analise sem LLM disponivel.")
        assert speech.source == "Solo"

        transcript = forum.transcript
        assert len(transcript) >= 2

        forum.conclude()
        assert forum.stage == DebateStage.CLOSED
