import os
import requests
import time
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Read API key from environment
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

API_URL = os.getenv("OPENROUTER_API") or "https://openrouter.ai/api/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "Content-Type": "application/json"
}


def generate_mistral_response(prompt):
    clean_prompt = prompt
    if "CONTEXT:" in prompt:
        clean_prompt = prompt[prompt.find("CONTEXT:"):]

    payload = {
        "model": "nvidia/nemotron-3-super-120b-a12b:free",
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a telecom customer-support AI assistant.\n\n"
                    "STRICT RULES:\n"
                    "1. Answer ONLY using the provided context.\n"
                    "2. NEVER use outside knowledge.\n"
                    "3. If answer is not in context, say: \"I could not find this information in the telecom knowledge base.\"\n"
                    "4. ALWAYS cite sources in this format: [SOURCE: doc_id, section_id]\n"
                    "5. Keep answer concise and factual.\n"
                    "6. Do NOT invent policies, taxes, fees, or rules.\n"
                    "7. Do NOT output any internal reasoning, thoughts, rule explanations, or step-by-step thinking. Output ONLY the direct final answer."
                )
            },
            {
                "role": "user",
                "content": clean_prompt
            }
        ],
        "temperature": 0.2,
        "max_tokens": 1024
    }

    try:

        response = requests.post(
            API_URL,
            headers=headers,
            json=payload,
            timeout=180
        )

        print(f"\n[OPENROUTER STATUS] {response.status_code}")

        # RATE LIMIT HANDLING
        if response.status_code == 429:
            print("Rate limit reached. Sleeping 10 seconds...")
            time.sleep(10)

            response = requests.post(
                API_URL,
                headers=headers,
                json=payload,
                timeout=180
            )

        result = response.json()

        print(result)

        if "choices" in result:
            return result["choices"][0]["message"]["content"]

        return str(result)

    except Exception as e:
        return f"[OPENROUTER ERROR] {e}"