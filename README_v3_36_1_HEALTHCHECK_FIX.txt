THE GAUR CRM v3.36.1 — RAILWAY HEALTHCHECK FIX

Screenshot diagnosis:
Initialization = passed
Build = passed
Deploy = passed
Network > Healthcheck = failed

v3.36 introduced PostgreSQL schema ALTER work during web-process startup. DDL can wait for a
database lock, delaying the HTTP process beyond Railway's healthcheck window.

v3.36.1 FIX
- Bank Manager DDL removed from startup.
- Gunicorn can bind HTTP immediately.
- /healthz returns 200 without depending on PostgreSQL.
- Bank Manager schema upgrades run lazily when Bank Manager/Payment Accounts is first opened.
- PostgreSQL ADD COLUMN uses IF NOT EXISTS.
- DDL lock timeout is limited to 3 seconds.
- Bank Manager, QR, WhatsApp sharing and audit history remain included.

DEPLOY
1. Keep v3.35 as rollback backup.
2. Replace only GitHub root app.py.
3. Commit: CRM v3.36.1 Railway Healthcheck Fix
4. Wait for Railway deployment success.
5. Open /healthz — expected: status ok.
6. Login as MD and open Accounts > Bank Manager.
