from flask import request, redirect, url_for, flash

REMOVED_PREFIXES=(
    "/chat",
    "/notifications",
    "/api/notifications",
    "/api/presence",
    "/md/chat-oversight",
)

def install_no_chat(app):
    if app.extensions.get("v502_no_chat_installed"):
        return
    @app.before_request
    def _no_chat_guard():
        p=request.path or ""
        if any(p==x or p.startswith(x+"/") for x in REMOVED_PREFIXES):
            flash("Chat / Notifications are removed in this build.","error")
            return redirect(url_for("dashboard"))
    app.extensions["v502_no_chat_installed"]=True
