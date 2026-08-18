"""GAUR CRM v4.0.1 — Railway-safe modular entrypoint.

Compatible with:
  python app.py
  gunicorn app:app
"""
import os
import traceback

from legacy_core import app, init_db
from modules import register_modules

register_modules(app)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5050"))

    # Preserve old Railway resilience: database/migration problems must not
    # prevent the HTTP server from binding, so /healthz remains reachable.
    try:
        init_db()
        print("GAUR CRM v4.0.1 database initialization: OK", flush=True)
    except Exception:
        print("\nGAUR CRM DATABASE INITIALIZATION WARNING:\n", flush=True)
        traceback.print_exc()

    print(f"GAUR CRM v4.0.1 listening on 0.0.0.0:{port}", flush=True)

    try:
        from waitress import serve
        serve(app, host="0.0.0.0", port=port, threads=8)
    except ImportError:
        # Fallback for environments where Railway starts with `python app.py`
        # before waitress is installed.
        app.run(host="0.0.0.0", port=port, debug=False)
