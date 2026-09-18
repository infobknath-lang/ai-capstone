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

def test_guardrails_policy_evaluation():
    """Verify that our underlying security policy checker intercepts forbidden claims."""
    from src.guardrails import inspect_generated_text
    
    # Verify that safe text passes
    safe_check = inspect_generated_text("To reset your account parameters, navigate to the portal [DOC-AUTH-003].")
    assert safe_check["status"] == "pass"
    
    # Verify that unauthorized liability statements are actively blocked
    blocked_check = inspect_generated_text("A full refund has been issued to your credit card account immediately.")
    assert blocked_check["status"] == "block"
