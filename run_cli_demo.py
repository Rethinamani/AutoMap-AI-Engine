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
        default="first_name, last_name, phone, email, dob",
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
    print("\n🤖 Querying AI (Qwen/Qwn3-30B-A3B) for mapping...")
    mapping = get_mapping(source_schema, target_schema)

    if not mapping:
        print("\n⚠️  No mapping was generated. Is your vLLM server running on port 8000?")
        sys.exit(1)

    print("\n🔗 Generated Mapping Rules:")
    print(json.dumps(mapping, indent=4))

    # 4. Confirmation
    if not args.yes:
        confirm = input("\n✅ Do you want to apply these transformations and save the output? (Y/n): ").strip().lower()
        if confirm not in ("", "y", "yes"):
            print("❌ Operation cancelled.")
            sys.exit(0)

    # 5. Apply Transformation
    print("\n⚡ Applying transformations...")
    try:
        new_df = apply_transformations(df, mapping)
    except Exception as e:
        print(f"❌ Error applying transformations: {e}")
        sys.exit(1)

    # 6. Save File
    output_dir = os.path.dirname(args.output)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        
    save_file(new_df, args.output)
    print(f"💾 File successfully saved to: {args.output}")

    # 7. Print preview
    print("\n📊 Preview (First 5 Rows of Transformed Data):")
    print("-" * 60)
    print(new_df.head(5).to_string(index=False))
    print("-" * 60)

    # 8. Save mapping to memory
    save_mapping(source_schema, mapping)
    print("💾 Mapping saved to learning memory for future use.")
    print("\n🎉 Done!")

if __name__ == "__main__":
    main()
