import os, requests
from dotenv import load_dotenv

# Load variables from the .env file
load_dotenv()

print("--- Environment Variables Verification ---")
print("Loaded Model Target:", os.getenv("MODEL_NAME"))

# Test the connection endpoint with a live API call
try:
    response = requests.post(
        "https://openrouter.ai",
        headers={"Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}"},
        json={"model": os.environ["MODEL_NAME"],
              "messages": [{"role": "user", "content": "Reply with the word ready."}]},
        timeout=30,
    )
    print("Status Code:", response.status_code)
    print("Response JSON:", response.json())
except Exception as e:
    print("An error occurred during communication:", e)
