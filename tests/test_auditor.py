from assurance_lab.auditor import audit_conclusion


def test_flags_unreliable_ai_conclusion():
    result = audit_conclusion(
        "The system is fully compliant with ISO/IEC 42001. Testing proves it will never leak data. The risk is Critical.",
        [{"description": "A short diagram"}], ["NIST AI RMF"], [{"severity": "Moderate"}]
    )
    assert result["rating"] == "High"
    flagged = {c["check"] for c in result["checks"] if c["status"] == "Flag"}
    assert {"Unsupported assertions", "Invented criteria", "Severity inflation", "Insufficient evidence"} <= flagged


def test_evidence_grounded_conclusion_scores_well():
    result = audit_conclusion(
        "EV-001 and EV-002 show that human review operated, while the Moderate injection finding remains open.",
        [{"description": "Documented approval records for sampled decisions"}, {"description": "Detailed injection test workbook and reviewer results"}],
        ["NIST AI RMF"], [{"severity": "Moderate"}]
    )
    assert result["reliability_score"] >= 80

