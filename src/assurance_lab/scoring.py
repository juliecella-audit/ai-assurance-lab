from __future__ import annotations

from collections import defaultdict
from typing import Iterable, Mapping

LIKELIHOOD = {"Low": 1, "Moderate": 2, "High": 3, "Very High": 4}
IMPACT = {"Low": 1, "Moderate": 2, "High": 3, "Severe": 4}
STATUS_FACTOR = {"Effective": 0.15, "Partially Effective": 0.55, "Ineffective": 1.0, "Not Assessed": 1.0}


def band(score: float) -> str:
    if score >= 12:
        return "Critical"
    if score >= 8:
        return "High"
    if score >= 4:
        return "Moderate"
    return "Low"


def inherent_score(likelihood: str, impact: str) -> int:
    return LIKELIHOOD[likelihood] * IMPACT[impact]


def residual_score(inherent: float, statuses: Iterable[str]) -> float:
    factors = [STATUS_FACTOR.get(s, 1.0) for s in statuses]
    factor = sum(factors) / len(factors) if factors else 1.0
    return round(max(1.0, inherent * factor), 1)


def domain_summary(controls: Iterable[Mapping[str, object]]) -> list[dict[str, object]]:
    grouped: dict[str, list[float]] = defaultdict(list)
    for control in controls:
        grouped[str(control["domain"])].append(1 - STATUS_FACTOR.get(str(control["status"]), 1.0))
    return [
        {"domain": domain, "effectiveness": round(100 * sum(scores) / len(scores))}
        for domain, scores in sorted(grouped.items())
    ]

