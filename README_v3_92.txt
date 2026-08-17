GAUR CRM v3.92 — Buttons + GM Merge Fix

• Rebuilt from stable v3.86.
• Back is now a direct Dashboard link, so it will not send the user back to Login.
• WhatsApp Share is a direct self-contained click action.
• Print / Save PDF directly calls the browser print dialog.
• Download Excel is self-contained and exports current page/report content.
• Reporting remains a direct server link.
• Old button event-listener dependency is bypassed.

GM Dashboard:
• Live Performance + Today's Report merge into ONE isolated luxury panel.
• No old scoreboard DOM elements are moved.
• Existing live values and progress meters are mirrored every second.
• Old separate boxes hide only after the merged panel is built successfully.
• No server-side Jinja dashboard cutting.

Validation:
• Python syntax PASSED.
• Direct-tools JavaScript syntax PASSED.
• GM merge JavaScript syntax PASSED.
