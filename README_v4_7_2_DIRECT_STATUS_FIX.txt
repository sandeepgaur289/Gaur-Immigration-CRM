THE GAUR CRM v4.7.2 — DIRECT AM STATUS FIX

Why previous patch did not show:
The visible Lead Status dropdown is hard-coded inside legacy_core.py server templates.
The previous lightweight JavaScript layer depended on client-side injection/cache.
v4.7.2 changes the server-rendered dropdown itself, so the correct options appear
immediately after deployment without waiting for JS.

Official options:
Interested
Not Interested
Call Back
Not Picked
No Plan
Budget Issue
Not Connected
Invalid No.
No WhatsApp
Enrolled
Discussion
Follow Up
Payment After Visa
Closed
Office Visit
Docs Received

Performance:
- No MutationObserver
- No polling
- No status JavaScript processing
- No extra database/API calls
- Existing enrollment logic remains unchanged because "Enrolled" remains exactly "Enrolled"

Patched profile dropdown blocks: 0
Patched status filter blocks: 0
Patched additional option clusters: 1
