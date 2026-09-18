import os
import uuid
from datetime import datetime, timezone
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

# Import our complete evidence-grounded blueprint architecture stack modules
from src.ingest import normalize_ticket
from src.classify import classify_ticket
from src.retrieve import query_vector_store
from src.route import route_ticket
from src.generate import generate_grounded_response
from src.guardrails import inspect_generated_text
from src.logging_store import log_decision

load_dotenv()

app = FastAPI(
    title="CloudServe Solutions Support Automation Platform API",
    version="2.0.0"
)

class TicketRequest(BaseModel):
    ticket_id: str
    content: str
    subject: str = "No Subject"
    channel: str = "web"
    group: str = "Standard"

@app.get("/")
def read_root():
    return {"status": "online", "system": "CloudServe Core RAG Router Active"}

@app.post("/process_ticket")
def process_ticket(request_payload: TicketRequest):
    try:
        # 1. Step 1: Multi-Channel Ingestion & Normalization (FR-01 / B-02)
        raw_dict = {
            "id": request_payload.ticket_id,
            "channel": request_payload.channel,
            "subject": request_payload.subject,
            "body": request_payload.content,
            "group": request_payload.group
        }
        ticket = normalize_ticket(raw_dict)
        
        # 2. Step 2: Intent Classification & Urgency Triaging Engine (FR-02 / B-06)
        classification = classify_ticket(ticket)
        
        # 3. Step 3: Dense Semantic Vector Lookups (FR-03 / B-04)
        # Pull top matches from our 500-character index
        retrieved_docs = query_vector_store(ticket["clean_body"], k=3)
        
        # 4. Step 4: Calibrated Deterministic Routing Gate (FR-04 / FR-08 / B-07)
        routing_decision = route_ticket(ticket, classification, retrieved_docs)
        
        # Format sources extracted to support tracking fields
        sources_used = [
            {"doc_id": d.metadata.get("doc_id"), "title": d.metadata.get("title")}
            for d in retrieved_docs
        ]
        
        # Intercept immediately if routing rules dictate escalation (FR-08 Interception Gate)
        if not routing_decision["should_generate"]:
            action_taken = routing_decision["action_taken"]
            prediction = classification.get("intent", "general_inquiry")
            reason = classification.get("routing_reason", "Escalated to human support lines.")
            output_response = "This ticket has been securely routed to a Tier 2 engineer for manual review."
            guardrail_status = "bypass"
            escalation_pkg = routing_decision["escalation_package"]
        else:
            # 5. Step 5: Grounded Response Drafting with Inline Citations (FR-05 / B-08)
            generated_draft = generate_grounded_response(ticket, retrieved_docs)
            
            # 6. Step 6: Active Pre-Release Output Guardrail Scanning (FR-06 / B-09)
            guardrail_check = inspect_generated_text(generated_draft)
            guardrail_status = guardrail_check["status"]
            
            if guardrail_status == "block":
                action_taken = "escalate_guardrail_blocked"
                prediction = classification.get("intent", "general_inquiry")
                reason = f"Guardrail blocked release: {guardrail_check['reason']}"
                output_response = "This ticket has been routed to human agents due to a safety control exception."
                routing_decision["action_taken"] = action_taken
                escalation_pkg = {"block_reason": reason}
            else:
                action_taken = "auto_respond"
                prediction = classification.get("intent", "general_inquiry")
                reason = "Confidence score and safety layers verified successfully."
                output_response = generated_draft
                escalation_pkg = None

        # 7. Step 7: Persistent 16-Field Decision Log Auditing Ledger (FR-07 / B-10)
        decision_payload = {
            "decision_id": str(uuid.uuid4()),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "ticket_id": ticket["ticket_id"],
            "stage": "api_live_route",
            "prediction": prediction,
            "confidence": classification.get("confidence", 0.0),
            "threshold": float(os.getenv("CONFIDENCE_THRESHOLD", "0.80")),
            "action_taken": action_taken,
            "reason": reason,
            "sources_used": sources_used,
            "guardrails_results": {"status": guardrail_status},
            "prompt_version": "PR-02 v1.2 / PR-03 v1.3",
            "requirement_ids": ["FR-01", "FR-02", "FR-03", "FR-04", "FR-05", "FR-06", "FR-07", "FR-08", "FR-09"]
        }
        log_decision(decision_payload)
        
        return {
            "ticket_id": ticket["ticket_id"],
            "action_taken": action_taken,
            "prediction": prediction,
            "confidence": decision_payload["confidence"],
            "reason": reason,
            "response": output_response,
            "escalation_package": escalation_pkg
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
