THE GAUR CRM v3.30 — MONTHLY AM LEADERBOARD • FINAL

BUILT ON v3.29 ADMIN CONTROL/OFFBOARDING.

NEW MONTHLY AM PERFORMANCE SYSTEM
• MD Dashboard: all Assistant Managers across SCIC + WWIC.
• MD also gets separate Smart Choice Top AMs and White Wave Top AMs.
• Every company employee portal/dashboard sees its own company's AM ranking.
• Month selector controls the complete leaderboard.
• All AMs are shown, not only Top 3.
• Rank #1 = Gold highlight.
• Rank #2 = Silver highlight.
• Rank #3 = Bronze highlight.
• Performer of the Month hero remains prominent.

AM DETAILS SHOWN
Rank
AM Name + Photograph
Company
Leads Allocated
Positive Leads
Enrollments
Revenue Generated
Conversion %
Business Performance Score

BUSINESS SCORE
45% Enrollment Index
45% Revenue Index
10% Positive Lead Index
The score is relative to the strongest AM performance in the selected scope/month.
Ranking tie-breakers: enrollments -> revenue -> positive leads.

DATA SOURCE
• Enrollments & Revenue: client_cases assigned to the AM's linked Employee ID for the selected enrollment month.
• Allocated/Positive Leads: non-archived leads assigned to that AM in the selected month.
• Recycle Bin leads are excluded from lead performance inputs.

PORTAL VISIBILITY
• MD: both-company combined leaderboard + individual company Top 2 panels.
• SCIC users: SCIC AM leaderboard.
• WWIC users: WWIC AM leaderboard.
This allows the same company ranking to motivate AM/GM/Reception and other dashboard users.

SAFE DEPLOY
1. Keep v3.29 as backup.
2. Extract ZIP.
3. Replace ONLY GitHub root app.py.
4. Commit: CRM v3.30 Monthly AM Leaderboard Final
5. Wait for Railway Deployment successful.
6. Ctrl+F5.
7. Test month selector.
8. Verify one known enrollment/payment against its assigned AM before using leaderboard for formal incentives.

IMPORTANT
Revenue/enrollment ranking depends on client_cases.assigned_employee_id being linked to the correct AM employee record.
