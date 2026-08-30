# Architecture

## Overview

```text
Browser
  │
  ▼
Streamlit UI (app.py)
  ├── scoring.py      deterministic risk calculations
  ├── findings.py     structured finding templates
  ├── auditor.py      explainable conclusion challenge rules
  └── storage.py      parameterized SQLite persistence
          │
          ├── assessments
          ├── evidence
          └── findings

Configuration: data/controls.yaml
Seed data:     data/claims_copilot.json
```

## Design choices

- **Local first:** the default path sends no content to an external AI service.
- **Explainable logic:** scoring and audit-of-auditor rules are short, deterministic Python functions with unit tests.
- **Configuration over code:** controls and mappings live in YAML; the fictional assessment lives in JSON.
- **Small persistence boundary:** SQLite provides a portable demonstration store while keeping query logic isolated in `Repository`.
- **Separation of concerns:** presentation, business rules, data, and sample content are independently replaceable.

## Data flow

On startup, the app reads the control library and Claims Copilot seed, creates the SQLite schema, and seeds evidence if needed. Session state holds active edits; Save actions persist the assessment. Evidence entries are inserted separately and retrieved by assessment ID. Audit-the-auditor reads the current conclusion, authorized criteria, stored evidence, and generated source findings, then returns check-level reasons and risk points.

## Security and production gaps

The demo does not provide authentication, authorization, encryption at rest, malware scanning, immutable audit logging, retention enforcement, concurrent-edit protection, or secure file content storage. The uploader stores filename metadata only. For production, add identity-aware access control, secrets management, encrypted object storage, tenant isolation, content scanning, backups, structured audit logs, input limits, dependency monitoring, and a privacy/threat assessment.

