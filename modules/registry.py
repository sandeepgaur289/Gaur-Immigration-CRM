from .system.blueprint import bp as system_bp
from .leads.blueprint import bp as leads_bp
from .report_tools import bp as report_tools_bp, install_report_tools
from .security_settings import bp as security_bp, install_security_settings
from .lead_statuses import bp as lead_statuses_bp, install_lead_statuses
from .runtime_lite import install_runtime_lite
from .core_clean import install_core_clean
from .no_chat import install_no_chat
from .direct_lead import bp as direct_lead_bp, install_direct_lead

def register_modules(app):
    if app.extensions.get("gaur_v4_modules_registered"):
        return app

    install_runtime_lite(app)
    install_core_clean(app)
    install_no_chat(app)
    app.register_blueprint(system_bp)
    app.register_blueprint(leads_bp)
    app.register_blueprint(report_tools_bp)
    app.register_blueprint(security_bp)
    app.register_blueprint(lead_statuses_bp)
    app.register_blueprint(direct_lead_bp)

    install_report_tools(app)
    install_security_settings(app)
    install_lead_statuses(app)
    install_direct_lead(app)

    app.extensions["gaur_v4_modules_registered"]=True
    return app
