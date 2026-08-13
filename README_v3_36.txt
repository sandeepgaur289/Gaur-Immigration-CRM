THE GAUR CRM v3.36 — BANK MANAGER + PAYMENT SHARING

NEW
• Accounts submenu now includes Bank Manager.
• MD can add approved company bank accounts with:
  Bank Name, Account Nickname, Account Name, Account Number, IFSC, Branch, City,
  UPI ID, Account Type, Opening Balance, Bank RM Name and RM Mobile.
• All authorized employee roles get Company Payment Accounts.
• Employees can see full approved receiving account details for their own company.
• Known Indian bank names attempt to show the bank logo automatically.
• If a bank logo cannot load, a clean initials badge is shown instead.
• UPI-enabled accounts get an on-screen QR code.
• Employee enters client WhatsApp number and clicks WhatsApp Payment Details.
• Professional company-specific WhatsApp message is generated.
• Client-facing message contains NO “Powered by THE GAUR Portal”.
• Every bank-details share is logged with employee, bank, recipient and date/time.
• MD/GM get Bank Details Share History.
• Existing Daily Passbook and Bank Reconciliation remain intact.

SECURITY
• Only MD can add bank accounts in the current management workflow.
• Employees can view/share only active approved accounts for their company.
• Share actions are audit logged.
• Management Bank Manager masks account number for GM; MD sees full number.
• Employee Payment View intentionally shows full approved receiving account details because it is designed for client sharing.

QR NOTE
The QR is generated from the configured UPI ID. The browser loads a QR rendering library from CDN.
If the CDN is unavailable, bank details still remain fully visible/shareable.

SAFE DEPLOY
1. Keep v3.35 backup.
2. Replace ONLY GitHub root app.py.
3. Commit: CRM v3.36 Bank Manager Payment Sharing
4. Wait for Railway success.
5. Ctrl+F5.
6. MD -> Accounts -> Bank Manager -> add one test account with UPI ID.
7. Login as AM/employee -> Company Payment Accounts -> test QR and WhatsApp.
8. MD/GM -> Bank Manager -> Share History -> verify audit entry.
