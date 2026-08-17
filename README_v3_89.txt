GAUR CRM v3.89 — GM MERGED LAYOUT FIX

Built from stable v3.86 again.

What was wrong in v3.88:
- The original competition bar still had its own top-level CSS grid rules.
- After inserting Today's cards into that same container, the browser tried to fit too many children
  into the existing grid, causing compressed/squashed cards.

v3.89 fix:
- No server-side Jinja/dashboard template cutting.
- Original Smart Choice, VS, White Wave elements are moved into a dedicated 3-column score row.
- The GM Today module is a separate full-width row below it.
- Today cards have controlled widths, padding, font sizes and overflow behavior.
- Original live score element IDs are retained, so the existing competition API keeps updating scores/meters.
- The old separate Today report is hidden only after the safe merge succeeds.
- MD dashboard remains on the stable v3.86 behavior.
- Reporting, Excel, Chat Up, Accounts, Payments, Enrollment and permissions are unchanged.

Python syntax validation passed.
