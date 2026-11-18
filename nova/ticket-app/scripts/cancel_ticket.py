"""Cancel/void tickets by searching for guest name, email, or token.

Usage:
    python scripts/cancel_ticket.py
"""
from __future__ import annotations
import csv
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import List, Dict, Any

ROOT_DIR = Path(__file__).resolve().parents[1]
TOKENS_CSV = ROOT_DIR / 'valid_tokens.csv'

# Casablanca timezone (GMT+1)
CASABLANCA_TZ = timezone(timedelta(hours=1))


def format_timestamp(iso_timestamp: str) -> str:
    """Convert ISO timestamp to readable format."""
    if not iso_timestamp:
        return 'N/A'
    
    try:
        dt = datetime.fromisoformat(iso_timestamp)
        return dt.strftime('%b %d, %Y at %I:%M %p')
    except (ValueError, AttributeError):
        return iso_timestamp


def load_all_tickets() -> List[Dict[str, str]]:
    """Load all tickets from valid_tokens.csv."""
    if not TOKENS_CSV.exists():
        return []
    
    tickets = []
    with open(TOKENS_CSV, 'r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            tickets.append(row)
    return tickets


def search_tickets(query: str, search_type: str) -> List[Dict[str, str]]:
    """Search tickets by name, email, or token."""
    tickets = load_all_tickets()
    results = []
    query_lower = query.lower().strip()
    
    for ticket in tickets:
        if search_type == 'name':
            if query_lower in ticket.get('guest_name', '').lower():
                results.append(ticket)
        elif search_type == 'email':
            if query_lower in ticket.get('guest_email', '').lower():
                results.append(ticket)
        elif search_type == 'token':
            if query_lower in ticket.get('uuid', '').lower() or query_lower in ticket.get('token', '').lower():
                results.append(ticket)
    
    return results


def display_ticket(ticket: Dict[str, str], index: int = None) -> None:
    """Display ticket details in a readable format."""
    prefix = f"[{index}] " if index is not None else ""
    status = ticket.get('status', ticket.get('used', 'no'))
    if status == 'yes':
        status = 'used'
    elif status == 'no':
        status = 'active'
    
    print(f"{prefix}Guest: {ticket.get('guest_name', 'N/A')}")
    print(f"    Email: {ticket.get('guest_email', 'N/A')}")
    print(f"    Phone: {ticket.get('guest_phone', 'N/A')}")
    print(f"    Token (short): {ticket.get('uuid', 'N/A')[:8]}")
    print(f"    Status: {status}")
    print(f"    Issued: {format_timestamp(ticket.get('issued_at', ''))}")
    if status == 'used':
        print(f"    Used At: {format_timestamp(ticket.get('used_at', ''))}")
    if status == 'voided':
        print(f"    Voided At: {format_timestamp(ticket.get('voided_at', ''))}")
        print(f"    Void Reason: {ticket.get('void_reason', 'N/A')}")
    print()


def void_ticket(ticket: Dict[str, str], reason: str) -> bool:
    """Mark a ticket as voided with reason and timestamp."""
    tickets = load_all_tickets()
    updated = False
    
    # Find and update the matching ticket
    for t in tickets:
        if t.get('uuid') == ticket.get('uuid') and t.get('signature') == ticket.get('signature'):
            t['status'] = 'voided'
            t['voided_at'] = datetime.now(CASABLANCA_TZ).isoformat()
            t['void_reason'] = reason
            updated = True
            break
    
    if not updated:
        return False
    
    # Write back to CSV
    fieldnames = ['token', 'uuid', 'signature', 'status', 'guest_name', 'guest_email', 'guest_phone', 
                  'issued_at', 'used_at', 'voided_at', 'void_reason']
    
    with open(TOKENS_CSV, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(tickets)
    
    return True


def main():
    print("=" * 60)
    print("TICKET CANCELLATION / VOID SYSTEM")
    print("=" * 60)
    print()
    
    # Search type selection
    print("Search by:")
    print("  1. Guest Name")
    print("  2. Email Address")
    print("  3. Token/UUID")
    print()
    
    search_choice = input("Enter choice (1-3): ").strip()
    search_type_map = {'1': 'name', '2': 'email', '3': 'token'}
    
    if search_choice not in search_type_map:
        print("Invalid choice. Exiting.")
        return
    
    search_type = search_type_map[search_choice]
    
    # Get search query
    search_label = {'name': 'Name', 'email': 'Email', 'token': 'Token/UUID'}[search_type]
    query = input(f"Enter {search_label} (partial match OK): ").strip()
    
    if not query:
        print("Empty search query. Exiting.")
        return
    
    # Search tickets
    results = search_tickets(query, search_type)
    
    if not results:
        print(f"\nNo tickets found matching '{query}'")
        return
    
    print(f"\nFound {len(results)} ticket(s):\n")
    
    # Display results
    for idx, ticket in enumerate(results):
        display_ticket(ticket, idx + 1)
    
    # Select ticket to void
    if len(results) == 1:
        selected = results[0]
        confirm = input("Void this ticket? (yes/no): ").strip().lower()
        if confirm != 'yes':
            print("Cancelled.")
            return
    else:
        selection = input(f"Select ticket to void (1-{len(results)}, or 0 to cancel): ").strip()
        if selection == '0':
            print("Cancelled.")
            return
        
        try:
            idx = int(selection) - 1
            if idx < 0 or idx >= len(results):
                print("Invalid selection. Exiting.")
                return
            selected = results[idx]
        except ValueError:
            print("Invalid input. Exiting.")
            return
    
    # Check if already voided or used
    status = selected.get('status', selected.get('used', 'no'))
    if status == 'voided':
        print("\n⚠️  This ticket is already voided.")
        print(f"Reason: {selected.get('void_reason', 'N/A')}")
        print(f"Voided at: {selected.get('voided_at', 'N/A')}")
        return
    
    if status == 'yes' or status == 'used':
        print("\n⚠️  Warning: This ticket has already been used for entry.")
        print(f"Used at: {selected.get('used_at', 'N/A')}")
        proceed = input("Void anyway? (yes/no): ").strip().lower()
        if proceed != 'yes':
            print("Cancelled.")
            return
    
    # Get cancellation reason
    print("\nCancellation reasons:")
    print("  1. Guest requested cancellation")
    print("  2. Refund issued")
    print("  3. Duplicate ticket")
    print("  4. Payment failed")
    print("  5. Guest banned/removed")
    print("  6. Other")
    print()
    
    reason_choice = input("Select reason (1-6): ").strip()
    reason_map = {
        '1': 'Guest requested cancellation',
        '2': 'Refund issued',
        '3': 'Duplicate ticket',
        '4': 'Payment failed',
        '5': 'Guest banned/removed',
        '6': None
    }
    
    reason = reason_map.get(reason_choice)
    if reason is None:
        reason = input("Enter custom reason: ").strip()
        if not reason:
            reason = "No reason provided"
    
    # Final confirmation
    print("\n" + "=" * 60)
    print("CONFIRM CANCELLATION")
    print("=" * 60)
    display_ticket(selected)
    print(f"Reason: {reason}")
    print()
    
    final_confirm = input("Type 'VOID' to confirm cancellation: ").strip()
    if final_confirm != 'VOID':
        print("Cancelled. Ticket not voided.")
        return
    
    # Void the ticket
    success = void_ticket(selected, reason)
    
    if success:
        print("\n✅ Ticket successfully voided.")
        print(f"Guest: {selected.get('guest_name')}")
        print(f"Reason: {reason}")
        print(f"Timestamp: {format_timestamp(datetime.now(CASABLANCA_TZ).isoformat())}")
    else:
        print("\n❌ Error: Could not void ticket.")


if __name__ == '__main__':
    main()
