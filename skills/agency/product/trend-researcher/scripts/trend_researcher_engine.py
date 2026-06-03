"""Trend Researcher — Market intelligence and trend analysis engine."""
from __future__ import annotations
from typing import Any


LIFECYCLE_THRESHOLDS = {
    "EMERGENCE": {"max_age": 6, "min_growth": 0.3, "max_volume": 500},
    "GROWTH": {"max_age": 18, "min_growth": 0.15, "max_volume": 5000},
    "MATURITY": {"max_age": 48, "min_growth": -0.05, "max_volume": 50000},
    "DECLINE": {"max_age": float("inf"), "min_growth": float("-inf"), "max_volume": float("inf")},
}


def classify_lifecycle(growth_rate: float, mention_volume: int, age_months: int) -> str:
    if age_months <= 6 and growth_rate >= 0.3 and mention_volume <= 500:
        return "EMERGENCE"
    if age_months <= 18 and growth_rate >= 0.15 and mention_volume <= 5000:
        return "GROWTH"
    if age_months <= 48 and growth_rate >= -0.05 and mention_volume <= 50000:
        return "MATURITY"
    return "DECLINE"


def calculate_market_size(
    total_population: int,
    target_pct: float,
    reachable_pct: float,
    competitive_share: float,
) -> dict[str, int]:
    tam = int(total_population * target_pct)
    sam = int(tam * reachable_pct)
    som = int(sam * competitive_share)
    return {"TAM": tam, "SAM": sam, "SOM": som}


SIGNAL_WEIGHTS = {
    "social_media": 0.30,
    "patent": 0.20,
    "investment": 0.25,
    "academic": 0.15,
    "expert": 0.10,
}


def calculate_signal_strength(signals: dict[str, float]) -> float:
    score = 0.0
    for source, strength in signals.items():
        weight = SIGNAL_WEIGHTS.get(source, 0.0)
        score += min(strength, 100) * weight
    return round(min(score, 100.0), 2)


def build_positioning_matrix(
    competitors: list[dict[str, Any]],
    features: list[str],
) -> dict[str, Any]:
    matrix: list[dict[str, Any]] = []
    all_features_covered: set[str] = set()
    for comp in competitors:
        comp_features = comp.get("features", {})
        feats_present = sum(1 for f in features if comp_features.get(f, 0) > 0)
        feats_total = len(features)
        differentiation = round(feats_present / max(feats_total, 1) * 100, 1)
        coverage = {f: comp_features.get(f, 0) for f in features}
        for f in features:
            if comp_features.get(f, 0) > 0:
                all_features_covered.add(f)
        matrix.append({
            "name": comp.get("name", "Unknown"),
            "coverage": coverage,
            "features_count": feats_present,
            "differentiation_score": differentiation,
        })
    white_space = [f for f in features if f not in all_features_covered]
    return {"competitors": matrix, "features": features, "white_space": white_space}


def adoption_forecast(
    current_users: int,
    growth_rate: float,
    total_market: int,
    months: int = 12,
) -> list[dict[str, Any]]:
    forecasts = []
    users = current_users
    for m in range(1, months + 1):
        users = int(users * (1 + growth_rate))
        users = min(users, total_market)
        forecasts.append({"month": m, "projected_users": users, "penetration_pct": round(users / total_market * 100, 1)})
    return forecasts
