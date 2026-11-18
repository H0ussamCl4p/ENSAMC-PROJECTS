"""
Script de test pour la distribution de boissons
"""
import csv
import hmac
import hashlib
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path

# Configuration
SECRET_FILE = Path(".secret_key")
CSV_PATH = Path("valid_tokens.csv")
DRINK_CONFIG_PATH = Path("drink_distribution_config.json")
CASABLANCA_TZ = timezone(timedelta(hours=1))

def load_secret_key() -> bytes:
    """Charge la clé secrète depuis le fichier"""
    if not SECRET_FILE.exists():
        raise SystemExit('Secret key missing. Run generate_tickets.py once to create .secret_key')
    with open(SECRET_FILE, 'rb') as f:
        return f.read()

def verify_signature(uuid: str, signature: str, secret_key: bytes) -> bool:
    """Vérifie la signature HMAC du token"""
    expected = hmac.new(
        secret_key,
        uuid.encode(),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)

def load_drink_config():
    """Charge la configuration de distribution"""
    if not DRINK_CONFIG_PATH.exists():
        return {"enabled": False}
    with open(DRINK_CONFIG_PATH, 'r') as f:
        return json.load(f)

def claim_drink(token: str, secret_key: bytes):
    """Teste la réclamation d'une boisson"""
    print(f"\n{'='*60}")
    print(f"TEST: Réclamation de boisson pour token: {token[:20]}...")
    print(f"{'='*60}\n")
    
    # Vérifier que la distribution est activée
    config = load_drink_config()
    if not config.get("enabled"):
        print("❌ ERREUR: La distribution de boissons n'est pas activée")
        return False
    
    print("✓ Distribution de boissons activée")
    
    # Parse le token
    try:
        uuid, signature = token.split('|')
    except ValueError:
        print("❌ ERREUR: Format de token invalide")
        return False
    
    print(f"✓ Token parsé: UUID={uuid[:16]}...")
    
    # Vérifier la signature
    if not verify_signature(uuid, signature, secret_key):
        print("❌ ERREUR: Signature invalide")
        return False
    
    print("✓ Signature valide")
    
    # Lire le CSV
    rows = []
    found = False
    with open(CSV_PATH, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['uuid'] == uuid:
                found = True
                print(f"\n✓ Ticket trouvé:")
                print(f"  - Nom: {row['guest_name']}")
                print(f"  - Email: {row['guest_email']}")
                print(f"  - Type: {row['ticket_type']}")
                print(f"  - Status: {row['status']}")
                print(f"  - Check-in: {row['used_at'] or 'Non'}")
                print(f"  - Boisson réclamée: {row['drink_claimed_at'] or 'Non'}")
                
                # Vérifier le statut
                if row['status'] != 'used':
                    print(f"\n❌ ERREUR: Le ticket n'a pas été check-in à l'entrée")
                    print(f"   Status actuel: {row['status']}")
                    return False
                
                print("\n✓ Ticket check-in confirmé")
                
                # Vérifier si déjà réclamé
                if row['drink_claimed_at']:
                    print(f"\n❌ ERREUR: Boisson déjà réclamée!")
                    print(f"   Réclamée le: {row['drink_claimed_at']}")
                    return False
                
                print("✓ Première réclamation")
                
                # Marquer comme réclamé
                row['drink_claimed_at'] = datetime.now(CASABLANCA_TZ).isoformat()
                print(f"\n✅ SUCCÈS: Boisson accordée à {row['guest_name']}")
                print(f"   Timestamp: {row['drink_claimed_at']}")
            
            rows.append(row)
    
    if not found:
        print("❌ ERREUR: Token non trouvé dans la base de données")
        return False
    
    # Écrire le CSV mis à jour
    with open(CSV_PATH, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['token', 'uuid', 'signature', 'status', 'guest_name', 'guest_email', 
                     'guest_phone', 'ticket_type', 'issued_at', 'used_at', 'voided_at', 
                     'void_reason', 'drink_claimed_at']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    
    print("\n✓ Base de données mise à jour")
    return True

if __name__ == "__main__":
    # Token de Bob Example (déjà check-in)
    test_token = "2099d47461b747d685b4f61d5c65966d|280a4d87d4a3255e9514f6840d1ec59cadb107cc5d385797bb3693739901186b"
    
    print("\n" + "="*60)
    print("SCÉNARIO DE TEST: Distribution de boissons")
    print("="*60)
    
    # Charger la clé secrète
    secret_key = load_secret_key()
    
    success = claim_drink(test_token, secret_key)
    
    print("\n" + "="*60)
    if success:
        print("✅ TEST RÉUSSI: Le système fonctionne correctement!")
    else:
        print("❌ TEST ÉCHOUÉ: Vérifiez les erreurs ci-dessus")
    print("="*60 + "\n")
