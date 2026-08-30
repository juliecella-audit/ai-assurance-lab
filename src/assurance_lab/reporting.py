from __future__ import annotations

from io import BytesIO
from typing import Iterable, Mapping

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

NAVY = colors.HexColor("#10213D")
TEAL = colors.HexColor("#2CB7A3")
PALE = colors.HexColor("#EAF8F6")
INK = colors.HexColor("#152238")
MUTED = colors.HexColor("#526279")
RED = colors.HexColor("#D94B64")
AMBER = colors.HexColor("#F2B84B")


def build_audit_report(assessment: Mapping[str, object], controls: Iterable[Mapping[str, object]],
                       evidence: Iterable[Mapping[str, object]], findings: Iterable[Mapping[str, object]],
                       inherent: float, residual: float, inherent_band: str, residual_band: str) -> bytes:
    """Create a polished, deterministic audit-summary PDF entirely in memory."""
    controls, evidence, findings = list(controls), list(evidence), list(findings)
    out = BytesIO()
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="CoverTitle", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=28,
                              leading=32, textColor=colors.white, alignment=TA_CENTER, spaceAfter=14))
    styles.add(ParagraphStyle(name="CoverSub", parent=styles["Normal"], fontSize=12, leading=17,
                              textColor=colors.HexColor("#D9E6F2"), alignment=TA_CENTER))
    styles.add(ParagraphStyle(name="H1x", parent=styles["Heading1"], fontName="Helvetica-Bold", fontSize=18,
                              leading=22, textColor=NAVY, spaceBefore=6, spaceAfter=10))
    styles.add(ParagraphStyle(name="H2x", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=12,
                              leading=15, textColor=NAVY, spaceBefore=8, spaceAfter=5))
    styles.add(ParagraphStyle(name="Bodyx", parent=styles["BodyText"], fontSize=9, leading=13, textColor=INK))
    styles.add(ParagraphStyle(name="Smallx", parent=styles["BodyText"], fontSize=7.5, leading=10, textColor=MUTED))

    def footer(canvas, doc):
        canvas.saveState()
        canvas.setStrokeColor(colors.HexColor("#DCE3EC")); canvas.line(0.65*inch, 0.55*inch, 7.85*inch, 0.55*inch)
        canvas.setFont("Helvetica", 7); canvas.setFillColor(MUTED)
        canvas.drawString(0.65*inch, 0.37*inch, "AI Assurance Lab | Internal Audit Demonstration")
        canvas.drawRightString(7.85*inch, 0.37*inch, f"Page {doc.page}")
        canvas.restoreState()

    doc = SimpleDocTemplate(out, pagesize=letter, rightMargin=.65*inch, leftMargin=.65*inch,
                            topMargin=.65*inch, bottomMargin=.72*inch, title=f"{assessment['system']['name']} AI Audit Report")
    story = []
    cover = Table([[Paragraph("AI ASSURANCE LAB", styles["Smallx"])],
                   [Paragraph(str(assessment["system"]["name"]), styles["CoverTitle"])],
                   [Paragraph("AI System Assurance Summary", styles["CoverSub"])],
                   [Spacer(1, .4*inch)],
                   [Paragraph(str(assessment["system"]["purpose"]), styles["CoverSub"])],
                   [Spacer(1, .5*inch)],
                   [Paragraph("Prepared for internal audit demonstration purposes", styles["CoverSub"])]],
                  colWidths=[7.2*inch], rowHeights=[.42*inch, .75*inch, .35*inch, .5*inch, .8*inch, .6*inch, .4*inch])
    cover.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),NAVY),("BOX",(0,0),(-1,-1),0,NAVY),
                               ("VALIGN",(0,0),(-1,-1),"MIDDLE"),("ALIGN",(0,0),(-1,-1),"CENTER"),
                               ("TEXTCOLOR",(0,0),(0,0),TEAL)]))
    story += [Spacer(1, .55*inch), cover, Spacer(1, .4*inch), Paragraph("LOCAL-FIRST | EXPLAINABLE | HUMAN-ACCOUNTABLE", styles["Smallx"]), PageBreak()]

    story += [Paragraph("Executive summary", styles["H1x"])]
    metrics = Table([["INHERENT RISK", "RESIDUAL RISK", "CONTROL EXCEPTIONS", "EVIDENCE ITEMS"],
                     [f"{inherent_band} ({inherent}/16)", f"{residual_band} ({residual}/16)",
                      str(sum(c.get("status") != "Effective" for c in controls)), str(len(evidence))]], colWidths=[1.8*inch]*4)
    metrics.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),NAVY),("TEXTCOLOR",(0,0),(-1,0),colors.white),
                                 ("BACKGROUND",(0,1),(-1,1),PALE),("TEXTCOLOR",(0,1),(-1,1),INK),
                                 ("FONTNAME",(0,0),(-1,-1),"Helvetica-Bold"),("FONTSIZE",(0,0),(-1,0),7),
                                 ("FONTSIZE",(0,1),(-1,1),10),("ALIGN",(0,0),(-1,-1),"CENTER"),
                                 ("VALIGN",(0,0),(-1,-1),"MIDDLE"),("GRID",(0,0),(-1,-1),.35,colors.white),
                                 ("TOPPADDING",(0,0),(-1,-1),8),("BOTTOMPADDING",(0,0),(-1,-1),8)]))
    story += [metrics, Spacer(1, 12), Paragraph("Overall conclusion", styles["H2x"]),
              Paragraph(f"{assessment['system']['name']} carries {inherent_band.lower()} inherent risk. Based on the recorded control statuses, the indicative residual risk is {residual_band.lower()}. Failed adversarial tests and ineffective controls require remediation and auditor validation before broader deployment or reliance.", styles["Bodyx"]),
              Paragraph("Scope and system profile", styles["H2x"])]
    profile = [["Owner", assessment["system"]["owner"]], ["Model", assessment["system"]["model"]],
               ["Users", assessment["system"]["users"]], ["Data", assessment["system"]["data"]],
               ["Stage", assessment["system"]["lifecycle"]]]
    pt = Table([[Paragraph(str(a), styles["Smallx"]), Paragraph(str(b), styles["Bodyx"])] for a,b in profile], colWidths=[1.2*inch,6*inch])
    pt.setStyle(TableStyle([("BACKGROUND",(0,0),(0,-1),colors.HexColor("#EEF2F7")),("GRID",(0,0),(-1,-1),.35,colors.HexColor("#DCE3EC")),
                            ("VALIGN",(0,0),(-1,-1),"TOP"),("TOPPADDING",(0,0),(-1,-1),6),("BOTTOMPADDING",(0,0),(-1,-1),6)]))
    story += [pt, PageBreak(), Paragraph("Control assessment", styles["H1x"])]
    control_data = [["ID", "Domain", "Control", "Status"]] + [[c["id"], c["domain"], Paragraph(str(c["title"]), styles["Smallx"]), c["status"]] for c in controls]
    ct = Table(control_data, colWidths=[.65*inch,1.25*inch,3.9*inch,1.4*inch], repeatRows=1)
    ct.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),NAVY),("TEXTCOLOR",(0,0),(-1,0),colors.white),("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
                            ("FONTSIZE",(0,0),(-1,-1),7.5),("GRID",(0,0),(-1,-1),.35,colors.HexColor("#DCE3EC")),
                            ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white,colors.HexColor("#F7F9FC")]),("VALIGN",(0,0),(-1,-1),"TOP"),
                            ("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5)]))
    story += [ct, Spacer(1, 12), Paragraph("Key findings", styles["H1x"])]
    for idx, f in enumerate(findings, 1):
        story += [Paragraph(f"{idx}. {f['title']} - {f['severity']}", styles["H2x"]),
                  Paragraph(f"<b>Condition:</b> {f['condition']}", styles["Bodyx"]),
                  Paragraph(f"<b>Risk:</b> {f['risk']}", styles["Bodyx"]),
                  Paragraph(f"<b>Recommendation:</b> {f['recommendation']}", styles["Bodyx"]), Spacer(1, 5)]
    story += [PageBreak(), Paragraph("GenAI test results", styles["H1x"])]
    test_data = [["Test", "Result", "Cases", "Failures", "Observation"]] + [[t["test"],t["result"],t["cases"],t["failures"],Paragraph(t["observation"],styles["Smallx"])] for t in assessment["genai_tests"]]
    tt = Table(test_data, colWidths=[1.25*inch,.7*inch,.55*inch,.6*inch,3.95*inch], repeatRows=1)
    tt.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),NAVY),("TEXTCOLOR",(0,0),(-1,0),colors.white),("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
                            ("FONTSIZE",(0,0),(-1,-1),7),("GRID",(0,0),(-1,-1),.35,colors.HexColor("#DCE3EC")),
                            ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white,colors.HexColor("#F7F9FC")]),("VALIGN",(0,0),(-1,-1),"TOP"),
                            ("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5)]))
    story += [tt, Spacer(1, 12), Paragraph("Evidence register", styles["H1x"])]
    ev_data = [["ID", "Title", "Linked control", "Description"]] + [[e["evidence_id"],e["title"],e["control_id"],Paragraph(e["description"],styles["Smallx"])] for e in evidence]
    et = Table(ev_data, colWidths=[.75*inch,1.7*inch,1*inch,3.6*inch], repeatRows=1)
    et.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),NAVY),("TEXTCOLOR",(0,0),(-1,0),colors.white),("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
                            ("FONTSIZE",(0,0),(-1,-1),7),("GRID",(0,0),(-1,-1),.35,colors.HexColor("#DCE3EC")),
                            ("VALIGN",(0,0),(-1,-1),"TOP"),("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5)]))
    story += [et, Spacer(1, 14), Paragraph("Important limitation", styles["H2x"]),
              Paragraph("This report is generated from demonstration data and deterministic rules. It is not a compliance certification or an issued audit opinion. A qualified auditor must validate scope, criteria, evidence, ratings, and conclusions.", styles["Bodyx"])]
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    return out.getvalue()

