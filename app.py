import os
import sys
import tempfile

# ── Ensure project root is importable ──────────────────────────────────
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
from utils.file_handler import read_file, save_file
from utils.schema_extractor import extract_schema
from mapping.mapper import get_mapping, save_mapping
from transform.transformer import apply_transformations

# ── Page Config ────────────────────────────────────────────────────────
st.set_page_config(page_title="Data Mapping AI", page_icon="🧠", layout="wide")

st.title("🧠 Data Mapping & Migration AI")
st.caption("Upload a legacy Excel file, define your target schema, and let the AI handle the rest.")

# ── Sidebar Info ───────────────────────────────────────────────────────
with st.sidebar:
    st.header("ℹ️ How it works")
    st.markdown(
        """
        1. **Upload** your legacy Excel file.
        2. **Enter** the target column names (comma-separated).
        3. The AI will **auto-map** source → target columns.
        4. **Review** the mapping, then click **Apply**.
        5. **Download** the transformed file.
        """
    )

# ── File Upload ────────────────────────────────────────────────────────
uploaded_file = st.file_uploader("Upload Legacy Excel", type=["xlsx", "xls"])

target_schema_input = st.text_input(
    "Enter Target Schema (comma separated)",
    value="first_name, last_name, phone, email, dob",
)

# ── Main Logic ─────────────────────────────────────────────────────────
if uploaded_file and target_schema_input:

    df = read_file(uploaded_file)
    source_schema = extract_schema(df)
    target_schema = [x.strip() for x in target_schema_input.split(",")]

    st.write("### 📋 Source Schema")
    st.info(", ".join(source_schema))

    st.write("### 🎯 Target Schema")
    st.info(", ".join(target_schema))

    # ── Generate Mapping (cached in session_state) ─────────────────────
    if "mapping" not in st.session_state or st.session_state.get("_last_source") != source_schema:
        with st.spinner("🤖 Generating mapping via AI..."):
            st.session_state["mapping"] = get_mapping(source_schema, target_schema)
            st.session_state["_last_source"] = source_schema

    mapping = st.session_state["mapping"]

    st.write("### 🔗 Generated Mapping")
    if mapping:
        st.json(mapping)
    else:
        st.warning("No mapping was generated. Check that your vLLM server is running.")

    # ── Apply Transformation ───────────────────────────────────────────
    if mapping and st.button("✅ Apply Transformation"):
        with st.spinner("Applying transformations..."):
            new_df = apply_transformations(df, mapping)

            # Write to a temp file so we don't pollute the project folder
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
            file_path = save_file(new_df, tmp.name)

            st.success("✅ File generated successfully!")
            st.write("### 📊 Preview (first 10 rows)")
            st.dataframe(new_df.head(10))

            with open(file_path, "rb") as f:
                st.download_button(
                    "⬇️ Download Mapped File",
                    f,
                    file_name="mapped.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )

            save_mapping(source_schema, mapping)
            st.info("💾 Mapping saved to learning memory for future use.")
