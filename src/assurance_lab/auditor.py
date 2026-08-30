from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from typing import Iterable, Mapping


@dataclass
class AuditCheck:
    check: str
    status: str
    detail: str
    score: int


def _sentences(text: str) -> list[str]:
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text.strip()) if s.strip()]


def audit_conclusion(conclusion: str, evidence: Iterable[Mapping[str, object]], criteria: Iterable[str],
                     findings: Iterable[Mapping[str, object]]) -> dict[str, object]:
    """Deterministic, explainable review of an AI-generated audit conclusion.

    This intentionally uses transparent heuristics rather than another opaque model.
    It is a screening aid; a human auditor makes the final judgment.
    """
    evidence = list(evidence)
    findings = list(findings)
    criteria_text = " ".join(criteria).lower()
    evidence_text = " ".join(str(e.get("description", "")) for e in evidence).lower()
    sentences = _sentences(conclusion)
    checks: list[AuditCheck] = []

    assertion_terms = ("always", "never", "all ", "none ", "proves", "guarantees", "fully compliant", "no risk")
    unsupported = [s for s in sentences if any(t in s.lower() for t in assertion_terms)]
    if not evidence:
        unsupported = sentences
    checks.append(AuditCheck("Unsupported assertions", "Flag" if unsupported else "Pass",
                             f"{len(unsupported)} absolute or unevidenced statement(s) detected.", min(25, 8 * len(unsupported))))

    named_frameworks = re.findall(r"\b(?:NIST AI RMF|ISO(?:/IEC)? 42001|OWASP(?: LLM Top 10)?|IIA Standards?)\b", conclusion, re.I)
    invented = sorted({x for x in named_frameworks if x.lower() not in criteria_text})
    checks.append(AuditCheck("Invented criteria", "Flag" if invented else "Pass",
                             "Criteria cited but not supplied: " + ", ".join(invented) if invented else "No unsupplied framework citation detected.",
                             min(20, 10 * len(invented))))

    stated_critical = bool(re.search(r"\bcritical\b", conclusion, re.I))
    supported_critical = any(str(f.get("severity", "")).lower() == "critical" for f in findings)
    inflation = stated_critical and not supported_critical
    checks.append(AuditCheck("Severity inflation", "Flag" if inflation else "Pass",
                             "Conclusion uses Critical without a Critical source finding." if inflation else "Severity language aligns with source findings.",
                             20 if inflation else 0))

    contradiction_pairs = [("effective", "ineffective"), ("compliant", "non-compliant"), ("adequate", "inadequate")]
    contradictions = [pair for pair in contradiction_pairs if all(re.search(rf"\b{re.escape(w)}\b", conclusion, re.I) for w in pair)]
    checks.append(AuditCheck("Internal inconsistency", "Flag" if contradictions else "Pass",
                             f"{len(contradictions)} contradictory term pair(s) detected.", min(15, 8 * len(contradictions))))

    cited_ids = set(re.findall(r"\b(?:EV|EVID)-?\d+\b", conclusion, re.I))
    evidence_thin = len(evidence) < 2 or not cited_ids or len(evidence_text.split()) < 8
    checks.append(AuditCheck("Insufficient evidence", "Flag" if evidence_thin else "Pass",
                             f"{len(evidence)} evidence item(s), {len(cited_ids)} explicit evidence reference(s).",
                             20 if evidence_thin else 0))

    risk = min(100, sum(c.score for c in checks))
    return {"reliability_score": 100 - risk, "risk_score": risk, "rating": "Low" if risk < 20 else "Moderate" if risk < 50 else "High",
            "checks": [asdict(c) for c in checks]}

