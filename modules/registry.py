from .system.blueprint import bp as system_bp
from .leads.blueprint import bp as leads_bp

def register_modules(app):
    if app.extensions.get("gaur_v4_modules_registered"):
        return app
    app.register_blueprint(system_bp)
    app.register_blueprint(leads_bp)
    app.extensions["gaur_v4_modules_registered"]=True
    return app
