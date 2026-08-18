"""
Railway to Render Database Migration Script
Run this on Railway web service console:
python3 migrate_to_render.py
"""
import os
import psycopg

RENDER_DB = "postgresql://gaur_crm_db_user:JWuMZaBkpEvP3Ad4N0nuxvycoUAQcNjM@dpg-da23jcbncjis738fb0q0-a/gaur_crm_db"

TABLES = [
    'companies', 'users', 'leads', 'client_cases',
    'employee_master', 'employee_documents', 'employee_performance',
    'allocation_history', 'visitors', 'employee_attendance',
    'lead_documents', 'lead_activity', 'chat_messages',
    'broadcasts', 'broadcast_reads', 'chat_attachments'
]

def migrate():
    src_url = os.environ.get('DATABASE_URL', '')
    if not src_url:
        print("ERROR: DATABASE_URL not found!")
        return

    print("Connecting to Railway DB...")
    src = psycopg.connect(src_url, row_factory=psycopg.rows.dict_row)
    
    print("Connecting to Render DB...")
    dst = psycopg.connect(RENDER_DB, row_factory=psycopg.rows.dict_row)

    for table in TABLES:
        try:
            rows = src.execute(f"SELECT * FROM {table}").fetchall()
            if not rows:
                print(f"{table}: 0 rows - skipped")
                continue
            
            cols = list(rows[0].keys())
            placeholders = ','.join(['%s'] * len(cols))
            col_names = ','.join(cols)
            
            dst.execute(f"DELETE FROM {table}")
            
            for row in rows:
                vals = [row[c] for c in cols]
                dst.execute(
                    f"INSERT INTO {table}({col_names}) VALUES({placeholders}) ON CONFLICT DO NOTHING",
                    vals
                )
            
            dst.commit()
            print(f"{table}: {len(rows)} rows migrated OK")
            
        except Exception as e:
            print(f"{table}: ERROR - {e}")
            dst.rollback()

    src.close()
    dst.close()
    print("\nMIGRATION COMPLETE!")

if __name__ == "__main__":
    migrate()
