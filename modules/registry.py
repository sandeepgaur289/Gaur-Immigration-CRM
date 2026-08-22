from .system.blueprint import bp as system_bp
from .leads.blueprint import bp as leads_bp
from .performance import install_performance_patch
from .chat import bp as chat_bp, install_chat_alerts
from .report_tools import bp as report_tools_bp, install_report_tools
from .security_settings import bp as security_bp, install_security_settings
from .lead_statuses import bp as lead_statuses_bp, install_lead_statuses
from .runtime_lite import install_runtime_lite

def register_modules(app):
    if app.extensions.get("gaur_v4_modules_registered"):
        return app

    install_runtime_lite(app)
    install_performance_patch()

    app.register_blueprint(system_bp)
    app.register_blueprint(leads_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(report_tools_bp)
    app.register_blueprint(security_bp)
    app.register_blueprint(lead_statuses_bp)

    install_chat_alerts(app)
    install_report_tools(app)
    install_security_settings(app)
    install_lead_statuses(app)

    app.extensions["gaur_v4_modules_registered"]=True
    return app
