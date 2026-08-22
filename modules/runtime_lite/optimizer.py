from flask import request
from legacy_core import db, IS_POSTGRES

def _create_indexes():
    con=db()
    cur=con.cursor()
    statements=[
      "CREATE INDEX IF NOT EXISTS idx_leads_assigned_am ON leads(assigned_am)",
      "CREATE INDEX IF NOT EXISTS idx_leads_company_code ON leads(company_code)",
      "CREATE INDEX IF NOT EXISTS idx_leads_imported_at ON leads(imported_at)",
      "CREATE INDEX IF NOT EXISTS idx_leads_assigned_at ON leads(assigned_at)",
      "CREATE INDEX IF NOT EXISTS idx_client_cases_enrollment_date ON client_cases(enrollment_date)",
      "CREATE INDEX IF NOT EXISTS idx_client_cases_lead_db_id ON client_cases(lead_db_id)",
      "CREATE INDEX IF NOT EXISTS idx_client_cases_assigned_employee ON client_cases(assigned_employee_id)",
      "CREATE INDEX IF NOT EXISTS idx_chat_recipient_id ON chat_messages(recipient_id,id)",
      "CREATE INDEX IF NOT EXISTS idx_chat_sender_recipient ON chat_messages(sender_id,recipient_id,id)",
    ]
    for sql in statements:
        try:
            cur.execute(sql)
        except Exception:
            pass
    con.commit()
    con.close()

def install_runtime_lite(app):
    if app.extensions.get("v47_runtime_lite_installed"):
        return

    try:
        _create_indexes()
    except Exception:
        app.logger.exception("v4.7 index creation skipped")

    @app.after_request
    def _lite_cache_headers(response):
        try:
            p=request.path or ""
            ctype=(response.headers.get("Content-Type") or "").lower()

            # Static JS/CSS/icons are versioned in this CRM: let browsers reuse them.
            if "/static/" in p:
                response.headers["Cache-Control"]="public, max-age=604800, immutable"
            # Profile images are requested repeatedly in dashboard/chat.
            elif p.startswith("/user-photo/") and response.status_code==200:
                response.headers["Cache-Control"]="private, max-age=300"
            # Dynamic HTML/API should not be cached accidentally.
            elif "text/html" in ctype or "application/json" in ctype:
                response.headers.setdefault("Cache-Control","private, no-store")
        except Exception:
            pass
        return response

    app.extensions["v47_runtime_lite_installed"]=True
