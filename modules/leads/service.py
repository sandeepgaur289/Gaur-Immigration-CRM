from legacy_core import db

COMPANY_NAMES={"SCIC":"Smart Choice","WWIC":"White Wave"}

def scoped_company(user, requested=""):
    requested=(requested or "").strip().upper()
    if user["role"]=="GM":
        return user["company_code"]
    return requested if requested in ("SCIC","WWIC") else ""

def dashboard_summary(user, company=""):
    company=scoped_company(user,company)
    con=db(); where=["COALESCE(deleted_at,'')=''"]; params=[]
    if company:
        where.append("company_code=?"); params.append(company)
    w=" WHERE "+" AND ".join(where)
    total=con.execute("SELECT COUNT(*) c FROM leads"+w,params).fetchone()["c"]
    unallocated=con.execute("SELECT COUNT(*) c FROM leads"+w+" AND assigned_am IS NULL",params).fetchone()["c"]
    worked=con.execute("SELECT COUNT(*) c FROM leads l"+w+" AND EXISTS(SELECT 1 FROM lead_activity a WHERE a.lead_id=l.id)",params).fetchone()["c"]
    positive=con.execute("SELECT COUNT(*) c FROM leads"+w+" AND COALESCE(interest_score,0)>=50",params).fetchone()["c"]
    archived=con.execute("SELECT COUNT(*) c FROM leads WHERE COALESCE(deleted_at,'')<>''").fetchone()["c"] if user["role"]=="MD" else 0
    con.close()
    return {"company":company,"total":int(total or 0),"allocated":int(total or 0)-int(unallocated or 0),
            "unallocated":int(unallocated or 0),"worked":int(worked or 0),"positive":int(positive or 0),"archived":int(archived or 0)}

def daily_report(user, report_date, company=""):
    company=scoped_company(user,company)
    start=report_date+"T00:00:00"; end=report_date+"T23:59:59"
    con=db(); company_rows=[]
    companies=[company] if company else ["SCIC","WWIC"]
    for cc in companies:
        imported=con.execute("SELECT COUNT(*) c FROM leads WHERE company_code=? AND COALESCE(imported_at,'') BETWEEN ? AND ?",(cc,start,end)).fetchone()["c"]
        active=con.execute("SELECT COUNT(*) c FROM leads WHERE company_code=? AND COALESCE(imported_at,'') BETWEEN ? AND ? AND COALESCE(deleted_at,'')=''",(cc,start,end)).fetchone()["c"]
        files=con.execute("""SELECT COUNT(*) files,COALESCE(SUM(total_rows),0) rows,
            COALESCE(SUM(same_company_duplicates),0) same_dup,COALESCE(SUM(cross_company_duplicates),0) cross_dup
            FROM imports WHERE company_code=? AND COALESCE(imported_at,'') BETWEEN ? AND ?""",(cc,start,end)).fetchone()
        company_rows.append({"company_code":cc,"company_name":COMPANY_NAMES[cc],"new_leads":int(imported or 0),
            "active_new":int(active or 0),"moved_to_bin":int(imported or 0)-int(active or 0),
            "uploaded_rows":int(files["rows"] or 0),"files":int(files["files"] or 0),
            "same_dup":int(files["same_dup"] or 0),"cross_dup":int(files["cross_dup"] or 0)})
    q="""SELECT ah.company_code,ah.am_user_id,u.full_name,COALESCE(SUM(ah.quantity),0) allocated_qty,COUNT(ah.id) actions
         FROM allocation_history ah LEFT JOIN users u ON u.id=ah.am_user_id
         WHERE COALESCE(ah.allocated_at,'') BETWEEN ? AND ?"""
    p=[start,end]
    if company:
        q+=" AND ah.company_code=?"; p.append(company)
    q+=" GROUP BY ah.company_code,ah.am_user_id,u.full_name ORDER BY ah.company_code,allocated_qty DESC,u.full_name"
    allocations=[dict(r) for r in con.execute(q,p).fetchall()]
    con.close()
    totals={"uploaded_rows":sum(x["uploaded_rows"] for x in company_rows),"new_leads":sum(x["new_leads"] for x in company_rows),
            "active_new":sum(x["active_new"] for x in company_rows),"moved_to_bin":sum(x["moved_to_bin"] for x in company_rows),
            "allocated":sum(int(x["allocated_qty"] or 0) for x in allocations)}
    return company,company_rows,allocations,totals

def recycle_rows(user):
    if user["role"]!="MD": return []
    con=db()
    rows=[dict(r) for r in con.execute("""SELECT id,lead_id,company_code,client_name,mobile,upload_batch,deleted_by,deleted_at,deletion_reason
        FROM leads WHERE COALESCE(deleted_at,'')<>'' ORDER BY deleted_at DESC LIMIT 1000""").fetchall()]
    con.close()
    return rows
