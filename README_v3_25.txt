THE GAUR CRM v3.25 — LEAD ALLOCATION CONTROL CENTER

Built on working v3.24.

NEW
• MD controls both companies; GM controls only own company.
• Exact checkbox selection + Select All Visible.
• Bulk Allocate / Re-allocate selected leads to chosen AM.
• Bulk Delete Selected uses safe Soft Delete / Archive.
• AM has no delete route/control.
• MD Recycle Bin + Restore.
• Worked / Not Worked / Follow-up Overdue based on real lead_activity.
• AM workload: Allocated, Worked, Not Worked, Hot, Positive, Overdue, Work %.
• Search/company/AM/work filters.
• Allocation, archive and restore are audited.
• Archived leads hidden from normal Leads list.

SAFE DEPLOY
1. Keep v3.24 ZIP as backup.
2. Extract this ZIP.
3. Replace ONLY root app.py.
4. Commit: CRM v3.25 Lead Allocation Control Center
5. Wait for Railway success.
6. Ctrl+F5.
7. Test with 2-3 test leads before bulk operations.

TEST
GM -> Lead Allocation Control -> allocate 2 test leads.
AM -> verify assigned leads and confirm there is no delete control.
Update one lead -> GM should show WORKED.
Leave one untouched -> NOT WORKED.
Archive a test lead -> MD Recycle Bin -> Restore.
