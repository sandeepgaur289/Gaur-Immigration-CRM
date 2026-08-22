THE GAUR CRM v4.9.0 — CORE ONLY / PERFORMANCE CLEANUP

TEMPORARILY REMOVED FROM ACTIVE CRM
- Performance Analysis
- Management Reporting
- Internal Chat
- Notifications
- MD Chat Oversight
- All Chat / Communication features:
  user list, private chat, profile-presence chat UI, online/last-seen,
  message notifications, sound alerts, file/image sending, audio/voice notes,
  WhatsApp-style chat UI.

WHAT REMAINS
- Login / role security
- MD / GM / AM dashboards
- Employee Details
- Accounts
- Lead Upload
- Lead Allocation
- My Leads
- Direct Single Lead
- Client Lead Profile
- Lead Status / Ranking / Follow-up
- Enrollment / Payment
- Filing
- Reporting tools other than Management Reporting
- Activity & Security Center
- Company Payment Accounts
- Daily Cash Book / core finance

PERFORMANCE CHANGES
- Chat module is NOT imported or registered.
- Chat alert JavaScript is NOT installed.
- Performance Analysis patch is NOT installed.
- Chat/Notification context processor now performs ZERO DB queries on normal pages.
- Dashboard reminders no longer query chat unread counts.
- Old removed-feature URLs redirect to Dashboard.
- No database schema changes and no data deletion.
- Removed feature code/data is not deleted from DB, so it can be rebuilt later.

This is intentionally reversible.
