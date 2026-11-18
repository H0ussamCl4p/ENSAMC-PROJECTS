"""Vercel runtime bootstrap: load Firebase service account from env var.

On Vercel, set environment variable:
  FIREBASE_SERVICE_ACCOUNT = <paste entire JSON content of service-account.json>

This script writes it to /tmp/service-account.json at cold start.
"""
import os
import json
from pathlib import Path

# Check if running on Vercel or similar serverless platform
if 'VERCEL' in os.environ or 'FIREBASE_SERVICE_ACCOUNT' in os.environ:
    sa_json = os.getenv('FIREBASE_SERVICE_ACCOUNT')
    if sa_json:
        try:
            # Validate it's valid JSON
            json.loads(sa_json)
            # Write to /tmp (ephemeral but survives during function lifetime)
            tmp_path = Path('/tmp/service-account.json')
            tmp_path.write_text(sa_json, encoding='utf-8')
            # Set env var so firebase-admin finds it
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = str(tmp_path)
            print('[VERCEL] Loaded Firebase SA from FIREBASE_SERVICE_ACCOUNT env var')
        except Exception as e:
            print(f'[VERCEL] Failed to load Firebase SA: {e}')
    else:
        print('[VERCEL] FIREBASE_SERVICE_ACCOUNT not set; Firestore may fail')
