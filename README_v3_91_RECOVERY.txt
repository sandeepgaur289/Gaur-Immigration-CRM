GAUR CRM v3.91 FUNCTIONALITY RECOVERY BUILD

IMPORTANT:
This build is restored directly from the last stable v3.86 base.
No dashboard DOM movement.
No base-template CSS surgery.
No replacement of existing navigation JavaScript.
No merged-panel experimental JavaScript.

Critical controls verified present:
- Back
- WhatsApp Share
- Print / Save PDF
- Download Excel
- Reporting
- Dashboard
- Employee Details
- Accounts
- Performance Analysis
- Lead Upload & Allocation
- Enrollment Payment Report
- Filing Department

Reason:
The v3.89/v3.90 experimental GM merged-panel patches modified the global base template.
That can interfere with global navigation/action controls. This recovery build removes those
experimental changes completely and restores the stable interaction layer first.

Python syntax: PASSED
