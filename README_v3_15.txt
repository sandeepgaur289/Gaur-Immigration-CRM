THE GAUR CRM v3.15 — STABLE PROFESSIONAL DESIGNATIONS

EXACT RAILWAY FIX
v3.14 had this startup-order error:
    app.jinja_env.globals["role_display"] = role_display
was executed BEFORE:
    def role_display(...)

Gunicorn imports app.py before Railway healthcheck runs.
That caused a Python NameError during startup, so Railway showed:
Initialization ✓
Build ✓
Deploy ✓
Network / Healthcheck ✗

v3.15 changes the order:
1. Flask app is created.
2. role_display() is defined.
3. ONLY THEN role_display is registered with Jinja.

VALIDATION COMPLETED
- Python syntax compile: PASS
- AST parse: PASS
- role_display registration order: PASS
- /healthz route present: PASS

PRESERVED FEATURES
- Managing Director, General Manager, Assistant Manager full professional naming.
- Human Resources Manager, Filing Officer, Reception Executive, Visa Counselor,
  Senior Visa Counselor, Telecalling Executive, Accounts Executive,
  Branch Manager and Team Leader naming.
- Professional Employee Identity System.
- Employee profile photos.
- Digital Employee ID Cards.
- Team Identity Center.
- Existing PostgreSQL cloud data, leads, client profiles, rankings and analytics.

DEPLOY
1. Extract this ZIP.
2. GitHub -> Gaur-Immigration-CRM -> Add file -> Upload files.
3. Upload ONLY app.py to repository root and replace existing app.py.
4. Commit directly to main.
5. Commit message:
   CRM v3.15 Stable Professional Designations
6. Wait for Railway deployment.
7. Confirm Network / Healthcheck passes and service becomes ACTIVE.
8. Press Ctrl+F5.

IMPORTANT
Do NOT modify DATABASE_URL or PostgreSQL.

NOTE
A full local Flask import test cannot be run in this ChatGPT file-building runtime because
the Flask package is not installed here. The exact v3.14 NameError was identified from
the source and fixed, and Python syntax/AST validation both pass.
