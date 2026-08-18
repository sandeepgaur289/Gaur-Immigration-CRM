# Railway Deployment — v4.0.1

The v4.0 foundation deployment failed because the new thin `app.py`
started Flask on a fixed port (5000) when Railway may start the project
with `python app.py`. Railway healthchecks reach only the dynamically
assigned `$PORT`.

v4.0.1 fixes this permanently:
- `app.py` binds to `0.0.0.0:$PORT`.
- `Procfile` explicitly starts Gunicorn on `$PORT`.
- `railway.json` explicitly starts Gunicorn and healthchecks `/healthz`.
- `requirements.txt` makes fresh builds reproducible.
- Database initialization errors are logged without preventing the HTTP
  server from binding, preserving the resilience of the earlier app.

Railway health endpoint:
  /healthz

v4 module diagnostic endpoint:
  /system/health
