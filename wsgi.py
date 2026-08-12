import os
from app import app, init_db, IS_POSTGRES

init_db()
print("GAUR CRM Cloud initialized with " + ("PostgreSQL" if IS_POSTGRES else "SQLite"), flush=True)
