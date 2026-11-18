"""Generate secure QR-code tickets, send via Email, and log tokens.

Usage:
    python generate_tickets.py            # full run
    python generate_tickets.py --no-email  # generate only, skip email

Environment Variables:
    GMAIL_ADDRESS        Your Gmail address used for SMTP sending.
    GMAIL_APP_PASSWORD   App Password generated in Google account.
    FROM_NAME            (Optional) Display name for From header.

Outputs:
    tickets/<guest_name_slug>.pdf
    valid_tokens.csv (appends rows)

Security:
    Token format: UUID|HMAC_SHA256(UUID, secret_key)
    Only token is encoded into QR (no PII).
    Secret key stored in .secret_key (created if missing).
"""
from __future__ import annotations
import argparse
import csv
import os
import sys
import uuid
import hmac
import hashlib
import json
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, Any

import qrcode
from fpdf import FPDF
try:
    # New positional enums for cell flow (FPDF >=2.5.2)
    from fpdf.enums import XPos, YPos
except ImportError:
    # Older FPDF version fallback – enums not available
    XPos = YPos = None  # type: ignore
from pypdf import PdfReader, PdfWriter

# Casablanca timezone (GMT+1)
CASABLANCA_TZ = timezone(timedelta(hours=1))
import smtplib, ssl
from email.message import EmailMessage
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

USE_FIRESTORE = os.getenv('FIRESTORE_ENABLED', '0') == '1'
if USE_FIRESTORE:
    try:
        from db.firestore_adapter import upsert_ticket as fs_upsert_ticket
    except Exception as e:
        print(f"[FIRESTORE] Adapter import failed: {e}")
        USE_FIRESTORE = False

BASE_DIR = Path(__file__).parent
TEMPLATES_JSON = BASE_DIR / 'config' / 'templates.json'
GUEST_LIST = BASE_DIR / 'guest_list.csv'
TOKENS_CSV = BASE_DIR / 'valid_tokens.csv'
TICKETS_DIR = BASE_DIR / 'tickets'
TICKET_TEMPLATES_DIR = BASE_DIR / 'ticket_templates'
SECRET_FILE = BASE_DIR / '.secret_key'
BG_IMAGE = BASE_DIR / 'templates' / 'ticket_bg.png'

# Flags controlled via CLI
SKIP_CSV = False

# (SMS sending removed; carrier gateway map deleted.)

def load_templates() -> Dict[str, Any]:
    with open(TEMPLATES_JSON, 'r', encoding='utf-8') as f:
        return json.load(f)

def _get_hmac_secret() -> bytes | None:
    """Resolve HMAC secret from env or file, avoiding writes on read-only FS.
    Priority: HMAC_SECRET_HEX, HMAC_SECRET_BASE64, HMAC_SECRET, then .secret_key file.
    """
    env_hex = os.getenv('HMAC_SECRET_HEX')
    if env_hex:
        try:
            return bytes.fromhex(env_hex.strip())
        except ValueError:
            print('[ERROR] Invalid HMAC_SECRET_HEX (not hex)')
    env_b64 = os.getenv('HMAC_SECRET_BASE64')
    if env_b64:
        try:
            import base64
            return base64.b64decode(env_b64.strip())
        except Exception:
            print('[ERROR] Invalid HMAC_SECRET_BASE64')
    env_raw = os.getenv('HMAC_SECRET')
    if env_raw:
        return env_raw.encode('utf-8')
    if SECRET_FILE.exists():
        try:
            return SECRET_FILE.read_bytes().strip()
        except Exception as e:
            print(f'[ERROR] Failed reading .secret_key: {e}')
    return None

def generate_token(secret_key: bytes) -> Dict[str, str]:
    token_uuid = uuid.uuid4().hex  # 32 hex chars
    signature = hmac.new(secret_key, token_uuid.encode('utf-8'), hashlib.sha256).hexdigest()
    full_token = f"{token_uuid}|{signature}"  # For QR
    return {
        'uuid': token_uuid,
        'signature': signature,
        'token': full_token
    }

def make_qr(token: str, out_path: Path) -> None:
    img = qrcode.make(token)
    img.save(out_path)

class TicketPDF(FPDF):
    def header(self):  # type: ignore
        pass  # Custom header drawn in render_pdf

    def footer(self):  # type: ignore
        pass  # Custom footer drawn in render_pdf


def render_pdf(guest_name: str, token_short: str, qr_img_path: Path, templates: Dict[str, Any], out_pdf: Path, ticket_type: str = 'externe', email: str = '', phone: str = '', school: str = '', cin: str = '', issued_at: str = '') -> None:
    pdf = TicketPDF('P', 'mm', 'A4')
    pdf.add_page()
    # Optional background image (full page if exists)
    if BG_IMAGE.exists():
        pdf.image(str(BG_IMAGE), x=0, y=0, w=210, h=297)

    # === HEADER SECTION (Dark band with white text) ===
    event_name = templates['event']['name']
    event_date = templates['event']['date']
    event_location = templates['event']['location']
    pdf_title = templates['pdf']['title'].format(event_name=event_name)
    pdf_subtitle = templates['pdf']['subtitle'].format(event_date=event_date, event_location=event_location)
    pdf_footer = templates['pdf']['footer']
    pdf.set_fill_color(17, 24, 39)  # Dark gray-blue
    pdf.rect(0, 0, 210, 50, 'F')
    pdf.set_xy(15, 12)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font('Helvetica', 'B', 32)
    pdf.cell(0, 12, pdf_title, align='C')
    pdf.set_xy(15, 28)
    pdf.set_font('Helvetica', '', 13)
    pdf.set_text_color(196, 181, 253)  # Light purple accent
    pdf.cell(0, 8, pdf_subtitle, align='C')

    temp_pdf = out_pdf.parent / f"temp_{out_pdf.name}"

    if ticket_type.lower() == 'exclusive':
        # Minimal info: first name, last name, email, type
        pdf.set_text_color(0, 0, 0)
        pdf.set_xy(20, 65)
        pdf.set_draw_color(200, 200, 200)
        pdf.set_line_width(0.5)
        pdf.rect(20, 65, 170, 48)
        pdf.set_font('Helvetica', '', 13)
        pdf.set_text_color(17, 24, 39)
        pdf.set_xy(25, 75)
        pdf.cell(0, 10, f"{guest_name}", align='C')
        pdf.set_font('Helvetica', '', 11)
        pdf.set_text_color(100, 100, 100)
        pdf.set_xy(25, 85)
        pdf.cell(0, 8, email, align='C')
        pdf.set_font('Helvetica', 'B', 16)
        pdf.set_text_color(220, 38, 38)  # Red accent for exclusive
        pdf.set_xy(25, 98)
        pdf.cell(0, 10, "EXCLUSIVE", align='C')
        issue_date_y = 113
        # QR, footer, and contact info as usual below
    else:
        # ...existing code for other ticket types...
        # Light border box (expanded for more info)
        pdf.set_draw_color(200, 200, 200)
        pdf.set_line_width(0.5)
        pdf.rect(20, 65, 170, 92)
        # Determine price based on ticket type
        if ticket_type.lower() in ('etudiant', 'ensamien'):
            price = '220 DHS'
        elif ticket_type.lower() == 'adherent':
            price = '190 DHS'
        elif ticket_type.lower() == 'organisateur-ade':
            price = None
        else:
            price = '250 DHS'
        # Guest information
        pdf.set_font('Helvetica', '', 11)
        pdf.set_text_color(100, 100, 100)
        pdf.set_xy(25, 70)
        pdf.cell(30, 6, 'Nom :', border=0, new_x=XPos.RIGHT, new_y=YPos.TOP if YPos else 0)
        pdf.set_font('Helvetica', 'B', 11)
        pdf.set_text_color(17, 24, 39)
        pdf.cell(0, 6, guest_name, new_x=XPos.LMARGIN, new_y=YPos.NEXT if YPos else 1)
        pdf.set_font('Helvetica', '', 11)
        pdf.set_text_color(100, 100, 100)
        pdf.set_xy(25, 77)
        pdf.cell(30, 6, 'Email :', border=0, new_x=XPos.RIGHT, new_y=YPos.TOP if YPos else 0)
        pdf.set_font('Helvetica', 'B', 11)
        pdf.set_text_color(17, 24, 39)
        pdf.cell(0, 6, email, new_x=XPos.LMARGIN, new_y=YPos.NEXT if YPos else 1)
        pdf.set_font('Helvetica', '', 11)
        pdf.set_text_color(100, 100, 100)
        pdf.set_xy(25, 84)
        pdf.cell(30, 6, 'Tel :', border=0, new_x=XPos.RIGHT, new_y=YPos.TOP if YPos else 0)
        pdf.set_font('Helvetica', 'B', 11)
        pdf.set_text_color(17, 24, 39)
        pdf.cell(0, 6, str(phone), new_x=XPos.LMARGIN, new_y=YPos.NEXT if YPos else 1)
        cin_display = cin if cin else 'N/A'
        pdf.set_font('Helvetica', '', 11)
        pdf.set_text_color(100, 100, 100)
        pdf.set_xy(25, 91)
        pdf.cell(30, 6, 'CIN :', border=0, new_x=XPos.RIGHT, new_y=YPos.TOP if YPos else 0)
        pdf.set_font('Helvetica', 'B', 11)
        pdf.set_text_color(17, 24, 39)
        pdf.cell(0, 6, str(cin_display), new_x=XPos.LMARGIN, new_y=YPos.NEXT if YPos else 1)
        school_display = school if school else 'N/A'
        pdf.set_font('Helvetica', '', 11)
        pdf.set_text_color(100, 100, 100)
        pdf.set_xy(25, 98)
        pdf.cell(30, 6, 'Provenance :', border=0, new_x=XPos.RIGHT, new_y=YPos.TOP if YPos else 0)
        pdf.set_font('Helvetica', 'B', 11)
        pdf.set_text_color(17, 24, 39)
        pdf.cell(0, 6, school_display, new_x=XPos.LMARGIN, new_y=YPos.NEXT if YPos else 1)
        if price:
            pdf.set_font('Helvetica', '', 11)
            pdf.set_text_color(100, 100, 100)
            pdf.set_xy(25, 105)
            pdf.cell(30, 6, 'Prix :', border=0, new_x=XPos.RIGHT, new_y=YPos.TOP if YPos else 0)
            pdf.set_font('Helvetica', 'B', 11)
            pdf.set_text_color(17, 24, 39)
            pdf.cell(0, 6, price, new_x=XPos.LMARGIN, new_y=YPos.NEXT if YPos else 1)
            issue_date_y = 112
        else:
            pdf.set_font('Helvetica', '', 11)
            pdf.set_text_color(100, 100, 100)
            pdf.set_xy(25, 105)
            pdf.cell(30, 6, 'Acces :', border=0, new_x=XPos.RIGHT, new_y=YPos.TOP if YPos else 0)
            pdf.set_font('Helvetica', 'B', 11)
            pdf.set_text_color(21, 128, 61)
            pdf.cell(0, 6, 'Gratuit - Organisateur', new_x=XPos.LMARGIN, new_y=YPos.NEXT if YPos else 1)
            issue_date_y = 112
        pdf.set_font('Helvetica', '', 11)
        pdf.set_text_color(100, 100, 100)
        pdf.set_xy(25, issue_date_y)
        pdf.cell(30, 6, 'Emis le :', border=0, new_x=XPos.RIGHT, new_y=YPos.TOP if YPos else 0)
        pdf.set_font('Helvetica', 'B', 11)
        pdf.set_text_color(17, 24, 39)
        if issued_at and 'T' in issued_at:
            from datetime import datetime
            dt = datetime.fromisoformat(issued_at.replace('Z', '+00:00'))
            formatted_date = dt.strftime('%d/%m/%Y %H:%M')
        else:
            formatted_date = issued_at or 'N/A'
        pdf.cell(0, 6, formatted_date, new_x=XPos.LMARGIN, new_y=YPos.NEXT if YPos else 1)
        pdf.set_font('Helvetica', '', 9)
        pdf.set_text_color(100, 100, 100)
        pdf.set_xy(25, 119)
        pdf.cell(0, 6, 'Organise par : ADE NOVA ENSAM Casablanca', new_x=XPos.LMARGIN, new_y=YPos.NEXT if YPos else 1)
        pdf.set_xy(25, 139)
        pdf.set_font('Helvetica', '', 10)
        pdf.set_text_color(80, 80, 80)
        pdf.cell(0, 6, 'Verification Token', new_x=XPos.LMARGIN, new_y=YPos.NEXT if YPos else 1)
        pdf.set_xy(25, 146)
        pdf.set_fill_color(238, 242, 255)
        pdf.set_text_color(55, 48, 163)
        pdf.set_font('Courier', 'B', 14)
        pdf.cell(60, 8, f' {token_short} ', border=1, fill=True)
        pdf.set_xy(95, 139)
        pdf.set_font('Helvetica', '', 10)
        pdf.set_text_color(80, 80, 80)
        pdf.cell(0, 6, 'Ticket Type', new_x=XPos.LMARGIN, new_y=YPos.NEXT if YPos else 1)
        pdf.set_xy(95, 146)
        ticket_type_display = ticket_type.upper()
        if ticket_type.lower() in ('etudiant', 'ensamien'):
            pdf.set_fill_color(255, 200, 7)
            pdf.set_text_color(117, 57, 111)
            ticket_type_display = 'ETUDIANT'
        elif ticket_type.lower() == 'adherent':
            pdf.set_fill_color(117, 57, 111)
            pdf.set_text_color(255, 200, 7)
            ticket_type_display = 'ADHERENT'
        elif ticket_type.lower() == 'organisateur-ade':
            pdf.set_fill_color(21, 128, 61)
            pdf.set_text_color(255, 255, 255)
            ticket_type_display = 'ORGANISATEUR'
        elif ticket_type.lower() == 'media':
            pdf.set_fill_color(59, 130, 246)  # blue-500
            pdf.set_text_color(255, 255, 255)
            ticket_type_display = 'MEDIA'
        else:
            pdf.set_fill_color(255, 200, 7)
            pdf.set_text_color(117, 57, 111)
            ticket_type_display = 'EXTERNE'
        pdf.set_font('Helvetica', 'B', 14)
        pdf.cell(60, 8, f' {ticket_type_display} ', border=1, fill=True)

    # === QR CODE SECTION (Centered with border) ===
    qr_x = 75
    qr_y = 170
    qr_size = 60
    pdf.set_fill_color(255, 255, 255)
    pdf.set_draw_color(17, 24, 39)
    pdf.set_line_width(1)
    pdf.rect(qr_x - 5, qr_y - 5, qr_size + 10, qr_size + 10, 'DF')
    pdf.image(str(qr_img_path), x=qr_x, y=qr_y, w=qr_size, h=qr_size)
    pdf.set_xy(10, qr_y + qr_size + 12)
    pdf.set_text_color(100, 100, 100)
    pdf.set_font('Helvetica', '', 11)
    pdf.cell(0, 6, 'SCAN AT ENTRANCE', align='C')
    pdf.set_y(250)
    pdf.set_font('Helvetica', 'I', 10)
    pdf.set_text_color(120, 120, 120)
    pdf.multi_cell(0, 5, pdf_footer, align='C')
    pdf.set_y(260)
    pdf.set_font('Helvetica', 'B', 9)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(0, 5, 'Pour toute information complementaire :', align='C', new_x=XPos.LMARGIN, new_y=YPos.NEXT if YPos else 1)
    pdf.set_font('Helvetica', '', 8)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 4, 'Contact : +212 6 60 29 69 98 | +212 6 96 44 23 32 | +212 6 45 76 03 81', align='C', new_x=XPos.LMARGIN, new_y=YPos.NEXT if YPos else 1)
    pdf.set_font('Helvetica', '', 8)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 4, 'Email : ade@ensam-casa.ma | nova.ensamc@gmail.com', align='C')
    pdf.set_draw_color(196, 181, 253)
    pdf.set_line_width(2)
    pdf.line(20, 280, 190, 280)
    pdf.output(str(temp_pdf))
    template_path = TICKET_TEMPLATES_DIR / f"{ticket_type.lower()}.pdf"
    if template_path.exists():
        merge_pdfs_with_template(template_path, temp_pdf, out_pdf)
        temp_pdf.unlink()
    else:
        temp_pdf.rename(out_pdf)


def merge_pdfs_with_template(template_path: Path, content_path: Path, output_path: Path) -> None:
    """Merge template PDF (first page) with content PDF (second page)."""
    writer = PdfWriter()
    
    # Add template as first page
    template_reader = PdfReader(str(template_path))
    writer.add_page(template_reader.pages[0])
    
    # Add content as second page
    content_reader = PdfReader(str(content_path))
    writer.add_page(content_reader.pages[0])
    
    # Write merged PDF
    with open(output_path, 'wb') as output_file:
        writer.write(output_file)


def send_email(
    gmail_address: str,
    app_password: str,
    subject: str,
    body: str,
    to_email: str,
    attachments: Dict[str, bytes],
    body_html: str | None = None,
) -> None:
    msg = EmailMessage()
    from_name = os.getenv('FROM_NAME', 'Event Team')
    msg['From'] = f"{from_name} <{gmail_address}>"
    msg['To'] = to_email
    # (SMS removed: no Cc for SMS gateway)
    msg['Subject'] = subject
    # Set plain text as the base content
    msg.set_content(body)
    # Add HTML alternative if provided
    if body_html:
        msg.add_alternative(body_html, subtype='html')

    for filename, data in attachments.items():
        msg.add_attachment(data, maintype='application', subtype='pdf', filename=filename)

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as server:
        server.login(gmail_address, app_password)
        server.send_message(msg)


## SMS helper removed (carrier_to_gateway)


def check_duplicate_ticket(guest_name: str, email: str, phone: str) -> Dict[str, Any] | None:
    """Check if a ticket already exists for this guest by name, email, or phone.
    
    Returns:
        Dict with duplicate info if found, None otherwise.
    """
    if not TOKENS_CSV.exists() or TOKENS_CSV.stat().st_size == 0:
        return None
    
    # Normalize for comparison
    guest_name_lower = guest_name.lower().strip()
    email_lower = email.lower().strip()
    phone_digits = ''.join(ch for ch in str(phone) if ch.isdigit())
    
    with open(TOKENS_CSV, 'r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            existing_name = row.get('guest_name', '').lower().strip()
            existing_email = row.get('guest_email', '').lower().strip()
            existing_phone = ''.join(ch for ch in str(row.get('guest_phone', '')) if ch.isdigit())
            
            # Check name match
            if existing_name and existing_name == guest_name_lower:
                return {'reason': 'name', 'value': row.get('guest_name'), 'issued_at': row.get('issued_at')}
            
            # Check email match
            if existing_email and email_lower and existing_email == email_lower:
                return {'reason': 'email', 'value': email, 'issued_at': row.get('issued_at')}
            
            # Check phone match (10+ digits)
            if existing_phone and phone_digits and len(phone_digits) >= 10 and existing_phone == phone_digits:
                return {'reason': 'phone', 'value': phone, 'issued_at': row.get('issued_at')}
    
    return None


def append_token_row(data: Dict[str, str], guest_name: str, email: str, phone: str, ticket_type: str = 'externe', school: str = '', cin: str = '') -> None:
    if SKIP_CSV:
        return
    write_header = not TOKENS_CSV.exists() or TOKENS_CSV.stat().st_size == 0
    with open(TOKENS_CSV, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if write_header:
            writer.writerow(['token', 'uuid', 'signature', 'status', 'guest_name', 'guest_email', 'guest_phone', 'ticket_type', 'school', 'cin', 'issued_at', 'used_at', 'voided_at', 'void_reason'])
        writer.writerow([
            data['token'], data['uuid'], data['signature'], 'active',
            guest_name, email, phone, ticket_type, school, cin,
            datetime.now(CASABLANCA_TZ).isoformat(), '', '', ''
        ])


def save_ticket_firestore(token_parts: Dict[str, str], guest_name: str, email: str, phone: str, ticket_type: str, school: str, cin: str, issued_at: str) -> None:
    if not USE_FIRESTORE:
        return
    try:
        data = {
            'uuid': token_parts['uuid'],
            'token': token_parts['token'],
            'signature': token_parts['signature'],
            'status': 'active',
            'guest_name': guest_name,
            'guest_email': email,
            'guest_phone': phone,
            'ticket_type': ticket_type,
            'school': school,
            'cin': cin,
            'issued_at': issued_at,
            'used_at': '',
            'voided_at': '',
            'void_reason': '',
            'drink_claimed_at': ''
        }
        fs_upsert_ticket(data)  # type: ignore
        print(f"[FIRESTORE] Ticket saved for {guest_name} ({token_parts['uuid']})")
    except Exception as e:
        print(f"[FIRESTORE] Failed to save ticket: {e}")


def generate_for_guest(row: Dict[str, Any], templates: Dict[str, Any], secret_key: bytes, send_email_flag: bool, allow_empty_exclusive: bool = False) -> None:
    # Name can be provided either as a single 'name' or split 'first_name' + 'last_name'
    first_name = str(row.get('first_name', '')).strip()
    last_name = str(row.get('last_name', '')).strip()
    if first_name or last_name:
        guest_name = f"{first_name} {last_name}".strip()
    else:
        guest_name = str(row.get('name', '')).strip()
    email = row['email']
    phone = row.get('phone', '')
    school = row.get('school', '')
    cin = str(row.get('cin', '')).strip()
    # SMS removed; ignore carrier column if present
    ticket_type = row.get('ticket_type', 'externe').lower()  # Default to externe

    # Canonicalize legacy value 'ensamien' to new internal 'etudiant'
    if ticket_type == 'ensamien':
        ticket_type = 'etudiant'

    # Accept both 'etudiant' (new) and legacy alias 'ensamien' in CSV by mapping earlier.
    valid_types = ['etudiant', 'adherent', 'externe', 'organisateur-ade', 'exclusive', 'media']
    if ticket_type not in valid_types:
        print(f"[WARNING] Invalid ticket type '{ticket_type}' for {guest_name}, using 'externe'")
        ticket_type = 'externe'

    # For exclusive tickets: normally require first_name+last_name+email
    # but allow a special mode to create anonymous exclusive tickets when requested.
    if ticket_type == 'exclusive' and not allow_empty_exclusive:
        if not first_name or not last_name or not email:
            print(f"[ERROR] Exclusive ticket requires first_name, last_name, and email for {guest_name}")
            return

    # If anonymous exclusive is allowed and guest_name is empty, use a placeholder
    if ticket_type == 'exclusive' and allow_empty_exclusive and not guest_name:
        # Assign a unique placeholder name to avoid collisions across runs
        guest_name = f'Exclusive Guest {uuid.uuid4().hex[:8]}'

    # Check for duplicate ticket
    duplicate = check_duplicate_ticket(guest_name, email, phone)
    if duplicate:
        reason = duplicate['reason']
        value = duplicate['value']
        issued_at = duplicate.get('issued_at', 'unknown time')
        print(f"[SKIP] Duplicate detected for {guest_name} - already issued by {reason} ({value}) at {issued_at}")
        return

    token_parts = generate_token(secret_key)
    token_full = token_parts['token']
    token_short = token_parts['uuid'][:8]
    
    # Get current timestamp for issue date (Casablanca time)
    issued_at = datetime.now(CASABLANCA_TZ).isoformat()

    # QR image temporary path
    qr_path = TICKETS_DIR / f"{slugify(guest_name)}_qr.png"
    make_qr(token_full, qr_path)

    pdf_path = TICKETS_DIR / f"{slugify(guest_name)}.pdf"
    render_pdf(guest_name, token_short, qr_path, templates, pdf_path, ticket_type, email, phone, school, cin, issued_at)

    append_token_row(token_parts, guest_name, email, phone, ticket_type, school, cin)

    # Save to Firestore if enabled
    save_ticket_firestore(token_parts, guest_name, email, phone, ticket_type, school, cin, issued_at)

    if send_email_flag:
        gmail_address = os.getenv('GMAIL_ADDRESS')
        app_password = os.getenv('GMAIL_APP_PASSWORD')
        if not gmail_address or not app_password:
            print("[WARN] Missing GMAIL env vars; skipping email for", guest_name)
        else:
            def substitute(template_str: str, ctx: Dict[str, str]) -> str:
                # Manual placeholder replacement to avoid str.format KeyErrors from CSS braces
                out = template_str
                for k, v in ctx.items():
                    out = out.replace(f'{{{k}}}', v)
                return out
            ctx = {
                'name': guest_name,
                'event_name': templates['event']['name'],
                'event_date': templates['event']['date'],
                'event_location': templates['event']['location'],
                'organizer': templates['event'].get('organizer', 'Event Team'),
                'token_short': token_short,
                'email': email,
            }
            subject = substitute(templates['email']['subject'], ctx)
            body = substitute(templates['email']['body'], ctx)
            body_html = None
            if 'body_html' in templates['email'] and templates['email']['body_html']:
                body_html = substitute(templates['email']['body_html'], ctx)
            # SMS removed: no gateway resolution
            with open(pdf_path, 'rb') as pf:
                attachments = {pdf_path.name: pf.read()}
            try:
                send_email(gmail_address, app_password, subject, body, email, attachments, body_html)
                print(f"[OK] Sent email to {guest_name}")
            except Exception as e:
                print(f"[ERROR] Failed sending to {guest_name}: {e}")
    else:
        print(f"[SKIP] Email disabled; generated ticket for {guest_name}")

    # Cleanup QR temp
    if qr_path.exists():
        try:
            qr_path.unlink()
        except OSError:
            pass


def slugify(name: str) -> str:
    return ''.join(c.lower() if c.isalnum() else '-' for c in name).strip('-')


def main():
    parser = argparse.ArgumentParser(description='Generate secure QR-code tickets and deliver them.')
    parser.add_argument('--no-email', action='store_true', help='Do not send emails')
    parser.add_argument('--no-csv', action='store_true', help='Do not write/update valid_tokens.csv')
    parser.add_argument('--allow-empty-exclusive', action='store_true', help='Allow generating EXCLUSIVE tickets without name/email (creates anonymous exclusive tickets)')
    parser.add_argument('--exclusive-count', type=int, default=0, help='Generate N anonymous EXCLUSIVE tickets (bypasses CSV).')
    parser.add_argument('--csv', dest='csv_path', help='Path to input CSV (defaults to guest_list.csv)')
    parser.add_argument('--out-dir', dest='out_dir', help='Directory to write PDFs (defaults to ./tickets)')
    args = parser.parse_args()
    global GUEST_LIST, TOKENS_CSV, TICKETS_DIR, SKIP_CSV
    SKIP_CSV = bool(args.no_csv)
    if args.csv_path:
        GUEST_LIST = Path(args.csv_path)
        # write tokens alongside the CSV by default
        TOKENS_CSV = GUEST_LIST.parent / 'valid_tokens.csv'
    if args.out_dir:
        TICKETS_DIR = Path(args.out_dir)
    # Ensure output directory exists (necessary on serverless when using /tmp)
    try:
        TICKETS_DIR.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print(f'[ERROR] Could not create tickets directory {TICKETS_DIR}: {e}')
        sys.exit(1)

    templates = load_templates()
    secret_key = _get_hmac_secret()
    if not secret_key:
        print('[WARN] No HMAC secret found in env or .secret_key; generating ephemeral key (not suitable for production).')
        secret_key = uuid.uuid4().hex.encode('utf-8') + os.urandom(32)

    # If exclusive-count is provided, we allow generating anonymous exclusive tickets
    # without requiring the guest CSV to exist. In that mode we also disable email
    # delivery (no recipient addresses are available).
    send_email_flag = not args.no_email
    generated_count = 0
    start = time.time()

    if args.exclusive_count and args.exclusive_count > 0:
        # Ensure output dir exists already created above. Generate anonymous exclusive tickets.
        if send_email_flag:
            # Avoid attempting to send emails to empty addresses for anonymous tickets
            send_email_flag = False
        for i in range(args.exclusive_count):
            anon_row = {
                'first_name': '',
                'last_name': '',
                'name': f"Exclusive Guest {uuid.uuid4().hex[:8]}",
                'email': '',
                'phone': '',
                'school': '',
                'cin': '',
                'ticket_type': 'exclusive'
            }
            generate_for_guest(anon_row, templates, secret_key, send_email_flag, allow_empty_exclusive=True)
            generated_count += 1
    else:
        # Normal CSV-driven mode: ensure guest list exists and is valid
        if not GUEST_LIST.exists():
            print('Guest list missing:', GUEST_LIST)
            sys.exit(1)

        with open(GUEST_LIST, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            rows = list(reader)
            cols = set(reader.fieldnames or [])
            has_fullname = {'name', 'email'}.issubset(cols)
            has_split = {'first_name', 'last_name', 'email'}.issubset(cols)
            if not (has_fullname or has_split):
                print('CSV must include either name,email OR first_name,last_name,email columns.')
                sys.exit(1)

        for row in rows:
            generate_for_guest(row, templates, secret_key, send_email_flag, allow_empty_exclusive=args.allow_empty_exclusive)
            generated_count += 1

    elapsed = time.time() - start
    print(f"Done. Generated {generated_count} tickets in {elapsed:.2f}s")

if __name__ == '__main__':
    main()
