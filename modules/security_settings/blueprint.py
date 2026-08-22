from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from legacy_core import current_user, require_roles
from .service import ensure_schema,create_reset_request,verify_and_reset,md_users,md_audit,md_update_user,admin_email,email_configured

bp=Blueprint("v4_security",__name__,url_prefix="/security",template_folder="templates")

@bp.get("/forgot-password")
def forgot_password():
    return render_template("forgot_password.html")

@bp.post("/forgot-password")
def forgot_password_submit():
    login_id=(request.form.get("login_id") or "").strip()
    try:
        result=create_reset_request(login_id,request.headers.get("X-Forwarded-For",request.remote_addr or ""),request.headers.get("User-Agent",""))
        if result and result.get("cooldown"):
            flash("A recent OTP request already exists. Wait about one minute before requesting again.","error")
        else:
            flash("If this is an active AM/GM account, a 6-digit OTP has been sent to the designated MD/admin Gmail.","success")
        return redirect(url_for("v4_security.reset_password",login_id=login_id))
    except Exception as exc:
        flash(str(exc),"error")
        return redirect(url_for("v4_security.forgot_password"))

@bp.get("/reset-password")
def reset_password():
    return render_template("reset_password.html",login_id=request.args.get("login_id",""))

@bp.post("/reset-password")
def reset_password_submit():
    login_id=(request.form.get("login_id") or "").strip()
    otp=(request.form.get("otp") or "").strip()
    pw=request.form.get("new_password") or ""
    confirm=request.form.get("confirm_password") or ""
    if len(pw)<8:
        flash("New password must be at least 8 characters.","error")
        return redirect(url_for("v4_security.reset_password",login_id=login_id))
    if pw!=confirm:
        flash("New Password and Confirm Password do not match.","error")
        return redirect(url_for("v4_security.reset_password",login_id=login_id))
    ok,msg=verify_and_reset(login_id,otp,pw)
    flash(msg,"success" if ok else "error")
    return redirect(url_for("login") if ok else url_for("v4_security.reset_password",login_id=login_id))

@bp.get("/settings")
@require_roles("MD")
def settings():
    u=current_user()
    return render_template("security_settings.html",u=u,users=md_users(),audit_rows=md_audit(),
                           admin_email=admin_email(),gmail_ready=email_configured())

@bp.post("/settings/user/<int:user_id>")
@require_roles("MD")
def update_user(user_id):
    u=current_user()
    new_password=request.form.get("new_password","")
    if new_password and len(new_password)<8:
        flash("Password must be at least 8 characters.","error")
        return redirect(url_for("v4_security.settings"))
    ok,msg=md_update_user(u,user_id,request.form.get("login_id",""),new_password,request.form.get("active")=="1")
    flash(msg,"success" if ok else "error")
    return redirect(url_for("v4_security.settings"))

@bp.get("/health")
@require_roles("MD")
def health():
    return jsonify({"ok":True,"gmail_configured":email_configured(),
                    "admin_gmail":admin_email() if email_configured() else "",
                    "otp_expiry_minutes":10,"max_attempts":5})

def install_security_settings(app):
    ensure_schema()
    if app.extensions.get("v46_security_settings_installed"):
        return

    @app.after_request
    def _inject_security_links(response):
        try:
            if response.status_code!=200 or "text/html" not in (response.headers.get("Content-Type") or "").lower():
                return response
            u=current_user()
            # LITE: only login page or MD pages require security-link injection.
            if request.path!="/" and (not u or u["role"]!="MD"):
                return response
            data=response.get_data(as_text=True)
            if request.path=="/" and "Forgot Password?" not in data and "</form>" in data:
                link="<div style='margin-top:12px;text-align:center'><a href='/security/forgot-password' style='color:#e6b73f;font-weight:800'>Forgot Password?</a></div>"
                data=data.replace("</form>",link+"</form>",1)
            if u and u["role"]=="MD" and "Security Settings" not in data and "</body>" in data:
                floating="<a href='/security/settings' title='Security Settings' style='position:fixed;left:18px;bottom:18px;z-index:2147482000;background:#0c2d49;color:#e6b73f;border:1px solid #e6b73f;border-radius:12px;padding:10px 12px;text-decoration:none;font-weight:900'>Security Settings</a>"
                data=data.replace("</body>",floating+"</body>",1)
            response.set_data(data); response.headers["Content-Length"]=str(len(response.get_data()))
        except Exception:
            pass
        return response

    app.extensions["v46_security_settings_installed"]=True
