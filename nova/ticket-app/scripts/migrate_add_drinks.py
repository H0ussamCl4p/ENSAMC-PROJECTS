"""Migration script to add drink tracking column to valid_tokens.csv"""
import csv
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
TOKENS_CSV = ROOT_DIR / 'valid_tokens.csv'

def migrate():
    """Add drink_claimed_at column if it doesn't exist"""
    
    # Read all rows
    with open(TOKENS_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fieldnames = reader.fieldnames or []
    
    # Check if column already exists
    if 'drink_claimed_at' in fieldnames:
        print("✓ Column 'drink_claimed_at' already exists")
        return
    
    # Add new column
    new_fieldnames = list(fieldnames) + ['drink_claimed_at']
    
    # Add empty value for existing rows
    for row in rows:
        row['drink_claimed_at'] = ''
    
    # Write back
    with open(TOKENS_CSV, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=new_fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"✓ Added 'drink_claimed_at' column to {len(rows)} rows")

if __name__ == '__main__':
    migrate()
