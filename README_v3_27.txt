THE GAUR CRM v3.27 — DATA BATCH + TIMELINE CONTROL

NEW
• Every new Excel upload gets a unique Batch ID.
• Every imported lead stores Batch ID + original file name + upload date/time + uploaded by.
• Allocation date/time + allocated by remain visible.
• Latest company batch = NEW/LATEST DATA.
• Previous tracked batches = OLD DATA.
• Pre-v3.27 leads = LEGACY DATA; history is not invented.

FILTERS
Company | Batch | Latest/New | Old | Legacy | AM | Worked/Not Worked/Overdue
Upload date range | Allocation date range | Name/Mobile/Lead/Batch search

BATCH SUMMARY
Batch | Company | Uploaded Date/Time | Uploaded By | File | Total | Allocated | Unallocated | Worked | Not Worked | Positive

AUDIT
Every new upload batch generates an Activity & Security event.

SAFE DEPLOY
1. Keep v3.26 backup.
2. Replace ONLY root app.py.
3. Commit: CRM v3.27 Data Batch Timeline Control
4. Wait for Railway success.
5. Ctrl+F5.
6. Upload one SMALL test Excel.
7. Confirm a Batch ID and NEW BATCH badge appear.
8. Allocate 1-2 test leads and confirm Allocated Date/Time + Allocated By.
9. Then use normal production data.
