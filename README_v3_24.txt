THE GAUR CRM v3.24 — AI FINANCE RECONCILIATION • FINAL STAGE

NEW
• Bank statement upload: XLSX / XLS / CSV.
• Automatic column discovery for Date, Narration, Reference/UTR, Debit, Credit, Balance and Time when available.
• Reconciliation against THE GAUR Finance transactions.
• Matching score uses:
  Amount
  Date proximity
  UTR / Reference
  Party/Narration similarity
• Result classes:
  VERIFIED (high-confidence)
  POSSIBLE
  REVIEW / Unmatched
• Portal entries without bank match highlighted.
• Bank entries without portal receipt/payment highlighted.
• Duplicate bank reference detection.
• Manual Confirm Match control for MD/GM.
• Reconciliation Excel export.
• Bank verification actions are written to Activity & Security Center.

IMPORTANT
This is an AI-style reconciliation assistant, not autonomous accounting.
It never silently edits/deletes finance entries.
Management remains responsible for confirming ambiguous matches.
Statement time is used only when provided by the bank; the portal never invents transaction times.

TEST
1. Add correct Bank Account in Bank & Cash Master.
2. Post 2-3 test receipts/payments.
3. Upload the matching bank XLSX/CSV.
4. Verify exact amount/date/UTR becomes VERIFIED.
5. Verify amount-only entries become POSSIBLE.
6. Verify unmatched bank credit appears under Needs Attention.
7. Confirm a possible match manually.
8. Export reconciliation Excel.

DEPLOY
Replace ONLY repository-root app.py.
Commit: CRM v3.24 AI Finance Reconciliation Final
Wait for Railway success -> Ctrl+F5.
MD/GM -> AI Bank Reconciliation.
