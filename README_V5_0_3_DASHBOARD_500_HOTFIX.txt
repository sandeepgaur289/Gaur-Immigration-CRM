THE GAUR CRM v5.0.3 — DASHBOARD 500 HOTFIX

CAUSE FOUND
The no-chat build correctly removed Chat / Notifications routes, but a later dashboard
template customization still had:
- url_for('notification_center')
- url_for('chat_center')

Because those endpoints no longer existed, Jinja/Flask could raise a BuildError while
rendering /dashboard, resulting in "Internal Server Error".

FIX
- Removed only the leftover Dashboard Notifications / Messages links.
- Removed the leftover Messages action button.
- Removed leftover notifications API string.
- Dashboard, Performance Analysis, Management Reporting, Accounts, Leads, Allocation,
  Client Profile, Enrollment, Filing, Security and all other core CRM features are preserved.
- No database schema or production data changed.
