THE GAUR CRM v3.21 — RAILWAY HEALTHCHECK + STARTUP RESCUE

WHY THIS BUILD EXISTS
Your Railway screenshot shows:
Initialization ✓
Build ✓
Deploy ✓
Network / Healthcheck ✗

That means the image builds, but Railway does not receive a healthy HTTP response in time.

WHAT v3.21 CHANGES
1. /healthz is now a pure liveness endpoint.
   It returns HTTP 200 as soon as the web application is listening.
   PostgreSQL latency/failure no longer makes Railway's liveness check fail.

2. /readyz is added separately.
   /readyz checks PostgreSQL and reports ready/degraded for database diagnostics.

3. Startup is resilient.
   If a database migration has a temporary problem, the error is logged but Waitress still binds to Railway's PORT.
   This prevents one migration exception from causing "Network / Healthcheck failure".

4. Gunicorn/import startup is also protected.
   If Railway starts `app:app`, schema initialization is attempted safely without crashing the process.

5. Attachment migration is idempotent.
   PostgreSQL uses:
   ALTER TABLE chat_messages ADD COLUMN IF NOT EXISTS attachment_id BIGINT

6. Chat/notification indexes are added as non-critical performance helpers.

PRESERVED
- Internal Chat
- Photo/document attachments
- Secure official lead sharing
- Priority Notification Center
- Management Broadcasts
- Employee identity/profile/rank system
- Existing PostgreSQL data and DATABASE_URL

DEPLOY
1. Extract this ZIP.
2. GitHub -> Gaur-Immigration-CRM -> Add file -> Upload files.
3. Replace ONLY root app.py.
4. Commit:
   CRM v3.21 Railway Healthcheck Startup Rescue
5. Wait for Railway.
6. Healthcheck should now be able to reach /healthz once the server binds.
7. Ctrl + F5 after deployment.

IMPORTANT RAILWAY SETTING
If Railway has a custom Healthcheck Path configured, set it to:
/healthz

Do not change DATABASE_URL or PostgreSQL.
