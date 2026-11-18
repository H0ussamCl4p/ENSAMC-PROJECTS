"""
Performance test for ticket generation.
- Disables Firestore and email sending via environment variables.
- Runs generate_for_guest N times with a small fake row (no heavy external network).
- Records per-iteration timings and prints summary.
Run with your venv active:
    & .venv\Scripts\Activate.ps1
    $env:FORCE_DISABLE_EMAIL="1"; $env:FIRESTORE_ENABLED="0"; $env:HMAC_SECRET="testsecret"; python performance_test.py
"""
import os
import time
import statistics
from pathlib import Path

# Ensure we don't send emails or use Firestore during the test
os.environ['FIRESTORE_ENABLED'] = '0'
# generate_tickets checks env vars for Gmail; to be safe, set a flag the test will respect
os.environ['FORCE_DISABLE_EMAIL'] = '1'
# Provide a deterministic HMAC secret
os.environ['HMAC_SECRET'] = 'perf_test_secret'

# Import the function under test
from generate_tickets import generate_for_guest, load_templates, _get_hmac_secret

# Prepare templates and secret
templates = load_templates()
secret = _get_hmac_secret()
if not secret:
    raise SystemExit('HMAC secret not found; set HMAC_SECRET env var')

# Prepare a fake row
row = {
    'first_name': 'Perf',
    'last_name': 'Tester',
    'email': 'perf.tester@example.com',
    'phone': '0600000000',
    'school': 'Test University',
    'cin': 'PT000001',
    'ticket_type': 'etudiant'
}

# Disable actual email sending by passing send_email_flag=False inside wrapper
from functools import partial

# We'll call a wrapper that uses send_email_flag=False
def run_once(i):
    start = time.perf_counter()
    generate_for_guest(row, templates, secret, send_email_flag=False)
    end = time.perf_counter()
    return end - start

# Run N iterations (small by default)
N = 5
print(f"Running {N} iterations of generate_for_guest (no email, no Firestore)...")
timings = []
for i in range(N):
    t = run_once(i)
    timings.append(t)
    print(f"  Iter {i+1}: {t:.3f} sec")

print('\nSummary:')
print(f"  Min: {min(timings):.3f}s")
print(f"  Max: {max(timings):.3f}s")
print(f"  Mean: {statistics.mean(timings):.3f}s")
print(f"  Median: {statistics.median(timings):.3f}s")

# Show suggestions based on observed mean
mean = statistics.mean(timings)
print('\nPreliminary recommendations:')
if mean > 1.0:
    print(' - PDF generation and image I/O are likely hotspots. Consider:')
    print('    * Reusing a single PDF template merge approach instead of rendering full pages for every ticket.')
    print('    * Generating QR images in-memory (PIL) and embedding without saving to disk.')
    print('    * Offloading PDF generation to a worker queue (Celery / RQ) for bulk ops.')
else:
    print(' - Current per-ticket time is okay; profile if you plan to generate many tickets concurrently.')

print('\nNote: For more detailed hotspots run the script under cProfile or use line_profiler.')
