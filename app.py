from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st
import yaml

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT / "src"))

from assurance_lab.auditor import audit_conclusion
from assurance_lab.findings import generate_finding
from assurance_lab.reporting import build_audit_report
from assurance_lab.scoring import band, domain_summary, inherent_score, residual_score
from assurance_lab.storage import Repository

st.set_page_config(page_title="AI Assurance Lab", page_icon="◈", layout="wide")


@st.cache_data
def load_demo() -> tuple[dict, list[dict]]:
    demo = json.loads((ROOT / "data" / "claims_copilot.json").read_text(encoding="utf-8"))
    library = yaml.safe_load((ROOT / "data" / "controls.yaml").read_text(encoding="utf-8"))["controls"]
    return demo, library


def init_state() -> None:
    demo, library = load_demo()
    st.session_state.setdefault("assessment", demo)
    st.session_state.setdefault("library", library)
    db_path = Path(os.getenv("AI_ASSURANCE_DB", str(ROOT / "data" / "ai_assurance_lab.db")))
    repo = Repository(db_path)
    assessment_id = repo.save_assessment(demo)
    if not repo.evidence(assessment_id):
        for item in demo["evidence"]:
            repo.add_evidence(assessment_id, item)
    st.session_state.setdefault("assessment_id", assessment_id)
    st.session_state.setdefault("db_path", str(db_path))


def apply_css() -> None:
    st.markdown("""
    <style>
    .stApp {background: #f5f7fb; color: #152238}
    [data-testid="stSidebar"] {background: #101a2d}
    [data-testid="stSidebar"] * {color: #eaf0fb}
    .hero {padding: 1.4rem 1.6rem; background: linear-gradient(120deg,#10213d,#173e5f); color:white;
           border-radius:18px; margin-bottom:1rem; box-shadow:0 8px 24px #10213d22}
    .eyebrow {letter-spacing:.12em;text-transform:uppercase;color:#63d6c6;font-size:.78rem;font-weight:700}
    .hero h1 {margin:.25rem 0 .2rem;font-size:2rem}.hero p{color:#d9e6f2;margin:0}
    .pill {display:inline-block;padding:.25rem .65rem;border-radius:999px;background:#e7f8f4;color:#11685c;font-weight:700;font-size:.78rem}
    .note {padding:.8rem 1rem;border-left:4px solid #2cb7a3;background:#eaf8f6;border-radius:8px}
    div[data-testid="stMetric"] {background:white;border:1px solid #e3e8ef;padding:1rem;border-radius:14px;box-shadow:0 3px 12px #10213d0d}
    .stTabs [data-baseweb="tab-list"] {gap:.4rem}.stTabs [data-baseweb="tab"] {background:white;border-radius:10px;padding:.6rem 1rem}
    </style>""", unsafe_allow_html=True)


def control_rows(assessment: dict, library: list[dict]) -> list[dict]:
    return [{**c, "status": assessment["controls"].get(c["id"], "Not Assessed")} for c in library]


init_state()
apply_css()
assessment = st.session_state.assessment
library = st.session_state.library
repo = Repository(st.session_state.db_path)

st.sidebar.markdown("## ◈ AI Assurance Lab")
st.sidebar.caption("Local-first audit workbench")
st.sidebar.markdown("---")
st.sidebar.markdown(f"**Assessment**  \n{assessment['system']['name']}")
st.sidebar.markdown(f"**Stage**  \n{assessment['system']['lifecycle']}")
st.sidebar.markdown("---")
st.sidebar.caption("Decision support—not a substitute for auditor judgment. Framework mappings are cross-references, not certifications.")

st.markdown(f"""<div class="hero"><div class="eyebrow">Internal Audit · AI Assurance</div>
<h1>{assessment['system']['name']}</h1><p>{assessment['system']['purpose']}</p></div>""", unsafe_allow_html=True)

tabs = st.tabs(["Overview", "Inventory", "Risk & controls", "GenAI tests", "Evidence", "Findings", "Audit the AI Auditor"])

rows = control_rows(assessment, library)
inh = inherent_score(assessment["risk"]["likelihood"], assessment["risk"]["impact"])
res = residual_score(inh, [r["status"] for r in rows])

with tabs[0]:
    a, b, c, d = st.columns(4)
    a.metric("Inherent risk", band(inh), f"{inh}/16")
    b.metric("Residual risk", band(res), f"{res}/16")
    effective = sum(r["status"] == "Effective" for r in rows)
    c.metric("Effective controls", f"{effective}/{len(rows)}")
    failed = sum(t["result"] == "Fail" for t in assessment["genai_tests"])
    d.metric("Failed GenAI tests", failed)
    report_findings = [generate_finding(r, assessment["system"]["name"]) for r in rows if r["status"] == "Ineffective"]
    report_pdf = build_audit_report(assessment, rows, repo.evidence(st.session_state.assessment_id), report_findings,
                                    inh, res, band(inh), band(res))
    st.download_button("Download executive audit report (PDF)", report_pdf,
                       "claims-copilot-ai-audit-report.pdf", "application/pdf", type="primary")
    left, right = st.columns([1.2, 1])
    with left:
        summary = pd.DataFrame(domain_summary(rows))
        fig = px.bar(summary, x="effectiveness", y="domain", orientation="h", range_x=[0, 100],
                     color="effectiveness", color_continuous_scale=["#d94b64", "#f2b84b", "#2cb7a3"],
                     labels={"effectiveness":"Control effectiveness (%)", "domain":""})
        fig.update_layout(height=360, coloraxis_showscale=False, margin=dict(l=0,r=20,t=35,b=0), title="Control effectiveness by domain")
        st.plotly_chart(fig, width="stretch")
    with right:
        st.subheader("Priority signals")
        for r in rows:
            if r["status"] == "Ineffective":
                st.error(f"{r['id']} · {r['title']}")
        for t in assessment["genai_tests"]:
            if t["result"] == "Fail":
                st.warning(f"{t['test']} · {t['failures']} of {t['cases']} cases failed")
        st.markdown('<div class="note">Start with failed adversarial tests, then confirm whether human oversight sufficiently reduces real-world impact.</div>', unsafe_allow_html=True)

with tabs[1]:
    st.subheader("AI system inventory")
    labels = {"name":"System name","owner":"Business owner","purpose":"Intended purpose","model":"Model / technique","vendor":"Third party","users":"Users","data":"Data processed","deployment":"Deployment","lifecycle":"Lifecycle stage"}
    cols = st.columns(2)
    for i, (key, label) in enumerate(labels.items()):
        value = cols[i % 2].text_area(label, value=assessment["system"][key], height=70, key=f"inv_{key}")
        assessment["system"][key] = value
    if st.button("Save inventory", type="primary"):
        repo.save_assessment(assessment)
        st.success("Inventory saved locally.")

with tabs[2]:
    st.subheader("Inherent risk")
    x, y = st.columns(2)
    assessment["risk"]["likelihood"] = x.select_slider("Likelihood", ["Low","Moderate","High","Very High"], value=assessment["risk"]["likelihood"])
    assessment["risk"]["impact"] = y.select_slider("Impact", ["Low","Moderate","High","Severe"], value=assessment["risk"]["impact"])
    st.caption("Inherent score = likelihood (1–4) × impact (1–4). Residual score applies the average control-status factor. See docs/METHODOLOGY.md.")
    st.subheader("Control assessment")
    statuses = ["Effective", "Partially Effective", "Ineffective", "Not Assessed"]
    for c in library:
        with st.expander(f"{c['id']} · {c['title']} — {assessment['controls'].get(c['id'], 'Not Assessed')}"):
            st.write(c["objective"])
            st.caption(" · ".join(c["frameworks"]))
            assessment["controls"][c["id"]] = st.selectbox("Operating effectiveness", statuses, index=statuses.index(assessment["controls"].get(c["id"], "Not Assessed")), key=f"ctl_{c['id']}")
    if st.button("Save risk and controls", type="primary"):
        repo.save_assessment(assessment)
        st.success("Assessment saved locally.")

with tabs[3]:
    st.subheader("GenAI-specific test results")
    test_df = pd.DataFrame(assessment["genai_tests"])
    st.dataframe(test_df, width="stretch", hide_index=True)
    chart = px.bar(test_df, x="test", y=["cases", "failures"], barmode="group", color_discrete_sequence=["#173e5f", "#d94b64"])
    chart.update_layout(height=340, margin=dict(l=0,r=0,t=20,b=0), xaxis_title="", yaxis_title="Test cases")
    st.plotly_chart(chart, width="stretch")
    st.info("Test records are observations, not vulnerability proof. Reproduce failures, assess exploitability, and document scope before concluding.")

with tabs[4]:
    st.subheader("Evidence locker")
    ev = repo.evidence(st.session_state.assessment_id)
    st.dataframe(pd.DataFrame(ev)[["evidence_id","title","description","control_id","created_at"]], width="stretch", hide_index=True)
    with st.form("evidence_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        eid = c1.text_input("Evidence ID", value=f"EV-{len(ev)+1:03d}")
        title = c2.text_input("Title")
        description = st.text_area("Description / provenance")
        control_id = st.selectbox("Linked control", [c["id"] for c in library])
        upload = st.file_uploader("Optional file (demo records filename only)")
        if st.form_submit_button("Add evidence", type="primary"):
            if title and description:
                repo.add_evidence(st.session_state.assessment_id, {"evidence_id":eid,"title":title,"description":description,"control_id":control_id,"path":upload.name if upload else ""})
                st.success("Evidence metadata added. Refreshing…")
                st.rerun()
            else:
                st.error("Title and description are required.")

with tabs[5]:
    st.subheader("Automated finding drafts")
    st.caption("Drafts use condition, criteria, cause, risk, and recommendation. Auditor review is required before issuance.")
    candidates = [r for r in control_rows(assessment, library) if r["status"] in ("Ineffective", "Partially Effective")]
    selected = st.selectbox("Control exception", [r["id"] for r in candidates], format_func=lambda cid: next(f"{r['id']} · {r['title']}" for r in candidates if r["id"] == cid))
    control = next(r for r in candidates if r["id"] == selected)
    finding = generate_finding(control, assessment["system"]["name"])
    st.markdown(f"### {finding['title']}")
    st.markdown(f"<span class='pill'>{finding['severity']} severity</span>", unsafe_allow_html=True)
    for key in ["condition","criteria","cause","risk","recommendation"]:
        st.markdown(f"**{key.title()}**")
        st.write(finding[key])
    st.download_button("Download finding JSON", json.dumps(finding, indent=2), f"{selected.lower()}-finding.json", "application/json")

with tabs[6]:
    st.subheader("Audit the AI Auditor")
    st.write("Challenge an AI-generated audit conclusion before a human auditor relies on it. The local rules look for unsupported assertions, invented criteria, severity inflation, inconsistency, and thin evidence.")
    conclusion = st.text_area("AI-generated audit conclusion", value=assessment["sample_conclusion"], height=170)
    criteria = st.multiselect("Authorized criteria for this conclusion", sorted({f for c in library for f in c["frameworks"]}), default=["NIST AI RMF GOVERN 1.1", "OWASP LLM01"])
    source_findings = [generate_finding(r, assessment["system"]["name"]) for r in rows if r["status"] == "Ineffective"]
    result = audit_conclusion(conclusion, repo.evidence(st.session_state.assessment_id), criteria, source_findings)
    a, b, c = st.columns(3)
    a.metric("Reliability score", f"{result['reliability_score']}/100")
    b.metric("Challenge risk", result["rating"])
    c.metric("Flags", sum(x["status"] == "Flag" for x in result["checks"]))
    st.dataframe(pd.DataFrame(result["checks"]), width="stretch", hide_index=True, column_config={"score":st.column_config.ProgressColumn("Risk points", min_value=0, max_value=25)})
    st.markdown('<div class="note"><b>Required disposition:</b> trace each material assertion to sufficient, relevant, and reliable evidence; confirm criteria applicability; reconcile contradictions; and have a qualified auditor approve the final conclusion.</div>', unsafe_allow_html=True)
    st.download_button("Download challenge report", json.dumps({"conclusion":conclusion, **result}, indent=2), "audit-the-ai-auditor.json", "application/json")
