GAUR CRM v3.65 — ENROLLMENT REPORT FULL STABILITY FIX

Video review:
• Dashboard, Accounts, Performance and other pages open normally.
• Only Enrollment Report (/accounts/client-ledger) returns HTTP 500.

This build removes every optional dependency from page opening:
• Enrollment ledger loads first from core client_cases only.
• Optional Lead ID/AM enrichment is best-effort.
• Optional Bank Manager enrichment is best-effort.
• Optional payment-proof links are best-effort.
• Missing newer columns are filled with safe defaults before rendering.
• Old Enrolled-lead repair is wrapped so legacy-data/schema issues cannot block the page.
• No active bank account does not block Enrollment Report.
• Full payment fields, Bank Manager selectors, payment modes and screenshots remain available when schema is ready.
• Expanded lazy migration covers all package/payment/split-payment/Lead-ID fields used by the ledger.
• Payment proof route is also backward-safe.

The goal of v3.65 is simple: Enrollment Report must OPEN first; optional finance features may degrade gracefully instead of causing a 500.
