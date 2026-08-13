THE GAUR CRM v3.31 — BACK-DATE CALENDAR FIX

ISSUE FIXED
The old custom calendar was designed mainly for nearby dates and required repeated previous-month clicks.
Date of Birth and Joining Date were therefore difficult/unreliable for historical dates.

NEW DATE PICKER
• Month dropdown directly inside calendar.
• Year dropdown directly inside calendar.
• Historical years available down to 1940 by default.
• Previous / Next month arrows still work.
• Direct typing supported: DD-MM-YYYY.
• Enter commits typed date.
• Selected date is written back to the real hidden form field.
• Both input and change events are fired so form state updates correctly.
• Existing stored DOB / Joining Date opens on its actual month/year.
• Clear and Today remain available.
• Existing min/max attributes are respected where a form intentionally uses them.

IMPORTANT
The fix applies globally to all portal input[type=date] controls, including:
Date of Birth
Joining Date
Follow-up Date
Visit Date
Enrollment Date
and other date fields.

SAFE DEPLOY
1. Keep v3.30 backup.
2. Replace ONLY GitHub root app.py.
3. Commit: CRM v3.31 Backdate Calendar Fix
4. Wait for Railway Deployment successful.
5. Ctrl + F5.
6. Test:
   DOB: 15-04-1990
   Joining: 01-06-2023
   Save employee.
   Re-open profile and confirm both dates persist.
