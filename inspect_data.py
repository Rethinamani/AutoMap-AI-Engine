import pandas as pd
import os

# Set pandas options for better terminal display
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)

file_path = os.path.join("sample_data", "legacy_crm_export.xlsx")
if os.path.exists(file_path):
    df = pd.read_excel(file_path)
    print("=== legacy_crm_export.xlsx ===")
    print(f"Shape: {df.shape}")
    print("\nColumns & Types:")
    print(df.dtypes)
    print("\nFirst 5 rows:")
    print(df.head())
else:
    print("legacy_crm_export.xlsx not found.")

output_path = os.path.join("sample_data", "mapped_output.xlsx")
if os.path.exists(output_path):
    df_out = pd.read_excel(output_path)
    print("\n=== mapped_output.xlsx ===")
    print(f"Shape: {df_out.shape}")
    print("\nColumns & Types:")
    print(df_out.dtypes)
    print("\nFirst 5 rows:")
    print(df_out.head())
else:
    print("\nmapped_output.xlsx not found (has not been generated yet).")
