from assurance_lab.findings import generate_finding


def test_finding_has_five_cs_and_recommendation():
    finding = generate_finding({"id":"SEC-01","title":"Prompt injection resistance","status":"Ineffective","frameworks":["OWASP LLM01"],"risk":"Unsafe behavior"}, "Claims Copilot")
    assert {"condition", "criteria", "cause", "risk", "recommendation"} <= finding.keys()
    assert finding["severity"] == "High"

