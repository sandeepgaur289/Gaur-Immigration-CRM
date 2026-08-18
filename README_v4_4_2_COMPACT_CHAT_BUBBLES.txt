GAUR CRM v4.4.2 — COMPACT SOPHISTICATED CHAT BUBBLES

Fixes the oversized/tall message boxes visible in the user's screenshots.

Changes:
• Message bubble width is now content-driven (auto), not stretched.
• Height is strictly auto with min-height removed.
• Maximum desktop bubble width = 72% / 640px.
• Mobile maximum bubble width = 86%.
• Short messages like “hello” remain small compact bubbles.
• Long messages wrap naturally.
• Time and sent/read ticks sit neatly at bottom-right.
• Added subtle incoming/outgoing bubble tails.
• Reduced vertical spacing for consecutive messages.
• Added a JS normalization pass so dynamically received messages cannot inherit oversized dimensions.
• Images, audio, documents, voice notes and CRM-client cards retain their media-specific sizing.

Architecture:
• legacy_core.py remains byte-for-byte unchanged.
• Only modules/chat presentation files changed.
• No database changes.
