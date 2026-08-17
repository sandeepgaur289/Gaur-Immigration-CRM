GAUR CRM v3.64 — ENROLLMENT REPORT CRASH FIX

Video-confirmed issue:
• Clicking Enrollment Report opened /accounts/client-ledger and returned HTTP 500.

Fixes:
• Enrollment Report now uses a best-effort, non-fatal schema migration.
• PostgreSQL/Railway DDL failures or lock delays can no longer crash the report.
• Optional bank/proof fields are detected dynamically before being queried.
• If payment-proof table or bank-id columns are not yet available, the core Enrollment ledger still opens.
• Bank Manager dropdown query is backward-compatible with older bank schemas.
• If no active bank exists, Enrollment Report still opens and shows a clear add-bank notice.
• Existing Bank Manager → 1st/2nd/Other payment selection, payment modes and screenshot/proof upload remain.
• Same Lead ID enrollment sync remains intact.

This build specifically targets the /accounts/client-ledger 500 shown in the supplied video.
