import os
import sys

# Ensure the project root is on sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rag.vector_store import load_memory


def retrieve_similar(source_schema):
    """
    Look up previously saved mappings whose source schema overlaps
    with the current source schema.  Returns the best-match mapping
    or None if nothing relevant is found.
    """
    memory = load_memory()
    best_match = None
    best_overlap = 0

    for m in memory:
        saved_schema = set(m.get("source_schema", []))
        overlap = len(set(source_schema).intersection(saved_schema))
        if overlap > best_overlap:
            best_overlap = overlap
            best_match = m.get("mapping")

    # Only return a match if at least half the source columns overlap
    if best_match and best_overlap >= len(source_schema) * 0.5:
        return best_match

    return None
