import pandas as pd


def apply_transformations(df, mapping):
    """
    Apply the mapping to the source DataFrame using direct column renaming.
    No transformations are applied — columns are simply renamed.

    Returns:
        (new_df, report)  where report is a dict with:
            - "dropped_rows": number of rows omitted due to empty values
            - "dropped_indices": list of original row indices that were dropped
            - "dtype_warnings": list of datatype mismatch warning strings
    """
    report = {
        "dropped_rows": 0,
        "dropped_indices": [],
        "dtype_warnings": [],
    }

    if not isinstance(mapping, list) or len(mapping) == 0:
        return pd.DataFrame(), report

    new_df = pd.DataFrame()

    # ── Step 1: Direct column rename ──────────────────────────────────
    for m in mapping:
        if not isinstance(m, dict):
            continue

        src = m.get("source")
        tgt = m.get("target")

        if src is None or tgt is None:
            continue

        if src not in df.columns:
            print(f"[Transform] Column not found in source data: '{src}'")
            continue

        # Direct copy (rename)
        new_df[tgt] = df[src]

    if new_df.empty:
        return new_df, report

    # ── Step 2: Detect datatype mismatches ────────────────────────────
    report["dtype_warnings"] = _detect_dtype_mismatches(df, mapping)

    # ── Step 3: Drop rows with any empty / missing value ──────────────
    before_count = len(new_df)

    # Treat empty strings and whitespace-only as missing
    new_df = new_df.replace(r"^\s*$", pd.NA, regex=True)

    # Identify rows with any null / empty value
    empty_mask = new_df.isna().any(axis=1)
    dropped_indices = new_df.index[empty_mask].tolist()

    new_df = new_df.dropna().reset_index(drop=True)
    dropped_count = before_count - len(new_df)

    report["dropped_rows"] = dropped_count
    report["dropped_indices"] = dropped_indices

    return new_df, report


def _detect_dtype_mismatches(df, mapping):
    """
    Check source data for values that don't match the expected datatype
    specified in the mapping.  Returns a list of warning strings.
    """
    warnings = []

    for m in mapping:
        if not isinstance(m, dict):
            continue

        src = m.get("source")
        expected = (m.get("expected_dtype") or "").lower()
        if not src or not expected or src not in df.columns:
            continue

        col = df[src].dropna()
        if col.empty:
            continue

        if expected == "string":
            # Flag if values are purely numeric (int/float) when text is expected
            numeric_mask = col.apply(_is_numeric_value)
            bad_count = numeric_mask.sum()
            if bad_count > 0:
                examples = col[numeric_mask].head(3).tolist()
                warnings.append(
                    f"Column '{src}' is expected to be text/string but "
                    f"{bad_count} value(s) are numeric. Examples: {examples}"
                )

        elif expected == "number":
            # Flag if values are non-numeric strings when number is expected
            non_numeric_mask = col.apply(lambda x: not _is_numeric_value(x))
            bad_count = non_numeric_mask.sum()
            if bad_count > 0:
                examples = col[non_numeric_mask].head(3).tolist()
                warnings.append(
                    f"Column '{src}' is expected to be numeric but "
                    f"{bad_count} value(s) are non-numeric. Examples: {examples}"
                )

        elif expected == "date":
            # Flag if values cannot be parsed as dates
            parsed = pd.to_datetime(col, errors="coerce", infer_datetime_format=True)
            bad_mask = parsed.isna()
            bad_count = bad_mask.sum()
            if bad_count > 0:
                examples = col[bad_mask].head(3).tolist()
                warnings.append(
                    f"Column '{src}' is expected to be a date but "
                    f"{bad_count} value(s) could not be parsed. Examples: {examples}"
                )

    return warnings


def _is_numeric_value(x):
    """Check whether a single value is numeric (int or float)."""
    if isinstance(x, (int, float)):
        return True
    try:
        float(str(x))
        return True
    except (ValueError, TypeError):
        return False
