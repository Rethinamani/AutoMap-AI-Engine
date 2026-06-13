import os
import sys

# Ensure the project root is on sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from llm.vllm_client import call_llm
from rag.retriever import retrieve_similar
from mapping.rules_engine import apply_rules
from rag.vector_store import load_memory, save_memory


def parse_llm_output(text):
    """
    Parse the raw LLM text into a Python list of mapping dicts.
    Handles cases where the LLM wraps JSON inside markdown code fences.
    """
    text = text.strip()

    # Strip markdown code fences if present
    if text.startswith("```"):
        lines = text.split("\n")
        lines = [l for l in lines if not l.strip().startswith("```")]
        text = "\n".join(lines).strip()

    # Try to find a JSON array in the text
    start = text.find("[")
    end = text.rfind("]")
    if start != -1 and end != -1 and end > start:
        text = text[start : end + 1]

    try:
        result = json.loads(text)
        if isinstance(result, list):
            return result
        return []
    except (json.JSONDecodeError, ValueError):
        print(f"[Mapper] Could not parse LLM output as JSON:\n{text[:200]}")
        return []


def get_mapping(source_schema, target_schema):
    """
    Generate a schema mapping using: Memory → LLM → Rules pipeline.
    """

    # Step 1: Check memory for a previously saved mapping
    memory_mapping = retrieve_similar(source_schema)
    if memory_mapping:
        return memory_mapping

    # Step 2: Call the LLM for a fresh mapping
    llm_output = call_llm(source_schema, target_schema)
    mapping = parse_llm_output(llm_output)

    # Step 3: Apply deterministic rules as a guardrail
    mapping = apply_rules(source_schema, mapping)

    return mapping


def save_mapping(source_schema, mapping):
    """Persist a validated mapping to the learning memory."""
    memory = load_memory()
    memory.append({
        "source_schema": source_schema,
        "mapping": mapping,
    })
    save_memory(memory)
