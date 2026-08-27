import os
import sys
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from legacy_core import app, init_db
from modules import register_modules
from flask import Response

register_modules(app)

@app.route("/privacy-policy")
def privacy_policy():
    html = """<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><title>Privacy Policy – Gaur Immigration CRM</title>
<style>body{font-family:Arial,sans-serif;max-width:800px;margin:40px auto;padding:0 20px;color:#333}h1{color:#1a1a1a}h2{color:#444}p{line-height:1.7}</style>
</head>
<body>
<h1>Privacy Policy</h1>
<p><strong>Gaur Immigration CRM</strong> is an internal business tool used by Gaur Immigration and associated entities.</p>

<h2>Data Collection</h2>
<p>This application collects lead information submitted through Facebook Lead Ads forms, including name, phone number, email address, and visa-related enquiry details. This data is collected solely for the purpose of responding to immigration enquiries.</p>

<h2>Data Use</h2>
<p>Collected data is used exclusively by authorised staff to follow up on immigration and visa enquiries. Data is never sold or shared with third parties.</p>

<h2>Data Storage</h2>
<p>All data is stored securely and accessible only to authorised personnel within the organisation.</p>

<h2>Contact</h2>
<p>For any privacy-related queries, contact us at: <a href="mailto:sandeepgaur289@yahoo.com">sandeepgaur289@yahoo.com</a></p>

<p><em>Last updated: September 2026</em></p>
</body>
</html>"""
    return Response(html, mimetype="text/html")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5050"))
    try:
        init_db()
        print("GAUR CRM v4.0.2 database initialization: OK", flush=True)
    except Exception:
        print("GAUR CRM DATABASE INITIALIZATION WARNING:", flush=True)
        traceback.print_exc()

    print(f"GAUR CRM v4.0.2 listening on 0.0.0.0:{port}", flush=True)

    try:
        from waitress import serve
        serve(app, host="0.0.0.0", port=port, threads=8)
    except ImportError:
        app.run(host="0.0.0.0", port=port, debug=False)
