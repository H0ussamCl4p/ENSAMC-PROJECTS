
from __future__ import annotations
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session, send_file, abort
from db.firestore_adapter import delete_ticket_by_uuid

"""Local web dashboard for ticket verification and check-in management.

Run with:
    python dashboard.py
    
Then open: http://localhost:5000

Features:
    - Real-time check-in statistics
    - Guest list with status
    - Web-based QR scanner (camera access)
    - Search and manual verification
    - Void ticket interface
"""
import csv
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Any
import hmac
import hashlib

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session, send_file
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps
import json
import base64
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import secrets
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Timezone configuration (GMT+1 Casablanca)
CASABLANCA_TZ = timezone(timedelta(hours=1))

app = Flask(__name__, template_folder='templates_web', static_folder='static')
# Prefer a stable secret from env for persistent sessions (e.g., on Vercel)
_env_secret = os.getenv('FLASK_SECRET')
app.config['SECRET_KEY'] = _env_secret if _env_secret else os.urandom(24).hex()
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=12)  # Session expires after 12h

BASE_DIR = Path(__file__).parent
TOKENS_CSV = BASE_DIR / 'valid_tokens.csv'
SECRET_FILE = BASE_DIR / '.secret_key'
TEMPLATES_FILE = BASE_DIR / 'config' / 'templates.json'
DRINK_CONFIG = BASE_DIR / 'drink_distribution_config.json'
USERS_FILE = BASE_DIR / 'users.json'
USE_FIRESTORE = os.getenv('FIRESTORE_ENABLED', '0') == '1'

if USE_FIRESTORE:
    try:
        from db.firestore_adapter import (
            list_tickets as fs_list_tickets,
            mark_ticket_used as fs_mark_ticket_used,
            compute_statistics as fs_compute_statistics,
            claim_drink as fs_claim_drink,
            get_user_by_email as fs_get_user_by_email,
            delete_all_tickets as fs_delete_all_tickets,
            bulk_void_tickets as fs_bulk_void_tickets,
            get_drink_config as fs_get_drink_config,
            set_drink_config as fs_set_drink_config,
        )
    except Exception as e:
        print(f"[FIRESTORE] Failed to import adapter: {e}")
        USE_FIRESTORE = False

# 2FA codes storage (in production, use Redis or database)
twofa_codes = {}


def format_timestamp(iso_timestamp: str) -> str:
    """Convert ISO timestamp to readable format."""
    if not iso_timestamp:
        return 'N/A'
    try:
        dt = datetime.fromisoformat(iso_timestamp)
        return dt.strftime('%b %d, %Y at %I:%M %p')
    except (ValueError, AttributeError):
        return iso_timestamp


# ============================================================================
# AUTHENTICATION & SECURITY
# ============================================================================

def load_users() -> Dict[str, Any]:
    """Load users from users.json"""
    if not USERS_FILE.exists():
        return {}
    with open(USERS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def login_required(f):
    """Decorator to protect routes - requires authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_email' not in session:
            flash('Veuillez vous connecter pour accéder à cette page', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def api_login_required(f):
    """Decorator to protect API routes - returns JSON on auth failure"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_email' not in session:
            return jsonify({'success': False, 'message': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function


def send_2fa_code(email: str, code: str, name: str) -> bool:
    """Send 2FA code via email"""
    try:
        # Optional fallback: log code instead of sending, for testing
        allow_fallback = os.getenv('ALLOW_2FA_FALLBACK_LOG', '0') == '1' or os.getenv('EMAIL_DELIVERY_MODE', '').lower() == 'log'
        gmail_address = os.getenv('GMAIL_ADDRESS')
        app_password = os.getenv('GMAIL_APP_PASSWORD')
        from_name = os.getenv('FROM_NAME', 'ADE NOVA Dashboard')
        
        if not gmail_address or not app_password:
            msg = "[ERROR] Gmail credentials not configured"
            if allow_fallback:
                print(msg)
                print(f"[2FA][FALLBACK] Code for {email}: {code}")
                return True
            print(msg)
            return False
        
        msg = MIMEMultipart('alternative')
        msg['From'] = f"{from_name} <{gmail_address}>"
        msg['To'] = email
        msg['Subject'] = f"🔐 Code de vérification 2FA - {code}"
        
        # Plain text version
        text = f"""
Hello / Bonjour {name},

Your 2FA verification code is: {code}
Votre code de vérification 2FA est : {code}

This code expires in 10 minutes.
Ce code expire dans 10 minutes.

If you didn't request this code, please ignore this email.
Si vous n'avez pas demandé ce code, veuillez ignorer cet email.

---
ADE NOVA ENSAM Casablanca
Ticket Management System / Système de gestion de tickets
"""
        
        # HTML version with bilingual content
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            line-height: 1.6; 
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            padding: 20px;
        }}
        .email-wrapper {{ max-width: 600px; margin: 0 auto; }}
        .header {{ 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            color: white; 
            padding: 40px 30px; 
            text-align: center; 
            border-radius: 20px 20px 0 0; 
            box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
        }}
        .header h1 {{ 
            font-size: 32px; 
            margin-bottom: 10px; 
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }}
        .header p {{ 
            font-size: 16px; 
            opacity: 0.95; 
            margin-top: 8px;
        }}
        .content {{ 
            background: white; 
            padding: 40px 35px; 
            box-shadow: 0 0 40px rgba(0,0,0,0.08);
        }}
        .language-section {{ 
            margin-bottom: 35px; 
            padding-bottom: 30px; 
            border-bottom: 2px solid #f0f0f0;
        }}
        .language-section:last-of-type {{ 
            border-bottom: none; 
            margin-bottom: 0;
            padding-bottom: 0;
        }}
        .lang-badge {{ 
            display: inline-block;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 6px 16px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: bold;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 15px;
            box-shadow: 0 4px 10px rgba(102, 126, 234, 0.3);
        }}
        .greeting {{ 
            font-size: 18px; 
            color: #2d3748; 
            margin-bottom: 15px;
        }}
        .greeting strong {{ 
            color: #667eea; 
            font-weight: 600;
        }}
        .description {{ 
            color: #4a5568; 
            font-size: 15px; 
            margin-bottom: 20px;
        }}
        .code-box {{ 
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            border: none;
            border-radius: 15px; 
            padding: 30px; 
            text-align: center; 
            margin: 25px 0; 
            box-shadow: 0 10px 30px rgba(240, 147, 251, 0.4);
            transform: perspective(1000px) rotateX(2deg);
        }}
        .code-label {{ 
            color: white; 
            font-size: 14px; 
            text-transform: uppercase; 
            letter-spacing: 2px; 
            margin-bottom: 12px;
            font-weight: 600;
            opacity: 0.95;
        }}
        .code {{ 
            font-size: 48px; 
            font-weight: 900; 
            color: white; 
            letter-spacing: 12px; 
            font-family: 'Courier New', monospace;
            text-shadow: 3px 3px 6px rgba(0,0,0,0.2);
            display: block;
        }}
        .warning {{ 
            background: linear-gradient(135deg, #ffeaa7 0%, #fdcb6e 100%); 
            border-left: 5px solid #f39c12;
            border-radius: 10px;
            padding: 18px 20px; 
            margin: 25px 0;
            box-shadow: 0 5px 15px rgba(253, 203, 110, 0.3);
        }}
        .warning-icon {{ 
            font-size: 24px; 
            margin-right: 10px;
        }}
        .warning-text {{ 
            color: #c0392b; 
            font-weight: 600;
            font-size: 15px;
        }}
        .security-note {{ 
            color: #718096; 
            font-size: 14px; 
            margin-top: 20px;
            line-height: 1.8;
        }}
        .footer {{ 
            background: linear-gradient(135deg, #2d3748 0%, #1a202c 100%); 
            padding: 30px; 
            text-align: center; 
            color: #e2e8f0; 
            border-radius: 0 0 20px 20px;
            box-shadow: 0 -5px 20px rgba(0,0,0,0.1);
        }}
        .footer-logo {{ 
            font-size: 22px; 
            font-weight: bold; 
            margin-bottom: 12px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        .footer-text {{ 
            font-size: 13px; 
            opacity: 0.8;
            margin: 8px 0;
        }}
        .footer-note {{ 
            font-size: 11px; 
            opacity: 0.6; 
            margin-top: 15px;
            font-style: italic;
        }}
        .divider {{ 
            height: 3px; 
            background: linear-gradient(90deg, transparent, #667eea, transparent); 
            margin: 30px 0;
            border-radius: 2px;
        }}
    </style>
</head>
<body>
    <div class="email-wrapper">
        <div class="header">
            <h1>🔐 Security Code</h1>
            <p>Two-Factor Authentication / Authentification à deux facteurs</p>
        </div>
        
        <div class="content">
            <!-- English Section -->
            <div class="language-section">
                <span class="lang-badge">🇬🇧 English</span>
                <p class="greeting">Hello <strong>{name}</strong>,</p>
                <p class="description">Your one-time verification code to access the dashboard:</p>
            </div>
            
            <!-- Code Box -->
            <div class="code-box">
                <div class="code-label">Your Verification Code</div>
                <span class="code">{code}</span>
            </div>
            
            <!-- French Section -->
            <div class="language-section">
                <span class="lang-badge">🇫🇷 Français</span>
                <p class="greeting">Bonjour <strong>{name}</strong>,</p>
                <p class="description">Votre code de vérification à usage unique pour accéder au tableau de bord :</p>
            </div>
            
            <div class="divider"></div>
            
            <!-- Warning -->
            <div class="warning">
                <span class="warning-icon">⏱️</span>
                <span class="warning-text">Important: This code expires in 10 minutes / Ce code expire dans 10 minutes</span>
            </div>
            
            <!-- Security Note -->
            <p class="security-note">
                <strong>🛡️ Security Note / Note de sécurité:</strong><br>
                If you didn't request this code, please ignore this email and secure your account.<br>
                Si vous n'avez pas demandé ce code, veuillez ignorer cet email et sécuriser votre compte.
            </p>
        </div>
        
        <div class="footer">
            <div class="footer-logo">✨ ADE NOVA ENSAM Casablanca</div>
            <p class="footer-text">Secure Ticket Management System<br>Système de gestion de tickets sécurisé</p>
            <p class="footer-note">This email was sent automatically, please do not reply.<br>Cet email a été envoyé automatiquement, merci de ne pas y répondre.</p>
        </div>
    </div>
</body>
</html>
"""
        
        msg.attach(MIMEText(text, 'plain'))
        msg.attach(MIMEText(html, 'html'))
        
        import ssl
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as server:
            server.login(gmail_address, app_password)
            server.send_message(msg)
        
        print(f"[2FA] Code sent to {email}")
        return True
        
    except Exception as e:
        err = f"[ERROR] Failed to send 2FA code: {e}"
        if allow_fallback:
            print(err)
            print(f"[2FA][FALLBACK] Code for {email}: {code}")
            return True
        print(err)
        return False


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if 'user_email' in session:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        user_data = None
        username = None

        if USE_FIRESTORE:
            # Lookup user from Firestore by email
            try:
                fs_user = fs_get_user_by_email(email)  # type: ignore
                if fs_user:
                    user_data = fs_user
                    username = fs_user.get('username')
            except Exception as e:
                print(f"[FIRESTORE] get_user_by_email failed: {e}")
        else:
            users = load_users()
            for uname, udata in users.items():
                if udata.get('email', '').lower() == email:
                    user_data = udata
                    username = uname
                    break
        
        if not user_data:
            flash('Email ou mot de passe incorrect', 'error')
            return render_template('login.html')
        
        # Check password
        if not check_password_hash(user_data['password_hash'], password):
            flash('Email ou mot de passe incorrect', 'error')
            return render_template('login.html')
        
        # Check if 2FA is enabled
        if user_data.get('2fa_enabled', True):
            # Generate 2FA code
            code = ''.join([str(secrets.randbelow(10)) for _ in range(6)])
            
            # Store code with timestamp (expires in 10 minutes)
            twofa_codes[email] = {
                'code': code,
                'timestamp': datetime.now(CASABLANCA_TZ),
                'username': username,
                'user_data': user_data
            }
            
            # Send code via email
            if send_2fa_code(email, code, user_data.get('name', 'Admin')):
                session['pending_2fa'] = email
                flash(f'Un code de vérification a été envoyé à {email}', 'success')
                return redirect(url_for('verify_2fa'))
            else:
                flash('Erreur lors de l\'envoi du code 2FA. Veuillez réessayer.', 'error')
                return render_template('login.html')
        else:
            # 2FA disabled, direct login
            session['user_email'] = email
            session['user_name'] = user_data.get('name', 'Admin')
            session['user_role'] = user_data.get('role', 'admin')
            session.permanent = True
            flash(f'Bienvenue {user_data.get("name", "Admin")} !', 'success')
            return redirect(url_for('index'))
    
    return render_template('login.html')


@app.route('/verify-2fa', methods=['GET', 'POST'])
def verify_2fa():
    """Verify 2FA code page"""
    if 'pending_2fa' not in session:
        return redirect(url_for('login'))
    
    email = session['pending_2fa']
    
    if request.method == 'POST':
        code = request.form.get('code', '').strip()
        
        if email not in twofa_codes:
            flash('Code expiré. Veuillez vous reconnecter.', 'error')
            session.pop('pending_2fa', None)
            return redirect(url_for('login'))
        
        stored_data = twofa_codes[email]
        
        # Check if code expired (10 minutes)
        time_diff = (datetime.now(CASABLANCA_TZ) - stored_data['timestamp']).total_seconds()
        if time_diff > 600:  # 10 minutes
            flash('Code expiré. Veuillez vous reconnecter.', 'error')
            del twofa_codes[email]
            session.pop('pending_2fa', None)
            return redirect(url_for('login'))
        
        # Verify code
        if code == stored_data['code']:
            # Successful login
            user_data = stored_data['user_data']
            session['user_email'] = email
            session['user_name'] = user_data.get('name', 'Admin')
            session['user_role'] = user_data.get('role', 'admin')
            session.permanent = True
            session.pop('pending_2fa', None)
            
            # Clean up code
            del twofa_codes[email]
            
            flash(f'Bienvenue {user_data.get("name", "Admin")} !', 'success')
            return redirect(url_for('index'))
        else:
            flash('Code incorrect. Veuillez réessayer.', 'error')
    
    return render_template('verify_2fa.html', user_email=email)


@app.route('/resend-2fa', methods=['POST'])
def resend_2fa():
    """Resend 2FA code"""
    if 'pending_2fa' not in session:
        return redirect(url_for('login'))
    
    email = session['pending_2fa']
    
    if email in twofa_codes:
        stored_data = twofa_codes[email]
        user_data = stored_data['user_data']
        
        # Generate new code
        code = ''.join([str(secrets.randbelow(10)) for _ in range(6)])
        
        # Update stored code
        twofa_codes[email]['code'] = code
        twofa_codes[email]['timestamp'] = datetime.now(CASABLANCA_TZ)
        
        # Resend
        if send_2fa_code(email, code, user_data.get('name', 'Admin')):
            flash('Un nouveau code a été envoyé', 'success')
        else:
            flash('Erreur lors de l\'envoi du code', 'error')
    
    return redirect(url_for('verify_2fa'))


@app.route('/logout')
def logout():
    """Logout user"""
    user_name = session.get('user_name', 'Utilisateur')
    session.clear()
    flash(f'À bientôt {user_name} !', 'success')
    return redirect(url_for('login'))


# ============================================================================
# DASHBOARD ROUTES (Protected)

# Delete a ticket by uuid (route must be after app is defined)
@app.route('/delete-ticket/<uuid>', methods=['POST'])
@login_required
def delete_ticket(uuid):
    import traceback
    try:
        success = delete_ticket_by_uuid(uuid)
        if success:
            flash('Ticket deleted successfully.', 'success')
        else:
            flash('Ticket not found or could not be deleted.', 'danger')
        return redirect(url_for('guests'))
    except Exception as e:
        error_details = traceback.format_exc()
        print(f"[ERROR] delete_ticket exception: {error_details}")
        flash(f'Error deleting ticket: {str(e)}', 'danger')
        return redirect(url_for('guests'))
# ============================================================================


def load_all_tickets() -> List[Dict[str, str]]:
    """Load all tickets from CSV."""
    if USE_FIRESTORE:
        # Firestore adapter returns list[dict]
        return fs_list_tickets()  # type: ignore
    if not TOKENS_CSV.exists():
        return []
    tickets: List[Dict[str, str]] = []
    with open(TOKENS_CSV, 'r', newline='', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            tickets.append(row)
    return tickets


def load_drink_config() -> Dict[str, Any]:
    """Load drink distribution configuration."""
    if USE_FIRESTORE:
        try:
            return fs_get_drink_config()  # type: ignore
        except Exception as e:
            print(f"[FIRESTORE] Failed to load drink config: {e}")
            return {'enabled': False, 'started_at': None, 'stopped_at': None}
    
    if not DRINK_CONFIG.exists():
        return {'enabled': False, 'started_at': None, 'stopped_at': None}
    
    with open(DRINK_CONFIG, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_drink_config(config: Dict[str, Any]) -> None:
    """Save drink distribution configuration."""
    if USE_FIRESTORE:
        try:
            fs_set_drink_config(config)  # type: ignore
            return
        except Exception as e:
            print(f"[FIRESTORE] Failed to save drink config: {e}")
            raise
    
    with open(DRINK_CONFIG, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2)


def get_statistics() -> Dict[str, Any]:
    """Calculate check-in statistics."""
    if USE_FIRESTORE:
        return fs_compute_statistics()  # type: ignore
    tickets = load_all_tickets()
    total = len(tickets)
    active = sum(1 for t in tickets if t.get('status') == 'active')
    used = sum(1 for t in tickets if t.get('status') == 'used')
    voided = sum(1 for t in tickets if t.get('status') == 'voided')
    drinks_claimed = sum(1 for t in tickets if t.get('drink_claimed_at'))
    # Treat legacy 'ensamien' as 'etudiant'
    etudiant = sum(1 for t in tickets if t.get('ticket_type', 'externe').lower() in ('etudiant', 'ensamien'))
    adherent = sum(1 for t in tickets if t.get('ticket_type', 'externe').lower() == 'adherent')
    externe = sum(1 for t in tickets if t.get('ticket_type', 'externe').lower() == 'externe')
    organisateur = sum(1 for t in tickets if t.get('ticket_type', 'externe').lower() == 'organisateur-ade')
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
    }


def _get_hmac_secret() -> bytes | None:
    """Resolve HMAC secret from environment or local file.
    Priority:
      1) HMAC_SECRET_HEX (hex string)
      2) HMAC_SECRET_BASE64 (base64 string)
      3) HMAC_SECRET (raw string, utf-8)
      4) .secret_key file (bytes)
    Returns bytes or None if not found.
    """
    # Env: hex
    env_hex = os.getenv('HMAC_SECRET_HEX')
    if env_hex:
        try:
            return bytes.fromhex(env_hex.strip())
        except ValueError:
            print('[ERROR] Invalid HMAC_SECRET_HEX (not hex)')
    # Env: base64
    env_b64 = os.getenv('HMAC_SECRET_BASE64')
    if env_b64:
        try:
            return base64.b64decode(env_b64.strip())
        except Exception:
            print('[ERROR] Invalid HMAC_SECRET_BASE64')
    # Env: raw string
    env_raw = os.getenv('HMAC_SECRET')
    if env_raw:
        return env_raw.encode('utf-8')
    # File fallback
    if SECRET_FILE.exists():
        try:
            return SECRET_FILE.read_bytes().strip()
        except Exception as e:
            print(f'[ERROR] Failed reading .secret_key: {e}')
    return None


def verify_token_signature(token: str) -> tuple[bool, str]:
    """Verify token signature. Returns (valid, error_message)."""
    if '|' not in token:
        return False, 'Bad token format'

    uuid_part, sig_part = token.split('|', 1)

    secret = _get_hmac_secret()
    if not secret:
        return False, 'Secret key missing'

    recomputed = hmac.new(secret, uuid_part.encode('utf-8'), hashlib.sha256).hexdigest()

    if not hmac.compare_digest(recomputed, sig_part):
        return False, 'Signature mismatch - possible tampering'

    return True, ''


def mark_ticket_used(token: str) -> tuple[bool, str, Dict[str, str] | None]:
    """Mark a ticket as used. Returns (success, message, ticket_data).
    
    Supports both:
    - Full token: uuid|signature (from QR code)
    - Short token: 8-char prefix (manual entry from PDF)
    """
    try:
        # Check if it's a short token (8 chars, no pipe)
        if '|' not in token:
            if len(token) == 8:
                # Short token - need to look up the full token
                if USE_FIRESTORE:
                    tickets = fs_list_tickets()  # type: ignore
                else:
                    tickets = load_all_tickets()
                
                for ticket in tickets:
                    if ticket.get('uuid', '')[:8].lower() == token.lower():
                        # Found matching ticket - reconstruct full token
                        uuid_part = ticket.get('uuid')
                        sig_part = ticket.get('signature')
                        if uuid_part and sig_part:
                            token = f"{uuid_part}|{sig_part}"
                            break
                else:
                    return False, 'Short token not found', None
            else:
                return False, 'Bad token format (expected full token with | or 8-char short code)', None
        
        valid, error = verify_token_signature(token)
        if not valid:
            return False, error, None
        uuid_part, sig_part = token.split('|', 1)
        if USE_FIRESTORE:
            ok, msg, data = fs_mark_ticket_used(uuid_part)  # type: ignore
            if not ok:
                return False, msg, data
            # ensure signature matches
            if data and data.get('signature') != sig_part:
                return False, 'Signature mismatch in DB', data
            return True, f"Welcome {data.get('guest_name', 'Guest')}!", data
        tickets = load_all_tickets()
        hit_index = None
        for idx, ticket in enumerate(tickets):
            if ticket.get('uuid') == uuid_part and ticket.get('signature') == sig_part:
                hit_index = idx
                break
        if hit_index is None:
            return False, 'Token not found', None
        ticket = tickets[hit_index]
        status = ticket.get('status', 'active')
        if status == 'voided':
            return False, f"Voided: {ticket.get('void_reason', 'No reason')}", ticket
        if status == 'used':
            return False, f"Already used at {format_timestamp(ticket.get('used_at', ''))}", ticket
        tickets[hit_index]['status'] = 'used'
        tickets[hit_index]['used_at'] = datetime.now(CASABLANCA_TZ).isoformat()
        fieldnames = list(tickets[0].keys()) if tickets else ['token', 'uuid', 'signature', 'status', 'guest_name', 'guest_email', 'guest_phone', 'ticket_type', 'issued_at', 'used_at', 'voided_at', 'void_reason', 'drink_claimed_at']
        
        with open(TOKENS_CSV, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
            writer.writeheader()
            writer.writerows(tickets)
        
        return True, f"Welcome {ticket.get('guest_name', 'Guest')}!", ticket
    
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"[ERROR] mark_ticket_used exception:\n{error_details}")
        return False, f'Error: {str(e)}', None


@app.route('/')
@login_required
def index():
    """Dashboard home page with statistics."""
    stats = get_statistics()
    return render_template('dashboard_home.html', stats=stats)


@app.route('/guests')
@login_required
def guests():
    """Guest list page."""
    tickets = load_all_tickets()
    
    # Add formatted timestamps
    for ticket in tickets:
        ticket['issued_formatted'] = format_timestamp(ticket.get('issued_at', ''))
        ticket['used_formatted'] = format_timestamp(ticket.get('used_at', ''))
        ticket['voided_formatted'] = format_timestamp(ticket.get('voided_at', ''))
    
    return render_template('dashboard_guests.html', tickets=tickets)


@app.route('/scan')
@login_required
def scan():
    """QR scanner page."""
    return render_template('dashboard_scan.html')


@app.route('/api/verify', methods=['POST'])
@api_login_required
def api_verify():
    """API endpoint to verify a token."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'Invalid request data'}), 400
        
        token = data.get('token', '').strip()
        
        # Log for debugging
        print(f"\n[DEBUG] Received token verification request")
        print(f"  Raw token length: {len(token)}")
        print(f"  Token preview: {token[:50]}..." if len(token) > 50 else f"  Token: {token}")
        print(f"  Has pipe: {'|' in token}")
        
        if not token:
            print(f"  Result: No token provided")
            return jsonify({'success': False, 'message': 'No token provided'})
        
        success, message, ticket = mark_ticket_used(token)
        
        print(f"  Result: success={success}, message={message}")
        
        response = {
            'success': success,
            'message': message
        }
        
        if ticket:
            response['guest'] = {
                'name': ticket.get('guest_name', 'Unknown'),
                'email': ticket.get('guest_email', ''),
                'status': ticket.get('status', 'active')
            }
        
        return jsonify(response)
    
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"[ERROR] api_verify exception:\n{error_details}")
        return jsonify({
            'success': False, 
            'message': f'Server error: {str(e)}'
        }), 500


@app.route('/api/stats')
@api_login_required
def api_stats():
    """API endpoint for real-time statistics."""
    stats = get_statistics()
    return jsonify(stats)


@app.route('/bulk-generate', methods=['GET', 'POST'])
@login_required
def bulk_generate():
    """Bulk ticket generation from CSV upload."""
    if request.method == 'POST':
        # If exclusive_count supplied and > 0, generate anonymous exclusive tickets
        exclusive_count = 0
        try:
            exclusive_count = int(request.form.get('exclusive_count', '0') or 0)
        except ValueError:
            exclusive_count = 0

        # If an exclusive_count is provided, bypass CSV upload and generate anonymous exclusives
        if exclusive_count and exclusive_count > 0:
            try:
                import tempfile
                import uuid as _uuid
                import shutil
                import subprocess
                import sys

                tmp_dir = Path(tempfile.gettempdir())
                job_dir = tmp_dir / f"tickets_job_{_uuid.uuid4().hex}"
                job_dir.mkdir(parents=True, exist_ok=True)

                python_exe = sys.executable

                # Chunk generation to avoid long-running single requests on serverless
                chunk_size = 10
                batches = []
                remaining = exclusive_count
                batch_index = 0

                # Use a placeholder CSV path in the job dir so generate_tickets will write
                # a local `valid_tokens.csv` next to it; this allows duplicate checks across batches.
                placeholder_csv = job_dir / 'placeholder.csv'

                while remaining > 0:
                    take = min(chunk_size, remaining)
                    batch_out = job_dir / f"out_{batch_index}"
                    batch_out.mkdir(parents=True, exist_ok=True)

                    cmd = [python_exe, 'generate_tickets.py', '--exclusive-count', str(take), '--out-dir', str(batch_out), '--csv', str(placeholder_csv), '--no-email']

                    result = subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True,
                        cwd=str(BASE_DIR)
                    )

                    if result.returncode != 0:
                        error_msg = result.stderr if result.stderr else result.stdout
                        flash(f'Error generating batch {batch_index+1}: {error_msg}', 'danger')
                        # Continue to next batch? we'll abort and cleanup
                        return redirect(request.url)

                    batches.append(batch_out)
                    remaining -= take
                    batch_index += 1

                # All batches generated successfully — create a ZIP incrementally to
                # avoid having all batch files on disk at once. Add files to the zip
                # and delete each batch directory after its files are added.
                zip_path = job_dir / f"exclusive_tickets_{_uuid.uuid4().hex}.zip"
                try:
                    import zipfile
                    with zipfile.ZipFile(str(zip_path), 'w', compression=zipfile.ZIP_DEFLATED) as zf:
                        # Walk job_dir and add PDFs from each batch_out, then remove them
                        for batch_out in sorted(job_dir.iterdir()):
                            if not batch_out.is_dir():
                                continue
                            for pdf in batch_out.rglob('*.pdf'):
                                # store files under a flat folder in the zip
                                arcname = pdf.name
                                zf.write(str(pdf), arcname=arcname)
                            # remove batch directory after adding
                            try:
                                shutil.rmtree(batch_out)
                            except Exception:
                                pass

                    if zip_path.exists():
                        # Send the ZIP and then clean up the job_dir
                        resp = send_file(str(zip_path), as_attachment=True, download_name='exclusive_tickets.zip')
                        try:
                            shutil.rmtree(job_dir)
                        except Exception:
                            pass
                        return resp
                    else:
                        flash('Generation finished but ZIP packaging failed', 'danger')
                        try:
                            shutil.rmtree(job_dir)
                        except Exception:
                            pass
                        return redirect(url_for('guests'))
                except Exception as e:
                    flash(f'Error packaging ZIP: {e}', 'danger')
                    try:
                        shutil.rmtree(job_dir)
                    except Exception:
                        pass
                    return redirect(request.url)

            except Exception as e:
                flash(f'Error generating exclusive tickets: {e}', 'danger')
                return redirect(request.url)

        # Otherwise fall back to CSV upload flow
        if 'csv_file' not in request.files:
            flash('No file uploaded', 'danger')
            return redirect(request.url)

        file = request.files['csv_file']
        if file.filename == '':
            flash('No file selected', 'danger')
            return redirect(request.url)

        if not file.filename.endswith('.csv'):
            flash('File must be a CSV', 'danger')
            return redirect(request.url)

        try:
            # Determine writable temp path (Vercel: /tmp)
            import tempfile
            import uuid as _uuid
            import shutil
            tmp_dir = Path(tempfile.gettempdir())
            tmp_csv = tmp_dir / f"guest_upload_{_uuid.uuid4().hex}.csv"
            tmp_out = tmp_dir / f"tickets_{_uuid.uuid4().hex}"
            # Save uploaded file to temp CSV
            file.save(str(tmp_csv))

            # Run generate_tickets.py on the uploaded file, write PDFs to temp output
            import subprocess
            import sys
            send_email = request.form.get('send_email') == 'on'
            python_exe = sys.executable
            cmd = [python_exe, 'generate_tickets.py', '--csv', str(tmp_csv), '--out-dir', str(tmp_out), '--no-csv']
            if not send_email:
                cmd.append('--no-email')
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=str(BASE_DIR)
            )

            if result.returncode == 0:
                # If PDFs were created, zip them and return as download
                if tmp_out.exists():
                    zip_base = tmp_dir / f"tickets_{_uuid.uuid4().hex}"
                    zip_path = shutil.make_archive(str(zip_base), 'zip', root_dir=str(tmp_out))
                    return send_file(zip_path, as_attachment=True, download_name='tickets.zip')
                if send_email:
                    flash('Tickets generated, saved to Firestore and emails attempted.', 'success')
                else:
                    flash('Tickets generated and saved to Firestore.', 'success')
            else:
                error_msg = result.stderr if result.stderr else result.stdout
                flash(f'Error generating tickets: {error_msg}', 'danger')

            return redirect(url_for('guests'))

        except Exception as e:
            flash(f'Error processing file: {str(e)}', 'danger')
            return redirect(request.url)
    
    return render_template('bulk_generate.html')


@app.route('/bulk-cancel', methods=['GET', 'POST'])
@login_required
def bulk_cancel():
    """Bulk ticket cancellation."""
    if request.method == 'POST':
        cancel_filter = request.form.get('filter', 'all')
        reason = request.form.get('reason', 'Bulk cancellation')
        if USE_FIRESTORE:
            try:
                cancelled_count = fs_bulk_void_tickets(cancel_filter, reason)  # type: ignore
                flash(f'Cancelled (voided) {cancelled_count} ticket(s) via Firestore', 'success')
            except Exception as e:
                flash(f'Error cancelling tickets: {e}', 'danger')
            return redirect(url_for('guests'))
        else:
            tickets = load_all_tickets()
            cancelled_count = 0
            for ticket in tickets:
                should_cancel = False
                if cancel_filter in ('all', 'pending') and ticket.get('status') == 'active':
                    should_cancel = True
                elif cancel_filter == 'used' and ticket.get('status') == 'used':
                    should_cancel = True
                if should_cancel:
                    ticket['status'] = 'voided'
                    ticket['voided_at'] = datetime.utcnow().isoformat()
                    ticket['void_reason'] = reason
                    cancelled_count += 1
            if tickets:
                fieldnames = list(tickets[0].keys())
                try:
                    with open(TOKENS_CSV, 'w', newline='', encoding='utf-8') as f:
                        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
                        writer.writeheader(); writer.writerows(tickets)
                except OSError as e:
                    flash(f'File write failed (read-only FS?): {e}', 'warning')
            flash(f'Successfully cancelled {cancelled_count} ticket(s)', 'success')
            return redirect(url_for('guests'))
    
    stats = get_statistics()
    return render_template('bulk_cancel.html', stats=stats)


@app.route('/clear-all-tickets', methods=['POST'])
@login_required
def clear_all_tickets():
    """Delete ALL tickets from the system (Firestore or CSV)."""
    confirmation = request.form.get('confirmation', '')
    
    if confirmation != 'DELETE ALL':
        flash('Confirmation text must be exactly "DELETE ALL"', 'danger')
        return redirect(url_for('guests'))
    
    try:
        if USE_FIRESTORE:
            from db.firestore_adapter import delete_all_tickets as fs_delete_all
            deleted_count = fs_delete_all()
            flash(f'✓ Deleted {deleted_count} tickets from Firestore', 'success')
        else:
            # Clear local CSV - keep header only
            with open(TOKENS_CSV, 'w', newline='', encoding='utf-8') as f:
                f.write('uuid,signature,name,email,checked_in,check_in_time,drink_redeemed,drink_redeem_time,voided\n')
            flash('✓ All tickets cleared from CSV', 'success')
        
    except Exception as e:
        flash(f'Error clearing tickets: {e}', 'danger')
    
    return redirect(url_for('guests'))


@app.route('/send-message', methods=['GET', 'POST'])
@login_required
def send_message():
    """Send custom messages to guests."""
    if request.method == 'POST':
        recipient_filter = request.form.get('recipients', 'all')
        message_type = request.form.get('message_type', 'email')
        subject = request.form.get('subject', '')
        message_body = request.form.get('message', '')
        
        tickets = load_all_tickets()
        recipients = []
        
        # Filter recipients
        for ticket in tickets:
            should_include = False
            
            if recipient_filter == 'all':
                should_include = True
            elif recipient_filter == 'active':
                should_include = ticket.get('status') == 'active'
            elif recipient_filter == 'used':
                should_include = ticket.get('status') == 'used'
            elif recipient_filter == 'voided':
                should_include = ticket.get('status') == 'voided'
            
            if should_include:
                recipients.append(ticket)
        
        # Send messages
        sent_count = 0
        failed_count = 0
        
        if message_type == 'email':
            sent_count, failed_count = send_bulk_emails(recipients, subject, message_body)
        
        if sent_count > 0:
            flash(f'Message sent to {sent_count} guest(s)', 'success')
        if failed_count > 0:
            flash(f'Failed to send to {failed_count} guest(s)', 'warning')
        
        return redirect(url_for('send_message'))
    
    stats = get_statistics()
    return render_template('send_message.html', stats=stats)


def send_bulk_emails(recipients: List[Dict], subject: str, body: str) -> tuple[int, int]:
    """Send bulk emails. Returns (sent_count, failed_count)."""
    # Load SMTP config from templates.json or environment variables
    try:
        smtp_server = None
        smtp_port = None
        smtp_user = None
        smtp_password = None
        from_email = None
        
        # Try loading from templates.json first
        try:
            with open(TEMPLATES_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            smtp_config = config.get('email', {})
            smtp_server = smtp_config.get('smtp_server', '')
            smtp_port = smtp_config.get('smtp_port', 587)
            smtp_user = smtp_config.get('smtp_user', '')
            smtp_password = smtp_config.get('smtp_password', '')
            from_email = smtp_config.get('from_email', smtp_user)
        except Exception as e:
            print(f"[EMAIL] Could not load from templates.json: {e}")
        
        # Fallback to environment variables (Gmail)
        if not all([smtp_server, smtp_user, smtp_password]):
            gmail_address = os.getenv('GMAIL_ADDRESS')
            app_password = os.getenv('GMAIL_APP_PASSWORD')
            from_name = os.getenv('FROM_NAME', 'ADE NOVA Dashboard')
            
            if gmail_address and app_password:
                smtp_server = 'smtp.gmail.com'
                smtp_port = 465  # Gmail uses SSL on port 465
                smtp_user = gmail_address
                smtp_password = app_password
                from_email = f"{from_name} <{gmail_address}>"
                print(f"[EMAIL] Using Gmail credentials from environment")
        
        print(f"\n[EMAIL] Bulk send initiated")
        print(f"  Recipients: {len(recipients)}")
        print(f"  SMTP Server: {smtp_server}:{smtp_port}")
        print(f"  From: {from_email}")
        
        if not all([smtp_server, smtp_user, smtp_password]):
            print(f"[EMAIL] ERROR: Missing SMTP configuration")
            print(f"  Server: {'✓' if smtp_server else '✗'}")
            print(f"  User: {'✓' if smtp_user else '✗'}")
            print(f"  Password: {'✓' if smtp_password else '✗'}")
            print(f"  Configure SMTP in config/templates.json or set GMAIL_ADDRESS/GMAIL_APP_PASSWORD env vars")
            return 0, len(recipients)
        
        sent = 0
        failed = 0
        failed_emails = []
        
        # Use SSL for Gmail (port 465), TLS for others (port 587)
        if smtp_port == 465:
            import ssl
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(smtp_server, smtp_port, context=context) as server:
                server.login(smtp_user, smtp_password)
                print(f"[EMAIL] SMTP SSL login successful")
                sent, failed, failed_emails = _send_emails_via_server(server, recipients, subject, body, from_email)
        else:
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(smtp_user, smtp_password)
                print(f"[EMAIL] SMTP TLS login successful")
                sent, failed, failed_emails = _send_emails_via_server(server, recipients, subject, body, from_email)
        
        print(f"\n[EMAIL] Summary:")
        print(f"  ✓ Sent: {sent}")
        print(f"  ✗ Failed: {failed}")
        if failed_emails:
            print(f"  Failed recipients:")
            for failed_email in failed_emails[:10]:  # Show first 10
                print(f"    - {failed_email}")
            if len(failed_emails) > 10:
                print(f"    ... and {len(failed_emails) - 10} more")
        
        return sent, failed
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"[EMAIL] AUTHENTICATION FAILED: {e}")
        print(f"  Check SMTP credentials")
        return 0, len(recipients)
    except smtplib.SMTPConnectError as e:
        print(f"[EMAIL] CONNECTION FAILED: {e}")
        print(f"  Cannot connect to {smtp_server}:{smtp_port}")
        return 0, len(recipients)
    except Exception as e:
        import traceback
        print(f"[EMAIL] UNEXPECTED ERROR: {e}")
        print(traceback.format_exc())
        return 0, len(recipients)


def _send_emails_via_server(server, recipients: List[Dict], subject: str, body: str, from_email: str) -> tuple[int, int, List[str]]:
    """Helper to send emails through an established SMTP connection."""
    sent = 0
    failed = 0
    failed_emails = []
    
    for idx, recipient in enumerate(recipients, 1):
        try:
            email = recipient.get('guest_email', '').strip()
            name = recipient.get('guest_name', 'Guest')
            
            if not email:
                print(f"  [{idx}/{len(recipients)}] SKIP - No email for {name}")
                failed += 1
                failed_emails.append(f"{name} (no email)")
                continue
            
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = from_email
            msg['To'] = email
            
            # Personalize message
            personalized_body = body.replace('{name}', name)
            personalized_body = personalized_body.replace('{email}', email)
            
            text_part = MIMEText(personalized_body, 'plain')
            msg.attach(text_part)
            
            server.send_message(msg)
            sent += 1
            print(f"  [{idx}/{len(recipients)}] ✓ Sent to {name} <{email}>")
            
        except smtplib.SMTPRecipientsRefused as e:
            failed += 1
            failed_emails.append(f"{name} <{email}> (invalid address)")
            print(f"  [{idx}/{len(recipients)}] ✗ Invalid address: {email} - {e}")
        except smtplib.SMTPException as e:
            failed += 1
            failed_emails.append(f"{name} <{email}> (SMTP error)")
            print(f"  [{idx}/{len(recipients)}] ✗ SMTP error for {email}: {e}")
        except Exception as e:
            failed += 1
            failed_emails.append(f"{name} <{email}> ({type(e).__name__})")
            print(f"  [{idx}/{len(recipients)}] ✗ Error sending to {email}: {e}")
    
    return sent, failed, failed_emails


## SMS bulk sending removed.


@app.route('/api/search')
@login_required
def api_search():
    """API endpoint for searching guests (including phone number)."""
    query = request.args.get('q', '').strip().lower()
    
    if not query:
        return jsonify([])
    
    tickets = load_all_tickets()
    results = []
    
    for ticket in tickets:
        name = ticket.get('guest_name', '').lower()
        email = ticket.get('guest_email', '').lower()
        phone = ticket.get('guest_phone', '').lower()
        token = ticket.get('uuid', '').lower()
        
        if query in name or query in email or query in phone or query in token:
            ticket['issued_formatted'] = format_timestamp(ticket.get('issued_at', ''))
            ticket['used_formatted'] = format_timestamp(ticket.get('used_at', ''))
            ticket['voided_formatted'] = format_timestamp(ticket.get('voided_at', ''))
            ticket['drink_claimed_formatted'] = format_timestamp(ticket.get('drink_claimed_at', ''))
            results.append(ticket)
    
    return jsonify(results)


@app.route('/drinks')
@login_required
def drinks_management():
    """Redirect to drinks scanner (merged page)."""
    return redirect(url_for('drinks_scanner'))


@app.route('/bulk-delete', methods=['GET', 'POST'])
@login_required
def bulk_delete():
    """Dangerous: permanently delete all tickets/guests."""
    if request.method == 'POST':
        phrase = request.form.get('confirm_phrase', '').strip()
        expected = 'DELETE ALL'
        if phrase != expected:
            flash(f'Confirmation phrase mismatch. Type: {expected}', 'danger')
            return redirect(url_for('bulk_delete'))
        deleted_count = 0
        if USE_FIRESTORE:
            try:
                deleted_count = fs_delete_all_tickets()  # type: ignore
            except Exception as e:
                flash(f'Error deleting tickets: {e}', 'danger')
                return redirect(url_for('bulk_delete'))
        else:
            # CSV fallback: truncate the file if exists
            if TOKENS_CSV.exists():
                try:
                    TOKENS_CSV.unlink()
                except OSError:
                    # If cannot unlink, attempt truncate
                    try:
                        open(TOKENS_CSV, 'w').close()
                    except Exception:
                        pass
            deleted_count = 0  # unknown exact count without reading
        flash(f'All tickets deleted. Count (Firestore): {deleted_count}', 'success')
        return redirect(url_for('guests'))
    stats = get_statistics()
    return render_template('bulk_delete.html', stats=stats)


@app.route('/bulk-delete-exclusive', methods=['GET', 'POST'])
@login_required
def bulk_delete_exclusive():
    """Dangerous: permanently delete all 'exclusive' tickets only."""
    if request.method == 'POST':
        phrase = request.form.get('confirm_phrase', '').strip()
        expected = 'DELETE EXCLUSIVE'
        if phrase != expected:
            flash(f'Confirmation phrase mismatch. Type: {expected}', 'danger')
            return redirect(url_for('bulk_delete_exclusive'))
        deleted_count = 0
        if USE_FIRESTORE:
            try:
                from db.firestore_adapter import delete_all_exclusive_tickets as fs_delete_exclusive  # type: ignore
                deleted_count = fs_delete_exclusive()  # type: ignore
            except Exception as e:
                flash(f'Error deleting exclusive tickets: {e}', 'danger')
                return redirect(url_for('bulk_delete_exclusive'))
        else:
            # CSV fallback: remove rows where ticket_type == 'exclusive'
            if TOKENS_CSV.exists():
                try:
                    with open(TOKENS_CSV, 'r', newline='', encoding='utf-8') as f:
                        reader = list(csv.DictReader(f))
                    before = len(reader)
                    remaining = [r for r in reader if (r.get('ticket_type') or '').lower() != 'exclusive']
                    after = len(remaining)
                    deleted_count = before - after
                    # write back remaining
                    fieldnames = list(remaining[0].keys()) if remaining else ['token', 'uuid', 'signature', 'status', 'guest_name', 'guest_email', 'guest_phone', 'ticket_type', 'issued_at', 'used_at', 'voided_at', 'void_reason', 'drink_claimed_at']
                    with open(TOKENS_CSV, 'w', newline='', encoding='utf-8') as f:
                        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
                        writer.writeheader(); writer.writerows(remaining)
                except Exception as e:
                    flash(f'Error updating CSV: {e}', 'danger')
                    return redirect(url_for('bulk_delete_exclusive'))
        flash(f"Deleted {deleted_count} exclusive tickets.", 'success')
        return redirect(url_for('guests'))
    stats = get_statistics()
    return render_template('bulk_delete_exclusive.html', stats=stats)


@app.route('/api/drinks/toggle', methods=['POST'])
@login_required
def toggle_drinks():
    """Toggle drink distribution on/off."""
    try:
        config = load_drink_config()
        current_status = config.get('enabled', False)
        
        # Toggle status
        config['enabled'] = not current_status
        
        # Update timestamps
        if config['enabled']:
            config['started_at'] = datetime.now(CASABLANCA_TZ).isoformat()
            config['stopped_at'] = None
            message = 'Drink distribution ENABLED'
        else:
            config['stopped_at'] = datetime.now(CASABLANCA_TZ).isoformat()
            message = 'Drink distribution DISABLED'
        
        save_drink_config(config)
        
        print(f"[DRINKS] Status toggled to: {'ENABLED' if config['enabled'] else 'DISABLED'}")
        
        return jsonify({
            'success': True,
            'enabled': config['enabled'],
            'message': message
        })
    except Exception as e:
        print(f"[ERROR] Failed to toggle drinks: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500


@app.route('/api/drinks/status')
@login_required
def drinks_status():
    """Get current drink distribution status."""
    config = load_drink_config()
    stats = get_statistics()
    
    return jsonify({
        'enabled': config.get('enabled', False),
        'started_at': config.get('started_at'),
        'stopped_at': config.get('stopped_at'),
        'drinks_claimed': stats.get('drinks_claimed', 0),
        'checked_in': stats.get('checked_in', 0),
        'drink_rate': stats.get('drink_rate', 0)
    })


@app.route('/drinks-scanner')
@login_required
def drinks_scanner():
    """Drink distribution scanner page."""
    config = load_drink_config()
    return render_template('drinks_scanner.html', config=config)


@app.route('/api/drinks/claim', methods=['POST'])
@api_login_required
def api_claim_drink():
    """API endpoint to claim a drink."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'Invalid request data'}), 400
        
        token = data.get('token', '').strip()
        
        # Log for debugging
        print(f"\n[DEBUG] Drink claim request")
        print(f"  Token length: {len(token)}")
        print(f"  Token preview: {token[:50]}..." if len(token) > 50 else f"  Token: {token}")
        print(f"  Has pipe: {'|' in token}")
        
        if not token:
            return jsonify({'success': False, 'message': 'No token provided'})
        
        # Check if distribution is enabled
        config = load_drink_config()
        if not config.get('enabled', False):
            print(f"  Result: Distribution disabled")
            return jsonify({'success': False, 'message': 'Drink distribution is not enabled'})
        
        # Support short tokens (8-char) like the check-in scanner
        if '|' not in token:
            if len(token) == 8:
                # Short token - look up the full token
                if USE_FIRESTORE:
                    tickets = fs_list_tickets()  # type: ignore
                else:
                    tickets = load_all_tickets()
                
                for ticket in tickets:
                    if ticket.get('uuid', '')[:8].lower() == token.lower():
                        # Found matching ticket - reconstruct full token
                        uuid_part = ticket.get('uuid')
                        sig_part = ticket.get('signature')
                        if uuid_part and sig_part:
                            token = f"{uuid_part}|{sig_part}"
                            print(f"  Short token matched: {uuid_part[:8]}")
                            break
                else:
                    print(f"  Result: Short token not found")
                    return jsonify({'success': False, 'message': 'Short token not found'})
            else:
                print(f"  Result: Bad format")
                return jsonify({'success': False, 'message': 'Invalid token format (expected full token with | or 8-char short code)'})
        
        uuid_part, sig_part = token.split('|', 1)
        
        # Verify signature
        valid, error = verify_token_signature(token)
        if not valid:
            print(f"  Result: {error}")
            return jsonify({'success': False, 'message': error})
        
        if USE_FIRESTORE:
            ok, msg, data = fs_claim_drink(uuid_part)  # type: ignore
            if not ok:
                print(f"  Result: {msg}")
                return jsonify({'success': False, 'message': msg})
            guest_name = data.get('guest_name', 'Guest') if data else 'Guest'
            print(f"  Result: SUCCESS - Drink given to {guest_name}")
            return jsonify({
                'success': True,
                'message': f'🥤 Drink given to {guest_name}!',
                'guest': {
                    'name': guest_name,
                    'email': data.get('guest_email', '') if data else '',
                    'type': (data.get('ticket_type', '') if data else '').upper(),
                    'checked_in': format_timestamp(data.get('used_at', '')) if data else '',
                    'drink_claimed': format_timestamp(data.get('drink_claimed_at', '')) if data else ''
                }
            })
        # CSV fallback
        tickets = load_all_tickets()
        hit_index = None
        for idx, ticket in enumerate(tickets):
            if ticket.get('uuid') == uuid_part and ticket.get('signature') == sig_part:
                hit_index = idx
                break
        if hit_index is None:
            print("  Result: Token not found")
            return jsonify({'success': False, 'message': 'Token not found'})
        
        ticket = tickets[hit_index]
        guest_name = ticket.get('guest_name', 'Guest')
        if ticket.get('status') != 'used':
            print("  Result: Not checked in")
            return jsonify({'success': False, 'message': f'{guest_name} has not checked in at the entrance yet'})
        if ticket.get('drink_claimed_at'):
            claimed_time = format_timestamp(ticket.get('drink_claimed_at'))
            print(f"  Result: Already claimed at {claimed_time}")
            return jsonify({'success': False, 'message': f'{guest_name} already claimed drink at {claimed_time}'})
        
        tickets[hit_index]['drink_claimed_at'] = datetime.now(CASABLANCA_TZ).isoformat()
        fieldnames = list(tickets[0].keys()) if tickets else ['token', 'uuid', 'signature', 'status', 'guest_name', 'guest_email', 'guest_phone', 'ticket_type', 'issued_at', 'used_at', 'voided_at', 'void_reason', 'drink_claimed_at']
        with open(TOKENS_CSV, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
            writer.writeheader(); writer.writerows(tickets)
        print(f"  Result: SUCCESS - Drink given to {guest_name}")
        return jsonify({
            'success': True,
            'message': f'🥤 Drink given to {guest_name}!',
            'guest': {
                'name': guest_name,
                'email': ticket.get('guest_email', ''),
                'type': ticket.get('ticket_type', '').upper(),
                'checked_in': format_timestamp(ticket.get('used_at', '')),
                'drink_claimed': format_timestamp(tickets[hit_index]['drink_claimed_at'])
            }
        })
    
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"[ERROR] api_claim_drink exception:\n{error_details}")
        return jsonify({
            'success': False, 
            'message': f'Server error: {str(e)}'
        }), 500


if __name__ == '__main__':
    print("=" * 60)
    print("TICKET DASHBOARD - LOCAL SERVER")
    print("=" * 60)
    print()
    print("Starting dashboard at: http://localhost:5000")
    print()
    print("Features:")
    print("  - Real-time statistics")
    print("  - Guest list with search")
    print("  - QR code scanner (camera)")
    print("  - Manual token entry")
    print()
    print("Press Ctrl+C to stop")
    print("=" * 60)
    print()
    
    app.run(debug=True, host='0.0.0.0', port=5000)
