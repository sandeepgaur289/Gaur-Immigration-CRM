"""GAUR CRM v4.0 stable entrypoint.

Deployment remains compatible with: gunicorn app:app

The v3.98 application is frozen in legacy_core.py. New v4 functionality is
registered through isolated Blueprints in modules/.
"""
from legacy_core import app
from modules import register_modules

register_modules(app)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
