import time
import os
from prometheus_client import Counter, Histogram, start_http_server

# Define core assessment metrics matching section 06 guidelines
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

def start_metrics_server(port=8001):
    """Starts a local metrics scraping server endpoint."""
    try:
        start_http_server(port)
        print(f"📡 Prometheus metrics exporter live at http://localhost:{port}/metrics")
    except Exception as e:
        print(f"Metrics engine already active or bound: {e}")

def simulate_ticket_processing(channel, data_content):
    """Wraps processing inside performance timer metrics context."""
    with LATENCY.time():
        # Simulate processing delay
        time.sleep(0.4) 
        
        # Simple structural rule-based validation guardrail checks
        if "password" in data_content.lower() or "reset" in data_content.lower():
            outcome = "auto_respond"
        else:
            outcome = "escalate"
            
        # Check for simulated compliance failures (e.g. PII leak risk check)
        if "ssn" in data_content.lower() or "credit card" in data_content.lower():
            GUARDRAIL.labels(guardrail="private_data").inc()
            outcome = "block"
            
        # Log to structural trackers
        TICKETS.labels(channel=channel, outcome=outcome).inc()
        return outcome
