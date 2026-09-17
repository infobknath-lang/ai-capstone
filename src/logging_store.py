import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()
DB_PATH = "./storage/decisions.db"

def init_db():
    # Ensure the storage directory exists
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    connection = sqlite3.connect(DB_PATH)
    connection.execute("""
        CREATE TABLE IF NOT EXISTS decisions (
            decision_id     TEXT PRIMARY KEY,
            created_at      TEXT NOT NULL,
            ticket_id       TEXT NOT NULL,
            stage           TEXT NOT NULL,
            prediction      TEXT,
            confidence      REAL,
            threshold       REAL,
            action_taken    TEXT NOT NULL,
            reason          TEXT NOT NULL,
            sources_used    TEXT,
            guardrails      TEXT,
            prompt_version  TEXT,
            requirement_ids TEXT
        )
    """)
    connection.commit()
    connection.close()
    print("SQLite Database checked/initialized at:", DB_PATH)

def log_decision(data: dict):
    # Missing function that harness.py needs to write logs
    pass

if __name__ == "__main__":
    init_db()
