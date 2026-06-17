import pandas as pd


def apply_transformations(df, mapping):
    """
    Apply the mapping transformations to the source DataFrame
    and return a new DataFrame with the target schema.
    """
    if not isinstance(mapping, list) or len(mapping) == 0:
        return pd.DataFrame()

    new_df = pd.DataFrame()

    for m in mapping:
        if not isinstance(m, dict):
            continue

        src = m.get("source")
        tgt = m.get("target")
        t = m.get("transformation", "direct")

        if src is None or tgt is None:
            continue

        try:
            if t == "split":
                # Split a single column (e.g. "Full Name") into two target columns
                targets = tgt if isinstance(tgt, list) else ["first_name", "last_name"]
                parts = df[src].astype(str).str.split(n=1, expand=True)

                # Assign first part (always present)
                new_df[targets[0]] = parts[0] if 0 in parts.columns else ""

                # Assign second part — use empty string Series (not scalar)
                # when the split didn't produce a second column
                second_target = targets[1] if len(targets) > 1 else "last_name"
                if 1 in parts.columns:
                    # Fill NaN for rows that had no space to split on
                    new_df[second_target] = parts[1].fillna("")
                else:
                    new_df[second_target] = ""

            elif t == "merge":
                # Merge two source columns into one target column
                if isinstance(src, list) and len(src) >= 2:
                    new_df[tgt] = df[src[0]].astype(str) + " " + df[src[1]].astype(str)
                else:
                    new_df[tgt] = df[src].astype(str)

            elif t == "date_format":
                new_df[tgt] = pd.to_datetime(df[src], errors="coerce")

            elif t == "phone_normalize":
                new_df[tgt] = df[src].astype(str).str.replace(r"\D", "", regex=True)

            elif t in ("direct", "none", None):
                new_df[tgt] = df[src]

            else:
                # Unknown transformation → fall back to direct copy
                new_df[tgt] = df[src]

        except KeyError as e:
            print(f"[Transform] Column not found: {e}")
        except Exception as e:
            print(f"[Transform] Error applying '{t}' on '{src}': {e}")

    return new_df
