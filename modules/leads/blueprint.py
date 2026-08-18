import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from legacy_core import current_user, require_roles, db
from .service import dashboard_summary, daily_report, recycle_rows, scoped_company

bp=Blueprint("v4_leads",__name__,url_prefix="/v4/leads",template_folder="templates")

@bp.get("/")
@require_roles("MD","GM")
def home():
    u=current_user(); company=scoped_company(u,request.args.get("company",""))
    return render_template("v4_leads_home.html",u=u,k=dashboard_summary(u,company),company=company)

@bp.get("/daily-report")
@require_roles("MD","GM")
def daily():
    u=current_user(); date=(request.args.get("date") or datetime.date.today().isoformat()).strip()
    company,company_rows,allocations,totals=daily_report(u,date,request.args.get("company",""))
    return render_template("v4_leads_daily.html",u=u,report_date=date,company=company,company_rows=company_rows,allocations=allocations,totals=totals)

@bp.get("/recycle-bin")
@require_roles("MD")
def recycle_bin():
    u=current_user()
    return render_template("v4_leads_recycle.html",u=u,rows=recycle_rows(u))

@bp.post("/recycle-bin/action")
@require_roles("MD")
def recycle_action():
    ids=[int(x) for x in request.form.getlist("lead_ids") if x.isdigit()]
    action=request.form.get("action","")
    if not ids:
        flash("Select at least one lead.","error"); return redirect(url_for("v4_leads.recycle_bin"))
    con=db(); ph=",".join(["?"]*len(ids))
    if action=="restore":
        con.execute(f"UPDATE leads SET deleted_at='',deleted_by='',deletion_reason='' WHERE id IN ({ph})",ids); con.commit()
        flash(f"{len(ids)} lead(s) restored.","success")
    elif action=="erase":
        con.execute(f"DELETE FROM leads WHERE id IN ({ph}) AND COALESCE(deleted_at,'')<>''",ids); con.commit()
        flash(f"{len(ids)} lead(s) permanently deleted.","success")
    else:
        flash("Invalid recycle action.","error")
    con.close()
    return redirect(url_for("v4_leads.recycle_bin"))
