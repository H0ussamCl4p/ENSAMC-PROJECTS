"""
Script de test simple pour la distribution de boissons
"""
import sys
sys.path.insert(0, '.')

from verify_drink import claim_drink

# Tokens des invités check-in
tokens = {
    'Fatima': '5ea7c68b2102468c95131fbca45aa0e3|f493e50e5d7e6e19d2dd95c902b221cabcf5bcbbcf1a99b83c3a15e0422a7b71',
    'Karim': 'f070846b4c13488ab188e457be6879a5|d9ea91197f602ea3f52c81d32aaaae178bb221e9bebd432f3faa3823c8b950af'
}

print("\n" + "="*70)
print("🥤 TEST DE DISTRIBUTION DE BOISSONS")
print("="*70)

print("\n1️⃣  Test avec Fatima Zahrae (déjà check-in)")
print("-"*70)
result = claim_drink(tokens['Fatima'])
print(f"\nRésultat: {result}")

print("\n" + "="*70)

print("\n2️⃣  Test avec Karim Alaoui (déjà check-in)")
print("-"*70)
result = claim_drink(tokens['Karim'])
print(f"\nRésultat: {result}")

print("\n" + "="*70)
print("✅ Tests terminés - Vérifiez le CSV pour voir les timestamps")
print("="*70 + "\n")
