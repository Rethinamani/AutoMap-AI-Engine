import pandas as pd

def read_file(file):
    return pd.read_excel(file)

def save_file(df, filename="output.xlsx"):
    df.to_excel(filename, index=False)
    return filename
