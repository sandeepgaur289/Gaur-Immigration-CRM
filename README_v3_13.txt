THE GAUR CRM v3.13 — PROFESSIONAL EMPLOYEE IDENTITY SYSTEM

MAJOR UPGRADE
1. Team Identity Center for MD / GM.
2. Permanent professional identity linking:
   Portal User -> Employee Record -> Employee ID -> Company -> Official Mobile -> Performance.
3. Management can create:
   - General Manager (MD only)
   - Assistant Manager
   - Reception
4. Every identity stores:
   - Employee ID
   - Official mobile
   - Official email
   - Designation
   - Department
   - Branch
   - Joining date
   - Reporting manager
   - Profile photo
   - Account status
   - Mobile verification status
5. Employee can personalize only:
   - Profile photo
   - Professional headline
   - Professional bio
   Management-controlled identity fields stay protected.
6. Digital Employee ID Card with Print / Save.
7. Current AM performance identity on personal profile.
8. Existing legacy MD / GM / AM accounts are automatically given permanent identity codes.
9. New AM creation also creates a linked employee record automatically.
10. OTP-ready architecture:
    Official mobile + mobile_verified status are now part of the permanent user identity.
    Actual SMS OTP sending/verification will be activated in the next security build after an SMS provider is connected.
11. Existing PostgreSQL data, leads, client profiles, monthly analytics, rankings and profile photos remain preserved.

DEPLOY
1. Extract ZIP.
2. GitHub -> Gaur-Immigration-CRM -> Add file -> Upload files.
3. Upload ONLY app.py to repository root and replace the current app.py.
4. Commit directly to main.
5. Commit message: CRM v3.13 Professional Employee Identity System
6. Wait for Railway Deployment successful.
7. Press Ctrl+F5.
8. Open Team Identity Center from MD/GM sidebar.
9. Verify footer shows: CRM v3.13 • PROFESSIONAL IDENTITY ACTIVE

IMPORTANT
- Do NOT change DATABASE_URL or PostgreSQL.
- This build prepares OTP security but does NOT send real SMS OTP yet.
