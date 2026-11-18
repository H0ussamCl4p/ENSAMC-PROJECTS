"""Verify and claim drinks for ticket holders.

Usage:
    python scripts/verify_drink.py
"""
from __future__ import annotations
import csv
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path
import hmac
import hashlib

ROOT_DIR = Path(__file__).resolve().parents[1]
TOKENS_CSV = ROOT_DIR / 'valid_tokens.csv'
SECRET_FILE = ROOT_DIR / '.secret_key'
DRINK_CONFIG = ROOT_DIR / 'drink_distribution_config.json'

# Casablanca timezone (GMT+1)
CASABLANCA_TZ = timezone(timedelta(hours=1))


def load_drink_config() -> dict:
    """Load drink distribution configuration"""
    if not DRINK_CONFIG.exists():
        return {'enabled': False, 'started_at': None, 'stopped_at': None}
    
    with open(DRINK_CONFIG, 'r', encoding='utf-8') as f:
        return json.load(f)


def format_timestamp(iso_timestamp: str) -> str:
    """Convert ISO timestamp to readable format"""
    if not iso_timestamp:
        return 'Unknown'
    
    try:
        dt = datetime.fromisoformat(iso_timestamp.replace('Z', '+00:00'))
        return dt.strftime('%b %d, %Y at %I:%M %p')
    except (ValueError, AttributeError):
        return iso_timestamp


def verify_hmac(uuid: str, signature: str, secret_key: bytes) -> bool:
    """Verify HMAC signature"""
    computed = hmac.new(secret_key, uuid.encode('utf-8'), hashlib.sha256).hexdigest()
    return hmac.compare_digest(computed, signature)


def claim_drink(token: str) -> bool:
    """Claim drink for a token"""
    
    # Check if drink distribution is enabled
    config = load_drink_config()
    if not config.get('enabled', False):
        print('\n❌ Drink distribution is not currently enabled.')
        print('Please ask the event organizer to enable it from the admin dashboard.')
        return False
    
    # Load secret key
    if not SECRET_FILE.exists():
        print('Error: Secret key file not found')
        return False
    
    with open(SECRET_FILE, 'rb') as f:
        secret_key = f.read()
    
    # Parse token
    parts = token.strip().split('|')
    if len(parts) != 2:
        print('Invalid token format')
        return False
    
    uuid, signature = parts
    
    # Verify HMAC
    if not verify_hmac(uuid, signature, secret_key):
        print('❌ Invalid token signature')
        return False
    
    # Read all tickets
    if not TOKENS_CSV.exists():
        print('Error: Tokens database not found')
        return False
    
    with open(TOKENS_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fieldnames = reader.fieldnames or []
    
    # Find matching ticket
    hit_index = -1
    for i, row in enumerate(rows):
        if row['uuid'] == uuid and row['signature'] == signature:
            hit_index = i
            break
    
    if hit_index == -1:
        print('❌ Token not found in database')
        return False
    
    ticket = rows[hit_index]
    status = ticket.get('status', '').lower()
    
    # Check if voided
    if status == 'voided':
        print('❌ Ticket has been cancelled')
        void_reason = ticket.get('void_reason', 'No reason provided')
        print(f'Reason: {void_reason}')
        return False
    
    # Check if ticket was used (guest checked in)
    if status != 'used':
        print('❌ Guest has not checked in yet')
        print('Please scan the ticket at the entrance first')
        return False
    
    # Check if drink already claimed
    drink_claimed_at = ticket.get('drink_claimed_at', '')
    if drink_claimed_at:
        print('❌ Drink already claimed for this ticket')
        print(f'Guest: {ticket.get("guest_name", "Unknown")}')
        print(f'Claimed at: {format_timestamp(drink_claimed_at)}')
        return False
    
    # Display ticket info
    print('\n' + '='*50)
    print('DRINK CLAIM')
    print('='*50)
    print(f'Guest: {ticket.get("guest_name", "Unknown")}')
    print(f'Email: {ticket.get("guest_email", "N/A")}')
    print(f'Type: {ticket.get("ticket_type", "externe").upper()}')
    print(f'Checked in: {format_timestamp(ticket.get("used_at", ""))}')
    print('='*50)
    
    confirm = input('\nGive drink to this guest? (yes/no): ').strip().lower()
    
    if confirm != 'yes':
        print('Cancelled.')
        return False
    
    # Mark drink as claimed
    rows[hit_index]['drink_claimed_at'] = datetime.now(CASABLANCA_TZ).isoformat()
    
    # Ensure drink_claimed_at column exists
    if 'drink_claimed_at' not in fieldnames:
        fieldnames = list(fieldnames) + ['drink_claimed_at']
    
    # Write back
    with open(TOKENS_CSV, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    
    print('\n✅ Drink claimed successfully!')
    print(f'Time: {format_timestamp(rows[hit_index]["drink_claimed_at"])})')
    return True


def main():
    """Main verification loop"""
    print('\n' + '='*50)
    print('DRINK DISTRIBUTION VERIFICATION')
    print('='*50)
    
    # Check if distribution is enabled
    config = load_drink_config()
    if config.get('enabled', False):
        print('✓ Drink distribution is ENABLED')
        if config.get('started_at'):
            print(f'  Started: {format_timestamp(config["started_at"])})')
    else:
        print('⚠ Drink distribution is DISABLED')
        print('  Ask admin to enable it from dashboard')
    
    print('='*50)
    print('\nScan QR code or paste token (Ctrl+C to exit)')
    print('Format: <uuid>|<hmac>')
    
    while True:
        try:
            print('\n> ', end='', flush=True)
            token = input().strip()
            
            if not token:
                continue
            
            claim_drink(token)
            
        except KeyboardInterrupt:
            print('\n\nExiting...')
            break
        except Exception as e:
            print(f'\nError: {e}')


if __name__ == '__main__':
    main()
