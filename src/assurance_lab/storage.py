from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

SCHEMA = """
CREATE TABLE IF NOT EXISTS assessments (id INTEGER PRIMARY KEY, name TEXT UNIQUE, payload TEXT NOT NULL, updated_at TEXT DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS evidence (id INTEGER PRIMARY KEY AUTOINCREMENT, assessment_id INTEGER, evidence_id TEXT, title TEXT, description TEXT, control_id TEXT, path TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS findings (id INTEGER PRIMARY KEY AUTOINCREMENT, assessment_id INTEGER, payload TEXT NOT NULL, created_at TEXT DEFAULT CURRENT_TIMESTAMP);
"""


class Repository:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as conn:
            conn.executescript(SCHEMA)

    def connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        return conn

    def save_assessment(self, payload: dict[str, Any]) -> int:
        with self.connect() as conn:
            conn.execute("INSERT INTO assessments(name,payload) VALUES(?,?) ON CONFLICT(name) DO UPDATE SET payload=excluded.payload,updated_at=CURRENT_TIMESTAMP", (payload["system"]["name"], json.dumps(payload)))
            row = conn.execute("SELECT id FROM assessments WHERE name=?", (payload["system"]["name"],)).fetchone()
            return int(row["id"])

    def add_evidence(self, assessment_id: int, item: dict[str, str]) -> None:
        with self.connect() as conn:
            conn.execute("INSERT INTO evidence(assessment_id,evidence_id,title,description,control_id,path) VALUES(?,?,?,?,?,?)", (assessment_id,item["evidence_id"],item["title"],item["description"],item["control_id"],item.get("path", "")))

    def evidence(self, assessment_id: int) -> list[dict[str, Any]]:
        with self.connect() as conn:
            return [dict(r) for r in conn.execute("SELECT * FROM evidence WHERE assessment_id=? ORDER BY id", (assessment_id,))]

