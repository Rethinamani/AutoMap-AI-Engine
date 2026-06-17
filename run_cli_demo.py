#!/usr/bin/env python
import os
import sys
import argparse
import pandas as pd
import json

# Ensure project root is importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.file_handler import read_file, save_file
from utils.schema_extractor import extract_schema
from mapping.mapper import get_mapping, save_mapping
from transform.transformer import apply_transformations
from config import MODEL_NAME


def main():
    parser = argparse.ArgumentParser(description="🧠 Data Mapping & Migration AI - CLI Demo")
    parser.add_argument(
        "--file", 
        type=str, 
        default=os.path.join("sample_data", "legacy_crm_export.xlsx"),
        help="Path to the legacy Excel file to map"
    )
    parser.add_argument(
        "--target-schema", 
        type=str, 
        default="Customer_name, phone, email, dob, address, city, postal_code",
        help="Comma-separated target schema columns"
    )
    parser.add_argument(
        "--output", 
        type=str, 
        default=os.path.join("sample_data", "mapped_output.xlsx"),
        help="Path to save the transformed Excel file"
    )
    parser.add_argument(
        "--yes", 
        action="store_true", 
        help="Skip confirmation prompt and automatically apply mapping"
    )
    
    args = parser.parse_args()

    print("=" * 60)
    print("🧠 DATA MAPPING & MIGRATION AI - CLI DEMO")
    print("=" * 60)

    # 1. Check if the input file exists
    if not os.path.exists(args.file):
        print(f"❌ Input file not found: {args.file}")
        print("💡 Tip: Run 'python generate_sample_data.py' first to generate sample data.")
        sys.exit(1)

    print(f"📁 Reading legacy file: {args.file}...")
    try:
        df = read_file(args.file)
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        sys.exit(1)

    # 2. Extract schemas
    source_schema = extract_schema(df)
    target_schema = [x.strip() for x in args.target_schema.split(",")]

    print("\n📋 Source Schema columns detected:")
    print(f"   {source_schema}")
    print("\n🎯 Target Schema columns defined:")
    print(f"   {target_schema}")

    # 3. Generate Mapping via AI
    print(f"\n🤖 Querying AI ({MODEL_NAME}) for mapping...")
    mapping = get_mapping(source_schema, target_schema)

    if not mapping:
        print("\n⚠️  No mapping was generated. Is your vLLM server running on port 8000?")
        sys.exit(1)

    print("\n🔗 Generated Mapping Rules:")
    print(json.dumps(mapping, indent=4))

    # 4. Confirmation
    if not args.yes:
        confirm = input("\n✅ Do you want to apply these mappings and save the output? (Y/n): ").strip().lower()
        if confirm not in ("", "y", "yes"):
            print("❌ Operation cancelled.")
            sys.exit(0)

    # 5. Apply Mapping (direct rename, no transformations)
    print("\n⚡ Applying column mappings...")
    try:
        new_df, report = apply_transformations(df, mapping)
    except Exception as e:
        print(f"❌ Error applying mappings: {e}")
        sys.exit(1)

    # 6. Save File
    output_dir = os.path.dirname(args.output)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        
    save_file(new_df, args.output)
    print(f"💾 File successfully saved to: {args.output}")

    # 7. Print preview
    print("\n📊 Preview (First 5 Rows of Mapped Data):")
    print("-" * 60)
    print(new_df.head(5).to_string(index=False))
    print("-" * 60)

    # 8. Report: Rows omitted due to empty values
    if report["dropped_rows"] > 0:
        print(f"\n⚠️  {report['dropped_rows']} row(s) were omitted because they "
              f"contained empty/missing values.")
        if report["dropped_indices"]:
            # Show first 10 dropped row numbers (1-indexed for user readability)
            shown = [str(i + 1) for i in report["dropped_indices"][:10]]
            suffix = f" (and {report['dropped_rows'] - 10} more)" if report["dropped_rows"] > 10 else ""
            print(f"   Omitted row numbers: {', '.join(shown)}{suffix}")
    else:
        print("\n✅ All rows are complete — no rows were omitted.")

    # 9. Report: Datatype mismatch warnings
    if report["dtype_warnings"]:
        print("\n🔍 Data Quality Warnings:")
        for w in report["dtype_warnings"]:
            print(f"   ⚠️  {w}")
    else:
        print("✅ No datatype mismatches detected.")

    # 10. Save mapping to memory
    save_mapping(source_schema, mapping)
    print("\n💾 Mapping saved to learning memory for future use.")
    print("\n🎉 Done!")

if __name__ == "__main__":
    main()
