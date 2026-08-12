THE GAUR CRM v3.16 — DASHBOARD EMPLOYEE IDENTITY CARD

The highlighted top-right dashboard space now carries the logged-in employee's required identity information:
• Photograph
• Full Name
• Full Professional Designation
• Permanent Employee ID
• Company
• Branch
• Official Mobile
• Selected Month Rank
• Performance Score
• Professional Profile shortcut

AMs use the existing monthly AM ranking engine. GM/Reception rank is displayed only when a real employee performance ranking exists. MD/management profiles without a measurable employee rank show Professional Identity rather than a fake rank.

This header is available on MD, GM, AM and Reception dashboards.
Existing PostgreSQL data, leads, client profiles, photos, rankings, monthly analytics and full professional designations remain untouched.

DEPLOY
1. Extract ZIP.
2. GitHub > Gaur-Immigration-CRM > Add file > Upload files.
3. Replace ONLY app.py at repository root.
4. Commit: CRM v3.16 Dashboard Employee Identity Card
5. Wait for Railway Deployment successful.
6. Ctrl + F5.
