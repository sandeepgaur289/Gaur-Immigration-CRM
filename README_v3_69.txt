GAUR CRM v3.69 — /CASES PAYMENT PAGE CRASH FIX

Screenshot-confirmed issue:
• Enrollment Report safe route works, but clicking "Open Full Payment Form" opens /cases and returns HTTP 500.

Root fix:
• Old complex /cases route has been moved to /cases-legacy.
• A brand-new isolated GET /cases route now opens the GM payment editor.
• It does NOT run old enrollment repair, legacy create logic, or fragile joins on page load.
• Core client_cases rows load first.
• Lead ID, passport, AM, bank labels and proof links are best-effort only.
• No active bank account cannot crash /cases.
• New screen visibly shows: SAFE PAYMENT ROUTE • /cases

Payment editing retained:
• Package Amount / After Visa
• 1st Payment Cash + RBL + Yes Bank + AU Bank
• 2nd Payment Cash + RBL + Yes Bank + AU Bank
• Other Payment
• Bank Manager active account selector
• QR/UPI / Net Banking / Cash Deposit / Cheque / Card-POS / Cash / Other
• Date & Time
• Screenshot / Proof upload + existing proof link
• Same Lead ID / Open Client

This version isolates both the report route and the payment-edit route from the failing legacy loader.
