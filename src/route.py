import os

def build_tier2_context(ticket: dict, classification: dict, retrieval_results: list) -> dict:
    """FR-09: Programmatic synthesis mechanism for structural escalation payloads."""
    return {
        "issue_summary": f"{ticket['subject']} — {ticket['clean_body'][:180]}...",
        "intent_tag": classification.get("intent", "general_inquiry"),
        "doc_links": [
            {
                "doc_id": doc.metadata.get("doc_id", "UNKNOWN"),
                "title": doc.metadata.get("title", "Untitled Document"),
                "score": round(float(doc.metadata.get("score", 1.0)), 3)
            }
            for doc in retrieval_results[:3]
        ],
        "escalation_reason": classification.get("routing_reason", "Manual Triage Mandatory")
    }

def route_ticket(ticket: dict, class_res: dict, retrieval_results: list) -> dict:
    """FR-04 / FR-08: Calibrated deterministic sub-routing gate interceptor."""
    threshold = float(os.getenv("CONFIDENCE_THRESHOLD", "0.80"))
    
    # 1. Check Governance Topic Rules First (FR-08 Interception Gate)
    if class_res.get("labels", {}).get("must_not_auto_respond", False):
        class_res["routing_reason"] = f"Mandatory human escalation for restricted intent: {class_res.get('intent')}"
        return {
            "action_taken": "escalate_restricted_topic",
            "should_generate": False,
            "escalation_package": build_tier2_context(ticket, class_res, retrieval_results)
        }
        
    # 2. Enforce Operational Fallback for Empty Context Matches (FR-04 Revision Layer)
    if not retrieval_results:
        class_res["routing_reason"] = "Empty Retrieval: No matching database documentation found."
        return {
            "action_taken": "escalate_empty_retrieval",
            "should_generate": False,
            "escalation_package": build_tier2_context(ticket, class_res, retrieval_results)
        }
        
    # 3. Check Confidence Calibration Threshold Limits
    confidence = class_res.get("confidence", 0.0)
    if confidence < threshold:
        class_res["routing_reason"] = f"Low Confidence ({confidence:.2f} < {threshold:.2f} Threshold)"
        return {
            "action_taken": "escalate_low_confidence",
            "should_generate": False,
            "escalation_package": build_tier2_context(ticket, class_res, retrieval_results)
        }
        
    return {
        "action_taken": "auto_respond",
        "should_generate": True,
        "escalation_package": None
    }
