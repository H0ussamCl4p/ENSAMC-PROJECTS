# QR-code Ticketing System (Local, Free, Secure)

This project generates secure, single-use QR-code tickets for an event, emails them to guests (via Gmail SMTP), optionally sends SMS via free email-to-SMS gateways, and verifies tickets offline at the door.

- 100% local: no paid APIs, no cloud.
- Open-source libs only.
- Cryptographically signed tokens (UUID + HMAC) to prevent tampering and reuse.
- Clean, minimal, student-friendly.

## Features
- Generate one PDF ticket per guest with QR code and a short token display
- Email delivery via Gmail SMTP (App Password)
- SMS delivery via email-to-SMS gateways (no Twilio)
- Offline verification that rejects tampered or reused codes

## Project Structure
- `generate_tickets.py` — Create tokens, QR codes, PDF tickets, send Email+SMS, log results
- `scripts/verify_ticket.py` — Offline CLI to verify scanned tokens and mark as used
- `config/templates.json` — JSON templates for event/email content
- `templates/` — Optional assets like `ticket_bg.png` background for PDFs
- `guest_list.csv` — Input with `name,email,phone,carrier`
- `valid_tokens.csv` — Issued tokens and usage status
- `tickets/` — Output PDF tickets
- `scripts/` — Maintenance and CLI tools
- `docs/` — Guides and production docs
- `tests/` — Test scripts and sample data

## Quick Start

### 1. Install Python Dependencies
Install Python 3.9+ and dependencies:

```powershell
python -m pip install -r requirements.txt
```

### 2. Setup Dashboard (Production-ready Tailwind CSS)
The dashboard uses Tailwind CSS for styling. You need Node.js installed to build the CSS.

**First-time setup:**
```powershell
# Install Node.js from https://nodejs.org/ (if not installed)

# Install Tailwind CSS dependencies
npm install

# Build production CSS
npm run build:css
```

**Optional - Watch mode for development:**
```powershell
# Auto-rebuild CSS when you make changes to templates
npm run watch:css
```

**Alternative - Quick setup script:**
```powershell
# Run the automated setup script
.\setup-tailwind.ps1
```

### 3. Configure Event Settings
Edit event and message templates in `config/templates.json` (event name, date, location).

### 4. Prepare Guest List
Put your guests in `guest_list.csv` with columns: `name,email,phone,carrier`.

### 5. Configure Gmail
   - Enable 2FA on your Google account
   - Create an App Password for “Mail” (Google Account → Security → App passwords)
   - Set environment variables (recommended) in your PowerShell session:

```powershell
$env:GMAIL_ADDRESS = "your.name@gmail.com"
$env:GMAIL_APP_PASSWORD = "abcd xyzx abcd xyzx"
$env:FROM_NAME = "Event Team"
```

### 6. Optional Background Image
Add a background image at `templates/ticket_bg.png` (PNG). The PDF will include it if present.

### 7. Generate and Send Tickets

```powershell
# Full run (emails + SMS)
python .\generate_tickets.py

# Generate only (no email, no SMS) — useful for testing
python .\generate_tickets.py --no-email --no-sms
```

### 8. Start Web Dashboard
Launch the web dashboard for real-time check-in management:

```powershell
python .\dashboard.py
```

Then open: **http://localhost:5000**

Production server (Windows):
```powershell
waitress-serve --host 0.0.0.0 --port 5000 dashboard:app
# Or
.\scripts\run-prod.ps1 -Port 5000 -BindHost 0.0.0.0
```

**Dashboard Features:**
- 📊 Real-time check-in statistics
- 👥 Searchable guest list (by name, email, or phone)
- 📷 QR code scanner (camera + manual entry)
- 📤 Bulk ticket generation (upload CSV)
- ❌ Bulk ticket cancellation
- 📧 Send custom messages to guests (email/SMS)
- 📱 Fully responsive (mobile, tablet, desktop)

### 9. Verify Tickets Offline (CLI)

```powershell
# Paste or scan the QR token string when prompted
python .\scripts\verify_ticket.py
```

### 10. Cancel/Void Tickets (if needed)

```powershell
# Interactive cancellation by name, email, or token
python .\scripts\cancel_ticket.py
```

## How it works
- On first run, a local secret key file `.secret_key` is created in the project folder (keep it safe).
- For each guest, the script creates a token `UUID|HMAC_SHA256(UUID, secret_key)`, stores it in `valid_tokens.csv`, renders a PDF with QR code, and sends email + SMS.
- Verification recomputes the HMAC to reject tampered tokens and marks valid tokens as `used` on first successful scan.
- Tickets have three statuses: `active` (can be used), `used` (already checked in), `voided` (cancelled/invalid).

## Ticket Cancellation
Use `scripts/cancel_ticket.py` to void tickets for refunds, duplicates, or bans:
- Search by guest name, email, or token
- Select from multiple matches
- Choose cancellation reason (refund, duplicate, banned, etc.)
- Voided tickets are rejected at verification with reason displayed
- Audit trail includes void timestamp and reason

## Email-to-SMS carriers (examples)
Put one of these in the `carrier` column (case-insensitive). If your carrier is missing, add the domain mapping in `generate_tickets.py`.

- AT&T: `att` → `txt.att.net`
- Verizon: `verizon` → `vtext.com`
- T-Mobile: `tmobile` → `tmomail.net`
- Sprint (legacy): `sprint` → `messaging.sprintpcs.com`
- US Cellular: `uscellular` → `email.uscc.net`
- Cricket: `cricket` → `sms.cricketwireless.net`
- Boost: `boost` → `sms.myboostmobile.com`
- Google Fi: `googlefi` → `msg.fi.google.com`
- Mint: `mint` → `mailmymobile.net`
- Rogers (CA): `rogers` → `pcs.rogers.com`
- Bell (CA): `bell` → `txt.bell.ca`
- Telus (CA): `telus` → `msg.telus.com`
- Fido (CA): `fido` → `fido.ca`
- Freedom (CA): `freedom` → `txt.freedommobile.ca`

## Safety & Privacy
- QR code encodes only the secure token (no personal data).
- `valid_tokens.csv` lives locally; don’t share it publicly.
- Keep `.secret_key` private so nobody can forge tickets.

## Troubleshooting
- Emails not sending? Double-check `$env:GMAIL_ADDRESS` and `$env:GMAIL_APP_PASSWORD`.
- SMS not arriving? Ensure the carrier gateway is correct and phone number is 10 digits.
- PDFs not showing background? Ensure `templates/ticket_bg.png` exists and is a valid PNG.

## License
MIT — do anything with attribution. No warranty.

## Deploy (GitHub → Vercel Docker → Firebase)

Quick path to put this online for free:

1) Push to GitHub
   - Initialize a repo and push (PowerShell):

```powershell
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/<you>/<repo>.git
git push -u origin main
```

2) Deploy to Vercel (Docker)
   - In Vercel, Import Project → select your GitHub repo
   - Vercel detects `Dockerfile` automatically
   - Set Environment Variables:
     - GMAIL_ADDRESS, GMAIL_APP_PASSWORD, FROM_NAME
     - HMAC_SECRET_HEX (hex string that matches your local `.secret_key`)
     - FLASK_SECRET (optional random string for sessions)
   - Deploy

3) Configure Firebase Hosting (optional front door/CDN)
   - Install Firebase CLI, run `firebase init hosting` in this repo
   - Edit `firebase.json` and set your Vercel URL in the redirect
   - Deploy Hosting:

```powershell
firebase login
firebase init hosting
firebase deploy --only hosting
```

Docs:
- Vercel: `docs/vercel.md`
- Firebase Hosting: `docs/firebase-hosting.md`
- Docker: `docs/docker.md`

Notes:
- Vercel deployments are ephemeral; `valid_tokens.csv` won’t persist across restarts. For production, migrate to a managed DB (e.g., Firestore, Supabase, Neon) and point the app to it.
- Do NOT commit `.secret_key`. Set `HMAC_SECRET_HEX` in Vercel so the dashboard can verify tokens generated locally.
