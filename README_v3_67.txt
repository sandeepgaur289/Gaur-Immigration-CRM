GAUR CRM v3.67 — ENROLLMENT ROUTE / LINK FIX

Root cause confirmed from the supplied screenshot:
• Browser URL was /accounts/client-ledger-legacy
• That means the application was STILL navigating to the old legacy Enrollment route.
• Therefore the isolated safe route created in v3.66 was not actually being opened.

v3.67 fixes the routing itself:
• Removes /accounts/client-ledger-legacy from the old complex cases() function.
• Adds a dedicated legacy redirect:
    /accounts/client-ledger-legacy -> /accounts/client-ledger
• Forces all Enrollment Report / Client Accounts menu links to the new isolated endpoint.
• Adds a global template rewrite for any stale legacy URL left in older embedded templates.
• Safe Enrollment page displays:
    SAFE ROUTE • /accounts/client-ledger
  so deployment can be visually verified.
• /cases remains the full editable payment form only.
• Existing Bank Manager / payment mode / payment proof features remain.

This version targets the URL-routing bug shown in the screenshot, not only the database loader.
