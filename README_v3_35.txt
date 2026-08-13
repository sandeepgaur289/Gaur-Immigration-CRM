THE GAUR CRM v3.35 — MODULAR SIDEBAR NAVIGATION

BUILT ON v3.34.

NEW CLEAN MD/GM SIDEBAR
1. Dashboard
2. Employee Details
   - Employee Information
   - Assistant Manager
   - Team Identity Center
3. Accounts
   - Daily Passbook
   - Bank Reconciliation
   - Tele Callers
   - Counselors
4. Performance Analysis
   - Performance Dashboard
   - Reception
   - HR Managers
5. Lead Upload & Allocation
   - Lead Upload
   - Lead Allocation
   - Batch Control
   - Filing Department
   - Employee Attendance
6. Enrolment Payment Report
7. Filing Department
8. GM Report

Communication & Security is kept as a separate compact utility group so Internal Chat,
Notifications and Activity & Security Center remain available without cluttering the main workflow.

BEHAVIOR
• Main sections are collapsible.
• The group containing the current page opens automatically.
• Current page gets the existing gold active highlight.
• Reception and Assistant Manager portals keep simplified role-specific navigation.
• No business/data routes were removed; this is a navigation/UI reorganization only.

ROUTE MAPPING
Tele Callers -> Performance Analysis filtered by designation=Telecaller
Counselors -> Performance Analysis filtered by designation=Counselor
HR Managers -> Performance Analysis filtered by designation=HR Manager
GM Report -> Performance Analysis filtered by designation=General Manager
Filing Department / Enrolment Payment Report -> existing Enrollment / Payment / Filing module

SAFE DEPLOY
1. Keep v3.34 backup.
2. Replace ONLY GitHub root app.py.
3. Commit: CRM v3.35 Modular Sidebar Navigation
4. Wait for Railway deployment success.
5. Ctrl+F5.
6. Check MD and GM navigation, then Reception and AM portals.
