"""Feedback Synthesizer — Multi-channel feedback analysis and synthesis engine."""
from __future__ import annotations
import re
from collections import Counter
from typing import Any

POSITIVE_WORDS = {"amazing", "love", "great", "excellent", "fantastic", "wonderful", "best", "perfect", "awesome", "helpful", "fast", "intuitive", " brilliant", "good", "happy", "like"}
NEGATIVE_WORDS = {"terrible", "worst", "hate", "awful", "horrible", "bad", "slow", "buggy", "broken", "frustrating", "confusing", "ugly", "useless", "annoying", "crash", "error", "difficult", "hard", "painful"}
NEUTRAL_WORDS = {"update", "change", "feature", "version", "app", "use", "need", "want", "would", "could"}

THEME_PATTERNS: dict[str, list[str]] = {
    "performance": ["slow", "lag", "loading", "speed", "fast", "performance", "timeout", "crash", "freeze"],
    "ux": ["confusing", "hard to find", "navigation", "usability", "interface", "design", "layout", "click", "menu", "flow", "intuitive"],
    "features": ["feature", "missing", "add", "functionality", "need", "want", "wish", "support for"],
    "reliability": ["bug", "crash", "error", "broken", "doesn't work", "fail", "glitch", "issue"],
    "pricing": ["price", "cost", "expensive", "cheap", "worth", "value", "plan", "subscription", "trial"],
    "support": ["support", "response", "help", "documentation", "tutorial", "guide", "customer service"],
    "onboarding": ["onboarding", "setup", "getting started", "first time", "tutorial", "walkthrough", "sign up"],
}


def analyze_sentiment(text: str) -> dict[str, Any]:
    words = set(re.findall(r"[a-zA-Z]+", text.lower()))
    pos_count = len(words & POSITIVE_WORDS)
    neg_count = len(words & NEGATIVE_WORDS)
    total = pos_count + neg_count
    if total == 0:
        return {"score": 0.0, "label": "neutral", "confidence": 0.5}
    score = (pos_count - neg_count) / max(total, 1)
    confidence = min(0.7 + (total * 0.1), 1.0)
    label = "positive" if score > 0.2 else ("negative" if score < -0.2 else "neutral")
    return {"score": round(score, 3), "label": label, "confidence": round(confidence, 2)}


def categorize_feedback(items: list[dict[str, str]]) -> dict[str, Any]:
    theme_counts: Counter[str] = Counter()
    classified: list[dict[str, Any]] = []
    for item in items:
        text = (item.get("text", "") + " " + item.get("title", "")).lower()
        matched_themes: set[str] = set()
        for theme, patterns in THEME_PATTERNS.items():
            if any(p in text for p in patterns):
                matched_themes.add(theme)
        if not matched_themes:
            matched_themes = {"general"}
        for t in matched_themes:
            theme_counts[t] += 1
        classified.append({"id": item.get("id", ""), "text": item.get("text", ""), "themes": sorted(matched_themes)})
    return {"theme_distribution": dict(theme_counts.most_common()), "classified_items": classified}


def calculate_rice_score(reach: float, impact: float, confidence: float, effort: float) -> float:
    if effort <= 0:
        raise ValueError("Effort must be greater than zero")
    if impact < 0.25 or impact > 3:
        raise ValueError("Impact must be between 0.25 and 3")
    if not (0 <= confidence <= 1):
        raise ValueError("Confidence must be between 0 and 1")
    return round((reach * impact * confidence) / effort, 2)


def generate_summary(items: list[dict[str, str]]) -> dict[str, Any]:
    sentiments = [analyze_sentiment(item.get("text", "")) for item in items]
    pos = sum(1 for s in sentiments if s["label"] == "positive")
    neg = sum(1 for s in sentiments if s["label"] == "negative")
    neu = sum(1 for s in sentiments if s["label"] == "neutral")
    categorized = categorize_feedback(items)
    themes_sorted = categorized["theme_distribution"]
    top_themes = dict(list(themes_sorted.items())[:5]) if themes_sorted else {}
    avg_score = sum(s["score"] for s in sentiments) / max(len(sentiments), 1)
    return {
        "total_count": len(items),
        "sentiment_distribution": {"positive": pos, "negative": neg, "neutral": neu},
        "average_sentiment_score": round(avg_score, 3),
        "top_themes": top_themes,
        "summary_verdict": "positive" if avg_score > 0.15 else ("negative" if avg_score < -0.15 else "neutral"),
    }


def filter_by_theme(items: list[dict[str, str]], theme: str) -> list[dict[str, str]]:
    patterns = THEME_PATTERNS.get(theme, [])
    if not patterns:
        return []
    return [item for item in items if any(p in (item.get("text", "") + " " + item.get("title", "")).lower() for p in patterns)]
