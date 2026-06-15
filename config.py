import os

# --- Project Root ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# --- vLLM Configuration ---
VLLM_BASE_URL = "http://localhost:8000/v1"
VLLM_URL = f"{VLLM_BASE_URL}/completions"
MODEL_NAME = "Qwen/Qwn3-30B-A3B"

# --- Memory / RAG ---
MEMORY_FILE = os.path.join(BASE_DIR, "memory", "mappings.json")
