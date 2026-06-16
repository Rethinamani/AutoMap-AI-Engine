import os

# --- Project Root ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# --- vLLM Configuration ---
VLLM_BASE_URL = os.environ.get("BASE_URL") or "http://localhost:8000/v1"
VLLM_URL = f"{VLLM_BASE_URL}/completions"
MODEL_NAME = os.environ.get("MODEL_NAME") or "Qwen/Qwn3-30B-A3B"
VLLM_API_KEY = os.environ.get("OPENAI_API_KEY") or os.environ.get("VLLM_API_KEY")

# --- Memory / RAG ---
MEMORY_FILE = os.path.join(BASE_DIR, "memory", "mappings.json")

