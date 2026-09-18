import json
import time
import uuid
import os
import statistics
from datetime import datetime, timezone
from src.logging_store import init_db, log_decision
from src.ingest import normalize_ticket
from src.classify import classify_ticket
from src.retrieve import query_vector_store
from src.route import route_ticket

def run_evaluation_harness(mock_dataset_path="data/test_dataset.json"):
    print("--- Starting Unattended Evaluation Gate Run Framework (B-11) ---")
    init_db()
    
    if not os.path.exists(mock_dataset_path):
        print(f"Error: Target data array asset missing at {mock_dataset_path}")
        return
        
    with open(mock_dataset_path, "r") as f:
        test_tickets = json.load(f)
        
    results = []
    latencies = []
    
    for raw_ticket in test_tickets:
        start_time = time.time()
        
        # Run live production components sequentially
        ticket = normalize_ticket(raw_ticket)
        classification = classify_ticket(ticket)
        retrieved_docs = query_vector_store(ticket["clean_body"], k=3)
        routing_decision = route_ticket(ticket, classification, retrieved_docs)
        
        elapsed = time.time() - start_time
        latencies.append(elapsed)
        
        # Map structured telemetry results
        action_taken = routing_decision["action_taken"]
        is_closed = (action_taken == "auto_respond")
        
        sources_used = [{"doc_id": d.metadata.get("doc_id")} for d in retrieved_docs]
        
        decision_payload = {
            "decision_id": str(uuid.uuid4()),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "ticket_id": ticket["ticket_id"],
            "stage": "evaluation_run",
            "prediction": classification.get("intent", "general_inquiry"),
            "confidence": classification.get("confidence", 0.0),
            "threshold": float(os.getenv("CONFIDENCE_THRESHOLD", "0.80")),
            "action_taken": action_taken,
            "reason": classification.get("routing_reason", "Evaluation processing validation run."),
            "sources_used": sources_used,
            "guardrails_results": {"status": "bypass_in_harness"},
            "prompt_version": "PR-02 v1.2",
            "requirement_ids": ["FR-01", "FR-02", "FR-03", "FR-04", "FR-07", "FR-08", "FR-09"]
        }
        log_decision(decision_payload)
        
        results.append({
            "closed": is_closed,
            "escalated": not is_closed,
            "latency": elapsed
        })

    # Output Business Performance Metrics Summary Report
    fcr = (sum(1 for r in results if r["closed"]) / len(results)) * 100
    mean_lat = statistics.mean(latencies)
    
    print("\n--- COMPULSORY UNATTENDED GATE RUN PERFORMANCE OVERVIEW ---")
    print(f"First Contact Resolution (FCR): {fcr:.1f}% (Blueprint Target: >= 60%)")
    print(f"Mean Pipeline Execution Latency: {mean_lat:.4f}s (SLA Target: < 3.0s)")
    print("------------------------------------------------------------")

if __name__ == "__main__":
    run_evaluation_harness()
