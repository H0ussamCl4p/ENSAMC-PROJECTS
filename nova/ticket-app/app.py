"""Vercel Python entrypoint for Flask.

This file exposes the Flask app object so Vercel's Python runtime can detect it
without needing a Dockerfile. For local/dev and Docker, use dashboard.py.
"""

# Bootstrap: load Firebase service account from env on Vercel
import vercel_bootstrap  # noqa: F401

from dashboard import app as app  # noqa: F401
