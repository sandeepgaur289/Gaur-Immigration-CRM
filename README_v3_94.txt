GAUR CRM v3.94 — CLEAN CODE LEAK FIX

Fixes:
• Removes the visible JavaScript/code text that was printing on the Dashboard.
• Global controls are clean markup only.
• WhatsApp / Print / Excel JavaScript is injected safely at runtime before </body>.
• Back is a direct Dashboard link.
• Reporting remains a normal server route link.
• Chat branding remains "Chat Upp GYS".
• User-supplied chat logo remains WhatsApp green in the chat header and floating button.
• Stable v3.86 dashboard/reporting behavior is retained.
• No dashboard Jinja cutting or risky DOM surgery in this build.

Validation:
• Python syntax PASSED.
