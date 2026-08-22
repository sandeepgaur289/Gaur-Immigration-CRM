from flask import request, redirect, url_for, flash

CHAT_PREFIXES = (
    "/chat",
    "/notifications",
    "/md/chat-oversight",
    "/api/presence",
    "/api/notifications",
)

def install_no_chat(app):
    if app.extensions.get("v492_no_chat_installed"):
        return

    @app.before_request
    def _disable_chat_system():
        p = request.path or ""
        if any(p == prefix or p.startswith(prefix + "/") for prefix in CHAT_PREFIXES):
            flash("Chat / Communication system is disabled in this build.", "error")
            return redirect(url_for("dashboard"))

    app.extensions["v492_no_chat_installed"] = True
