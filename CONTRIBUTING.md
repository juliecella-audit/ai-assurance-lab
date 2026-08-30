# Contributing

Contributions are welcome. Open an issue describing the audit problem, expected behavior, and any framework/version assumptions before a large change.

1. Create a virtual environment and install `requirements.txt`.
2. Add or update tests for business-rule changes.
3. Run `python -m pytest -q` and `python -m compileall app.py src`.
4. Keep framework text to short cross-references; do not copy licensed standards.
5. Never commit confidential evidence, real personal data, API keys, or generated databases.

For new conclusion checks, document the false-positive risk and required human disposition in `docs/METHODOLOGY.md`.

