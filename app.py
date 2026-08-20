import os
import sys
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Load .env file if present
_env_path = ROOT / ".env"
if _env_path.exists():
    with open(_env_path) as _f:
        for _line in _f:
            _line = _line.strip()
            if _line and not _line.startswith("#") and "=" in _line:
                _k, _v = _line.split("=", 1)
                os.environ.setdefault(_k.strip(), _v.strip())

from legacy_core import app, init_db
from modules import register_modules

register_modules(app)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5050"))
    try:
        init_db()
        print("GAUR CRM v4.0.2 database initialization: OK", flush=True)
    except Exception:
        print("GAUR CRM DATABASE INITIALIZATION WARNING:", flush=True)
        traceback.print_exc()

    print(f"GAUR CRM v4.0.2 listening on 0.0.0.0:{port}", flush=True)

    try:
        from waitress import serve
        serve(app, host="0.0.0.0", port=port, threads=8)
    except ImportError:
        app.run(host="0.0.0.0", port=port, debug=False)