import os

# --- Project Root ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# --- Load .env file if it exists ---
env_path = os.path.join(BASE_DIR, ".env")
if os.path.exists(env_path):
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                parts = line.split("=", 1)
                if len(parts) == 2:
                    k, v = parts[0].strip(), parts[1].strip()
                    # Remove surrounding quotes if present
                    if v.startswith(('"', "'")) and v.endswith(v[0]):
                        v = v[1:-1]
                    os.environ[k] = v



# --- vLLM Configuration ---
VLLM_BASE_URL = os.environ.get("BASE_URL") or "http://localhost:8000/v1"
VLLM_URL = f"{VLLM_BASE_URL}/completions"
MODEL_NAME = os.environ.get("MODEL_NAME") or "Qwen/Qwn3-30B-A3B"
VLLM_API_KEY = os.environ.get("OPENAI_API_KEY") or os.environ.get("VLLM_API_KEY")

# --- Memory / RAG ---
MEMORY_FILE = os.path.join(BASE_DIR, "memory", "mappings.json")

