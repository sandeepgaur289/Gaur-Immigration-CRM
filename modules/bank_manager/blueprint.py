"""
Bank Manager Extension Module
- Bank Account Delete with OTP verification (email to admin Gmail)
- Expense Sheet (/finance/expenses)
- Database Backup (/admin/db-backup)
"""

import os, io, csv, secrets, hmac, hashlib, datetime, smtplib, ssl
from email.message import EmailMessage
from flask import Blueprint, request, redirect, url_for, flash, render_template_string, jsonify, send_file
from legacy_core import current_user, require_roles, db, IS_POSTGRES, log_activity

bp = Blueprint("bank_manager", __name__, url_prefix="/bank-manager")

EXPENSE_HEADS = [
    "Office Rent", "Salaries & Wages", "Utilities", "Internet & Phone",
    "Marketing & Advertising", "Travel & Conveyance", "Stationery",
    "Maintenance & Repairs", "Miscellaneous Expense", "Staff Welfare",
    "Professional Fees", "Equipment Purchase", "Software Subscription",
    "Bank Charges", "Other"
]

# ── OTP helpers ────────────────────────────────────────────────────────────────

def _secret():
    return (os.environ.get("SECRET_KEY") or "gaur-local-security-key").encode()

def _otp_hash(key, otp):
    return hmac.new(_secret(), (key + "|" + otp).encode(), hashlib.sha256).hexdigest()

def _admin_email():
    return (os.environ.get("GAUR_ADMIN_GMAIL") or "").strip()

def _email_configured():
    return bool(_admin_email() and (os.environ.get("GAUR_GMAIL_APP_PASSWORD") or "").strip())

def _send_delete_otp_email(bank, otp, actor):
    sender = _admin_email()
    password = (os.environ.get("GAUR_GMAIL_APP_PASSWORD") or "").strip()
    if not sender or not password:
        raise RuntimeError("Gmail OTP not configured.")
    msg = EmailMessage()
    msg["Subject"] = f"THE GAUR • Bank Account Delete OTP • {bank['bank_name']}"
    msg["From"] = sender
    msg["To"] = sender
    msg.set_content(f"""THE GAUR SECURITY ALERT

A bank account DELETE request has been initiated.

Bank: {bank['bank_name']}
Account Name: {bank['account_name']}
Account No.: {bank['account_number']}
IFSC: {bank.get('ifsc_code', '-')}
Company: {bank['company_code']}

Requested by: {actor['full_name']} ({actor['role']})
Time: {datetime.datetime.now().strftime('%d %b %Y %H:%M:%S')}

ONE TIME PASSWORD: {otp}

OTP expires in 10 minutes. Only approve if you authorised this deletion.
If this was NOT you, change your portal password immediately.

THE GAUR • Bank Security Center
""")
    context = ssl.create_default_context()
    with smtplib.SMTP("smtp.gmail.com", 587, timeout=20) as smtp:
        smtp.ehlo(); smtp.starttls(context=context); smtp.ehlo()
        smtp.login(sender, password); smtp.send_message(msg)

def _ensure_bank_otp_table():
    con = db(); cur = con.cursor()
    try:
        if IS_POSTGRES:
            cur.execute("""CREATE TABLE IF NOT EXISTS bank_delete_otps(
              id BIGSERIAL PRIMARY KEY, bank_id BIGINT NOT NULL, requested_by_id BIGINT NOT NULL,
              otp_hash TEXT NOT NULL, created_at TEXT NOT NULL, expires_at TEXT NOT NULL,
              used_at TEXT DEFAULT '', attempts INTEGER DEFAULT 0
            )""")
        else:
            cur.execute("""CREATE TABLE IF NOT EXISTS bank_delete_otps(
              id INTEGER PRIMARY KEY AUTOINCREMENT, bank_id INTEGER NOT NULL, requested_by_id INTEGER NOT NULL,
              otp_hash TEXT NOT NULL, created_at TEXT NOT NULL, expires_at TEXT NOT NULL,
              used_at TEXT DEFAULT '', attempts INTEGER DEFAULT 0
            )""")
        con.commit()
    except Exception:
        try: con.rollback()
        except Exception: pass
    finally:
        con.close()

# ── Bank Delete OTP routes ─────────────────────────────────────────────────────

@bp.route("/bank-delete-request/<int:bank_id>", methods=["POST"])
@require_roles("MD", "GM")
def bank_delete_request(bank_id):
    """Step 1 — User requests bank delete → sends OTP to admin Gmail."""
    _ensure_bank_otp_table()
    u = current_user(); con = db()
    from legacy_core import ensure_bank_manager_schema, _finance_companies
    ensure_bank_manager_schema()
    companies = _finance_companies(u)
    bank = con.execute("SELECT * FROM finance_banks WHERE id=? AND active=1", (bank_id,)).fetchone()
    if not bank or bank["company_code"] not in companies:
        con.close(); flash("Bank account not found or access denied.", "error")
        return redirect(url_for("finance_banks"))

    if not _email_configured():
        con.close()
        flash("Gmail OTP not configured. Contact MD to set GAUR_ADMIN_GMAIL in environment variables.", "error")
        return redirect(url_for("finance_banks"))

    # Cooldown check — 60 seconds
    last = con.execute(
        "SELECT created_at FROM bank_delete_otps WHERE bank_id=? AND COALESCE(used_at,'')='' ORDER BY id DESC LIMIT 1",
        (bank_id,)
    ).fetchone()
    if last:
        try:
            elapsed = (datetime.datetime.now() - datetime.datetime.fromisoformat(last["created_at"])).total_seconds()
            if elapsed < 60:
                con.close()
                flash(f"Please wait {int(60-elapsed)} seconds before requesting another OTP.", "error")
                return redirect(url_for("finance_banks"))
        except Exception:
            pass

    otp = f"{secrets.randbelow(1000000):06d}"
    now = datetime.datetime.now()
    expires = now + datetime.timedelta(minutes=10)
    # Invalidate old OTPs
    con.execute("UPDATE bank_delete_otps SET used_at=? WHERE bank_id=? AND COALESCE(used_at,'')=''",
                (now.isoformat(timespec="seconds"), bank_id))
    con.execute("""INSERT INTO bank_delete_otps(bank_id, requested_by_id, otp_hash, created_at, expires_at)
                   VALUES(?,?,?,?,?)""",
                (bank_id, u["id"], _otp_hash(str(bank_id), otp),
                 now.isoformat(timespec="seconds"), expires.isoformat(timespec="seconds")))
    con.commit()

    try:
        _send_delete_otp_email(dict(bank), otp, u)
        con.close()
        flash(f"OTP sent to admin Gmail. Enter OTP below to confirm deletion of '{bank['bank_name']}'.", "success")
        log_activity("BANK_DELETE_OTP_SENT", "Bank Delete OTP Sent", "FINANCE", "Bank Account",
                     bank_id, bank["bank_name"],
                     details={"company": bank["company_code"], "requested_by": u["full_name"]},
                     severity="WARNING", actor=u, company_code=bank["company_code"])
    except Exception as e:
        con.close()
        flash(f"OTP email failed: {str(e)[:120]}. Check Gmail configuration.", "error")
        return redirect(url_for("finance_banks"))

    return redirect(url_for("finance_banks", _anchor="delete-otp-" + str(bank_id), pending_delete=bank_id))


@bp.route("/bank-delete-confirm/<int:bank_id>", methods=["POST"])
@require_roles("MD", "GM")
def bank_delete_confirm(bank_id):
    """Step 2 — User enters OTP → permanently soft-deletes bank account."""
    _ensure_bank_otp_table()
    u = current_user(); con = db()
    from legacy_core import ensure_bank_manager_schema, _finance_companies
    ensure_bank_manager_schema()
    companies = _finance_companies(u)
    bank = con.execute("SELECT * FROM finance_banks WHERE id=?", (bank_id,)).fetchone()
    if not bank or bank["company_code"] not in companies:
        con.close(); flash("Bank account not found or access denied.", "error")
        return redirect(url_for("finance_banks"))

    entered_otp = (request.form.get("otp") or "").strip()
    row = con.execute(
        "SELECT * FROM bank_delete_otps WHERE bank_id=? AND requested_by_id=? AND COALESCE(used_at,'')='' ORDER BY id DESC LIMIT 1",
        (bank_id, u["id"])
    ).fetchone()

    if not row:
        con.close(); flash("No active OTP found. Please request a new OTP.", "error")
        return redirect(url_for("finance_banks"))

    # Expiry check
    try:
        if datetime.datetime.now() > datetime.datetime.fromisoformat(row["expires_at"]):
            con.execute("UPDATE bank_delete_otps SET used_at=? WHERE id=?",
                        (datetime.datetime.now().isoformat(timespec="seconds"), row["id"]))
            con.commit(); con.close()
            flash("OTP has expired. Please request a new OTP.", "error")
            return redirect(url_for("finance_banks"))
    except Exception:
        pass

    if int(row["attempts"] or 0) >= 5:
        con.execute("UPDATE bank_delete_otps SET used_at=? WHERE id=?",
                    (datetime.datetime.now().isoformat(timespec="seconds"), row["id"]))
        con.commit(); con.close()
        flash("Too many wrong attempts. Request a new OTP.", "error")
        return redirect(url_for("finance_banks"))

    if not hmac.compare_digest(row["otp_hash"], _otp_hash(str(bank_id), entered_otp)):
        con.execute("UPDATE bank_delete_otps SET attempts=attempts+1 WHERE id=?", (row["id"],))
        con.commit(); con.close()
        flash("Incorrect OTP. Please try again.", "error")
        return redirect(url_for("finance_banks"))

    # OTP verified — soft delete
    now = datetime.datetime.now().isoformat(timespec="seconds")
    con.execute("UPDATE finance_banks SET active=0, share_enabled=0 WHERE id=?", (bank_id,))
    con.execute("UPDATE bank_delete_otps SET used_at=? WHERE id=?", (now, row["id"]))
    con.commit(); con.close()

    log_activity("BANK_ACCOUNT_DELETED_OTP_VERIFIED", "Bank Account Deleted (OTP Verified)", "FINANCE",
                 "Bank Account", bank_id, bank["bank_name"],
                 details={"company": bank["company_code"], "last4": bank["account_last4"]},
                 severity="CRITICAL", actor=u, company_code=bank["company_code"])
    flash(f"Bank account '{bank['bank_name']}' deleted successfully. Historical transactions are preserved.", "success")
    return redirect(url_for("finance_banks"))


# ── Expense Sheet ──────────────────────────────────────────────────────────────

_EXPENSE_TMPL = r"""{% extends "base.html" %}{% block content %}
<style>
.exp-card{background:#071d32;border:1px solid #315a7b;border-radius:14px;padding:16px;margin-bottom:16px}
.exp-stat{background:linear-gradient(145deg,#0c2847,#071b30);border:1px solid #315a7b;border-radius:12px;padding:14px;text-align:center}
.exp-stat b{display:block;font-size:26px;color:#e6b73f;margin-top:4px}
.exp-stat span{font-size:13px;opacity:.75}
.exp-badge-out{padding:3px 8px;border-radius:10px;font-size:12px;background:#4a1a1a;color:#ff9a9a}
.exp-badge-in{padding:3px 8px;border-radius:10px;font-size:12px;background:#174f34;color:#48d58b}
</style>

<div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px;margin-bottom:16px">
  <h1 class="title" style="margin:0">💸 Expense Sheet</h1>
  <div style="display:flex;gap:8px;flex-wrap:wrap">
    <a href="{{url_for('finance_center')}}" class="toolbtn">← Daily Passbook</a>
    <a href="{{url_for('accounts_report_center')}}" class="toolbtn">📊 Accounts Report</a>
  </div>
</div>

<!-- Summary Cards -->
<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:12px;margin-bottom:16px">
  <div class="exp-stat"><span>Total Expenses</span><b>₹{{"{:,.0f}".format(stats.total)}}</b></div>
  <div class="exp-stat"><span>Today</span><b>₹{{"{:,.0f}".format(stats.today)}}</b></div>
  <div class="exp-stat"><span>This Month</span><b>₹{{"{:,.0f}".format(stats.month)}}</b></div>
  <div class="exp-stat"><span>Total Entries</span><b>{{stats.count}}</b></div>
</div>

<!-- Add Expense Form -->
<div class="exp-card" id="add-expense">
  <h2 style="color:#e6b73f;margin:0 0 14px">➕ Add Expense</h2>
  <form method="post" enctype="multipart/form-data">
    <input type="hidden" name="action" value="add_expense">
    <div class="grid3">
      <div><label>Expense Date *</label><input type="date" name="txn_date" value="{{today}}" required></div>
      <div><label>Amount (₹) *</label><input type="number" name="amount" step="0.01" min="0.01" required placeholder="0.00"></div>
      <div><label>Category *</label>
        <select name="head" required>
          {% for h in expense_heads %}<option>{{h}}</option>{% endfor %}
        </select>
      </div>
      <div><label>Party / Vendor Name *</label><input name="party_name" required placeholder="Vendor ya party ka naam"></div>
      <div><label>Bank Account</label>
        <select name="account_id">
          <option value="">— Cash / Select Bank —</option>
          {% for b in banks %}<option value="{{b['id']}}">{{b['bank_name']}} ({{b['account_last4']}})</option>{% endfor %}
        </select>
      </div>
      <div><label>Payment Mode</label>
        <select name="payment_mode">
          <option>Cash</option><option>NEFT</option><option>IMPS</option><option>UPI</option>
          <option>Cheque</option><option>RTGS</option><option>Card</option>
        </select>
      </div>
      <div><label>Reference No.</label><input name="reference_no" placeholder="UTR / Cheque No."></div>
      {% if u['role']=='MD' %}
      <div><label>Company</label>
        <select name="company_code">
          <option value="SCIC">Smart Choice</option>
          <option value="WWIC">White Wave</option>
        </select>
      </div>
      {% endif %}
      <div><label>Bill Attachment</label><input type="file" name="bill" accept=".jpg,.jpeg,.png,.pdf"></div>
    </div>
    <label>Description / Remarks</label>
    <textarea name="remarks" placeholder="Expense ka description..."></textarea>
    <br>
    <button class="btn">💾 Save Expense</button>
  </form>
</div>

<!-- Filters -->
<div class="exp-card">
  <form method="get" style="display:flex;gap:10px;flex-wrap:wrap;align-items:flex-end">
    <div><label style="font-size:13px">From Date</label><input type="date" name="date_from" value="{{f.date_from}}" style="padding:8px;background:#071d32;border:1px solid #427398;color:#fff;border-radius:8px"></div>
    <div><label style="font-size:13px">To Date</label><input type="date" name="date_to" value="{{f.date_to}}" style="padding:8px;background:#071d32;border:1px solid #427398;color:#fff;border-radius:8px"></div>
    <div><label style="font-size:13px">Bank Account</label>
      <select name="account_id" style="padding:8px;background:#071d32;border:1px solid #427398;color:#fff;border-radius:8px">
        <option value="">All Banks</option>
        {% for b in banks %}<option value="{{b['id']}}" {{'selected' if f.account_id==b['id']|string else ''}}>{{b['bank_name']}} ({{b['account_last4']}})</option>{% endfor %}
      </select>
    </div>
    <div><label style="font-size:13px">Category</label>
      <select name="head" style="padding:8px;background:#071d32;border:1px solid #427398;color:#fff;border-radius:8px">
        <option value="">All Categories</option>
        {% for h in expense_heads %}<option {{'selected' if f.head==h else ''}}>{{h}}</option>{% endfor %}
      </select>
    </div>
    <button class="btn" style="padding:8px 16px">🔍 Filter</button>
    <a href="{{url_for('bank_manager.expense_sheet')}}" class="toolbtn">Reset</a>
  </form>
</div>

<!-- Expenses Table -->
<div class="exp-card">
  <h2 style="color:#e6b73f;margin:0 0 12px">📋 Expense Records — {{rows|length}} entries</h2>
  <div class="tablewrap">
  <table>
    <tr>
      <th>Date</th><th>Voucher</th><th>Category</th><th>Party</th>
      <th>Amount</th><th>Bank Account</th><th>Mode</th><th>Ref No.</th><th>Remarks</th>
    </tr>
    {% for r in rows %}
    <tr>
      <td style="white-space:nowrap">{{r['txn_date']}}</td>
      <td><small style="color:#8fc8ff">{{r['voucher_no']}}</small></td>
      <td><span class="exp-badge-out">{{r['head']}}</span></td>
      <td>{{r['party_name']}}</td>
      <td style="color:#ff9a9a;font-weight:bold">₹{{"{:,.2f}".format(r['amount'])}}</td>
      <td style="font-size:12px">{{r['bank_name'] or 'Cash'}}{% if r['account_last4'] %} (...{{r['account_last4']}}){% endif %}</td>
      <td style="font-size:12px">{{r['payment_mode'] or '-'}}</td>
      <td style="font-size:12px">{{r['reference_no'] or '-'}}</td>
      <td style="font-size:12px;max-width:200px;word-break:break-word">{{r['remarks'] or '-'}}</td>
    </tr>
    {% else %}
    <tr><td colspan="9" style="text-align:center;padding:30px;opacity:.6">Koi expense record nahi mila.</td></tr>
    {% endfor %}
  </table>
  </div>
  {% if rows %}
  <div style="margin-top:12px;text-align:right">
    <b style="color:#ff9a9a">Total: ₹{{"{:,.2f}".format(rows|sum(attribute='amount'))}}</b>
  </div>
  {% endif %}
</div>
{% endblock %}"""


@bp.route("/expenses", methods=["GET", "POST"])
@require_roles("MD", "GM")
def expense_sheet():
    from legacy_core import ensure_bank_manager_schema, _finance_companies, _finance_voucher, log_activity
    from werkzeug.utils import secure_filename
    ensure_bank_manager_schema()
    u = current_user(); con = db()
    companies = _finance_companies(u)

    if request.method == "POST" and request.form.get("action") == "add_expense":
        company = request.form.get("company_code") or u["company_code"]
        if company not in companies:
            flash("Company access denied.", "error")
            return redirect(url_for("bank_manager.expense_sheet"))
        amount = float(request.form.get("amount") or 0)
        if amount <= 0:
            flash("Amount must be greater than zero.", "error")
            return redirect(url_for("bank_manager.expense_sheet"))
        txn_date = request.form.get("txn_date") or datetime.date.today().isoformat()
        voucher = _finance_voucher(con, company, "OUT", txn_date)
        aid = request.form.get("account_id", "").strip()
        aid = int(aid) if aid.isdigit() else None
        bill = request.files.get("bill"); bn = ""; bm = ""; bb = None
        if bill and bill.filename:
            bn = secure_filename(bill.filename)[:180]; bb = bill.read()
            if len(bb) > 10 * 1024 * 1024:
                flash("Bill attachment must be 10 MB or smaller.", "error")
                return redirect(url_for("bank_manager.expense_sheet"))
            bm = bill.mimetype or "application/octet-stream"
        con.execute("""INSERT INTO finance_transactions(voucher_no,txn_date,company_code,direction,head,party_name,
            client_ref,amount,payment_mode,account_id,reference_no,remarks,bill_name,bill_mime,bill_bytes,
            status,created_by_id,created_by_name,created_at)
            VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,'POSTED',?,?,?)""",
            (voucher, txn_date, company, "OUT",
             request.form.get("head", "Miscellaneous Expense"),
             request.form.get("party_name", "").strip(), "",
             amount, request.form.get("payment_mode", "Cash"),
             aid, request.form.get("reference_no", "").strip(),
             request.form.get("remarks", "").strip(),
             bn, bm, bb, u["id"], u["full_name"],
             datetime.datetime.now().isoformat(timespec="seconds")))
        con.commit()
        log_activity("EXPENSE_ADDED", "Expense Added", "FINANCE", "Voucher", voucher, voucher,
                     details={"head": request.form.get("head"), "amount": amount,
                               "party": request.form.get("party_name")},
                     actor=u, company_code=company)
        flash(f"Expense saved: {voucher}", "success")
        return redirect(url_for("bank_manager.expense_sheet"))

    # Filters
    df = request.args.get("date_from", "")
    dt = request.args.get("date_to", "")
    acc = request.args.get("account_id", "")
    head = request.args.get("head", "")
    wh = ["t.company_code IN (" + ",".join(["?"] * len(companies)) + ")", "t.direction='OUT'"]
    pa = list(companies)
    if df: wh.append("t.txn_date>=?"); pa.append(df)
    if dt: wh.append("t.txn_date<=?"); pa.append(dt)
    if acc and acc.isdigit(): wh.append("t.account_id=?"); pa.append(int(acc))
    if head: wh.append("t.head=?"); pa.append(head)
    rows = con.execute("""SELECT t.*, b.bank_name, b.account_last4
        FROM finance_transactions t
        LEFT JOIN finance_banks b ON b.id = t.account_id
        WHERE """ + " AND ".join(wh) + " ORDER BY t.txn_date DESC, t.id DESC", pa).fetchall()
    banks = con.execute("SELECT * FROM finance_banks WHERE active=1 AND company_code IN (" +
                        ",".join(["?"] * len(companies)) + ") ORDER BY bank_name", companies).fetchall()

    today_str = datetime.date.today().isoformat()
    month_str = today_str[:7]
    total = sum(r["amount"] for r in rows)
    today_sum = sum(r["amount"] for r in rows if r["txn_date"] == today_str)
    month_sum = sum(r["amount"] for r in rows if (r["txn_date"] or "")[:7] == month_str)

    class Stats:
        def __init__(self):
            self.total = total; self.today = today_sum
            self.month = month_sum; self.count = len(rows)
    con.close()
    return render_template_string(_EXPENSE_TMPL, u=u, rows=rows, banks=banks,
                                   expense_heads=EXPENSE_HEADS, today=today_str,
                                   stats=Stats(),
                                   f={"date_from": df, "date_to": dt,
                                      "account_id": acc, "head": head})


# ── Database Backup ────────────────────────────────────────────────────────────

@bp.route("/db-backup")
@require_roles("MD", "GM")
def db_backup():
    """Download full database as CSV backup (works on both SQLite and PostgreSQL)."""
    u = current_user(); con = db()
    try:
        output = io.StringIO()
        writer = csv.writer(output)

        # Get all table names
        if IS_POSTGRES:
            tables = [r[0] for r in con.execute(
                "SELECT table_name FROM information_schema.tables WHERE table_schema='public' ORDER BY table_name"
            ).fetchall()]
        else:
            tables = [r[0] for r in con.execute(
                "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
            ).fetchall()]

        # Skip binary/blob-heavy tables
        skip_tables = {"bank_statement_rows", "chat_messages", "chat_attachments",
                       "broadcast_messages", "notification_reads", "broadcast_reads"}

        for table in tables:
            if table in skip_tables:
                continue
            try:
                rows = con.execute(f"SELECT * FROM {table} LIMIT 50000").fetchall()
                if not rows:
                    continue
                writer.writerow([f"=== TABLE: {table} ==="])
                writer.writerow(rows[0].keys())
                for row in rows:
                    # Mask sensitive fields
                    safe = []
                    for k, v in zip(row.keys(), tuple(row)):
                        if any(s in k.lower() for s in ("password", "hash", "secret", "otp",
                                                          "bill_bytes", "photo_data", "file_bytes")):
                            safe.append("[REDACTED]")
                        else:
                            safe.append(str(v) if v is not None else "")
                    writer.writerow(safe)
                writer.writerow([])
            except Exception:
                writer.writerow([f"Error reading {table}"])
                writer.writerow([])

        con.close()
        now = datetime.datetime.now().strftime("%Y%m%d_%H%M")
        company = u.get("company_code") or "ALL"
        filename = f"gaur_crm_backup_{company}_{now}.csv"
        output.seek(0)
        return send_file(
            io.BytesIO(output.getvalue().encode("utf-8-sig")),
            mimetype="text/csv",
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        con.close()
        flash(f"Backup failed: {str(e)[:200]}", "error")
        return redirect(url_for("dashboard"))


def install_bank_manager(app):
    """Register the bank_manager blueprint."""
    if app.extensions.get("bank_manager_installed"):
        return
    app.register_blueprint(bp)
    app.extensions["bank_manager_installed"] = True
