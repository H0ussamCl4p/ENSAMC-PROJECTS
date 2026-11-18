# Ticket app

Ticketing for the students' association party on 23 November 2025 (Palais des Ambassadeurs). Each guest gets a PDF ticket with a signed QR code by email, and the team scans tickets at the door from a web dashboard.

- Tickets carry a UUID signed with HMAC, so edited or reused codes are rejected.
- One PDF template per ticket type: student, member, external, media, exclusive, organiser.
- Dashboard: check-in stats, guest search, camera QR scanner, bulk generation and cancellation from CSV, drink vouchers, admin login with 2FA by email.
- Data in Firestore, or local CSV files for testing.

Stack: Python, Flask, fpdf2, qrcode, Firestore, Tailwind CSS.

## Run it

```bash
pip install -r requirements.txt
cp .env.example .env    # fill in the Gmail app password and the secrets
python dashboard.py
```

Generate tickets from a guest list with `python generate_tickets.py`. Use `static/guest_list_template.csv` as the format.
