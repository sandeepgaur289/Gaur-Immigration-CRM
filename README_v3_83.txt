GAUR CRM v3.83 — SAFE RECOVERY

Why:
• v3.82 attempted to cut/rebuild the dashboard Jinja template after startup.
• That could leave an invalid dashboard template and cause HTTP 500.

Recovery approach:
• Rolled back to the working v3.81 merged-dashboard build.
• No template slicing/reassembly is used.
• On MD dashboard only, CSS hides:
  1) the old standalone Live Performance bar;
  2) the old outer Today's Report header/border.
• The existing merged "LIVE PERFORMANCE + TODAY'S REPORT" panel remains visible.
• GM/AM/other portal behavior remains unchanged.
• No database, lead, enrollment, payment, account or permission logic changed.

Python syntax validation passed.
