THE GAUR CRM v3.29 — ADMIN CONTROL + OFFBOARDING

BUILT ON v3.28.

1. ACTIVE SIDEBAR
• Current module automatically receives gold active highlight.
• Highlight follows nested/sub-pages by URL path.

2. RECYCLE BIN — MD + GM
• Select individual leads / Select All.
• Restore Selected.
• Permanently Delete Selected.
• Empty Recycle Bin.
• GM is restricted to own-company archived leads.
• MD can manage both companies.
• Permanent erase removes lead + lead_activity data.
• A minimal security audit event is retained.

3. DASHBOARD TOTALS
• Archived/Recycle Bin leads are excluded from dashboard lead KPIs.
• Company totals/charts using dashboard lead queries also exclude archived leads.
• Restored leads return to active calculations.

4. EMPLOYEE OFFBOARDING
• MD/GM can Deactivate Employee ID within authorization scope.
• Deactivation immediately blocks login while preserving history.
• Reactivate option is available.
• MD-only Permanent Delete ID for inactive IDs.
• Permanent ID deletion is BLOCKED if leads remain assigned to that employee.
• Employee master/audit history is retained.

SAFE DEPLOY
1. Keep v3.28 backup.
2. Replace ONLY GitHub root app.py.
3. Commit: CRM v3.29 Admin Control Offboarding
4. Wait for Railway deployment success.
5. Ctrl+F5.
6. Test with a test lead + test employee first:
   archive lead -> dashboard count should drop -> restore -> count returns.
   deactivate test employee -> login blocked -> reactivate.
   permanent erase only on disposable test data.
