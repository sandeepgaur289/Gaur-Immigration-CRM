from flask import request, redirect, url_for, flash

REMOVED_PREFIXES=(
    "/chat","/notifications","/api/notifications","/api/presence",
    "/md/chat-oversight","/management-reporting","/performance"
)

def install_core_clean(app):
    if app.extensions.get("v501_core_clean_installed"):
        return

    @app.before_request
    def _guard_removed_features():
        p=request.path or ""
        if any(p==x or p.startswith(x+"/") for x in REMOVED_PREFIXES):
            flash("This feature has been removed from the CORE CLEAN CRM.","error")
            return redirect(url_for("dashboard"))

    app.extensions["v501_core_clean_installed"]=True
