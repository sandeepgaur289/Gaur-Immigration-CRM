THE GAUR CRM v4.7 — SPEED LITE

Built after reviewing the user's screen recording of slow page transitions.

Runtime optimizations:
1. AM performance ranking:
   - Removed N+1 database pattern (previously ~2 queries per AM).
   - Replaced with grouped queries.
   - Added a 15-second in-process dashboard result cache.

2. Database indexes:
   - Leads: assigned AM, company, import date, assignment date.
   - Enrollment/client cases: enrollment date, lead link, assigned employee.
   - Chat: recipient and sender/recipient message indexes.
   These are additive and preserve existing data.

3. Chat server load:
   - Global new-message check: 12 seconds while active, 30 seconds when tab is hidden.
   - Active conversation refresh: 4 seconds; 12 seconds when hidden.
   - Focus/visibility still triggers an immediate refresh.

4. Browser caching:
   - Versioned JS/CSS/icons cached for 7 days.
   - Profile photos cached for 5 minutes.
   - Dynamic HTML/JSON remains no-store.

5. HTML injection cleanup:
   - Lead Status JS loads only on pages with a status dropdown.
   - Report Tools JS loads only when report toolbar buttons exist.
   - Security injection runs only on login or MD pages.
   - Standalone Chat page skips duplicate global chat injection.

Preserved:
- Dashboard calculations
- Leads and allocations
- Enrollment automation
- Accounts
- Reporting / Print / Excel / WhatsApp
- Lets Chat Upp!!!!
- Security Settings / Gmail OTP
- All role permissions

legacy_core.py remains byte-for-byte unchanged.
No destructive DB migration.
