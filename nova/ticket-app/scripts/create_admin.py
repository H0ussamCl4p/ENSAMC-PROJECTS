"""Script to create or update admin user with hashed password.

Usage:
    python scripts/create_admin.py
"""
import json
from pathlib import Path
from werkzeug.security import generate_password_hash
import getpass

ROOT_DIR = Path(__file__).resolve().parents[1]
USERS_FILE = ROOT_DIR / 'users.json'


def load_users():
    if USERS_FILE.exists():
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def save_users(users):
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, indent=2, ensure_ascii=False)


def create_admin():
    print("=== Création d'un compte administrateur ===\n")
    
    username = input("Nom d'utilisateur (par défaut: admin): ").strip() or "admin"
    name = input("Nom complet (par défaut: Admin ADE NOVA): ").strip() or "Admin ADE NOVA"
    email = input("Email (par défaut: nova.ensamc@gmail.com): ").strip() or "nova.ensamc@gmail.com"
    
    while True:
        password = getpass.getpass("Mot de passe (min 8 caractères): ")
        if len(password) < 8:
            print("❌ Le mot de passe doit contenir au moins 8 caractères!")
            continue
        
        password_confirm = getpass.getpass("Confirmez le mot de passe: ")
        if password != password_confirm:
            print("❌ Les mots de passe ne correspondent pas!")
            continue
        
        break
    
    # Hash the password
    password_hash = generate_password_hash(password, method='scrypt')
    
    # Load existing users
    users = load_users()
    
    # Create/update user
    users[username] = {
        "email": email,
        "password_hash": password_hash,
        "name": name,
        "role": "admin",
        "2fa_enabled": True
    }
    
    # Save
    save_users(users)
    
    print(f"\n✅ Compte créé avec succès!")
    print(f"   Username: {username}")
    print(f"   Email: {email}")
    print(f"   2FA: Activé")
    print(f"\nVous pouvez maintenant vous connecter au dashboard.")


if __name__ == '__main__':
    create_admin()
