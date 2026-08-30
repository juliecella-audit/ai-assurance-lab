from assurance_lab.reporting import build_audit_report


def test_report_is_valid_pdf():
    assessment = {"system":{"name":"Test AI","purpose":"Testing","owner":"Audit","model":"Rules","users":"Auditors","data":"Synthetic","lifecycle":"Pilot"},
                  "genai_tests":[{"test":"Injection","result":"Pass","cases":1,"failures":0,"observation":"No failure."}]}
    controls = [{"id":"C-1","domain":"Governance","title":"Ownership","status":"Effective"}]
    evidence = [{"evidence_id":"EV-001","title":"Approval","control_id":"C-1","description":"Signed approval."}]
    findings = [{"title":"Sample","severity":"Moderate","condition":"Gap.","risk":"Impact.","recommendation":"Fix."}]
    pdf = build_audit_report(assessment, controls, evidence, findings, 8, 4.4, "High", "Moderate")
    assert pdf.startswith(b"%PDF-")
    assert len(pdf) > 4000
