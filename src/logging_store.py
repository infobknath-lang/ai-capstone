import sqlite3
import os
import json
from dotenv import load_dotenv

load_dotenv()
DB_PATH = "./storage/decisions.db"

def init_db():
    """Fulfills FR-07 and NFR-05 by initializing a 16-field persistent compliance ledger."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    connection = sqlite3.connect(DB_PATH)
    connection.execute("""
        CREATE TABLE IF NOT EXISTS decisions (
            decision_id     TEXT PRIMARY KEY,
            created_at      TEXT NOT NULL,
            ticket_id       TEXT NOT NULL,
            stage           TEXT NOT NULL,
            input_summary   TEXT NOT NULL,
            model_name      TEXT NOT NULL,
            prediction      TEXT,
            confidence      REAL,
            threshold       REAL,
            action_taken    TEXT NOT NULL,
            reason          TEXT NOT NULL,
            sources_used    TEXT,
            guardrail_results TEXT,
            prompt_version  TEXT NOT NULL,
            requirement_ids TEXT NOT NULL,
            execution_time_ms REAL NOT NULL
        )
    """)
    connection.commit()
    connection.close()
    print(f"SQLite 16-field database initialized at: {DB_PATH}")

def log_decision(data: dict):
    """Writes a 100% complete transaction array block to the local ledger layer."""
    connection = sqlite3.connect(DB_PATH)
    connection.execute("""
        INSERT INTO decisions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data.get("decision_id"), data.get("created_at"), data.get("ticket_id"),
        data.get("stage"), data.get("input_summary"), data.get("model_name"),
        data.get("prediction"), data.get("confidence"), data.get("threshold"),
        data.get("action_taken"), data.get("reason"), 
        json.dumps(data.get("sources_used")), json.dumps(data.get("guardrails_results")),
        data.get("prompt_version"), json.dumps(data.get("requirement_ids")),
        data.get("execution_time_ms")
    ))
    connection.commit()
    connection.close()
