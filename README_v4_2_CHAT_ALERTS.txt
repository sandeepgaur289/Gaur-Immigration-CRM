GAUR CRM v4.2 — CHAT ALERTS

• New internal chat is checked every 5 seconds.
• WhatsApp-style two-tone notification chime.
• In-app popup with sender photo/name, message preview and Open Message.
• Browser notification appears when CRM tab is in background, if permission is allowed.
• Browser-tab title shows unread count.
• One-time Enable Chat Alerts button unlocks sound and asks notification permission.
• Old unread messages do not ring on first load.
• Alerts work while the CRM page remains open/logged in, including background tabs.

Browser limitation:
Modern browsers require one user click before sound can play automatically. This build handles that with the
Enable Chat Alerts button. Alerts after the browser is fully closed or the phone is locked require true Web Push/PWA
push subscription, which should be a separate next enhancement.

Architecture:
• legacy_core.py unchanged.
• Chat alert implementation is isolated in modules/chat/.
• Existing chat database and routes reused.
• No DB schema changes.
