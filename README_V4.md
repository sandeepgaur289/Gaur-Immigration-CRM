# GAUR CRM v4.0 — Stable Foundation

This release is intentionally a **foundation release**.

It preserves the current v3.98 application and database behavior as a frozen compatibility core,
while changing the development architecture so future work is isolated by module.

Deployment command remains unchanged:

    gunicorn app:app

New v4 work should be added only under `modules/`.
