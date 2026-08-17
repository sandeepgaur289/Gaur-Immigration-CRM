GAUR CRM v3.74 — Login/Dashboard Emergency Fix

Root cause found from the supplied video:
• Login itself succeeds.
• The HTTP 500 happens immediately after redirecting to Dashboard.
• Enrollment Recycle Bin introduced client_cases.deleted_at in v3.72.
• The live Railway database can still be on the older client_cases schema.
• Dashboard was using deleted_at before guaranteeing the column existed.

Fix:
• Dashboard now runs the recycle-bin schema migration before any dashboard query.
• Dashboard detects whether client_cases.deleted_at exists.
• If it is not available, dashboard safely falls back instead of returning HTTP 500.
• Today's Report and monthly revenue queries use the safe condition.
• No credentials, leads, payments, enrollment records, profile data, or other features are reset.
• v3.73 larger sidebar profile is retained.

This is intentionally a minimal emergency fix to restore login/dashboard access.
