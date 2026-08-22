import time
import threading

_CACHE={}
_CACHE_LOCK=threading.Lock()
_CACHE_TTL=15.0

def _cache_key(start_date,end_date,company_code):
    return (str(start_date),str(end_date),str(company_code or ""))

def clear_performance_cache():
    with _CACHE_LOCK:
        _CACHE.clear()

def corrected_am_business_month_rankings(con,start_date,end_date,company_code=None):
    """
    v4.7 FAST calculator.
    Previous implementation executed 2 SQL queries per AM.
    This version calculates the same leaderboard with grouped SQL queries.
    A short 15-second process cache prevents repeated dashboard refreshes
    from re-running identical month/company calculations.
    """
    key=_cache_key(start_date,end_date,company_code)
    now=time.monotonic()
    with _CACHE_LOCK:
        cached=_CACHE.get(key)
        if cached and (now-cached[0])<_CACHE_TTL:
            return [dict(x) for x in cached[1]]

    q="""SELECT u.id,u.full_name,u.company_code,u.designation,u.photo_mime,u.active,u.employee_id
         FROM users u WHERE u.role='AM'"""
    params=[]
    if company_code:
        q+=" AND u.company_code=?"
        params.append(company_code)
    q+=" ORDER BY u.company_code,u.full_name"
    ams=con.execute(q,params).fetchall()

    start_ts=str(start_date)+"T00:00:00"
    end_ts=str(end_date)+"T23:59:59"

    lead_q="""
        SELECT assigned_am,
               COUNT(*) allocated,
               COALESCE(SUM(CASE WHEN COALESCE(interest_score,0)>=50 THEN 1 ELSE 0 END),0) positive,
               COALESCE(SUM(CASE WHEN COALESCE(interest_score,0)>=71 THEN 1 ELSE 0 END),0) hot
        FROM leads
        WHERE assigned_am IS NOT NULL
          AND COALESCE(deleted_at,'')=''
          AND COALESCE(NULLIF(assigned_at,''),imported_at,'') BETWEEN ? AND ?
    """
    lead_params=[start_ts,end_ts]
    if company_code:
        lead_q+=" AND company_code=?"
        lead_params.append(company_code)
    lead_q+=" GROUP BY assigned_am"
    lead_stats={int(r["assigned_am"]):dict(r) for r in con.execute(lead_q,lead_params).fetchall() if r["assigned_am"] is not None}

    # Current cases linked through lead_db_id.
    linked_q="""
        SELECT l.assigned_am,
               COUNT(DISTINCT c.id) enrollments,
               COALESCE(SUM(COALESCE(c.total_received,0)),0) revenue
        FROM client_cases c
        JOIN leads l ON l.id=c.lead_db_id
        WHERE c.enrollment_date BETWEEN ? AND ?
          AND l.assigned_am IS NOT NULL
    """
    linked_params=[start_date,end_date]
    if company_code:
        linked_q+=" AND l.company_code=?"
        linked_params.append(company_code)
    linked_q+=" GROUP BY l.assigned_am"
    linked={int(r["assigned_am"]):dict(r) for r in con.execute(linked_q,linked_params).fetchall() if r["assigned_am"] is not None}

    # Legacy cases not linked to a lead are grouped once by employee_id.
    legacy_q="""
        SELECT assigned_employee_id,
               COUNT(DISTINCT id) enrollments,
               COALESCE(SUM(COALESCE(total_received,0)),0) revenue
        FROM client_cases
        WHERE enrollment_date BETWEEN ? AND ?
          AND lead_db_id IS NULL
          AND assigned_employee_id IS NOT NULL
        GROUP BY assigned_employee_id
    """
    legacy_stats={str(r["assigned_employee_id"]):dict(r) for r in con.execute(legacy_q,(start_date,end_date)).fetchall() if r["assigned_employee_id"] is not None}

    rows=[]
    for u in ams:
        uid=int(u["id"])
        ls=lead_stats.get(uid,{})
        cs=linked.get(uid,{})
        legacy=legacy_stats.get(str(u["employee_id"]),{}) if u["employee_id"] else {}

        allocated=int(ls.get("allocated") or 0)
        positive=int(ls.get("positive") or 0)
        hot=int(ls.get("hot") or 0)
        enrollments=int(cs.get("enrollments") or 0)+int(legacy.get("enrollments") or 0)
        revenue=float(cs.get("revenue") or 0)+float(legacy.get("revenue") or 0)
        conversion=round((enrollments/allocated*100),1) if allocated else 0.0

        rows.append({
            "id":uid,"full_name":u["full_name"],"company_code":u["company_code"],
            "designation":u["designation"] or "Assistant Manager",
            "photo_mime":u["photo_mime"],"active":int(u["active"] or 0),
            "employee_id":u["employee_id"],"allocated":allocated,"positive":positive,
            "hot":hot,"enrollments":enrollments,"revenue":revenue,"conversion":conversion
        })

    max_enroll=max([x["enrollments"] for x in rows],default=0)
    for x in rows:
        x["score"]=round((x["enrollments"]/max_enroll*100) if max_enroll else 0,1)

    rows.sort(key=lambda x:(-x["enrollments"],-x["revenue"],-x["positive"],-x["allocated"],x["full_name"].lower()))
    rank=0
    previous=None
    for idx,x in enumerate(rows,1):
        key2=(x["enrollments"],x["revenue"],x["positive"],x["allocated"])
        if previous is None or key2!=previous:
            rank=idx
            previous=key2
        x["rank"]=rank

    with _CACHE_LOCK:
        _CACHE[key]=(now,[dict(x) for x in rows])
        # Avoid unbounded cache growth.
        if len(_CACHE)>40:
            oldest=sorted(_CACHE.items(),key=lambda kv:kv[1][0])[:15]
            for k,_ in oldest:
                _CACHE.pop(k,None)
    return rows
