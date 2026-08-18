from .system.blueprint import bp as system_bp
from .leads.blueprint import bp as leads_bp
from .performance import install_performance_patch

def register_modules(app):
    if app.extensions.get("gaur_v4_modules_registered"):
        return app

    # Calculation patch first, before any dashboard request is served.
    install_performance_patch()

    app.register_blueprint(system_bp)
    app.register_blueprint(leads_bp)

    app.extensions["gaur_v4_modules_registered"]=True
    return app
