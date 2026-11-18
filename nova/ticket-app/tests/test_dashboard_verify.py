"""
Test complet de la vérification de token comme dans le dashboard
"""
import csv
import hmac
import hashlib
from pathlib import Path
from datetime import datetime, timezone, timedelta

SECRET_FILE = Path('.secret_key')
CSV_PATH = Path('valid_tokens.csv')
CASABLANCA_TZ = timezone(timedelta(hours=1))

def verify_token_signature(token: str):
    """Vérifie la signature HMAC d'un token"""
    if '|' not in token:
        return False, 'Bad token format'
    
    uuid_part, sig_part = token.split('|', 1)
    
    if not SECRET_FILE.exists():
        return False, 'Secret key missing'
    
    secret = SECRET_FILE.read_bytes().strip()
    recomputed = hmac.new(secret, uuid_part.encode('utf-8'), hashlib.sha256).hexdigest()
    
    if not hmac.compare_digest(recomputed, sig_part):
        return False, 'Signature mismatch - possible tampering'
    
    return True, ''

def mark_ticket_used(token: str):
    """Marque un ticket comme utilisé"""
    if '|' not in token:
        return False, 'Bad token format', None
    
    valid, error = verify_token_signature(token)
    if not valid:
        return False, error, None
    
    uuid_part, sig_part = token.split('|', 1)
    
    # Load tickets
    tickets = []
    with open(CSV_PATH, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        tickets = list(reader)
    
    hit_index = None
    
    for idx, ticket in enumerate(tickets):
        if ticket.get('uuid') == uuid_part and ticket.get('signature') == sig_part:
            hit_index = idx
            break
    
    if hit_index is None:
        return False, 'Token not found', None
    
    ticket = tickets[hit_index]
    status = ticket.get('status', 'active')
    
    if status == 'voided':
        return False, f"Voided: {ticket.get('void_reason', 'No reason')}", ticket
    
    if status == 'used':
        return False, f"Already used at {ticket.get('used_at', '')}", ticket
    
    # Mark as used
    tickets[hit_index]['status'] = 'used'
    tickets[hit_index]['used_at'] = datetime.now(CASABLANCA_TZ).isoformat()
    
    # Write back
    fieldnames = list(tickets[0].keys()) if tickets else ['token', 'uuid', 'signature', 'status', 'guest_name', 'guest_email', 'guest_phone', 'ticket_type', 'issued_at', 'used_at', 'voided_at', 'void_reason', 'drink_claimed_at']
    
    with open(CSV_PATH, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(tickets)
    
    return True, f"Welcome {ticket.get('guest_name', 'Guest')}!", ticket

# Test avec les tokens
print("="*70)
print("TEST DE VÉRIFICATION (simulation dashboard)")
print("="*70)

# Token de Karim (actif)
token = "f070846b4c13488ab188e457be6879a5|d9ea91197f602ea3f52c81d32aaaae178bb221e9bebd432f3faa3823c8b950af"

print(f"\n🎫 Test token de Karim Alaoui")
print(f"Token: {token[:50]}...")

success, message, ticket_data = mark_ticket_used(token)

print(f"\nRésultat:")
print(f"  Success: {success}")
print(f"  Message: {message}")

if ticket_data:
    print(f"\n  Données du ticket:")
    print(f"    - Nom: {ticket_data.get('guest_name')}")
    print(f"    - Email: {ticket_data.get('guest_email')}")
    print(f"    - Status: {ticket_data.get('status')}")
    print(f"    - Used at: {ticket_data.get('used_at')}")

print("\n" + "="*70)
