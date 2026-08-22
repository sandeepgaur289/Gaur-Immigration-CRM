from flask import request, redirect, url_for, flash

REMOVED_PREFIXES=(
    "/chat",
    "/notifications",
    "/md/chat-oversight",
    "/management-reporting",
    "/performance",
)

def install_core_only(app):
    if app.extensions.get("v490_core_only_installed"):
        return

    @app.before_request
    def _v490_removed_features_guard():
        p=request.path or ""
        if any(p==x or p.startswith(x+"/") for x in REMOVED_PREFIXES):
            flash("This feature is temporarily removed in CORE mode for performance.","error")
            return redirect(url_for("dashboard"))

    app.extensions["v490_core_only_installed"]=True
