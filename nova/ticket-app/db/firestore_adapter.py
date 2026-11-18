from __future__ import annotations


def delete_ticket_by_uuid(uuid: str) -> bool:
    """Delete a single ticket document from Firestore by uuid."""
    import traceback
    try:
        db = init_client()
        doc_ref = db.collection('tickets').document(uuid)
        if doc_ref.get().exists:
            doc_ref.delete()
            return True
        return False
    except Exception as e:
        error_details = traceback.format_exc()
        print(f"[ERROR] delete_ticket_by_uuid exception: {error_details}")
        return False

def delete_all_exclusive_tickets() -> int:
    """Delete all exclusive ticket documents from Firestore."""
    db = init_client()
    collection_ref = db.collection('tickets')
    deleted = 0
    batch = db.batch()
    ops = 0
    for doc in collection_ref.stream():
        data = doc.to_dict() or {}
        if data.get('ticket_type', '').lower() == 'exclusive':
            batch.delete(doc.reference)
            ops += 1
            deleted += 1
            if ops == 500:
                batch.commit()
                batch = db.batch()
                ops = 0
    if ops:
        batch.commit()
    return deleted
"""Firestore adapter providing persistence for tickets and users.

Environment Requirements:
    FIRESTORE_ENABLED=1 to activate Firestore usage in the app.
    GOOGLE_APPLICATION_CREDENTIALS=/path/to/serviceAccount.json (or use Application Default Credentials)

Collections:
    users (doc id = username)
    tickets (doc id = uuid) fields: signature, token, guest_name, guest_email, guest_phone,
                     ticket_type, status, issued_at, used_at, voided_at, void_reason, drink_claimed_at
    system (doc id = hmac_secret) optional storing the HMAC secret if desired.

All timestamps stored as RFC3339 strings for consistency with existing code.
"""
from typing import Optional, Dict, Any, List, Tuple
import os
import tempfile
from pathlib import Path
from datetime import datetime, timezone
import json

import firebase_admin
from firebase_admin import credentials, firestore

CASABLANCA_TZ = timezone.utc  # store as UTC; convert for display in app

_db = None


def init_client():
    global _db
    if _db is not None:
        return _db
    if not firebase_admin._apps:
        cred_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        sa_json = os.getenv('FIREBASE_SERVICE_ACCOUNT')
        # Prefer direct JSON in env var (sa_json) for serverless deployments like Vercel
        if sa_json:
            try:
                tmp_path = Path(tempfile.gettempdir()) / 'firebase_service_account.json'
                tmp_path.write_text(sa_json, encoding='utf-8')
                cred = credentials.Certificate(str(tmp_path))
                firebase_admin.initialize_app(cred)
            except Exception as e:
                print(f"[FIRESTORE] Failed to init from FIREBASE_SERVICE_ACCOUNT: {e}")
                # Fallback to file path or ADC
                if cred_path and os.path.exists(cred_path):
                    cred = credentials.Certificate(cred_path)
                    firebase_admin.initialize_app(cred)
                else:
                    firebase_admin.initialize_app()
        elif cred_path and os.path.exists(cred_path):
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
        else:
            # Application Default (Workload Identity / local gcloud auth)
            firebase_admin.initialize_app()
    _db = firestore.client()
    return _db


# ---------------- Users -----------------

def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    db = init_client()
    # naive scan; for scale create an email->username mapping doc
    users_ref = db.collection('users').stream()
    for doc in users_ref:
        data = doc.to_dict()
        if data.get('email', '').lower() == email.lower():
            data['username'] = doc.id
            return data
    return None


def update_user_password_by_email(email: str, password_hash: str) -> bool:
    """Update a user's password_hash by email.

    Returns True if updated, False if user not found.
    """
    db = init_client()
    users_ref = db.collection('users').stream()
    target_doc = None
    for doc in users_ref:
        data = doc.to_dict()
        if data.get('email', '').lower() == email.lower():
            target_doc = doc.reference
            break
    if not target_doc:
        return False
    target_doc.update({'password_hash': password_hash})
    return True


def list_users() -> List[Dict[str, Any]]:
    db = init_client()
    return [doc.to_dict() | {'username': doc.id} for doc in db.collection('users').stream()]


# ---------------- Tickets -----------------

def list_tickets() -> List[Dict[str, Any]]:
    db = init_client()
    docs = db.collection('tickets').stream()
    out: List[Dict[str, Any]] = []
    for d in docs:
        data = d.to_dict()
        # Ensure uuid field present
        data.setdefault('uuid', d.id)
        out.append(data)
    return out


def upsert_ticket(data: Dict[str, Any]) -> None:
        """Create or update a ticket document in Firestore.

        Expected fields:
            - uuid (str) document id
            - token, signature, guest_name, guest_email, guest_phone
            - ticket_type, status, issued_at, used_at, voided_at, void_reason
            - optional: school, cin, drink_claimed_at
        """
        db = init_client()
        uuid = data.get('uuid')
        if not uuid:
                raise ValueError('upsert_ticket requires data["uuid"]')
        doc_ref = db.collection('tickets').document(uuid)
        # never store None values: filter them out to keep docs tidy
        clean = {k: v for k, v in data.items() if v is not None}
        doc_ref.set(clean)


def get_ticket_by_uuid(uuid: str) -> Optional[Dict[str, Any]]:
    db = init_client()
    snap = db.collection('tickets').document(uuid).get()
    if snap.exists:
        data = snap.to_dict()
        data.setdefault('uuid', uuid)
        return data
    return None


def mark_ticket_used(uuid: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
    """Mark a ticket as used with atomic transaction."""
    db = init_client()
    doc_ref = db.collection('tickets').document(uuid)

    @firestore.transactional
    def update_in_transaction(transaction):
        snapshot = doc_ref.get(transaction=transaction)
        if not snapshot.exists:
            return False, 'Ticket not found', None
        
        data = snapshot.to_dict()
        status = data.get('status', 'active')
        
        if status == 'voided':
            return False, f"Voided: {data.get('void_reason', 'No reason')}", data
        if status == 'used':
            return False, f"Already used at {data.get('used_at', '')}", data
        
        # Update the ticket
        data['status'] = 'used'
        data['used_at'] = datetime.utcnow().isoformat()
        transaction.update(doc_ref, {
            'status': 'used',
            'used_at': data['used_at']
        })
        
        data.setdefault('uuid', uuid)
        return True, 'OK', data

    transaction = db.transaction()
    return update_in_transaction(transaction)


def claim_drink(uuid: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
    """Claim drink with atomic transaction."""
    db = init_client()
    doc_ref = db.collection('tickets').document(uuid)

    @firestore.transactional
    def update_in_transaction(transaction):
        snapshot = doc_ref.get(transaction=transaction)
        if not snapshot.exists:
            return False, 'Ticket not found', None
        
        data = snapshot.to_dict()
        
        if data.get('status') != 'used':
            return False, 'Guest has not checked in yet', data
        if data.get('drink_claimed_at'):
            return False, f"Already claimed at {data.get('drink_claimed_at')}", data
        
        # Update the ticket
        data['drink_claimed_at'] = datetime.utcnow().isoformat()
        transaction.update(doc_ref, {
            'drink_claimed_at': data['drink_claimed_at']
        })
        
        data.setdefault('uuid', uuid)
        return True, 'OK', data

    transaction = db.transaction()
    return update_in_transaction(transaction)


def void_ticket(uuid: str, reason: str) -> Tuple[bool, str]:
    """Void a ticket with atomic transaction."""
    db = init_client()
    doc_ref = db.collection('tickets').document(uuid)

    @firestore.transactional
    def update_in_transaction(transaction):
        snapshot = doc_ref.get(transaction=transaction)
        if not snapshot.exists:
            return False, 'Ticket not found'
        
        data = snapshot.to_dict()
        if data.get('status') == 'voided':
            return False, 'Already voided'
        
        # Update the ticket
        now_iso = datetime.utcnow().isoformat()
        transaction.update(doc_ref, {
            'status': 'voided',
            'voided_at': now_iso,
            'void_reason': reason
        })
        
        return True, 'OK'

    transaction = db.transaction()
    return update_in_transaction(transaction)


# ---------------- Statistics -----------------

def compute_statistics() -> Dict[str, Any]:
    tickets = list_tickets()
    total = len(tickets)
    active = sum(1 for t in tickets if t.get('status') == 'active')
    used = sum(1 for t in tickets if t.get('status') == 'used')
    voided = sum(1 for t in tickets if t.get('status') == 'voided')
    drinks_claimed = sum(1 for t in tickets if t.get('drink_claimed_at'))
    def count_type(ty: str) -> int:
        if ty == 'etudiant':  # aggregate legacy 'ensamien'
            return sum(1 for t in tickets if t.get('ticket_type', '').lower() in ('etudiant', 'ensamien'))
        return sum(1 for t in tickets if t.get('ticket_type', '').lower() == ty)
    etudiant = count_type('etudiant')
    adherent = count_type('adherent')
    externe = count_type('externe')
    organisateur = count_type('organisateur-ade')
    exclusive = count_type('exclusive')
    media = count_type('media')
    checkin_rate = (used / total * 100) if total else 0
    drink_rate = (drinks_claimed / used * 100) if used else 0
    return {
        'total': total,
        'active': active,
        'checked_in': used,
        'voided': voided,
        'checkin_rate': round(checkin_rate, 1),
        'drinks_claimed': drinks_claimed,
        'drink_rate': round(drink_rate, 1),
        'etudiant': etudiant,
        'adherent': adherent,
        'externe': externe,
        'organisateur': organisateur,
        'exclusive': exclusive,
        'media': media,
    }


def delete_all_tickets() -> int:
    """Delete ALL ticket documents from Firestore.

    Returns number of deleted documents.
    Uses batch writes of 500 for efficiency and to respect Firestore limits.
    """
    db = init_client()
    collection_ref = db.collection('tickets')
    deleted = 0
    # Firestore doesn't have a built-in mass delete; iterate and batch.
    batch = db.batch()
    ops = 0
    for doc in collection_ref.stream():
        batch.delete(doc.reference)
        ops += 1
        deleted += 1
        if ops == 500:  # commit batch
            batch.commit()
            batch = db.batch()
            ops = 0
    if ops:
        batch.commit()
    return deleted

def bulk_void_tickets(filter_mode: str, reason: str) -> int:
    """Void tickets in bulk according to filter_mode.

    filter_mode: 'all' (active only), 'pending' (active), 'used' (used only).
    Returns number of tickets updated.
    """
    db = init_client()
    collection_ref = db.collection('tickets')
    # stream all tickets (for scale, convert to queries by status)
    to_void = []
    for doc in collection_ref.stream():
        data = doc.to_dict() or {}
        status = data.get('status', 'active')
        if filter_mode in ('all', 'pending') and status == 'active':
            to_void.append(doc.reference)
        elif filter_mode == 'used' and status == 'used':
            to_void.append(doc.reference)
    if not to_void:
        return 0
    batch = db.batch()
    count = 0
    now_iso = datetime.utcnow().isoformat()
    for ref in to_void:
        batch.update(ref, {
            'status': 'voided',
            'voided_at': now_iso,
            'void_reason': reason or 'Bulk cancellation'
        })
        count += 1
        if count % 500 == 0:
            batch.commit()
            batch = db.batch()
    # commit remaining
    batch.commit()
    return count


# ---------------- Drink Distribution Config -----------------

def get_drink_config() -> Dict[str, Any]:
    """Load drink distribution configuration from Firestore."""
    db = init_client()
    doc_ref = db.collection('system').document('drink_config')
    doc = doc_ref.get()
    if doc.exists:
        return doc.to_dict()
    # Default config
    return {'enabled': False, 'started_at': None, 'stopped_at': None}


def set_drink_config(config: Dict[str, Any]) -> None:
    """Save drink distribution configuration to Firestore."""
    db = init_client()
    doc_ref = db.collection('system').document('drink_config')
    doc_ref.set(config)


__all__ = [
    'get_user_by_email', 'update_user_password_by_email',
    'list_users', 'list_tickets', 'upsert_ticket', 'get_ticket_by_uuid',
    'mark_ticket_used', 'claim_drink', 'void_ticket', 'compute_statistics', 'delete_all_tickets', 'bulk_void_tickets',
    'get_drink_config', 'set_drink_config'
]
