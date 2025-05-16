import httpx
import os

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://example.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "your-anon-or-service-key")

table = "inference_results"
data = {
    "job_id": "test123",
    "input_text": "hello",
    "parameters": "{}",
    "model_name": "distilgpt2",
    "result": "world"
}

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

url = f"{SUPABASE_URL}/rest/v1/{table}"

response = httpx.post(url, json=data, headers=headers)
print(response.status_code, response.text) 