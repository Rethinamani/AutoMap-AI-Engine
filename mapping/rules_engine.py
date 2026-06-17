def apply_rules(source_schema, mapping):
    """
    Apply deterministic post-processing rules to the LLM-generated mapping.
    Since we only do direct column renaming (no transformations), the rules
    engine now focuses on validation and filling in missing expected_dtype.
    """
    if not isinstance(mapping, list):
        return mapping

    source_set = {s.lower() for s in source_schema}

    cleaned = []
    for m in mapping:
        if not isinstance(m, dict):
            continue

        src = m.get("source", "")
        tgt = m.get("target", "")
        if not src or not tgt:
            continue

        # Validate that the source column actually exists (case-insensitive check)
        if src.lower() not in source_set:
            print(f"[Rules] Skipping mapping: source column '{src}' not found in schema")
            continue

        # Ensure expected_dtype is present; infer from column name if missing
        if not m.get("expected_dtype"):
            src_lower = src.lower()
            if "date" in src_lower or "dob" in src_lower or "birth" in src_lower:
                m["expected_dtype"] = "date"
            elif "zip" in src_lower or "postal" in src_lower:
                m["expected_dtype"] = "string"
            else:
                m["expected_dtype"] = "string"

        cleaned.append(m)

    return cleaned
