GAUR CRM v3.41 — STRUCTURED PAYMENT LEDGER

Requested payment structure implemented:
1. Package Amount + entry date/time
2. After Visa Payment + entry date/time
3. First Payment + payment date/time
4. First Payment Status
5. 2nd Payment + payment date/time
6. 2nd Payment Status
7. Other Payment Received + payment date/time

CALCULATION:
• Package Amount = contractual package value; NOT counted as collection.
• After Visa Payment = contractual/due amount; NOT counted until actually received elsewhere.
• First Payment counts only when status = Received / Partially Received.
• 2nd Payment counts only when status = Received / Partially Received.
• Other Payment Received always counts as actual received amount.
• Actual Collection = qualifying First + qualifying Second + Other Received.
• Pending payments never inflate Dashboard, Competition, AM Performance or Revenue.

AUDIT/TIME:
• All payment fields have date/time storage.
• New amounts auto-stamp current date/time if date/time is left blank.
• Existing timestamps are preserved during later updates unless manually changed.
• Historical records are migrated using the best available created/updated timestamp.

Dashboard SQL expressions replaced with total_received in 8 locations.

The build remains compatible with the existing booking_amount/payment_status columns so older records can be upgraded in place.
