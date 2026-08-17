GAUR CRM v3.60 — Lead ID Enrollment → GM Accounts Sync

FIXED CORE WORKFLOW
1. AM updates the SAME lead/client status to Enrolled.
2. System automatically creates ONE linked Enrollment/Client Account shell using lead_db_id.
3. Client immediately appears in GM Enrollment / Client Accounts.
4. GM gets the existing modular payment form for Package, After Visa, 1st Payment breakup/status/date-time,
   2nd Payment breakup/status/date-time, Other Payment/date-time, Filing, Counselor and Remarks.
5. Until GM fills finance details, record is highlighted PENDING GM COMPLETION.
6. Open Client returns to the exact AM-maintained Lead ID; no duplicate client is created.
7. Existing Enrolled leads that were missed by older versions are auto-repaired when GM/MD opens Enrollment.
8. AM quick-update (/my-leads) and full client profile update both trigger the same sync.
9. Payment values start at 0 / Pending. AM does not create or invent payment values.
10. Existing v3.59 features remain included.
