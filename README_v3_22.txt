THE GAUR CRM v3.22 — ACTIVITY & SECURITY CENTER

MD now has a centralized audit trail for portal activity.

TRACKED
• Successful Login
• Failed Login attempts when invalid credentials are rejected
• Logout
• Client / Lead data-changing actions
• Lead Management actions
• Chat / Management Broadcast actions
• Employee / Portal Identity changes
• Reception / Visitor changes
• Notification actions
• Other authenticated POST/data-changing actions

CLIENT OLD -> NEW
For client/lead profile POST updates, the audit captures old and new:
Status • Interest % • Next Follow-up.

ACTIVITY CENTER FILTERS
Date range • Company • Employee • Activity category • Severity • Search.

SECURITY
• MD: both companies.
• GM: own-company scope only.
• Employees cannot edit/delete audit records through normal portals.
• Password/OTP fields are masked and never stored in audit details.
• Audit event includes timestamp, IP, request path and user-agent where available.
• Audit logging failure never blocks the user's normal work.

DEPLOY
Extract ZIP -> replace ONLY repository-root app.py -> commit:
CRM v3.22 Activity Security Center
Wait for Railway success -> Ctrl+F5 -> MD sidebar -> Activity & Security Center.

TEST
AM login -> update client -> send chat -> logout -> MD login -> Activity & Security Center.
