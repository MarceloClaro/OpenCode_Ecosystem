"""
TDD tests for ConfigGenerator — Gera simulacoes com fallback heuristico.
CT-1: test_init — inicializacao do ConfigGenerator
CT-2: test_fallback — geracao com fallback heuristico (sem LLM)
CT-3: test_parse_config — parsing de TimeSimulationConfig
CT-4: test_available — type rules e aliases disponiveis
"""

import os
import sys
import pytest

SCRIPT_DIR = os.path.join(os.path.dirname(__file__), "..", "scripts")
sys.path.insert(0, SCRIPT_DIR)

from generator import (
    ConfigGenerator, TimeSimulationConfig, EventConfig,
    AgentActivityConfig, PlatformConfig, BRAZIL_TIMEZONE,
    TYPE_RULES, TYPE_ALIASES,
)


class TestConfigGenerator:

    def test_init(self):
        gen = ConfigGenerator(api_key=None, model="gpt-4o")
        assert gen.llm_available is False
        assert gen.model == "gpt-4o"

        gen2 = ConfigGenerator(api_key="sk-test", model="test-model")
        assert gen2.llm_available is True
        assert gen2.model == "test-model"

    def test_fallback(self):
        gen = ConfigGenerator(api_key=None)
        entities = [
            {"name": "Universidade Federal", "type": "Official",
             "summary": "Instituicao publica federal"},
            {"name": "Joao Aluno", "type": "Student",
             "summary": "Estudante de ciencias sociais"},
        ]
        params = gen.generate("test-001", "Debate sobre educacao", entities)
        assert params.simulation_id == "test-001"
        assert params.time_config is not None
        assert isinstance(params.time_config, TimeSimulationConfig)
        assert params.time_config.total_rounds > 0
        assert params.event_config is not None
        assert isinstance(params.event_config, EventConfig)
        assert len(params.agent_configs) == 2
        assert params.platform_config is not None
        assert isinstance(params.platform_config, PlatformConfig)

    def test_parse_config(self):
        gen = ConfigGenerator(api_key=None)
        tc = gen._parse_time_config({}, 10)
        assert tc.total_rounds >= 10
        assert 0 <= tc.peak_activity_probability <= 1.0
        assert 0 <= tc.random_activity_ratio <= 1.0

        pc = gen._get_default_platform_config("Media")
        assert abs(sum(pc.algorithm_weights.values()) - 1.0) < 0.01

    def test_available(self):
        assert len(TYPE_RULES) >= 5
        assert len(TYPE_ALIASES) >= 10
        assert "dead_hours" in BRAZIL_TIMEZONE
        assert "peak_hours" in BRAZIL_TIMEZONE

        gen = ConfigGenerator(api_key=None)
        etype = gen._resolve_type_alias("prof")
        assert etype == "Professor"

        etype2 = gen._resolve_type_alias("jornal")
        assert etype2 == "MediaOutlet" or etype2 in TYPE_RULES
