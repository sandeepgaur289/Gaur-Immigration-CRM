GAUR CRM v4.5 — MD / GM MANAGEMENT REPORT TOOLS

Fixes the top MD/GM buttons:
• WhatsApp Share
• Print / Save PDF
• Download Excel

Why the previous buttons were unreliable:
Legacy base.html contains old injected JavaScript handlers and an HTML-as-.xls export approach.
v4.5 does not edit the frozen legacy core. Instead it installs a modular, high-priority handler that intercepts
the existing buttons before old handlers can execute.

WhatsApp Share:
• Shares page/report name, company scope, key visible metrics and direct CRM page link.
• Opens WhatsApp in a new tab.

Print / Save PDF:
• Uses the browser's native print/PDF flow from the current report page.

Download Excel:
• Uses a real backend OpenPyXL generator.
• Produces a true .xlsx file.
• Captures visible dashboard/page metrics.
• Captures all visible tables into separate Excel worksheets.
• Works even on dashboard pages that have no table by exporting available KPI/metric cards.

Architecture:
• legacy_core.py remains byte-for-byte unchanged.
• New module: modules/report_tools/
• Existing Dashboard / Leads / Performance / Chat remain untouched.
• No database schema changes.
