"""
Generate synthetic legacy Excel files for testing the Data Mapping AI.
No external dependencies beyond pandas + openpyxl.
"""
import os
import random
import pandas as pd

# ── Sample data pools ─────────────────────────────────────────────────
FIRST_NAMES = [
    "James", "Mary", "Robert", "Patricia", "John", "Jennifer", "Michael",
    "Linda", "David", "Elizabeth", "William", "Barbara", "Richard", "Susan",
    "Joseph", "Jessica", "Thomas", "Sarah", "Christopher", "Karen",
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
    "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez",
    "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin",
]

DOMAINS = ["gmail.com", "yahoo.com", "outlook.com", "company.org", "mail.co"]


def random_phone():
    """Generate a phone number with random formatting (always a string)."""
    digits = f"{random.randint(200,999)}{random.randint(1000000,9999999)}"
    fmt = random.choice([
        "{0}{1}{2}-{3}{4}{5}-{6}{7}{8}{9}",
        "({0}{1}{2}) {3}{4}{5}-{6}{7}{8}{9}",
        "{0}{1}{2}.{3}{4}{5}.{6}{7}{8}{9}",
        "{0}{1}{2} {3}{4}{5} {6}{7}{8}{9}",
    ])
    return fmt.format(*digits)


def random_date():
    """Generate a date string in a standard YYYY-MM-DD format."""
    y = random.randint(1960, 2005)
    m = random.randint(1, 12)
    d = random.randint(1, 28)
    return f"{y}-{m:02d}-{d:02d}"


def generate_legacy_data(n=100):
    """Generate a DataFrame that looks like a legacy CRM export."""
    rows = []
    for _ in range(n):
        first = random.choice(FIRST_NAMES)
        last = random.choice(LAST_NAMES)
        rows.append({
            "Cust_Nm": f"{first} {last}",
            "Telephone_No": random_phone(),
            "Email_Addr": f"{first.lower()}.{last.lower()}@{random.choice(DOMAINS)}",
            "DOB": random_date(),
            "Addr_Line1": f"{random.randint(1, 9999)} {random.choice(['Main', 'Oak', 'Pine', 'Elm', 'Cedar'])} St",
            "City": random.choice(["New York", "Los Angeles", "Chicago", "Houston", "Phoenix"]),
            "St": random.choice(["NY", "CA", "IL", "TX", "AZ"]),
            "Zip_Cd": f"{random.randint(10000, 99999)}",
        })
    return pd.DataFrame(rows)


if __name__ == "__main__":
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sample_data")
    os.makedirs(output_dir, exist_ok=True)

    df = generate_legacy_data(100)
    path = os.path.join(output_dir, "legacy_crm_export.xlsx")
    df.to_excel(path, index=False)
    print(f"[OK] Generated {len(df)} rows -> {path}")
    print(f"     Columns: {list(df.columns)}")
    print(df.head())
