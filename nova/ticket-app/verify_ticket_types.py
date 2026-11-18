"""
Verification script: List and count all ticket_type values in Firestore tickets.
Run with your Firestore credentials loaded (see .env or GOOGLE_APPLICATION_CREDENTIALS).
"""
from collections import Counter
from google.cloud import firestore

client = firestore.Client()
collection = client.collection('tickets')

counter = Counter()
for doc in collection.stream():
    data = doc.to_dict()
    ticket_type = data.get('ticket_type', '').lower()
    counter[ticket_type] += 1

print("\nTicket type summary:")
for ttype, count in counter.items():
    print(f"  {ttype or '(empty)'}: {count}")

print(f"\nTotal tickets: {sum(counter.values())}")
