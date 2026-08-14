GAUR CRM v3.50 — LIVE PROFILE PHOTO REFRESH

BUG FIXED:
• Old profile photo was being cached for 3600 seconds (1 hour) by the browser.
• Uploading a new photo successfully changed database data, but the same /user-photo URL kept displaying the cached old image.

FIXES:
• Removed 1-hour browser caching from user profile photos.
• Added no-store / no-cache headers to profile photos.
• Added a v3.50 cache-busting query to existing profile photo URLs.
• Synced employee/celebration photo responses also use no-cache behavior.
• After photo upload, profile page redirects with a fresh timestamp.
• Empty photo upload protection added.

RESULT:
Choose a different Profile Photo → Save My Professional Profile → the new photo should show immediately in sidebar/profile without waiting or clearing browser cache manually.

Mobile/PWA support from the clean v3.49 base remains included.
