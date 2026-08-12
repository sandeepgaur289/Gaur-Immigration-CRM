GAUR CRM v3.3 ROOT-ONLY UI FIX

WHY THIS PATCH EXISTS
The latest Railway deployment was successful, but GitHub browser upload had not replaced the
templates/static folders. Therefore Railway kept showing the old My Leads layout.

THIS PATCH FIXES THAT PERMANENTLY:
- Corrected templates are embedded inside app.py itself.
- Only app.py needs to be replaced in the GitHub repository root.
- No templates folder replacement is required.
- Smart Choice and White Wave logos are embedded directly in app.py.
- My Leads shows a clear OPEN CLIENT PROFILE button.
- Client profile workspace is available even if lead_profile.html is missing from GitHub.
- MD/GM dashboard uses the AM-wise allocation table.
- Existing PostgreSQL data and DATABASE_URL are untouched.

UPLOAD:
1. GitHub repository -> Add file -> Upload files.
2. Upload ONLY app.py from this patch folder.
3. Commit directly to main.
4. Commit message: CRM v3.3 Root UI Fix
5. Wait for Railway deployment to show Active / Deployment successful.
6. Refresh CRM using Ctrl+F5.
7. Bottom-right must show: CRM v3.3 • ROOT UI FIX ACTIVE
