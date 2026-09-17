import time
from src.guardrails import start_metrics_server, simulate_ticket_processing

if __name__ == "__main__":
    # Start telemetry server
    start_metrics_server(8001)

    print("Simulating test ticket runs... (Press Ctrl+C to stop)")
    while True:
        simulate_ticket_processing("web", "Requesting a password reset process links.")
        simulate_ticket_processing("chat", "Exposing dangerous data ssn profile leak.")
        time.sleep(2)
