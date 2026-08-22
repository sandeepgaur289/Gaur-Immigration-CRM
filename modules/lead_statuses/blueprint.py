from flask import Blueprint

bp=Blueprint(
    "v4_lead_statuses",
    __name__,
    url_prefix="/v4/lead-statuses"
)

def install_lead_statuses(app):
    """
    v4.7.2 DIRECT/LITE:
    Status options are rendered directly by the existing server template.
    No status JavaScript is injected, so there is zero client-side overhead.
    """
    app.extensions["v472_lead_statuses_installed"]=True
