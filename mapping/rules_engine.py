def apply_rules(source_schema, mapping):
    """
    Apply deterministic post-processing rules to the LLM-generated mapping.
    This acts as a guardrail to fix common patterns the LLM may miss.
    """
    if not isinstance(mapping, list):
        return mapping

    # ── Collect all target columns already assigned, to detect conflicts ──
    # Build a set of targets that each source *should* map to based on rules
    # so we can correct the LLM when it maps a phone column to "first_name", etc.

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
        #         Also fix the target if the LLM incorrectly mapped it
        if "phone" in src_lower or "tel" in src_lower or "mobile" in src_lower:
            m["transformation"] = "phone_normalize"
            # Guard: if LLM mapped a phone column to a name target, fix it
            tgt = m.get("target", "")
            if isinstance(tgt, str) and tgt in ("first_name", "last_name", "email", "dob"):
                m["target"] = "phone"

        # Rule 3: Date-like columns → standardise to datetime
        #         Also fix the target if the LLM incorrectly mapped it
        if "date" in src_lower or "dob" in src_lower or "birth" in src_lower:
            m["transformation"] = "date_format"
            tgt = m.get("target", "")
            if isinstance(tgt, str) and tgt in ("first_name", "last_name", "phone", "email"):
                m["target"] = "dob"

        # Rule 4: Email columns → ensure correct target
        if "email" in src_lower or "e_mail" in src_lower or "mail" in src_lower:
            tgt = m.get("target", "")
            if isinstance(tgt, str) and tgt in ("first_name", "last_name", "phone", "dob"):
                m["target"] = "email"

    return mapping
