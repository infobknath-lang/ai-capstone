import re

def normalize_ticket(raw_ticket: dict) -> dict:
    """
    FR-01: Multi-Channel Ingestion & Normalization.
    Normalizes multi-channel support data and strips header/footer noise.
    """
    channel = raw_ticket.get("channel", "web").lower()
    ticket_id = raw_ticket.get("id", raw_ticket.get("ticket_id", "UNKNOWN-ID"))
    
    # Extract raw content depending on structure variations
    subject = raw_ticket.get("subject", raw_ticket.get("title", "No Subject")).strip()
    body = raw_ticket.get("body", raw_ticket.get("content", raw_ticket.get("text", ""))).strip()
    
    # Key Design Control: Clean out greetings and signature rows (noise stripping)
    clean_body = body
    noise_patterns = [
        r"^(hi|hello|hey|dear support team|greetings|good morning|good afternoon)[,\.\s]*" ,
        r"(thanks|thank you|regards|best regards|sincerely|cheers)[\s\S]*$"
    ]
    
    for pattern in noise_patterns:
        clean_body = re.sub(pattern, "", clean_body, flags=re.IGNORECASE).strip()
        
    return {
        "ticket_id": ticket_id,
        "channel": channel,
        "subject": subject,
        "body": body,
        "clean_subject": subject,
        "clean_body": clean_body if clean_body else body,
        "customer_group": raw_ticket.get("group", "Standard")
    }
