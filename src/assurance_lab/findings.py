from __future__ import annotations

from typing import Mapping


def generate_finding(control: Mapping[str, object], system_name: str) -> dict[str, str]:
    title = f"{control['title']} is not operating effectively"
    return {
        "title": title,
        "severity": "High" if control.get("status") == "Ineffective" else "Moderate",
        "condition": f"For {system_name}, control {control['id']} ({control['title']}) was assessed as {str(control.get('status')).lower()}.",
        "criteria": f"The control is expected by {', '.join(control.get('frameworks', []))} and internal AI governance requirements.",
        "cause": "Control ownership, design, or execution has not been fully embedded in the operating process.",
        "risk": str(control.get("risk", "The AI system may produce outcomes outside the organization's risk appetite.")),
        "recommendation": f"Assign an accountable owner, document the procedure for {str(control['title']).lower()}, retain execution evidence, and test effectiveness before closure.",
    }

