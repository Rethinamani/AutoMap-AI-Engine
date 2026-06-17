import os
import sys

# Ensure the project root is on sys.path so 'config', 'rag', etc. resolve
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
from config import VLLM_URL, MODEL_NAME, VLLM_API_KEY


def call_llm(source_schema, target_schema):
    """Send source/target schemas to the local vLLM server and return the raw text."""

    prompt = f"""### Instruction:
Map each source column to the best matching target column using direct renaming only.
Do NOT apply any transformations — just map source columns to their closest target columns.
Each source column should map to exactly one target column.
Also specify the "expected_dtype" for each source column: "string", "number", or "date".

Return ONLY a JSON array. Each element must have these keys:
- "source": the source column name (exact match)
- "target": the target column name (exact match)
- "expected_dtype": the expected data type of the source column ("string", "number", or "date")

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
