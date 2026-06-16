import os
import sys

# Ensure the project root is on sys.path so 'config', 'rag', etc. resolve
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
from config import VLLM_URL, MODEL_NAME, VLLM_API_KEY


def call_llm(source_schema, target_schema):
    """Send source/target schemas to the local vLLM server and return the raw text."""

    prompt = f"""### Instruction:
Map each source column to the best matching target column.
Return a JSON array where each element has "source", "target", and "transformation" keys.
Valid transformations: "direct", "split", "merge", "date_format", "phone_normalize".

### Input:
{{"source_schema": {source_schema}, "target_schema": {target_schema}}}

### Output:
"""

    headers = {}
    if VLLM_API_KEY:
        headers["Authorization"] = f"Bearer {VLLM_API_KEY}"

    try:
        response = requests.post(
            VLLM_URL,
            headers=headers,
            json={
                "model": MODEL_NAME,
                "prompt": prompt,
                "max_tokens": 512,
                "temperature": 0.1,
            },
            timeout=60,
        )
        response.raise_for_status()
        text = response.json()["choices"][0]["text"]
        return text.strip()
    except requests.ConnectionError:
        print("[vLLM] Connection refused — is the vLLM server running?")
        return "[]"
    except Exception as e:
        print(f"[vLLM] Error calling LLM: {e}")
        return "[]"

