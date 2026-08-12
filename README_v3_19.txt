THE GAUR CRM v3.19 — PRIORITY NOTIFICATION CENTER

BUILT FROM THE INTERNAL CHAT SCREEN REVIEW

WHAT CHANGED
• Every logged-in employee now gets a Notification Bell.
• A compact Priority Update strip appears at the top of normal CRM pages.
• Important unread updates are shown before routine messages.
• Full Notification Center added to sidebar.
• Notifications combine:
  - Direct employee chat messages
  - MD / GM Management Broadcasts
  - Urgent Notices
  - Lead Alerts
  - Target Updates
  - Announcements
• New/Unread highlighting.
• Mark All Read.
• Priority sorting:
  URGENT > LEAD ALERT > TARGET UPDATE > ANNOUNCEMENT > DIRECT CHAT > NORMAL.
• Notification visibility automatically follows existing company/role broadcast rules.
• AM, GM, MD and other logged-in employee portals receive the same notification mechanism.

IMPORTANT
The system does not depend on the user opening Internal Chat first.
The highest-priority unread update is surfaced on normal portal screens via the top Priority Update bar and bell badge.

TEST
1. MD sends URGENT broadcast to Only AMs.
2. Login as an AM. Confirm:
   - red/high-priority update strip on portal
   - bell unread count
   - Notification Center NEW item
3. MD sends normal direct message to AM.
4. Confirm urgent broadcast stays above normal direct message.
5. GM sends Target Update to own company.
6. Confirm only authorized company staff receive it.
7. Mark All Read and confirm badges clear.

DEPLOY
1. Extract ZIP.
2. GitHub -> Add file -> Upload files.
3. Replace ONLY root app.py.
4. Commit: CRM v3.19 Priority Notification Center
5. Wait for Railway Deployment successful.
6. Ctrl + F5.

Existing PostgreSQL data, chats, attachments, leads, profiles, rankings and performance remain preserved.
Do NOT change DATABASE_URL or PostgreSQL.
