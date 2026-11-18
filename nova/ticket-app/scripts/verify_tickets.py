from pypdf import PdfReader
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
tickets_dir = ROOT_DIR / 'tickets'
test_tickets = ['test-ensamien.pdf', 'test-adherent.pdf', 'test-externe.pdf']

print("Verification des tickets generes:")
print("-" * 50)

for ticket in test_tickets:
    ticket_path = tickets_dir / ticket
    if ticket_path.exists():
        reader = PdfReader(str(ticket_path))
        num_pages = len(reader.pages)
        size_mb = ticket_path.stat().st_size / (1024 * 1024)
        status = "OK" if num_pages == 2 else "WARNING"
        print(f"{status} {ticket}: {num_pages} pages, {size_mb:.2f} MB")
    else:
        print(f"ERROR {ticket}: Fichier non trouve")

print("-" * 50)
print("Test complete!")
