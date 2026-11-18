"""Offline verification for QR ticket tokens.

Usage:
    python scripts/verify_ticket.py
    # Paste/scanned token like: <uuid>|<hmac>
"""
from __future__ import annotations
import csv
from datetime import datetime, timezone, timedelta
from pathlib import Path
import hmac
import hashlib

ROOT_DIR = Path(__file__).resolve().parents[1]
TOKENS_CSV = ROOT_DIR / 'valid_tokens.csv'
SECRET_FILE = ROOT_DIR / '.secret_key'

# Casablanca timezone (GMT+1)
CASABLANCA_TZ = timezone(timedelta(hours=1))


def format_timestamp(iso_timestamp: str) -> str:
    """Convert ISO timestamp to readable format."""
    if not iso_timestamp:
        return 'Unknown'
    
    try:
        dt = datetime.fromisoformat(iso_timestamp)
        return dt.strftime('%b %d, %Y at %I:%M %p')
    except (ValueError, AttributeError):
        return iso_timestamp


def ensure_secret_key() -> bytes:
    if not SECRET_FILE.exists():
        raise SystemExit('Secret key missing. Run generate_tickets.py once to create .secret_key')
    return SECRET_FILE.read_bytes().strip()


def verify_and_mark(token: str) -> bool:
    # Check if it's a short token (8 chars, no pipe)
    if '|' not in token and len(token.strip()) == 8:
        return verify_by_short_token(token.strip())
    
    if '|' not in token:
        print('Bad token format.')
        print('Expected: <uuid>|<hmac> OR short token (8 chars)')
        return False
    
    uuid_part, sig_part = token.split('|', 1)
    secret = ensure_secret_key()
    recomputed = hmac.new(secret, uuid_part.encode('utf-8'), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(recomputed, sig_part):
        print('Signature mismatch. Possible tampering.')
        return False

    rows = []
    hit_index = None
    with open(TOKENS_CSV, 'r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for idx, row in enumerate(reader):
            rows.append(row)
            if row['uuid'] == uuid_part and row['signature'] == sig_part:
                hit_index = idx

    if hit_index is None:
        print('Token not found.')
        return False

    # Check status (backwards compatible with old 'used' column)
    status = rows[hit_index].get('status', rows[hit_index].get('used', 'active'))
    
    if status == 'voided':
        print('Ticket has been voided/cancelled.')
        void_reason = rows[hit_index].get('void_reason', 'No reason provided')
        voided_at = rows[hit_index].get('voided_at', 'Unknown time')
        print(f'Reason: {void_reason}')
        print(f'Voided at: {format_timestamp(voided_at)}')
        return False
    
    if status in ('used', 'yes', 'true', '1'):
        print('Already used.')
        used_at = rows[hit_index].get('used_at', '')
        print(f'Used at: {format_timestamp(used_at)}')
        return False

    # Mark as used
    rows[hit_index]['status'] = 'used'
    rows[hit_index]['used_at'] = datetime.now(CASABLANCA_TZ).isoformat()

    # Determine fieldnames (backwards compatible)
    fieldnames = list(rows[0].keys()) if rows else ['token', 'uuid', 'signature', 'status', 'guest_name', 'guest_email', 'guest_phone', 'issued_at', 'used_at', 'voided_at', 'void_reason']
    
    # Ensure new columns exist
    for row in rows:
        row.setdefault('status', 'active')
        row.setdefault('voided_at', '')
        row.setdefault('void_reason', '')
        row.setdefault('guest_email', '')
        row.setdefault('guest_phone', '')

    # Rewrite CSV
    with open(TOKENS_CSV, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(rows)

    return True


def verify_by_short_token(short_token: str) -> bool:
    """Verify ticket using the 8-character short token displayed on PDF."""
    rows = []
    matches = []
    
    with open(TOKENS_CSV, 'r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for idx, row in enumerate(reader):
            rows.append(row)
            # Check if UUID starts with the short token
            if row.get('uuid', '').startswith(short_token.lower()):
                matches.append((idx, row))
    
    if not matches:
        print(f'No ticket found with short token: {short_token}')
        return False
    
    if len(matches) > 1:
        print(f'⚠️  Multiple tickets match short token {short_token}:')
        for idx, (_, row) in enumerate(matches, 1):
            guest = row.get('guest_name', 'Unknown')
            status = row.get('status', 'active')
            print(f'  {idx}. {guest} ({status})')
        print('\nPlease use the full QR token or contact support.')
        return False
    
    # Single match found
    hit_index, ticket = matches[0]
    guest_name = ticket.get('guest_name', 'Unknown')
    
    # Check status
    status = ticket.get('status', ticket.get('used', 'active'))
    
    if status == 'voided':
        print(f'Ticket for {guest_name} has been voided/cancelled.')
        void_reason = ticket.get('void_reason', 'No reason provided')
        voided_at = ticket.get('voided_at', 'Unknown time')
        print(f'Reason: {void_reason}')
        print(f'Voided at: {format_timestamp(voided_at)}')
        return False
    
    if status in ('used', 'yes', 'true', '1'):
        print(f'Ticket for {guest_name} already used.')
        used_at = ticket.get('used_at', '')
        print(f'Used at: {format_timestamp(used_at)}')
        return False
    
    # Confirm with staff before marking as used
    print(f'\n📋 Guest: {guest_name}')
    print(f'   Email: {ticket.get("guest_email", "N/A")}')
    print(f'   Short Token: {short_token}')
    confirm = input('\nConfirm entry? (yes/no): ').strip().lower()
    
    if confirm != 'yes':
        print('Entry cancelled.')
        return False
    
    # Mark as used
    rows[hit_index]['status'] = 'used'
    rows[hit_index]['used_at'] = datetime.now(CASABLANCA_TZ).isoformat()
    
    # Determine fieldnames
    fieldnames = list(rows[0].keys()) if rows else ['token', 'uuid', 'signature', 'status', 'guest_name', 'guest_email', 'guest_phone', 'issued_at', 'used_at', 'voided_at', 'void_reason']
    
    # Ensure new columns exist
    for row in rows:
        row.setdefault('status', 'active')
        row.setdefault('voided_at', '')
        row.setdefault('void_reason', '')
        row.setdefault('guest_email', '')
        row.setdefault('guest_phone', '')
    
    # Rewrite CSV
    with open(TOKENS_CSV, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(rows)
    
    return True


def main():
    print('Paste scanned QR token (format: <uuid>|<hmac>) OR short token (8 chars):')
    token = input('> ').strip()
    ok = verify_and_mark(token)
    if ok:
        print('✅ Valid entry')
    else:
        print('🚫 Invalid / already used')

if __name__ == '__main__':
    main()
