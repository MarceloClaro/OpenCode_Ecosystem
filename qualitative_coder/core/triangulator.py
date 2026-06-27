"""
QualitativeCoder Triangulator — Triangulação de Métodos e Fontes
SPEC-048 | Ciclo R27

Compara dados quantitativos e qualitativos para identificar convergência,
divergência e lacunas (gaps).
"""
from __future__ import annotations
from typing import Any


class Triangulator:
    """
    Triangulador de métodos e fontes.

    Compara resultados de diferentes métodos de pesquisa para
    identificar pontos de convergência, divergência e lacunas.
    """

    def __init__(self):
        """Inicializa o triangulador."""
        pass

    def triangulate(
        self,
        data_quant: dict,
        data_qual: list[dict],
        method: str = "convergence",
    ) -> dict:
        """
        Triangula dados quantitativos e qualitativos.

        Args:
            data_quant: Dados quantitativos (dict de métricas -> valores).
            data_qual: Dados qualitativos (lista de dicts com 'code' e 'confidence').
            method: Método de triangulação ('convergence', 'divergence', 'mixed').

        Returns:
            Dict com:
            - convergence: float (0.0-1.0) — grau de convergência
            - divergence: list — pontos de divergência
            - gaps: list — lacunas identificadas
        """
        result = {
            "convergence": 0.0,
            "divergence": [],
            "gaps": [],
        }

        if not data_quant and not data_qual:
            result["gaps"].append({
                "type": "no_data",
                "description": "Nenhum dado fornecido para triangulação",
            })
            return result

        if not data_quant:
            result["gaps"].append({
                "type": "missing_quantitative",
                "description": "Dados quantitativos ausentes",
            })
            result["convergence"] = 0.0
            return result

        if not data_qual:
            result["gaps"].append({
                "type": "missing_qualitative",
                "description": "Dados qualitativos ausentes",
            })
            result["convergence"] = 0.0
            return result

        # Calcular convergência
        quant_values = list(data_quant.values())
        qual_confidences = [c.get("confidence", 0.5) for c in data_qual]

        avg_quant = sum(quant_values) / len(quant_values) if quant_values else 0
        avg_qual = sum(qual_confidences) / len(qual_confidences) if qual_confidences else 0

        # Convergência = similaridade entre médias
        result["convergence"] = round(1.0 - abs(avg_quant - avg_qual), 3)

        # Detectar divergências
        result["divergence"] = self._find_divergences(data_quant, data_qual)

        # Detectar gaps
        result["gaps"] = self._find_gaps(data_quant, data_qual)

        return result

    def _find_divergences(self, data_quant: dict, data_qual: list[dict]) -> list[dict]:
        """Encontra pontos de divergência entre dados quant e qual."""
        divergences = []

        quant_values = list(data_quant.values())
        qual_confidences = [c.get("confidence", 0.5) for c in data_qual]

        # Se há alta variância nos dados qual e baixa nos quant
        if qual_confidences:
            qual_var = self._variance(qual_confidences)
            quant_var = self._variance(quant_values) if quant_values else 0

            if qual_var > 0.05 and quant_var < 0.01:
                divergences.append({
                    "type": "variance_mismatch",
                    "description": "Alta variância qualitativa vs. baixa variância quantitativa",
                    "qual_variance": round(qual_var, 4),
                    "quant_variance": round(quant_var, 4),
                })

        # Verificar inversão de sinais (valores altos quant vs. baixa confiança qual)
        for q_val in quant_values:
            for c in qual_confidences:
                if q_val > 0.7 and c < 0.3:
                    divergences.append({
                        "type": "signal_inversion",
                        "description": f"Valor quantitativo alto ({q_val}) vs. confiança qualitativa baixa ({c})",
                        "quant_value": q_val,
                        "qual_confidence": c,
                    })
                    break

        return divergences

    def _find_gaps(self, data_quant: dict, data_qual: list[dict]) -> list[dict]:
        """Encontra lacunas nos dados."""
        gaps = []

        # Gap: dados quantitativos sem correspondência qualitativa
        quant_keys = set(data_quant.keys())
        qual_codes = set(c.get("code", "") for c in data_qual)

        # Converter códigos qual para chaves comparáveis
        qual_keys = set()
        for code in qual_codes:
            # Normalizar: "resistencia_mudanca" -> "resistencia"
            parts = code.split("_")
            if parts:
                qual_keys.add(parts[0])

        # Chaves sem correspondência
        quant_only = quant_keys - qual_keys
        qual_only = qual_keys - quant_keys

        if quant_only:
            gaps.append({
                "type": "quant_only",
                "description": f"Métricas sem cobertura qualitativa: {', '.join(quant_only)}",
                "keys": list(quant_only),
            })

        if qual_only:
            gaps.append({
                "type": "qual_only",
                "description": f"Códigos sem cobertura quantitativa: {', '.join(qual_only)}",
                "keys": list(qual_only),
            })

        return gaps

    def _variance(self, values: list[float]) -> float:
        """Calcula variância de uma lista de valores."""
        if len(values) < 2:
            return 0.0
        mean = sum(values) / len(values)
        return sum((x - mean) ** 2 for x in values) / (len(values) - 1)
