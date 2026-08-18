import sys
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from legacy_core import app, init_db
from modules import register_modules

register_modules(app)

try:
    init_db()
    print("GAUR CRM database initialization: OK", flush=True)
except Exception:
    print("GAUR CRM DATABASE INITIALIZATION WARNING:", flush=True)
    traceback.print_exc()

application = app
