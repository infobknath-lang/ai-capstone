import os
import pytest
from src.logging_store import DB_PATH

def test_environment_variables_loaded():
    """Verify that important configurations are loaded into the environment variables."""
    assert os.getenv("MODEL_NAME") is not None
    assert os.getenv("CONFIDENCE_THRESHOLD") is not None

def test_database_path_configuration():
    """Ensure that the local SQLite tracking ledger points to the right directory."""
    assert "decisions.db" in DB_PATH

def test_metrics_logic_evaluation():
    """Verify that our underlying telemetry processing rules function as intended."""
    from src.guardrails import simulate_ticket_processing
    outcome = simulate_ticket_processing("web", "I need to trigger a password reset.")
    assert outcome == "auto_respond"
