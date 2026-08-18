GAUR CRM v4.0.2 — MODULES PACKAGING + RAILWAY BOOT FIX

Exact issue fixed:
Railway Deploy Logs showed:
  ModuleNotFoundError: No module named 'modules'

Fixes:
• modules/ is included at repository root.
• Every module directory has __init__.py.
• app.py explicitly adds repository root to sys.path before imports.
• wsgi.py explicitly adds repository root to sys.path before importing app.
• Railway starts with gunicorn wsgi:app on $PORT.
• /healthz remains the Railway healthcheck path.
• requirements.txt and Procfile are included.
• Existing legacy_core.py and application data behavior are preserved.

Important GitHub rule:
Extract this ZIP and upload/commit all contents to repository root.
Do not upload the ZIP itself as one repository file.
