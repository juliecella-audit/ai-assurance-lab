# Methodology

## Purpose and principles

AI Assurance Lab models a risk-based internal audit, not a certification. It separates facts, criteria, auditor judgment, and generated text. The workflow follows five principles: preserve traceability, challenge management and machine assertions, assess both design and operation, make uncertainty visible, and keep a human auditor accountable for the conclusion.

## Risk scoring

Likelihood and impact are independently rated from 1 to 4. Inherent risk is their product (1–16), before control effect:

| Score | Band |
|---:|---|
| 1–3 | Low |
| 4–7 | Moderate |
| 8–11 | High |
| 12–16 | Critical |

Control status factors are Effective 0.15, Partially Effective 0.55, Ineffective 1.00, and Not Assessed 1.00. Residual score is inherent score multiplied by the average factor, with a floor of 1. This simple model is intentionally inspectable. It is not statistically calibrated and should be configured and validated against an organization's risk taxonomy before real use.

## Control assessment

Each control has an objective, risk statement, domain, and cross-framework references. An assessor selects one status:

- **Effective** — appropriately designed and operating consistently, supported by sufficient evidence.
- **Partially Effective** — some elements operate, but gaps reduce reliability.
- **Ineffective** — absent, poorly designed, or not operating.
- **Not Assessed** — no defensible conclusion has been reached.

Framework mappings are navigation aids. They do not reproduce full standard text, establish applicability, or demonstrate compliance.

## GenAI tests

The sample includes five test families: prompt injection, data leakage, hallucination/factuality, system-prompt disclosure, and excessive agency. A test record needs a defined population, prompt and expected result, actual output, reproducibility notes, environment/model version, reviewer, and disposition. Counts alone do not establish exploitability or business impact.

## Evidence and findings

Evidence should be sufficient, relevant, reliable, and traceable to a control and testing period. Finding drafts use condition, criteria, cause, risk/effect, and recommendation. Automated text is a starting point; auditors must validate all facts, criteria, severity, and feasibility.

## Audit the AI Auditor

The module applies deterministic screening rules to a proposed conclusion:

| Check | Screening logic | Required human response |
|---|---|---|
| Unsupported assertions | Absolute language or conclusions with no evidence | Trace each material assertion to evidence; narrow or remove unsupported language |
| Invented criteria | Named framework absent from authorized criteria | Establish applicability and exact criterion or remove citation |
| Severity inflation | “Critical” used without a Critical source finding | Reconcile to approved rating criteria and impact evidence |
| Inconsistency | Opposing conclusion terms appear together | Resolve scope, period, control, and population differences |
| Insufficient evidence | Fewer than two items, no explicit evidence ID, or sparse descriptions | Obtain stronger evidence and cite it directly |

The reliability score is `100 - risk points`. The rules are conservative prompts for challenge, not a semantic truth engine. False positives are expected and require documented disposition.

