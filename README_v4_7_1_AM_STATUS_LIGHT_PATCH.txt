THE GAUR CRM v4.7.1 — AM STATUS LIGHT PATCH

Final official AM revert/status options:
1. Interested
2. Not Interested
3. Call Back
4. Not Picked
5. No Plan
6. Budget Issue
7. Not Connected
8. Invalid No.
9. No WhatsApp
10. Enrolled
11. Discussion
12. Follow Up
13. Payment After Visa
14. Closed
15. Office Visit
16. Docs Received

Performance / safety:
- No MutationObserver.
- No polling.
- No API/database request added.
- Script loads only on pages that actually contain select[name="status"].
- Existing legacy_core.py remains byte-for-byte unchanged.
- Existing Dashboard, Chat, Accounts, Enrollment, Reporting, Security and DB remain untouched.
- "Enrolled" remains the exact canonical value required by the current enrollment workflow.

Historical compatibility:
Called -> Call Back
Follow-up -> Follow Up
Visit -> Office Visit
Documents Pending -> Docs Received
Enroled -> Enrolled
