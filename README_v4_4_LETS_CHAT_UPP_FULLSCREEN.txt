GAUR CRM v4.4 — LETS CHAT UPP!!!! FULL-SCREEN MESSENGER

What changed:
• /chat is now a true standalone full-screen messenger page.
• It does NOT extend the CRM dashboard base template.
• Therefore Live Performance, dashboard cards, report buttons, broadcast box and leaked report JavaScript
  cannot overlap the chat screen anymore.
• Left column = recent conversations, profile photo, last message, time, unread counter, online status.
• Right column = selected conversation with familiar messenger-style bubbles and fixed composer.
• Search filters: All / Unread / Online / Smart Choice / White Wave.
• Home/Dashboard button available from chat header.
• Mobile layout switches cleanly between chat list and conversation.

Messaging:
• 2-second live refresh.
• AJAX send; no full-page reload.
• Enter to send / Shift+Enter for new line.
• Sent/read ticks.
• Images inline.
• Documents and Excel/PDF cards.
• Audio files inline.
• Microphone voice notes.
• Emoji picker.
• CRM Client sharing.
• 25 MB attachments.

Notifications:
• Existing cross-page sound/toast/browser notification retained.
• Old floating launcher label is changed client-side to “Lets Chat Upp!!!!”.
• Browser autoplay rule still requires one initial “Enable Chat Alerts” click.

Architecture safety:
• legacy_core.py remains byte-for-byte unchanged.
• Dashboard, Leads, Accounts, Enrollment and Performance code are not edited.
• All chat work stays in modules/chat/.
• No DB schema change.

Design note:
The layout is intentionally familiar to modern messaging apps, but uses GAUR CRM branding and original code/assets
rather than copying proprietary WhatsApp branding or assets.
