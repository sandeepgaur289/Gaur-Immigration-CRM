GAUR CRM v3.12 — PROFILE PHOTOS + UNIFIED BRANDING

NEW:
- Smart Choice / White Wave logos are larger and consistent across portals.
- Every logged-in portal user has My Profile / Photo under their name.
- MD, GM, AM and other portal users can upload JPG/PNG/WEBP profile photos.
- Photo displays beside the user's name in the sidebar.
- If the same person exists in Employee Information with same company + same full name, the photo automatically syncs to that employee record, so Performance Analysis can use it too.
- Photos are stored in PostgreSQL database, not Railway's temporary filesystem.
- User can replace/remove their photo anytime.

DEPLOY:
1. Extract ZIP.
2. GitHub -> Gaur-Immigration-CRM -> Add file -> Upload files.
3. Upload ONLY app.py to repository root.
4. Commit: CRM v3.12 Profile Photos Unified Branding
5. Wait for Railway Deployment successful.
6. Ctrl+F5.
7. Click My Profile / Photo under the logged-in user's name.

Do NOT change DATABASE_URL or PostgreSQL.
