GAUR CRM v3.66 — ISOLATED ENROLLMENT REPORT FIX

Why this version is different:
• The video still shows HTTP 500 only on /accounts/client-ledger while all other pages work.
• Previous versions kept repairing the same large legacy route.
• v3.66 REMOVES /accounts/client-ledger from that legacy route completely.
• A brand-new isolated GET route now owns /accounts/client-ledger.
• It does NOT run schema migrations, legacy auto-repair, complex joins or payment writes while opening.
• It first loads only SELECT * FROM client_cases.
• Lead ID, AM name, Bank Manager labels and payment-proof links are all best-effort enrichment.
• Any optional enrichment failure degrades to '-' instead of HTTP 500.
• No bank accounts = report still opens.
• A separate "Open Full Payment Form" takes GM to the existing editable payment ledger.
• Existing Bank Manager, payment methods, proof uploads and Lead ID workflow remain in the application.

This is an architectural isolation fix, not another patch to the same failing loader.
