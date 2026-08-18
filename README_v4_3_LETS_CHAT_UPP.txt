GAUR CRM v4.3 — LETS CHAT UPP!!!!

Purpose:
Rebuild the internal chat as a fast messenger-style experience while keeping the existing CRM database,
permissions, users, broadcasts, attachments and chat history.

Features:
• Chat name: "Lets Chat Upp!!!!"
• Familiar WhatsApp-style two-column messenger layout (without copying proprietary branding/assets).
• Recent chats automatically sorted by latest message.
• Last-message preview, time, unread badge and online presence dot.
• Existing profile photos are used.
• Live conversation refresh every 2 seconds — no manual page refresh required.
• AJAX send — messages stay on the same screen.
• Enter sends; Shift+Enter creates a new line.
• Sent / read ticks.
• Images display inline.
• Documents download/open in a file card.
• Audio files display with an inline audio player.
• Audio file upload supported: MP3, WAV, M4A, AAC, OGG, OPUS, WEBM.
• Built-in microphone voice-note recorder.
• Emoji picker.
• CRM Client sharing retained.
• Management Broadcasts retained.
• Cross-page sound/toast/browser notifications from v4.2 retained.
• Attachment limit increased to 25 MB.

Architecture protection:
• legacy_core.py remains byte-for-byte unchanged.
• Existing /chat and /chat/send URLs are retained by replacing endpoint handlers at runtime.
• New chat implementation lives only under modules/chat/.
• Leads and Performance modules remain unchanged.
• No database schema change.

Browser note:
Voice recording requires microphone permission and HTTPS. Railway HTTPS supports this.
Cross-page sound still requires the user to enable chat alerts once due to browser autoplay rules.
