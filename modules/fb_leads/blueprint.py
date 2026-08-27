"""
Facebook Lead Ads → Gaur CRM Integration
-----------------------------------------
Routes:
  GET  /fb-leads/               Dashboard + manual fetch UI
  POST /fb-leads/fetch           Manual pull: fetch leads from all configured forms
  GET  /fb-leads/webhook         Facebook webhook verification (hub.challenge)
  POST /fb-leads/webhook         Facebook real-time lead notification receiver
  GET  /fb-leads/settings        Settings page (page tokens, form→company mapping)
  POST /fb-leads/settings/save   Save settings
  GET  /fb-leads/logs            Show recent fetch log

Env vars (add to .env):
  FB_APP_SECRET          - your Meta App Secret (for webhook signature verification)
  FB_WEBHOOK_VERIFY_TOKEN - any random string you set in Meta Dashboard
  FB_PAGE_ACCESS_TOKEN   - long-lived Page Access Token (default, can be overridden per form in settings)
"""

import os, json, hmac, hashlib, datetime, traceback
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from legacy_core import current_user, require_roles, db

bp = Blueprint("fb_leads", __name__, url_prefix="/fb-leads", template_folder="templates")

# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def _get_setting(con, key, default=""):
    row = con.execute("SELECT val FROM fb_settings WHERE key=?", (key,)).fetchone()
    return row["val"] if row else default


def _set_setting(con, key, val):
    con.execute("INSERT OR REPLACE INTO fb_settings(key,val) VALUES(?,?)", (key, val))


def _log(con, level, message, lead_id=None):
    con.execute(
        "INSERT INTO fb_fetch_log(level,message,lead_id,created_at) VALUES(?,?,?,?)",
        (level, message[:1000], lead_id, datetime.datetime.now().isoformat())
    )


def _ensure_tables(con):
    """Create FB module tables if not exist."""
    con.execute("""
        CREATE TABLE IF NOT EXISTS fb_settings (
            key   TEXT PRIMARY KEY,
            val   TEXT NOT NULL DEFAULT ''
        )
    """)
    con.execute("""
        CREATE TABLE IF NOT EXISTS fb_fetch_log (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            level      TEXT NOT NULL DEFAULT 'INFO',
            message    TEXT NOT NULL DEFAULT '',
            lead_id    TEXT,
            created_at TEXT NOT NULL DEFAULT ''
        )
    """)
    con.execute("""
        CREATE TABLE IF NOT EXISTS fb_form_map (
            form_id      TEXT PRIMARY KEY,
            company_code TEXT NOT NULL DEFAULT 'SCIC',
            page_token   TEXT NOT NULL DEFAULT '',
            form_name    TEXT NOT NULL DEFAULT '',
            active       INTEGER NOT NULL DEFAULT 1
        )
    """)
    con.commit()


def _fetch_lead_from_fb(lead_id, page_token):
    """
    Call Graph API to get a single lead's field data.
    Returns dict of {field_name: value} or raises on error.
    """
    import urllib.request, urllib.parse
    url = f"https://graph.facebook.com/v19.0/{lead_id}?fields=field_data,created_time,ad_id,form_id,page_id&access_token={page_token}"
    with urllib.request.urlopen(url, timeout=15) as resp:
        return json.loads(resp.read().decode())


def _fetch_leads_for_form(form_id, page_token, after_cursor=None):
    """
    Fetch all leads from a form via Graph API (paginated).
    Returns list of lead objects.
    """
    import urllib.request
    leads = []
    url = f"https://graph.facebook.com/v19.0/{form_id}/leads?fields=field_data,created_time,ad_id,page_id&limit=100&access_token={page_token}"
    if after_cursor:
        url += f"&after={after_cursor}"
    while url:
        with urllib.request.urlopen(url, timeout=20) as resp:
            data = json.loads(resp.read().decode())
        leads.extend(data.get("data", []))
        url = data.get("paging", {}).get("next")
    return leads


def _insert_lead(con, lead_data, company_code, source="facebook"):
    """
    Insert a Facebook lead into the CRM leads table.
    Returns (inserted: bool, lead_db_id or None)
    """
    # Parse field_data list into a flat dict
    fields = {}
    for item in lead_data.get("field_data", []):
        fields[item["name"].lower()] = ", ".join(item.get("values", []))

    fb_lead_id = str(lead_data.get("id", ""))
    
    # Check if already imported (avoid duplicates)
    existing = con.execute(
        "SELECT id FROM leads WHERE fb_lead_id=?", (fb_lead_id,)
    ).fetchone()
    if existing:
        return False, None

    # Map common Facebook form field names to CRM fields
    client_name = (
        fields.get("full_name") or
        fields.get("name") or
        fields.get("first_name", "") + " " + fields.get("last_name", "")
    ).strip() or "Unknown"

    mobile = (
        fields.get("phone_number") or
        fields.get("mobile") or
        fields.get("phone") or
        fields.get("contact_number") or ""
    ).strip()

    email = (
        fields.get("email") or
        fields.get("email_address") or ""
    ).strip()

    city = (
        fields.get("city") or
        fields.get("location") or ""
    ).strip()

    country_interest = (
        fields.get("country_interested") or
        fields.get("which_country") or
        fields.get("visa_country") or
        fields.get("country") or ""
    ).strip()

    visa_category = (
        fields.get("visa_type") or
        fields.get("visa_category") or
        fields.get("service") or ""
    ).strip()

    notes_parts = []
    if country_interest:
        notes_parts.append(f"Country: {country_interest}")
    if visa_category:
        notes_parts.append(f"Visa: {visa_category}")
    # Dump all remaining fields
    known = {"full_name","name","first_name","last_name","phone_number","mobile","phone",
             "contact_number","email","email_address","city","location",
             "country_interested","which_country","visa_country","country",
             "visa_type","visa_category","service"}
    for k, v in fields.items():
        if k not in known and v:
            notes_parts.append(f"{k}: {v}")

    notes = " | ".join(notes_parts)

    created_at = lead_data.get("created_time", datetime.datetime.now().isoformat())
    ad_id = str(lead_data.get("ad_id", ""))
    form_id = str(lead_data.get("form_id", ""))

    lead_id_str = f"FB-{fb_lead_id[-8:]}" if fb_lead_id else f"FB-{datetime.datetime.now().strftime('%H%M%S%f')}"

    try:
        cur = con.execute("""
            INSERT INTO leads (
                lead_id, company_code, client_name, mobile, email,
                city, notes, source, fb_lead_id, fb_ad_id, fb_form_id,
                imported_at, upload_batch
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            lead_id_str, company_code, client_name, mobile, email,
            city, notes, source, fb_lead_id, ad_id, form_id,
            created_at, f"fb_{form_id[:8]}_{datetime.date.today().isoformat()}"
        ))
        con.commit()
        return True, cur.lastrowid
    except Exception:
        # If leads table doesn't have fb columns yet, try minimal insert
        try:
            cur = con.execute("""
                INSERT INTO leads (
                    lead_id, company_code, client_name, mobile, email,
                    city, notes, source, imported_at, upload_batch
                ) VALUES (?,?,?,?,?,?,?,?,?,?)
            """, (
                lead_id_str, company_code, client_name, mobile, email,
                city, notes[:500], source,
                created_at, f"fb_{datetime.date.today().isoformat()}"
            ))
            con.commit()
            return True, cur.lastrowid
        except Exception:
            con.rollback()
            return False, None


# ─────────────────────────────────────────────
# ROUTES
# ─────────────────────────────────────────────

@bp.get("/")
@require_roles("MD", "GM")
def home():
    u = current_user()
    con = db()
    _ensure_tables(con)
    
    total_fb = con.execute(
        "SELECT COUNT(*) c FROM leads WHERE COALESCE(source,'')='facebook'"
    ).fetchone()["c"]
    today = datetime.date.today().isoformat()
    today_fb = con.execute(
        "SELECT COUNT(*) c FROM leads WHERE source='facebook' AND imported_at LIKE ?",
        (today + "%",)
    ).fetchone()["c"]
    
    form_maps = [dict(r) for r in con.execute(
        "SELECT * FROM fb_form_map ORDER BY form_name"
    ).fetchall()]
    
    logs = [dict(r) for r in con.execute(
        "SELECT * FROM fb_fetch_log ORDER BY id DESC LIMIT 30"
    ).fetchall()]
    
    webhook_url = request.host_url.rstrip("/") + url_for("fb_leads.webhook")
    con.close()
    
    return render_template(
        "fb_leads_home.html",
        u=u,
        total_fb=total_fb,
        today_fb=today_fb,
        form_maps=form_maps,
        logs=logs,
        webhook_url=webhook_url
    )


@bp.post("/fetch")
@require_roles("MD", "GM")
def manual_fetch():
    """Manually pull all leads from all active form mappings."""
    con = db()
    _ensure_tables(con)
    
    default_token = os.environ.get("FB_PAGE_ACCESS_TOKEN", "").strip()
    form_maps = [dict(r) for r in con.execute(
        "SELECT * FROM fb_form_map WHERE active=1"
    ).fetchall()]
    
    if not form_maps:
        _log(con, "WARN", "No active form mappings. Go to Settings to add form IDs.")
        con.commit(); con.close()
        flash("No active form mappings configured. Add forms in Settings first.", "error")
        return redirect(url_for("fb_leads.home"))
    
    total_new = 0
    errors = 0
    for fm in form_maps:
        token = fm["page_token"].strip() or default_token
        if not token:
            _log(con, "ERROR", f"No token for form {fm['form_id']} ({fm['form_name']}). Skipping.")
            errors += 1
            continue
        try:
            leads = _fetch_leads_for_form(fm["form_id"], token)
            inserted = 0
            for lead in leads:
                ok, _ = _insert_lead(con, lead, fm["company_code"])
                if ok:
                    inserted += 1
            total_new += inserted
            _log(con, "INFO", f"Form {fm['form_name'] or fm['form_id']} ({fm['company_code']}): fetched {len(leads)}, new={inserted}")
        except Exception as e:
            err_msg = str(e)[:300]
            _log(con, "ERROR", f"Form {fm['form_id']}: {err_msg}")
            errors += 1
    
    con.commit(); con.close()
    
    if errors:
        flash(f"Fetch complete. {total_new} new leads added. {errors} form(s) had errors — check logs.", "error")
    else:
        flash(f"✓ {total_new} new leads imported from Facebook.", "success")
    return redirect(url_for("fb_leads.home"))


@bp.get("/webhook")
def webhook():
    """Facebook webhook verification endpoint."""
    verify_token = os.environ.get("FB_WEBHOOK_VERIFY_TOKEN", "gaur-crm-fb-webhook-2026")
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    
    if mode == "subscribe" and token == verify_token:
        return challenge, 200
    return "Verification failed", 403


@bp.post("/webhook")
def webhook_receive():
    """Receive real-time lead from Facebook."""
    app_secret = os.environ.get("FB_APP_SECRET", "").strip()
    
    # Verify signature if secret is configured
    if app_secret:
        sig_header = request.headers.get("X-Hub-Signature-256", "")
        expected = "sha256=" + hmac.new(
            app_secret.encode(), request.data, hashlib.sha256
        ).hexdigest()
        if not hmac.compare_digest(sig_header, expected):
            return jsonify({"error": "Invalid signature"}), 403
    
    payload = request.get_json(silent=True) or {}
    
    con = db()
    _ensure_tables(con)
    
    default_token = os.environ.get("FB_PAGE_ACCESS_TOKEN", "").strip()
    
    try:
        for entry in payload.get("entry", []):
            for change in entry.get("changes", []):
                if change.get("field") != "leadgen":
                    continue
                value = change.get("value", {})
                fb_lead_id = str(value.get("leadgen_id", ""))
                form_id = str(value.get("form_id", ""))
                
                if not fb_lead_id:
                    continue
                
                # Find token and company for this form
                fm = con.execute(
                    "SELECT * FROM fb_form_map WHERE form_id=? AND active=1", (form_id,)
                ).fetchone()
                
                company_code = dict(fm)["company_code"] if fm else "SCIC"
                token = (dict(fm)["page_token"].strip() if fm else "") or default_token
                
                if not token:
                    _log(con, "ERROR", f"Webhook: no token for form {form_id}. Configure FB_PAGE_ACCESS_TOKEN.")
                    continue
                
                try:
                    lead_data = _fetch_lead_from_fb(fb_lead_id, token)
                    ok, db_id = _insert_lead(con, lead_data, company_code)
                    if ok:
                        _log(con, "INFO", f"Webhook: new lead {fb_lead_id} → {company_code}", fb_lead_id)
                    else:
                        _log(con, "INFO", f"Webhook: duplicate lead {fb_lead_id} skipped")
                except Exception as e:
                    _log(con, "ERROR", f"Webhook: failed to fetch lead {fb_lead_id}: {e}")
        
        con.commit()
    except Exception:
        _log(con, "ERROR", f"Webhook parse error: {traceback.format_exc()[:400]}")
        con.commit()
    finally:
        con.close()
    
    return jsonify({"status": "ok"}), 200


@bp.get("/settings")
@require_roles("MD")
def settings():
    u = current_user()
    con = db()
    _ensure_tables(con)
    form_maps = [dict(r) for r in con.execute("SELECT * FROM fb_form_map ORDER BY form_name").fetchall()]
    verify_token = os.environ.get("FB_WEBHOOK_VERIFY_TOKEN", "gaur-crm-fb-webhook-2026")
    webhook_url = request.host_url.rstrip("/") + url_for("fb_leads.webhook")
    con.close()
    return render_template("fb_leads_settings.html", u=u, form_maps=form_maps,
                           verify_token=verify_token, webhook_url=webhook_url)


@bp.post("/settings/save")
@require_roles("MD")
def settings_save():
    """Add / update a form mapping."""
    con = db()
    _ensure_tables(con)
    
    action = request.form.get("action", "add")
    
    if action == "delete":
        form_id = request.form.get("form_id", "").strip()
        if form_id:
            con.execute("DELETE FROM fb_form_map WHERE form_id=?", (form_id,))
            con.commit()
            flash("Form mapping deleted.", "success")
    
    elif action in ("add", "update"):
        form_id = request.form.get("form_id", "").strip()
        form_name = request.form.get("form_name", "").strip()
        company_code = request.form.get("company_code", "SCIC").strip().upper()
        page_token = request.form.get("page_token", "").strip()
        active = 1 if request.form.get("active") else 0
        
        if not form_id:
            flash("Form ID is required.", "error")
        else:
            con.execute("""
                INSERT OR REPLACE INTO fb_form_map(form_id, company_code, page_token, form_name, active)
                VALUES (?,?,?,?,?)
            """, (form_id, company_code, page_token, form_name, active))
            con.commit()
            flash(f"Form '{form_name or form_id}' saved for {company_code}.", "success")
    
    con.close()
    return redirect(url_for("fb_leads.settings"))


@bp.get("/logs")
@require_roles("MD", "GM")
def logs():
    u = current_user()
    con = db()
    _ensure_tables(con)
    rows = [dict(r) for r in con.execute(
        "SELECT * FROM fb_fetch_log ORDER BY id DESC LIMIT 200"
    ).fetchall()]
    con.close()
    return render_template("fb_leads_logs.html", u=u, rows=rows)


# ─────────────────────────────────────────────
# INSTALL
# ─────────────────────────────────────────────

def install_fb_leads(app):
    """Run table migrations on startup."""
    with app.app_context():
        try:
            from legacy_core import IS_POSTGRES
            con = db()
            _ensure_tables(con)
            # Add fb columns to leads table if missing
            fb_cols = {
                "fb_lead_id": "TEXT DEFAULT ''",
                "fb_ad_id":   "TEXT DEFAULT ''",
                "fb_form_id": "TEXT DEFAULT ''",
                "source":     "TEXT DEFAULT ''",
                "email":      "TEXT DEFAULT ''",
                "notes":      "TEXT DEFAULT ''",
            }
            if IS_POSTGRES:
                for col, typedef in fb_cols.items():
                    try:
                        con.execute(f"ALTER TABLE leads ADD COLUMN IF NOT EXISTS {col} {typedef}")
                        con.commit()
                    except Exception:
                        try: con.rollback()
                        except Exception: pass
            else:
                existing = [r[1] for r in con.execute("PRAGMA table_info(leads)").fetchall()]
                for col, typedef in fb_cols.items():
                    if col not in existing:
                        try:
                            con.execute(f"ALTER TABLE leads ADD COLUMN {col} {typedef}")
                            con.commit()
                        except Exception:
                            try: con.rollback()
                            except Exception: pass
            con.close()
        except Exception:
            pass
