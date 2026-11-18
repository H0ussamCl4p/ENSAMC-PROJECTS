"""
Migration script: Update Firestore ticket_type from 'ensamien' to 'etudiant'.
Run with your Firestore credentials loaded (see .env).
"""
from google.cloud import firestore

client = firestore.Client()
collection = client.collection('tickets')

count = 0
updated = 0
for doc in collection.stream():
    data = doc.to_dict()
    count += 1
    if data.get('ticket_type', '').lower() == 'ensamien':
        doc.reference.update({'ticket_type': 'etudiant'})
        updated += 1
        print(f"Updated ticket {doc.id}: 'ensamien' -> 'etudiant'")

print(f"\nMigration complete. {updated} of {count} tickets updated.")