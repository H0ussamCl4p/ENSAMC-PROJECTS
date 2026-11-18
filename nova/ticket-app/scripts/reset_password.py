"""Reset a user's password.

Usage:
  python scripts/reset_password.py --email EMAIL --password NEW_PASSWORD

Notes:
- Requires FIRESTORE_ENABLED=1 and Firebase credentials configured (same as app).
- Hashes the password with Werkzeug and updates the Firestore users collection.
- If FIRESTORE is disabled, it will update local users.json instead.
"""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path

from werkzeug.security import generate_password_hash

BASE_DIR = Path(__file__).resolve().parents[1]
USERS_FILE = BASE_DIR / 'users.json'

USE_FIRESTORE = os.getenv('FIRESTORE_ENABLED', '0') == '1'


def update_local_users(email: str, password_hash: str) -> bool:
    if not USERS_FILE.exists():
        print('[local] users.json not found')
        return False
    data = json.loads(USERS_FILE.read_text(encoding='utf-8'))
    found = False
    for uname, udata in data.items():
        if udata.get('email', '').lower() == email.lower():
            udata['password_hash'] = password_hash
            found = True
            break
    if not found:
        print('[local] user not found in users.json')
        return False
    USERS_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')
    return True


def update_firestore_user(email: str, password_hash: str) -> bool:
    from db.firestore_adapter import update_user_password_by_email
    return update_user_password_by_email(email, password_hash)


def main():
    parser = argparse.ArgumentParser(description='Reset a user\'s password (admin tool).')
    parser.add_argument('--email', required=True, help='User\'s email')
    parser.add_argument('--password', required=True, help='New password')
    args = parser.parse_args()

    ph = generate_password_hash(args.password)

    if USE_FIRESTORE:
        ok = update_firestore_user(args.email, ph)
        if not ok:
            print('[firestore] user not found')
            raise SystemExit(1)
        print('[firestore] password updated successfully')
    else:
        ok = update_local_users(args.email, ph)
        if not ok:
            raise SystemExit(1)
        print('[local] password updated successfully')


if __name__ == '__main__':
    main()
