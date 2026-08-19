"""
Temporary migration route - Railway to Render
Access: /run-migration-now?key=GAUR-MIGRATE-2026
"""
from flask import Blueprint, request, jsonify
import os
import psycopg
from psycopg.rows import dict_row

migrate_bp = Blueprint("migrate", __name__)

RENDER_DB = "postgresql://gaur_crm_db_user:JWuMZaBkpEvP3Ad4N0nuxvycoUAQcNjM@dpg-da23jcbncjis738fb0q0-a/gaur_crm_db"

TABLES = [
    'companies', 'users', 'leads', 'client_cases',
    'employee_master', 'employee_performance',
    'allocation_history', 'visitors', 'employee_attendance',
    'lead_activity', 'broadcasts', 'broadcast_reads',
]

@migrate_bp.route("/run-migration-now")
def run_migration():
    key = request.args.get("key", "")
    if key != "GAUR-MIGRATE-2026":
        return jsonify({"error": "Unauthorized"}), 403

    src_url = os.environ.get("DATABASE_URL", "")
    if not src_url:
        return jsonify({"error": "No DATABASE_URL"}), 500

    results = {}
    errors = {}

    try:
        src = psycopg.connect(src_url, row_factory=dict_row)
        dst = psycopg.connect(RENDER_DB, row_factory=dict_row)

        for table in TABLES:
            try:
                rows = src.execute(f"SELECT * FROM {table}").fetchall()
                if not rows:
                    results[table] = 0
                    continue

                cols = list(rows[0].keys())
                placeholders = ",".join(["%s"] * len(cols))
                col_names = ",".join(cols)

                dst.execute(f"DELETE FROM {table}")
                for row in rows:
                    vals = [row[c] for c in cols]
                    try:
                        dst.execute(
                            f"INSERT INTO {table}({col_names}) VALUES({placeholders}) ON CONFLICT DO NOTHING",
                            vals
                        )
                    except Exception:
                        pass

                dst.commit()
                results[table] = len(rows)

            except Exception as e:
                errors[table] = str(e)[:200]
                try:
                    dst.rollback()
                except Exception:
                    pass

        src.close()
        dst.close()

    except Exception as e:
        return jsonify({"error": str(e)[:300]}), 500

    return jsonify({
        "status": "MIGRATION COMPLETE",
        "migrated": results,
        "errors": errors
    })
