"""Script to clear all tickets from the system.

This will delete all tickets from:
- Firestore (if FIRESTORE_ENABLED=1)
- Local valid_tokens.csv file
- Generated ticket PDFs in the tickets/ directory

Usage:
    python clear_tickets.py
    
WARNING: This action cannot be undone!
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BASE_DIR = Path(__file__).parent
TOKENS_CSV = BASE_DIR / 'valid_tokens.csv'
TICKETS_DIR = BASE_DIR / 'tickets'

USE_FIRESTORE = os.getenv('FIRESTORE_ENABLED', '0') == '1'

def clear_firestore_tickets():
    """Delete all tickets from Firestore."""
    try:
        from db.firestore_adapter import list_tickets, delete_all_tickets
        
        print("[FIRESTORE] Fetching ticket count...")
        tickets = list_tickets()
        ticket_count = len(tickets)
        
        if ticket_count == 0:
            print("[FIRESTORE] No tickets found in Firestore.")
            return 0
        
        print(f"[FIRESTORE] Found {ticket_count} tickets. Deleting in batches...")
        deleted_count = delete_all_tickets()
        
        print(f"[FIRESTORE] ✓ Deleted {deleted_count} tickets from Firestore.")
        return deleted_count
        
    except ImportError as e:
        print(f"[FIRESTORE] Could not import Firestore adapter: {e}")
        return 0
    except Exception as e:
        print(f"[FIRESTORE] Error clearing tickets: {e}")
        return 0

def clear_csv_tickets():
    """Clear the local CSV file."""
    try:
        if TOKENS_CSV.exists():
            # Keep the header, remove all data rows
            with open(TOKENS_CSV, 'w', newline='', encoding='utf-8') as f:
                f.write('uuid,signature,name,email,checked_in,check_in_time,drink_redeemed,drink_redeem_time,voided\n')
            print(f"[CSV] ✓ Cleared {TOKENS_CSV}")
            return True
        else:
            print(f"[CSV] File not found: {TOKENS_CSV}")
            return False
    except Exception as e:
        print(f"[CSV] Error clearing file: {e}")
        return False

def clear_pdf_tickets():
    """Delete all generated ticket PDFs."""
    try:
        if not TICKETS_DIR.exists():
            print(f"[PDF] Directory not found: {TICKETS_DIR}")
            return 0
        
        pdf_files = list(TICKETS_DIR.glob('*.pdf'))
        
        if not pdf_files:
            print(f"[PDF] No PDF files found in {TICKETS_DIR}")
            return 0
        
        deleted_count = 0
        for pdf_file in pdf_files:
            try:
                pdf_file.unlink()
                deleted_count += 1
            except Exception as e:
                print(f"[PDF] Failed to delete {pdf_file.name}: {e}")
        
        print(f"[PDF] ✓ Deleted {deleted_count} PDF files from {TICKETS_DIR}")
        return deleted_count
        
    except Exception as e:
        print(f"[PDF] Error clearing directory: {e}")
        return 0

def main():
    print("=" * 60)
    print("TICKET CLEARING SCRIPT")
    print("=" * 60)
    print(f"Environment: {'PRODUCTION (Firestore)' if USE_FIRESTORE else 'DEVELOPMENT (Local CSV)'}")
    print()
    
    # Confirm action
    response = input("⚠️  WARNING: This will DELETE ALL TICKETS!\nType 'YES' to confirm: ")
    
    if response != 'YES':
        print("\n❌ Aborted. No tickets were deleted.")
        sys.exit(0)
    
    print("\n" + "=" * 60)
    print("CLEARING TICKETS...")
    print("=" * 60 + "\n")
    
    # Clear Firestore if enabled
    firestore_count = 0
    if USE_FIRESTORE:
        firestore_count = clear_firestore_tickets()
    else:
        print("[FIRESTORE] Skipped (FIRESTORE_ENABLED=0)")
    
    # Clear CSV
    csv_cleared = clear_csv_tickets()
    
    # Clear PDFs
    pdf_count = clear_pdf_tickets()
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    if USE_FIRESTORE:
        print(f"Firestore tickets deleted: {firestore_count}")
    print(f"CSV file cleared: {'Yes' if csv_cleared else 'No'}")
    print(f"PDF files deleted: {pdf_count}")
    print("\n✓ All tickets have been cleared!")
    print("=" * 60)

if __name__ == '__main__':
    main()
