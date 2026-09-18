import time
import os
import re
from prometheus_client import Counter, Histogram, start_http_server

# --- Section 06: Telemetry Configurations ---
TICKETS = Counter(
    "tickets_processed_total", 
    "Total tickets processed by the platform", 
    ["channel", "outcome"]
)
LATENCY = Histogram(
    "response_seconds", 
    "End-to-end processing execution time in seconds"
)
GUARDRAIL = Counter(
    "guardrail_blocks_total", 
    "Total responses blocked by safety infrastructure checks", 
    ["guardrail"]
)

# --- FR-08 / FR-06 Post-Generation Policy Enforcement ---
FORBIDDEN_CLAIMS_REGEX = [
    r"refund (has been|will be) issued", 
    r"guarantee (100%|full) uptime",
    r"override security policy", 
    r"credit applied to account"
]

def start_metrics_server(port=8001):
    """Starts a local metrics scraping server endpoint."""
    try:
        start_http_server(port)
        print(f"📡 Prometheus metrics exporter live at http://localhost:{port}/metrics")
    except Exception as e:
        pass

def inspect_generated_text(generated_text: str) -> dict:
    """FR-06: Pre-release output scanner to catch unauthorized financial or security statements."""
    for pattern in FORBIDDEN_CLAIMS_REGEX:
        if re.search(pattern, generated_text, re.IGNORECASE):
            GUARDRAIL.labels(guardrail="forbidden_claim").inc()
            return {"status": "block", "reason": f"Forbidden claim detected: {pattern}"}
            
    # Inline PII protection regex pass
    if re.search(r"\b\d{3}-\d{2}-\d{4}\b", generated_text):  # Basic SSN pattern
        GUARDRAIL.labels(guardrail="pii_leak").inc()
        return {"status": "block", "reason": "PII leak caught by pre-release scanners"}
        
    return {"status": "pass", "reason": "All active security policies passed."}
