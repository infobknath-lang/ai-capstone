import os
import requests
from dotenv import load_dotenv

load_dotenv()

def generate_grounded_response(normalized_ticket: dict, retrieval_results: list) -> str:
    """
    FR-05 / PR-03 v1.3: Grounded Answer Generator with Inline Citations.
    Drafts responses strictly anchored to vector documentation text blocks.
    """
    api_key = os.getenv("OPENROUTER_API_KEY")
    model_name = os.getenv("MODEL_NAME", "meta-llama/llama-3.1-8b-instruct")
    
    # 1. Format the retrieved context segments into explicit template blocks
    context_blocks = []
    for doc in retrieval_results:
        doc_id = doc.metadata.get("doc_id", "UNKNOWN")
        title = doc.metadata.get("title", "Untitled Document")
        content = doc.page_content
        context_blocks.append(f"<document id=\"{doc_id}\" title=\"{title}\">\n{content}\n</document>")
        
    formatted_context = "\n\n".join(context_blocks)
    
    # 2. Establish Prompt PR-03 v1.3 Contract Criteria Rules
    system_prompt = (
        "You are the primary grounded response generator engine for CloudServe Solutions.\n"
        "Your sole task is to draft a helpful, professional technical response to the customer ticket.\n"
        "You must strictly adhere to the following <grounding_rules>:\n"
        "1. Rely ONLY on the information provided inside the <retrieved_documentation> tags.\n"
        "2. Every technical claim, instruction step, or fact you state must end with its exact inline citation matching the document ID format like [DOC-XXX].\n"
        "3. If the retrieved documentation does not contain enough concrete information to completely resolve the query, state exactly: 'unable to fully resolve from official docs'.\n"
        "4. NEVER make financial commitments, SLA promises, release dates, or mention security override steps."
    )
    
    user_content = (
        f"<retrieved_documentation>\n{formatted_context}\n</retrieved_documentation>\n\n"
        f"<customer_ticket>\n"
        f"SUBJECT: {normalized_ticket['clean_subject']}\n"
        f"BODY: {normalized_ticket['clean_body']}\n"
        f"</customer_ticket>"
    )
    
    fallback_text = "unable to fully resolve from official docs"
    
    try:
        response = requests.post(
            "https://openrouter.ai",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": model_name,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content}
                ],
                "temperature": 0.0,
                "max_tokens": 500
            },
            timeout=20
        )
        
        if response.status_code == 200:
            generated_text = response.json()["choices"]["message"]["content"].strip()
            return generated_text
            
    except Exception as e:
        print(f"Generation layer timed out or failed: {e}")
        
    return fallback_text
