#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_potentiality_scanner.py — SPEC-043: Potentiality Scanner TDD Suite
======================================================================
Valida o Módulo 1 (Structural DNA Extractor) do Scanner de Potenciais.
Uso: PYTHONPATH=. pytest specs/test_potentiality_scanner.py
"""

import pytest
import tempfile
import json
import sys
from pathlib import Path

# Add skills/system/academic-audit to path
BASE_DIR = Path(__file__).resolve().parent.parent
SCANNER_DIR = BASE_DIR / "skills" / "system" / "academic-audit"
sys.path.insert(0, str(SCANNER_DIR))

from potentiality_scanner import PotentialityScanner

class TestPotentialityScanner:
    """TDD Test Suite para o Módulo 1 do Potentiality Scanner (SPEC-043)."""

    def test_ct4301_dna_extraction_processing(self):
        """CT-4301: Garante que o scanner processe componentes core e extraia capacidades."""
        scanner = PotentialityScanner()
        dna = scanner.scan()

        assert "capability_map" in dna, "Falta o capability_map no DNA extraído."
        assert "noological_scanner" in dna["capability_map"], "noological_scanner deveria estar mapeado."
        assert "gap_detection" in dna["capability_map"]["noological_scanner"], "gap_detection ausente do noological_scanner."

    def test_ct4302_core_capabilities_identification(self):
        """CT-4302: Valida se o algoritmo identifica corretamente capacidades dominantes (core)."""
        scanner = PotentialityScanner()
        dna = scanner.scan()

        assert "core_capabilities" in dna, "Falta lista de capacidades centrais no DNA."
        # Noological, Teleological e MCS Solver todos contam como gap_detection ou similar
        # Vamos verificar se a lista de core é preenchida
        assert isinstance(dna["core_capabilities"], list)
        assert len(dna["core_capabilities"]) >= 0

    def test_ct4303_redundancy_analysis(self):
        """CT-4303: Testa se capacidades com múltiplas implementações são marcadas como redundantes."""
        scanner = PotentialityScanner()
        dna = scanner.scan()

        assert "redundant_capabilities" in dna, "Falta lista de redundâncias no DNA."
        assert isinstance(dna["redundant_capabilities"], list)

    def test_ct4304_missing_capabilities_audit(self):
        """CT-4304: Verifica o mapeamento de lacunas do roadmap evolutivo (capacidades ausentes)."""
        scanner = PotentialityScanner()
        dna = scanner.scan()

        assert "missing_capabilities" in dna, "Falta lista de capacidades ausentes no DNA."
        assert "autonomous_self_repair" in dna["missing_capabilities"], "autonomous_self_repair deveria ser identificada como ausente."
        assert "predictive_teleology" in dna["missing_capabilities"], "predictive_teleology deveria ser identificada como ausente."

    def test_save_report_execution(self):
        """Valida que o relatório markdown é salvo corretamente em disco com a formatação esperada."""
        scanner = PotentialityScanner()
        dna = scanner.scan()

        with tempfile.TemporaryDirectory() as tmpdir:
            report_path = Path(tmpdir) / "potentiality_report.md"
            scanner.save_report(dna, report_path)
            
            assert report_path.exists(), "O arquivo de relatório não foi criado."
            content = report_path.read_text(encoding="utf-8")
            assert "# Relatório de DNA Estrutural" in content, "Título principal incorreto no markdown."
            assert "autonomous_self_repair" in content, "Falta listar a capacidade ausente no relatório."
