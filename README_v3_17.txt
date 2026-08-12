THE GAUR CRM v3.17 — INTERNAL CHAT + MANAGEMENT BROADCAST

READY FOR TESTING

NEW
• Floating modern chat button on every logged-in portal.
• Full Internal Chat Center.
• Secure one-to-one employee messaging.
• Unread badges and Read/Delivered status.
• Employee photos + full professional designations in chat.
• Secure Client Lead sharing with Open Client Profile link.
• PostgreSQL-backed messages and broadcasts.

PERMISSIONS
Managing Director:
• Private chat with authorized staff across both companies.
• Broadcast to All GMs + AMs.
• Broadcast only to GMs.
• Broadcast only to AMs.
• Broadcast to one selected company.
• Broadcast to all staff across both companies.

General Manager:
• Private chat with own company team + management.
• Broadcast to own-company AMs.
• Broadcast to entire own-company team.

AM / Reception:
• Private chat with authorized own-company staff + management.

BROADCAST TYPES
Announcement • Urgent Notice • Target Update • Lead Alert • Normal.

SECURE LEAD SHARING
AM can attach only leads assigned to that AM.
GM can attach company leads.
MD can attach authorized leads across both companies.
Chat never bypasses existing client-profile authorization.

TEST PLAN
1. MD -> one GM private message.
2. MD -> one AM private message.
3. MD broadcast -> Only GMs.
4. MD broadcast -> Only AMs.
5. MD broadcast -> GMs + AMs.
6. GM -> own company AM broadcast.
7. AM login -> confirm unread badge.
8. AM shares one assigned lead with GM.
9. GM opens the shared client profile.
10. Repeat from the second office computer.

DEPLOY
1. Extract ZIP.
2. GitHub -> Add file -> Upload files.
3. Replace ONLY repository-root app.py.
4. Commit: CRM v3.17 Internal Chat Broadcast
5. Wait for Railway Deployment successful.
6. Ctrl + F5.
7. Confirm floating chat button appears.

Do NOT change DATABASE_URL or PostgreSQL.
