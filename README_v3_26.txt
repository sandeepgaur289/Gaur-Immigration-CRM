THE GAUR CRM v3.26 — VISIBLE LEAD CONTROL FIX

WHY v3.25 LOOKED UNCHANGED
The backend Lead Allocation Control Center was present and Railway deployed successfully,
but the menu injection targeted an older menu label. Therefore the new page was effectively hidden.

v3.26 FIXES
• MD and GM now visibly get “🎯 Lead Allocation Control” in the left menu.
• Existing “Lead Upload & Allocation” page also gets a large “Open Lead Allocation Control Center” card.
• MD: both-company control.
• GM: own-company control.
• Select individual leads or Select All Visible.
• Allocate / re-allocate selected leads to an authorized AM.
• Delete Selected = safe Archive / Recycle Bin.
• AM gets NO delete permission.
• MD can restore archived leads.
• Worked / Not Worked / Overdue monitoring remains active.
• Allocation/archive/restore remains audit logged.

DEPLOY
Replace ONLY root app.py with the app.py in this ZIP.
Commit: CRM v3.26 Visible Lead Control Fix
Wait for Railway “Deployment successful”.
Then Ctrl+F5 and login as MD/GM.

EXPECTED LEFT MENU
Lead Upload & Allocation
🎯 Lead Allocation Control
Team Identity Center
...
