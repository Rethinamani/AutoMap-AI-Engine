def apply_rules(source_schema, mapping):
    """
    Apply deterministic post-processing rules to the LLM-generated mapping.
    This acts as a guardrail to fix common patterns the LLM may miss.
    """
    if not isinstance(mapping, list):
        return mapping

    for m in mapping:
        if not isinstance(m, dict):
            continue

        src = m.get("source", "")
        if not isinstance(src, str):
            continue

        src_lower = src.lower()

        # Rule 1: Full-name columns → split into first_name + last_name
        if "name" in src_lower and "first" not in src_lower and "last" not in src_lower:
            if isinstance(m.get("target"), str):
                m["target"] = ["first_name", "last_name"]
                m["transformation"] = "split"

        # Rule 2: Phone columns → strip non-digit characters
        if "phone" in src_lower or "tel" in src_lower or "mobile" in src_lower:
            m["transformation"] = "phone_normalize"

        # Rule 3: Date-like columns → standardise to datetime
        if "date" in src_lower or "dob" in src_lower or "birth" in src_lower:
            m["transformation"] = "date_format"

    return mapping
