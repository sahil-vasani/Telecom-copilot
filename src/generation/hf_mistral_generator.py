import os
import requests
import time
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Read API key from environment
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

API_URL = "https://openrouter.ai/api/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "Content-Type": "application/json"
}


def generate_mistral_response(prompt):

    payload = {
        # "model": "openai/gpt-3.5-turbo",
        "model": "mistralai/ministral-3b-2512",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.2,
        "max_tokens": 256
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