"""One-time migration from the old local mini_crm.db into the cloud PostgreSQL database.

Usage (run from the CRM folder after setting DATABASE_URL):
    python MIGRATE_OLD_LOCAL_DATA.py

The script never deletes cloud rows. Existing primary/unique-key conflicts are skipped.
"""
import os, sqlite3, mimetypes
from pathlib import Path

DATABASE_URL=os.environ.get("DATABASE_URL","").strip()
if not DATABASE_URL:
    raise SystemExit("DATABASE_URL is not set. Migration cancelled.")

try:
    import psycopg
except ImportError:
    raise SystemExit("psycopg is not installed. Run: pip install -r requirements.txt")

ROOT=Path(__file__).resolve().parent
SQLITE_PATH=ROOT/"mini_crm.db"
if not SQLITE_PATH.exists():
    raise SystemExit(f"Old database not found: {SQLITE_PATH}")

# Ensure destination schema exists first.
from app import init_db
init_db()

TABLES=[
    "companies","users","visitors","leads","imports","employee_master",
    "employee_documents","employee_performance","allocation_history","client_cases"
]

src=sqlite3.connect(SQLITE_PATH)
src.row_factory=sqlite3.Row
dst=psycopg.connect(DATABASE_URL)

def target_columns(table):
    with dst.cursor() as c:
        c.execute("""SELECT column_name FROM information_schema.columns
                     WHERE table_schema='public' AND table_name=%s ORDER BY ordinal_position""",(table,))
        return [r[0] for r in c.fetchall()]

def source_columns(table):
    return [r[1] for r in src.execute(f"PRAGMA table_info({table})").fetchall()]

def maybe_embed_employee_photo(data):
    if "photo_data" in data and data.get("photo_data"): return data
    rel=data.get("photo_path") or ""
    if rel and rel != "DB":
        fp=ROOT/rel
        if fp.exists() and fp.is_file():
            data["photo_data"]=fp.read_bytes()
            data["photo_mime"]=mimetypes.guess_type(fp.name)[0] or "image/jpeg"
            data["photo_path"]="DB"
    return data

def maybe_embed_document(data):
    if "file_data" in data and data.get("file_data"): return data
    rel=data.get("stored_path") or ""
    if rel and rel != "DB":
        fp=ROOT/rel
        if fp.exists() and fp.is_file():
            data["file_data"]=fp.read_bytes()
            data["mime_type"]=mimetypes.guess_type(fp.name)[0] or "application/octet-stream"
            data["stored_path"]="DB"
    return data

try:
    with dst.cursor() as out:
        for table in TABLES:
            try:
                scols=set(source_columns(table)); tcols=target_columns(table)
            except sqlite3.OperationalError:
                print(f"SKIP {table}: not present in old database")
                continue
            cols=[c for c in tcols if c in scols]
            # Target has new cloud BLOB columns absent from old source; add them to data below.
            if table=="employee_master":
                for c in ("photo_data","photo_mime"):
                    if c in tcols and c not in cols: cols.append(c)
            if table=="employee_documents":
                for c in ("file_data","mime_type"):
                    if c in tcols and c not in cols: cols.append(c)

            rows=src.execute(f"SELECT * FROM {table}").fetchall()
            moved=0
            for row in rows:
                data={k:row[k] for k in row.keys()}
                if table=="employee_master": data=maybe_embed_employee_photo(data)
                if table=="employee_documents": data=maybe_embed_document(data)
                vals=[data.get(c) for c in cols]
                quoted=','.join('"'+c+'"' for c in cols)
                placeholders=','.join(['%s']*len(cols))
                sql=f'INSERT INTO "{table}" ({quoted}) VALUES ({placeholders}) ON CONFLICT DO NOTHING'
                out.execute(sql,vals)
                moved += out.rowcount if out.rowcount and out.rowcount>0 else 0
            print(f"{table}: {moved} rows inserted / {len(rows)} old rows checked")

        # Bring serial sequences forward after preserving old IDs.
        for table in TABLES:
            out.execute("SELECT pg_get_serial_sequence(%s,'id')",(table,))
            seq=out.fetchone()[0]
            if seq:
                out.execute(f'SELECT COALESCE(MAX(id),1) FROM "{table}"')
                maxid=out.fetchone()[0]
                out.execute("SELECT setval(%s,%s,true)",(seq,maxid))
    dst.commit()
    print("Migration completed. Old local database was not modified.")
except Exception:
    dst.rollback()
    raise
finally:
    src.close(); dst.close()
