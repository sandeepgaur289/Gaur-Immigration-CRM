from flask import Blueprint
from legacy_core import current_user

bp=Blueprint(
    "v4_lead_statuses",
    __name__,
    url_prefix="/v4/lead-statuses",
    static_folder="static",
    static_url_path="/static"
)

def install_lead_statuses(app):
    """
    v4.7.1 LITE:
    Inject the status helper ONLY on pages that actually contain a status dropdown.
    This avoids unnecessary JS/DOM work across Dashboard, Accounts, Chat, Reports, etc.
    """
    if app.extensions.get("v471_lead_statuses_installed"):
        return

    @app.after_request
    def _inject_status_manager(response):
        try:
            if response.status_code != 200:
                return response
            ctype=(response.headers.get("Content-Type") or "").lower()
            if "text/html" not in ctype:
                return response

            u=current_user()
            if not u or u["role"] not in ("MD","GM","AM"):
                return response

            data=response.get_data(as_text=True)

            # Critical LITE optimization:
            # Do not inject this module unless the page actually has a lead-status control.
            if 'name="status"' not in data and "name='status'" not in data:
                return response
            if "</body>" not in data or "v471-lead-status-manager" in data:
                return response

            tag='<script id="v471-lead-status-manager" src="/v4/lead-statuses/static/lead_statuses.js?v=4.7.1" defer></script>'
            data=data.replace("</body>",tag+"</body>",1)
            response.set_data(data)
            response.headers["Content-Length"]=str(len(response.get_data()))
        except Exception:
            pass
        return response

    app.extensions["v471_lead_statuses_installed"]=True
