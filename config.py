import os

# --- Project Root ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# --- vLLM Configuration ---
VLLM_URL = "http://localhost:8000/v1/completions"
MODEL_NAME = "final-model"

# --- Memory / RAG ---
MEMORY_FILE = os.path.join(BASE_DIR, "memory", "mappings.json")
