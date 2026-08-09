"""
SQLite-backed analysis history and provenance tracking.
Stores analysis metadata, input snapshots, and result references.
"""

import sqlite3
import json
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone


DB_PATH = Path(__file__).parent.parent.parent / "data" / "analysis_history.db"


def _get_connection() -> sqlite3.Connection:
    """Get SQLite connection, creating DB and tables if needed."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("""
        CREATE TABLE IF NOT EXISTS analyses (
            analysis_id TEXT PRIMARY KEY,
            timestamp TEXT NOT NULL,
            drug_id TEXT NOT NULL,
            drug_name TEXT NOT NULL,
            polymer_ids TEXT NOT NULL,
            mode TEXT NOT NULL DEFAULT 'exploratory',
            top_polymer TEXT,
            topsis_cl REAL,
            confidence_tier TEXT,
            software_version TEXT,
            config_checksum TEXT,
            random_seed INTEGER DEFAULT 42,
            input_snapshot TEXT,
            result_dir TEXT,
            warnings TEXT DEFAULT '[]',
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    return conn


def save_analysis(
    analysis_id: str,
    drug_id: str,
    drug_name: str,
    polymer_ids: List[str],
    mode: str,
    top_polymer: str,
    topsis_cl: float,
    confidence_tier: str,
    software_version: str,
    config_checksum: str,
    random_seed: int,
    input_snapshot: Dict[str, Any],
    result_dir: str,
    warnings: List[str],
) -> None:
    """Save a completed analysis to history."""
    conn = _get_connection()
    now = datetime.now(timezone.utc).isoformat()
    conn.execute(
        """INSERT INTO analyses
           (analysis_id, timestamp, drug_id, drug_name, polymer_ids, mode,
            top_polymer, topsis_cl, confidence_tier, software_version,
            config_checksum, random_seed, input_snapshot, result_dir, warnings, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            analysis_id, now, drug_id, drug_name,
            json.dumps(polymer_ids), mode, top_polymer, topsis_cl,
            confidence_tier, software_version, config_checksum, random_seed,
            json.dumps(input_snapshot), result_dir, json.dumps(warnings), now,
        ),
    )
    conn.commit()
    conn.close()


def list_analyses() -> List[Dict[str, Any]]:
    """List all analyses in reverse chronological order."""
    conn = _get_connection()
    rows = conn.execute(
        "SELECT * FROM analyses ORDER BY created_at DESC"
    ).fetchall()
    conn.close()
    results = []
    for row in rows:
        d = dict(row)
        d["polymer_ids"] = json.loads(d["polymer_ids"])
        d["warnings"] = json.loads(d["warnings"])
        results.append(d)
    return results


def get_analysis(analysis_id: str) -> Optional[Dict[str, Any]]:
    """Get a single analysis by ID."""
    conn = _get_connection()
    row = conn.execute(
        "SELECT * FROM analyses WHERE analysis_id = ?", (analysis_id,)
    ).fetchone()
    conn.close()
    if row is None:
        return None
    d = dict(row)
    d["polymer_ids"] = json.loads(d["polymer_ids"])
    d["warnings"] = json.loads(d["warnings"])
    d["input_snapshot"] = json.loads(d["input_snapshot"])
    return d


def delete_analysis(analysis_id: str) -> bool:
    """Delete an analysis record."""
    conn = _get_connection()
    cursor = conn.execute(
        "DELETE FROM analyses WHERE analysis_id = ?", (analysis_id,)
    )
    conn.commit()
    deleted = cursor.rowcount > 0
    conn.close()
    return deleted
