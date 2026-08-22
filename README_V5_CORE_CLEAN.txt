THE GAUR CRM v5.0.1 — STRICT CORE CLEAN

REMOVED FROM SOURCE / UI
- Performance Analysis
- Management Reporting
- Internal Chat
- Notifications
- MD Chat Oversight
- Chat UI / launchers / polling
- Chat sound, files, audio, voice notes and presence UI
- Active chat/presence/notification routes
- modules/chat
- modules/performance
- modules/reporting

PRESERVED
- Login and role security
- MD / GM / AM dashboards
- Employee Details
- Accounts
- Lead Upload and Allocation
- My Leads
- Direct Lead
- Client Profile
- Lead Status / Ranking / Follow-up
- Enrollment / Payments
- Filing
- Core report tools
- Security Settings / Gmail OTP
- Activity & Security
- Company Payment Accounts / Cash Book

DATABASE
Existing historical chat rows are not destructively deleted from PostgreSQL.
The cleaned application no longer loads, polls, reads or writes the removed communication features.
