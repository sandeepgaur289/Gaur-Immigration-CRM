GAUR CRM v4.4.1 — LETS CHAT UPP LAYOUT FIX

Observed issue from user video:
• Chat list page opened correctly.
• After clicking a person, the conversation view became visually broken:
  sidebar/header/composer were effectively lost and only a narrow stack of message bubbles remained.

Fix:
• Stabilized desktop grid columns.
• Forced sidebar + conversation panel visibility on desktop.
• Fixed conversation panel width/overflow.
• Fixed thread padding and bubble max-width.
• Fixed dynamic message CSS class names from old v4.3 names to current v4.4 standalone names.
• Fixed search selectors and message rendering selectors.
• Added resize guard so the layout cannot collapse after navigation.
• Header and composer are explicitly kept visible above the thread.

Preserved:
• Full-screen standalone chat
• 2-second live updates
• AJAX send
• voice notes
• audio files
• images
• documents
• CRM client share
• unread counts / online presence
• cross-page notification sounds

Architecture:
• legacy_core.py remains unchanged.
• Only modules/chat files changed.
