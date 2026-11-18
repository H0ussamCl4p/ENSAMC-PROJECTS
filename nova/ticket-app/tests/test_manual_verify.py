"""
Test de vérification manuelle de token
"""
import csv
import hmac
import hashlib
from pathlib import Path

SECRET_FILE = Path('.secret_key')
CSV_PATH = Path('valid_tokens.csv')

# Charger la clé secrète
with open(SECRET_FILE, 'rb') as f:
    secret_key = f.read().strip()

# Charger les tickets
with open(CSV_PATH, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    tickets = list(reader)

print("="*70)
print("TEST DE VÉRIFICATION MANUELLE")
print("="*70)

for ticket in tickets:
    full_token = ticket['token']
    uuid = ticket['uuid']
    signature = ticket['signature']
    
    print(f"\n📋 Ticket: {ticket['guest_name']}")
    print(f"   Token complet: {full_token}")
    print(f"   UUID extrait:  {uuid}")
    print(f"   Signature:     {signature}")
    
    # Vérifier le format du token
    if '|' in full_token:
        parts = full_token.split('|')
        token_uuid = parts[0]
        token_sig = parts[1]
        
        print(f"\n   Token split:")
        print(f"   - UUID du token:  {token_uuid}")
        print(f"   - Sig du token:   {token_sig}")
        
        # Comparer avec le CSV
        print(f"\n   Comparaison avec CSV:")
        print(f"   - UUID match: {token_uuid == uuid}")
        print(f"   - Sig match:  {token_sig == signature}")
        
        # Recalculer la signature
        recomputed = hmac.new(secret_key, uuid.encode('utf-8'), hashlib.sha256).hexdigest()
        print(f"\n   Vérification HMAC:")
        print(f"   - Signature CSV:       {signature}")
        print(f"   - Signature recalculée: {recomputed}")
        print(f"   - HMAC valide: {hmac.compare_digest(recomputed, signature)}")
        
        # Test avec la signature du token
        recomputed_token = hmac.new(secret_key, token_uuid.encode('utf-8'), hashlib.sha256).hexdigest()
        print(f"   - HMAC token valide: {hmac.compare_digest(recomputed_token, token_sig)}")
    
    print("-"*70)

print("\n✅ Test terminé")
