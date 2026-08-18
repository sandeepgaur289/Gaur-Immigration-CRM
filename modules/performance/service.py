def corrected_am_business_month_rankings(con,start_date,end_date,company_code=None):
    """
    v4.1.1 authoritative AM leaderboard calculation.

    Sources:
      Leads Allocated  -> leads.assigned_am + assigned_at/imported_at in selected month
      Positive Leads   -> same allocated leads with interest_score >= 50
      Enrollments      -> client_cases enrollment_date in selected month, linked by lead_db_id;
                          fallback to assigned_employee_id for legacy cases
      Revenue          -> client_cases.total_received for those enrollments
      Conversion       -> enrollments / allocated * 100
      Enrollment Score -> relative enrollment count against best AM in current scope
    """
    q="""SELECT u.id,u.full_name,u.company_code,u.designation,u.photo_mime,u.active,u.employee_id
         FROM users u WHERE u.role='AM'"""
    params=[]
    if company_code:
        q+=" AND u.company_code=?"; params.append(company_code)
    q+=" ORDER BY u.company_code,u.full_name"
    ams=con.execute(q,params).fetchall()

    start_ts=start_date+"T00:00:00"
    end_ts=end_date+"T23:59:59"
    rows=[]

    for u in ams:
        lead_stats=con.execute("""
            SELECT COUNT(*) allocated,
                   COALESCE(SUM(CASE WHEN COALESCE(interest_score,0)>=50 THEN 1 ELSE 0 END),0) positive,
                   COALESCE(SUM(CASE WHEN COALESCE(interest_score,0)>=71 THEN 1 ELSE 0 END),0) hot
            FROM leads
            WHERE assigned_am=?
              AND COALESCE(deleted_at,'')=''
              AND COALESCE(NULLIF(assigned_at,''),imported_at,'') BETWEEN ? AND ?
        """,(u["id"],start_ts,end_ts)).fetchone()

        # New/current enrollment shells are linked back to the originating lead by lead_db_id.
        # Older rows may only carry assigned_employee_id, so that path is included as fallback.
        if u["employee_id"]:
            case_stats=con.execute("""
                SELECT COUNT(DISTINCT c.id) enrollments,
                       COALESCE(SUM(COALESCE(c.total_received,0)),0) revenue
                FROM client_cases c
                LEFT JOIN leads l ON l.id=c.lead_db_id
                WHERE c.enrollment_date BETWEEN ? AND ?
                  AND (
                       l.assigned_am=?
                       OR (c.lead_db_id IS NULL AND c.assigned_employee_id=?)
                  )
            """,(start_date,end_date,u["id"],u["employee_id"])).fetchone()
        else:
            case_stats=con.execute("""
                SELECT COUNT(DISTINCT c.id) enrollments,
                       COALESCE(SUM(COALESCE(c.total_received,0)),0) revenue
                FROM client_cases c
                JOIN leads l ON l.id=c.lead_db_id
                WHERE c.enrollment_date BETWEEN ? AND ?
                  AND l.assigned_am=?
            """,(start_date,end_date,u["id"])).fetchone()

        allocated=int(lead_stats["allocated"] or 0)
        positive=int(lead_stats["positive"] or 0)
        hot=int(lead_stats["hot"] or 0)
        enrollments=int(case_stats["enrollments"] or 0)
        revenue=float(case_stats["revenue"] or 0)
        conversion=round((enrollments/allocated*100),1) if allocated else 0.0

        rows.append({
            "id":u["id"],"full_name":u["full_name"],"company_code":u["company_code"],
            "designation":u["designation"] or "Assistant Manager",
            "photo_mime":u["photo_mime"],"active":int(u["active"] or 0),
            "employee_id":u["employee_id"],"allocated":allocated,"positive":positive,"hot":hot,
            "enrollments":enrollments,"revenue":revenue,"conversion":conversion
        })

    max_enroll=max([x["enrollments"] for x in rows],default=0)
    for x in rows:
        x["score"]=round((x["enrollments"]/max_enroll*100) if max_enroll else 0,1)

    # Business-relevant order. This also prevents every AM showing rank #1
    # merely because all enrollment counts are zero.
    rows.sort(key=lambda x:(-x["enrollments"],-x["revenue"],-x["positive"],-x["allocated"],x["full_name"].lower()))

    rank=0
    previous=None
    for idx,x in enumerate(rows,1):
        key=(x["enrollments"],x["revenue"],x["positive"],x["allocated"])
        if previous is None or key!=previous:
            rank=idx
            previous=key
        x["rank"]=rank
    return rows
