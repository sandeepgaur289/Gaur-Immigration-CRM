import os, hmac, hashlib, secrets, smtplib, ssl, datetime
from email.message import EmailMessage
from werkzeug.security import generate_password_hash
from legacy_core import db, IS_POSTGRES

def now_iso():
    return datetime.datetime.now().isoformat(timespec="seconds")

def ensure_schema():
    con=db(); cur=con.cursor()
    if IS_POSTGRES:
        cur.executescript("""
        CREATE TABLE IF NOT EXISTS password_reset_otps(
          id BIGSERIAL PRIMARY KEY,user_id BIGINT NOT NULL,login_id TEXT NOT NULL,otp_hash TEXT NOT NULL,
          created_at TEXT NOT NULL,expires_at TEXT NOT NULL,attempts INTEGER DEFAULT 0,used_at TEXT DEFAULT '',
          requested_ip TEXT DEFAULT '',requested_user_agent TEXT DEFAULT ''
        );
        CREATE TABLE IF NOT EXISTS security_audit(
          id BIGSERIAL PRIMARY KEY,user_id BIGINT,login_id TEXT DEFAULT '',action TEXT NOT NULL,
          actor_user_id BIGINT,actor_name TEXT DEFAULT '',details TEXT DEFAULT '',created_at TEXT NOT NULL
        );
        ALTER TABLE users ADD COLUMN IF NOT EXISTS password_changed_at TEXT DEFAULT '';
        """)
    else:
        cur.executescript("""
        CREATE TABLE IF NOT EXISTS password_reset_otps(
          id INTEGER PRIMARY KEY AUTOINCREMENT,user_id INTEGER NOT NULL,login_id TEXT NOT NULL,otp_hash TEXT NOT NULL,
          created_at TEXT NOT NULL,expires_at TEXT NOT NULL,attempts INTEGER DEFAULT 0,used_at TEXT DEFAULT '',
          requested_ip TEXT DEFAULT '',requested_user_agent TEXT DEFAULT ''
        );
        CREATE TABLE IF NOT EXISTS security_audit(
          id INTEGER PRIMARY KEY AUTOINCREMENT,user_id INTEGER,login_id TEXT DEFAULT '',action TEXT NOT NULL,
          actor_user_id INTEGER,actor_name TEXT DEFAULT '',details TEXT DEFAULT '',created_at TEXT NOT NULL
        );
        """)
        cols=[r[1] for r in cur.execute("PRAGMA table_info(users)").fetchall()]
        if "password_changed_at" not in cols:
            cur.execute("ALTER TABLE users ADD COLUMN password_changed_at TEXT DEFAULT ''")
    con.commit();con.close()

def _secret():
    return (os.environ.get("SECRET_KEY") or os.environ.get("FLASK_SECRET_KEY") or "gaur-local-security-key").encode()

def otp_hash(login_id,otp):
    return hmac.new(_secret(),(login_id.lower().strip()+"|"+otp.strip()).encode(),hashlib.sha256).hexdigest()

def admin_email():
    return (os.environ.get("GAUR_ADMIN_GMAIL") or "").strip()

def email_configured():
    return bool(admin_email() and (os.environ.get("GAUR_GMAIL_APP_PASSWORD") or "").strip())

def audit(action,user_id=None,login_id="",actor=None,details=""):
    con=db()
    con.execute("""INSERT INTO security_audit
      (user_id,login_id,action,actor_user_id,actor_name,details,created_at)
      VALUES(?,?,?,?,?,?,?)""",
      (user_id,login_id,action,actor["id"] if actor else None,actor["full_name"] if actor else "",
       str(details or "")[:1000],now_iso()))
    con.commit();con.close()

def send_admin_otp(user,otp):
    sender=admin_email()
    password=(os.environ.get("GAUR_GMAIL_APP_PASSWORD") or "").strip()
    if not sender or not password:
        raise RuntimeError("Gmail OTP sender is not configured in Railway Variables.")
    msg=EmailMessage()
    msg["Subject"]=f"THE GAUR • Password Reset OTP • {user['full_name']}"
    msg["From"]=sender; msg["To"]=sender
    msg.set_content(f"""THE GAUR SECURITY ALERT

Password reset requested.

Employee: {user['full_name']}
Role: {user['role']}
Company: {user['company_code'] or 'THE GAUR'}
Login ID: {user['login_id']}

ONE TIME PASSWORD: {otp}

OTP expires in 10 minutes and can be used only once.
Do not share it unless you approve this employee password reset.

THE GAUR • Security Center
""")
    context=ssl.create_default_context()
    with smtplib.SMTP("smtp.gmail.com",587,timeout=20) as smtp:
        smtp.ehlo(); smtp.starttls(context=context); smtp.ehlo()
        smtp.login(sender,password); smtp.send_message(msg)

def create_reset_request(login_id,ip="",user_agent=""):
    login_id=(login_id or "").strip().lower()
    con=db()
    user=con.execute("""SELECT id,login_id,full_name,role,company_code,active
      FROM users WHERE lower(login_id)=? AND active=1""",(login_id,)).fetchone()
    if not user or user["role"] not in ("AM","GM"):
        con.close(); return None

    last=con.execute("""SELECT created_at FROM password_reset_otps
      WHERE user_id=? ORDER BY id DESC LIMIT 1""",(user["id"],)).fetchone()
    if last and last["created_at"]:
        try:
            if (datetime.datetime.now()-datetime.datetime.fromisoformat(last["created_at"])).total_seconds()<60:
                con.close(); return {"cooldown":True}
        except Exception:
            pass

    otp=f"{secrets.randbelow(1000000):06d}"
    created=datetime.datetime.now()
    expires=created+datetime.timedelta(minutes=10)
    con.execute("UPDATE password_reset_otps SET used_at=? WHERE user_id=? AND COALESCE(used_at,'')=''",
                (now_iso(),user["id"]))
    con.execute("""INSERT INTO password_reset_otps
      (user_id,login_id,otp_hash,created_at,expires_at,attempts,used_at,requested_ip,requested_user_agent)
      VALUES(?,?,?,?,?,0,'',?,?)""",
      (user["id"],user["login_id"],otp_hash(user["login_id"],otp),
       created.isoformat(timespec="seconds"),expires.isoformat(timespec="seconds"),
       str(ip or "")[:100],str(user_agent or "")[:300]))
    con.commit();con.close()

    send_admin_otp(user,otp)
    audit("PASSWORD_RESET_OTP_SENT",user["id"],user["login_id"],None,
          f"OTP sent to designated admin Gmail for {user['full_name']}")
    return {"cooldown":False}

def verify_and_reset(login_id,otp,new_password):
    login_id=(login_id or "").strip().lower(); otp=(otp or "").strip()
    con=db()
    user=con.execute("""SELECT id,login_id,full_name,role,company_code,active
      FROM users WHERE lower(login_id)=? AND active=1""",(login_id,)).fetchone()
    if not user or user["role"] not in ("AM","GM"):
        con.close(); return False,"Invalid or expired OTP."
    row=con.execute("""SELECT * FROM password_reset_otps
      WHERE user_id=? AND COALESCE(used_at,'')='' ORDER BY id DESC LIMIT 1""",(user["id"],)).fetchone()
    if not row:
        con.close(); return False,"Invalid or expired OTP."
    try:
        if datetime.datetime.now()>datetime.datetime.fromisoformat(row["expires_at"]):
            con.execute("UPDATE password_reset_otps SET used_at=? WHERE id=?",(now_iso(),row["id"]))
            con.commit();con.close(); return False,"OTP has expired. Request a new OTP."
    except Exception:
        con.close(); return False,"OTP has expired. Request a new OTP."
    if int(row["attempts"] or 0)>=5:
        con.execute("UPDATE password_reset_otps SET used_at=? WHERE id=?",(now_iso(),row["id"]))
        con.commit();con.close(); return False,"Too many incorrect attempts. Request a new OTP."
    if not hmac.compare_digest(row["otp_hash"],otp_hash(user["login_id"],otp)):
        con.execute("UPDATE password_reset_otps SET attempts=attempts+1 WHERE id=?",(row["id"],))
        con.commit();con.close(); return False,"Incorrect OTP."

    con.execute("UPDATE users SET password_hash=?,password_changed_at=? WHERE id=?",
                (generate_password_hash(new_password),now_iso(),user["id"]))
    con.execute("UPDATE password_reset_otps SET used_at=? WHERE id=?",(now_iso(),row["id"]))
    con.commit();con.close()
    audit("PASSWORD_RESET_COMPLETED",user["id"],user["login_id"],None,"OTP approved password reset completed.")
    return True,"Password changed successfully. You can now log in."

def md_users():
    con=db()
    rows=[dict(r) for r in con.execute("""SELECT id,login_id,full_name,role,company_code,active,
      official_email,official_mobile,designation,password_changed_at,last_login_at
      FROM users ORDER BY CASE role WHEN 'MD' THEN 1 WHEN 'GM' THEN 2 WHEN 'AM' THEN 3 ELSE 4 END,
      company_code,full_name""").fetchall()]
    con.close(); return rows

def md_audit():
    con=db()
    rows=[dict(r) for r in con.execute("SELECT * FROM security_audit ORDER BY id DESC LIMIT 300").fetchall()]
    con.close(); return rows

def md_update_user(actor,user_id,login_id,new_password,active):
    login_id=(login_id or "").strip().lower()
    if not login_id: return False,"Login ID cannot be blank."
    con=db()
    target=con.execute("SELECT * FROM users WHERE id=?",(user_id,)).fetchone()
    if not target:
        con.close(); return False,"User not found."
    dup=con.execute("SELECT id FROM users WHERE lower(login_id)=? AND id<>?",(login_id,user_id)).fetchone()
    if dup:
        con.close(); return False,"This Login ID is already in use."
    fields=["login_id=?","active=?"]; params=[login_id,1 if active else 0]
    changes=["Login ID/status updated"]
    if new_password:
        fields+=["password_hash=?","password_changed_at=?"]
        params+=[generate_password_hash(new_password),now_iso()]
        changes.append("Password reset by MD")
    params.append(user_id)
    con.execute("UPDATE users SET "+",".join(fields)+" WHERE id=?",params)
    con.commit();con.close()
    audit("MD_USER_SECURITY_UPDATE",user_id,login_id,actor,", ".join(changes))
    return True,"User security settings updated."
