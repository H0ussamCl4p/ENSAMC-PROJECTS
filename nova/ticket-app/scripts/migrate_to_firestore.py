"""Migrate local CSV/JSON data into Firestore.

Usage (after setting GOOGLE_APPLICATION_CREDENTIALS or ADC):
    python scripts/migrate_to_firestore.py

Sets FIRESTORE_ENABLED=1 after migration optionally.
"""
from __future__ import annotations
import os
import csv
import json
from pathlib import Path

from firebase_admin import credentials, firestore, initialize_app

ROOT = Path(__file__).parents[1]
USERS_FILE = ROOT / 'users.json'
TOKENS_CSV = ROOT / 'valid_tokens.csv'
SECRET_FILE = ROOT / '.secret_key'


def init():
    cred_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    if cred_path and Path(cred_path).exists():
        initialize_app(credentials.Certificate(cred_path))
    else:
        initialize_app()  # ADC
    return firestore.client()


def migrate_users(db):
    if not USERS_FILE.exists():
        print('[users] skip (missing users.json)')
        return
    data = json.loads(USERS_FILE.read_text(encoding='utf-8'))
    batch = db.batch()
    for username, u in data.items():
        ref = db.collection('users').document(username)
        batch.set(ref, u)
    batch.commit()
    print(f'[users] migrated {len(data)} users')


def migrate_tickets(db):
    if not TOKENS_CSV.exists():
        print('[tickets] skip (missing valid_tokens.csv)')
        return
    with open(TOKENS_CSV, 'r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    batch = db.batch()
    for row in rows:
        uuid = row.get('uuid') or row.get('token', '').split('|')[0]
        ref = db.collection('tickets').document(uuid)
        batch.set(ref, row)
    batch.commit()
    print(f'[tickets] migrated {len(rows)} tickets')


def migrate_secret(db):
    if not SECRET_FILE.exists():
        print('[secret] skip (missing .secret_key)')
        return
    secret_bytes = SECRET_FILE.read_bytes()
    db.collection('system').document('hmac_secret').set({
        'hex': secret_bytes.hex(),
        'length': len(secret_bytes)
    })
    print('[secret] stored hmac_secret in Firestore')


def main():
    db = init()
    migrate_users(db)
    migrate_tickets(db)
    migrate_secret(db)
    print('Migration complete.')

if __name__ == '__main__':
    main()
