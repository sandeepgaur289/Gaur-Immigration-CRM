import datetime
import re
import uuid

from flask import Blueprint, render_template, request, redirect, url_for, flash
from legacy_core import db, current_user, require_roles

bp=Blueprint("v4_direct_lead",__name__,url_prefix="/direct-lead",template_folder="templates")

STATUSES=[
    "Interested","Not Interested","Call Back","Not Picked","No Plan","Budget Issue",
    "Not Connected","Invalid No.","No WhatsApp","Enrolled","Discussion","Follow Up",
    "Payment After Visa","Closed","Office Visit","Docs Received"
]

def _clean_mobile(value):
    return re.sub(r"\D","",str(value or ""))[:20]

def _new_lead_id(company):
    stamp=datetime.datetime.now().strftime("%y%m%d")
    return f"{company}-LEAD-{stamp}-{uuid.uuid4().hex[:6].upper()}"

@bp.route("/new",methods=["GET","POST"])
@require_roles("GM","AM")
def new_direct_lead():
    u=current_user()
    con=db()

    if u["role"]=="GM":
        ams=con.execute(
            "SELECT id,full_name FROM users WHERE role='AM' AND active=1 AND company_code=? ORDER BY full_name",
            (u["company_code"],)
        ).fetchall()
    else:
        ams=[]

    if request.method=="POST":
        company=u["company_code"]
        client_name=(request.form.get("client_name") or "").strip()
        mobile=_clean_mobile(request.form.get("mobile"))
        email=(request.form.get("email") or "").strip()
        city=(request.form.get("city") or "").strip()
        country=(request.form.get("country") or "").strip()
        visa_type=(request.form.get("visa_type") or "").strip()
        source=(request.form.get("source") or "Direct Contact").strip() or "Direct Contact"
        status=(request.form.get("status") or "Interested").strip()
        remarks=(request.form.get("remarks") or "").strip()

        try:
            interest=max(0,min(100,int(float((request.form.get("interest_score") or "0").strip()))))
        except Exception:
            interest=0

        if not client_name:
            con.close()
            flash("Client Name is required.","error")
            return redirect(url_for("v4_direct_lead.new_direct_lead"))
        if len(mobile)<8:
            con.close()
            flash("Please enter a valid client mobile number.","error")
            return redirect(url_for("v4_direct_lead.new_direct_lead"))

        duplicate_type=""
        same=con.execute(
            "SELECT id FROM leads WHERE company_code=? AND REPLACE(REPLACE(COALESCE(mobile,''),' ',''),'-','')=? AND COALESCE(deleted_at,'')='' LIMIT 1",
            (company,mobile)
        ).fetchone()
        cross=con.execute(
            "SELECT id FROM leads WHERE company_code<>? AND REPLACE(REPLACE(COALESCE(mobile,''),' ',''),'-','')=? AND COALESCE(deleted_at,'')='' LIMIT 1",
            (company,mobile)
        ).fetchone()
        if same:
            duplicate_type="same"
        elif cross:
            duplicate_type="cross"

        assigned_am=u["id"] if u["role"]=="AM" else None
        if u["role"]=="GM":
            raw_am=(request.form.get("assigned_am") or "").strip()
            if raw_am.isdigit():
                valid=con.execute(
                    "SELECT id FROM users WHERE id=? AND role='AM' AND active=1 AND company_code=?",
                    (int(raw_am),company)
                ).fetchone()
                if valid:
                    assigned_am=int(raw_am)

        now=datetime.datetime.now().isoformat(timespec="seconds")
        lead_id=_new_lead_id(company)

        lead_db_id=None
        for _ in range(3):
            try:
                cur=con.execute(
                    """INSERT INTO leads(
                    lead_id,company_code,client_name,mobile,email,city,country,visa_type,source,
                    duplicate_type,assigned_am,status,remarks,interest_score,imported_by,imported_at,
                    assigned_at,assigned_by
                    ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (
                        lead_id,company,client_name,mobile,email,city,country,visa_type,source,
                        duplicate_type,assigned_am,status,remarks,interest,u["login_id"],now,
                        now if assigned_am else "",u["login_id"] if assigned_am else ""
                    )
                )
                lead_db_id=cur.lastrowid
                con.commit()
                break
            except Exception as exc:
                if "lead_id" in str(exc).lower() or "unique" in str(exc).lower():
                    lead_id=_new_lead_id(company)
                    continue
                con.close()
                raise

        if lead_db_id is None:
            con.close()
            flash("Could not generate a unique Lead ID. Please try again.","error")
            return redirect(url_for("v4_direct_lead.new_direct_lead"))

        con.close()
        msg=f"Direct lead created successfully • {lead_id}"
        if duplicate_type=="same":
            msg+=" • Existing mobile found in same company."
        elif duplicate_type=="cross":
            msg+=" • Mobile also exists in the other company."
        flash(msg,"success")
        return redirect(url_for("lead_profile",lead_db_id=lead_db_id))

    con.close()
    return render_template("direct_lead_new.html",u=u,ams=ams,statuses=STATUSES)

def install_direct_lead(app):
    if app.extensions.get("v474_direct_lead_installed"):
        return

    @app.after_request
    def _inject_direct_lead_button(response):
        try:
            if response.status_code!=200 or "text/html" not in (response.headers.get("Content-Type") or "").lower():
                return response

            u=current_user()
            if not u or u["role"] not in ("GM","AM"):
                return response

            if request.path not in ("/my-leads","/leads"):
                return response

            data=response.get_data(as_text=True)
            if "v474AddDirectLead" in data:
                return response

            button = (
                '<a id="v474AddDirectLead" class="btn" href="/direct-lead/new" '
                'style="display:inline-block;margin:0 0 14px 0;background:#e6b73f;'
                'color:#071829;font-weight:900">+ Add Direct Lead</a>'
            )

            if request.path=="/my-leads":
                marker='<h1 class="title">My Leads</h1>'
                if marker in data:
                    data=data.replace(marker,marker+button,1)
            else:
                marker='<h1 class="title">'
                idx=data.find(marker)
                if idx>=0:
                    end=data.find("</h1>",idx)
                    if end>=0:
                        end+=5
                        data=data[:end]+button+data[end:]

            response.set_data(data)
            response.headers["Content-Length"]=str(len(response.get_data()))
        except Exception:
            pass
        return response

    app.extensions["v474_direct_lead_installed"]=True
