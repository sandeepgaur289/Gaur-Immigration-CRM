GAUR CRM v4.1.1 — AM PERFORMANCE CALCULATION FIX

Problem found:
The old am_business_month_rankings() function intentionally hard-coded:
  allocated = 0
  positive = 0
  revenue = 0
  conversion = 0
and calculated only enrollment count through employee_id.
That is why the leaderboard stayed at zero even after leads were uploaded and allocated.

v4.1.1 fixes the calculator without editing legacy_core.py.

Leaderboard sources now:
• Leads Allocated = actual leads assigned to each AM during selected month.
• Positive Leads = actual assigned leads with Interest Score >= 50%.
• Enrollments = client cases linked to the AM's lead during selected month.
• Revenue Generated = total_received from those enrolled client cases.
• Conversion = Enrollments / Leads Allocated × 100.
• Enrollment Score = enrollment count relative to the best AM in the current company/scope.
• Ranking ties consider Enrollment, Revenue, Positive Leads and Allocated Leads.

Architecture safety:
• legacy_core.py remains byte-for-byte unchanged.
• Fix lives only in modules/performance/.
• Existing Dashboard UI is reused; only its data calculator is replaced.
• No DB schema changes.
• No global CSS or Jinja changes.

Python syntax validation PASSED.
