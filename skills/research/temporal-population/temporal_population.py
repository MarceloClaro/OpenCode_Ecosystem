#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
temporal_population.py — Análise Temporal e Populacional
========================================================
Implementa modelagem de séries temporais, análise longitudinal,
delineamento amostral e generalização populacional.

Capabilities:
  - temporal_modeling: Modelagem temporal, longitudinal e transversal
  - longitudinal_analysis: Análise prospectiva e desenvolvimental
  - population_generalization: Generalização populacional e amostral
  - sampling_design: Delineamento amostral para contextos clínicos e comunitários
"""

from __future__ import annotations
import math
import statistics
from typing import Dict, List, Optional, Tuple


# ─── Temporal Modeling ───────────────────────────────────────────────

class TimeSeriesAnalyzer:
    """Analisador básico de séries temporais."""

    @staticmethod
    def moving_average(data: List[float], window: int = 3) -> List[float]:
        """Calcula média móvel de uma série temporal."""
        if window < 1 or window > len(data):
            raise ValueError(f"Window {window} inválida para dados de tamanho {len(data)}")
        result = []
        for i in range(len(data) - window + 1):
            result.append(sum(data[i:i + window]) / window)
        return result

    @staticmethod
    def growth_rate(data: List[float]) -> List[float]:
        """Calcula taxa de crescimento período a período."""
        if len(data) < 2:
            return []
        return [(data[i] - data[i-1]) / data[i-1] * 100 if data[i-1] != 0 else 0.0
                for i in range(1, len(data))]

    @staticmethod
    def trend_direction(data: List[float]) -> str:
        """Identifica direção da tendência."""
        if len(data) < 2:
            return "insuficiente"
        rates = TimeSeriesAnalyzer.growth_rate(data)
        avg_rate = statistics.mean(rates) if rates else 0
        if avg_rate > 1.0:
            return "crescente_forte"
        elif avg_rate > 0.1:
            return "crescente_suave"
        elif avg_rate < -1.0:
            return "decrescente_forte"
        elif avg_rate < -0.1:
            return "decrescente_suave"
        else:
            return "estavel"


class LongitudinalAnalyzer:
    """Analisador de dados longitudinais e prospectivos."""

    @staticmethod
    def characterize_design(
        waves: int,
        total_time_years: float,
        n_participants: int,
        has_comparison_group: bool = False,
    ) -> Dict[str, str]:
        """Caracteriza o delineamento longitudinal."""
        design_type = "transversal" if waves == 1 else "longitudinal"
        if waves >= 3 and total_time_years >= 2:
            design_type = "longitudinal_prospectivo"
        elif waves >= 2 and total_time_years >= 1:
            design_type = "longitudinal_painel"

        power_assessment = "baixo"
        if n_participants >= 100 and waves >= 2:
            power_assessment = "moderado"
        if n_participants >= 300 and waves >= 3:
            power_assessment = "adequado"
        if n_participants >= 500 and waves >= 3:
            power_assessment = "robusto"

        return {
            "design_type": design_type,
            "waves": waves,
            "time_span_years": total_time_years,
            "statistical_power": power_assessment,
            "has_comparison_group": str(has_comparison_group),
        }

    @staticmethod
    def developmental_stage(age: float) -> str:
        """Classifica estágio desenvolvimental."""
        if age < 2:
            return "bebe"
        elif age < 12:
            return "crianca"
        elif age < 18:
            return "adolescente"
        elif age < 30:
            return "adulto_jovem"
        elif age < 60:
            return "adulto"
        else:
            return "idoso"


# ─── Population & Sampling ──────────────────────────────────────────

class SampleSizeCalculator:
    """Calculadora de tamanho amostral para diferentes delineamentos."""

    @staticmethod
    def for_prevalence(
        population: float,
        expected_prevalence: float = 0.5,
        margin_error: float = 0.05,
        confidence_level: float = 0.95,
    ) -> Dict[str, float]:
        """Calcula tamanho amostral para estudos de prevalência."""
        z = {0.90: 1.645, 0.95: 1.96, 0.99: 2.576}.get(confidence_level, 1.96)
        p = expected_prevalence
        q = 1 - p
        e = margin_error

        # Amostra infinita
        n_infinite = (z**2 * p * q) / (e**2)

        # Correção para população finita
        n = n_infinite / (1 + (n_infinite - 1) / population) if population > 0 else n_infinite

        return {
            "sample_size": math.ceil(n),
            "sample_size_infinite": math.ceil(n_infinite),
            "population": population,
            "margin_error": margin_error,
            "confidence_level": confidence_level,
        }

    @staticmethod
    def for_clinical_trial(
        effect_size: float = 0.5,
        alpha: float = 0.05,
        power: float = 0.80,
        allocation_ratio: float = 1.0,
    ) -> Dict[str, float]:
        """Calcula tamanho amostral para ensaios clínicos."""
        z_alpha = {0.01: 2.576, 0.05: 1.96, 0.10: 1.645}.get(alpha, 1.96)
        z_beta = {0.80: 0.842, 0.90: 1.282, 0.95: 1.645}.get(power, 0.842)
        d = effect_size

        n_per_group = (2 * (z_alpha + z_beta)**2) / (d**2)
        n_total = n_per_group * (1 + allocation_ratio)

        return {
            "n_per_group": math.ceil(n_per_group),
            "n_total": math.ceil(n_total),
            "effect_size": effect_size,
            "alpha": alpha,
            "power": power,
        }


class PopulationGeneralizer:
    """Analisador de generalização populacional."""

    @staticmethod
    def assess_generalizability(
        sample_n: int,
        population_n: int,
        coverage_regions: List[str],
        age_range: Tuple[float, float],
        clinical_context: bool = False,
    ) -> Dict[str, str]:
        """Avalia a capacidade de generalização de uma amostra."""
        coverage_pct = sample_n / population_n * 100 if population_n > 0 else 0
        regions_score = len(coverage_regions)

        limitations = []
        if coverage_pct < 0.1:
            limitations.append("amostra_reduzida_frente_populacao")
        if age_range[1] - age_range[0] < 20:
            limitations.append("faixa_etaria_restrita")
        if regions_score < 2:
            limitations.append("poucas_regioes_geograficas")
        if clinical_context:
            limitations.append("contexto_clinico_requer_cuidado_extrapolacao")

        if not limitations:
            generalization = "alta"
        elif len(limitations) <= 2:
            generalization = "moderada"
        else:
            generalization = "limitada"

        return {
            "generalization_level": generalization,
            "sample_pct_of_population": f"{coverage_pct:.4f}%",
            "regions_covered": regions_score,
            "age_range": f"{age_range[0]}-{age_range[1]}",
            "limitations": limitations,
        }


def analyze_temporal_population(data: dict) -> dict:
    """Pipeline completo de análise temporal e populacional."""
    results = {}

    if "time_series" in data:
        ts = TimeSeriesAnalyzer()
        series = data["time_series"]
        results["moving_average"] = ts.moving_average(series)
        results["growth_rate"] = ts.growth_rate(series)
        results["trend"] = ts.trend_direction(series)

    if "longitudinal" in data:
        la = LongitudinalAnalyzer()
        ld = data["longitudinal"]
        results["design"] = la.characterize_design(
            ld.get("waves", 1),
            ld.get("total_time_years", 0),
            ld.get("n_participants", 0),
            ld.get("has_comparison_group", False),
        )
        if "age" in ld:
            results["developmental_stage"] = la.developmental_stage(ld["age"])

    if "sampling" in data:
        s = data["sampling"]
        if "population" in s and "expected_prevalence" in s:
            results["sample_size"] = SampleSizeCalculator.for_prevalence(
                s["population"], s.get("expected_prevalence", 0.5),
                s.get("margin_error", 0.05), s.get("confidence_level", 0.95),
            )
        if "effect_size" in s:
            results["clinical_trial_size"] = SampleSizeCalculator.for_clinical_trial(
                s["effect_size"], s.get("alpha", 0.05), s.get("power", 0.80),
            )

    if "population_context" in data:
        pc = data["population_context"]
        results["generalizability"] = PopulationGeneralizer.assess_generalizability(
            pc.get("sample_n", 0), pc.get("population_n", 1),
            pc.get("regions", []), tuple(pc.get("age_range", (0, 100))),
            pc.get("clinical_context", False),
        )

    return results


def main():
    """Demonstra análise temporal e populacional."""
    # Exemplo: série temporal
    ts_data = [10, 12, 15, 14, 18, 22, 25, 24, 28, 30]
    ts = TimeSeriesAnalyzer()
    print(f"Série temporal: {ts_data}")
    print(f"Média móvel (w=3): {ts.moving_average(ts_data)}")
    print(f"Taxa de crescimento: {[f'{r:.1f}%' for r in ts.growth_rate(ts_data)]}")
    print(f"Tendência: {ts.trend_direction(ts_data)}")

    # Exemplo: delineamento longitudinal
    la = LongitudinalAnalyzer()
    design = la.characterize_design(waves=3, total_time_years=5, n_participants=350)
    print(f"\nDelineamento: {design}")

    # Exemplo: tamanho amostral
    ssc = SampleSizeCalculator()
    sample = ssc.for_prevalence(population=100000, expected_prevalence=0.3)
    print(f"\nTamanho amostral (prevalência): {sample['sample_size']}")
    trial = ssc.for_clinical_trial(effect_size=0.5)
    print(f"Tamanho amostral (ensaio clínico): {trial['n_total']}")

    # Exemplo: generalização
    pg = PopulationGeneralizer()
    gen = pg.assess_generalizability(
        sample_n=500, population_n=100000,
        coverage_regions=["sul", "sudeste"],
        age_range=(18, 65),
    )
    print(f"\nGeneralização: {gen['generalization_level']}")


if __name__ == "__main__":
    main()
