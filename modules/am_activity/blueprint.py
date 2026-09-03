"""
AM Activity Report — MD Portal
"""
import datetime
import traceback
from flask import Blueprint, render_template_string, request, redirect, url_for, flash, jsonify
from legacy_core import current_user, require_roles, db, IS_POSTGRES

bp = Blueprint("am_activity", __name__, url_prefix="/md/am-activity")

def _ph():
    return "%s" if IS_POSTGRES else "?"

def _date_bounds(date_range):
    today = datetime.date.today()
    if date_range == "yesterday":
        yd = (today - datetime.timedelta(days=1)).isoformat()
        return yd + "T00:00:00", yd + "T23:59:59", "Yesterday"
    elif date_range == "week":
        start = (today - datetime.timedelta(days=today.weekday())).isoformat()
        return start + "T00:00:00", today.isoformat() + "T23:59:59", "This Week"
    elif date_range == "month":
        start = today.replace(day=1).isoformat()
        return start + "T00:00:00", today.isoformat() + "T23:59:59", "This Month"
    elif date_range == "all":
        return "2000-01-01T00:00:00", "2099-12-31T23:59:59", "All Time"
    else:  # today
        return today.isoformat() + "T00:00:00", today.isoformat() + "T23:59:59", "Today"


_TMPL = r"""{% extends "base.html" %}{% block content %}
<style>
.ac{background:#071d32;border:1px solid #1e4060;border-radius:12px;padding:16px;margin-bottom:16px}
.ath{background:#0a2540;color:#e6b73f;font-size:13px;padding:9px 12px;text-align:left}
.atd{padding:8px 12px;font-size:13px;border-bottom:1px solid #0d2e4a;vertical-align:top}
.bd{display:inline-block;padding:2px 8px;border-radius:20px;font-size:12px;font-weight:600}
.bg{background:#0d3020;color:#48d58b}.br{background:#3d1515;color:#ff7a7a}
.bw{background:#3d2e10;color:#f0a030}.bb{background:#0d2040;color:#8fc8ff}
.by{background:#1a2535;color:#8899aa}
.sn{font-size:24px;font-weight:800;color:#e6b73f}
.sl{font-size:12px;color:#8899aa;margin-top:3px}
</style>
<h1 class="title">📋 AM Activity Report</h1>
<p style="opacity:.7;margin:-8px 0 16px">Har AM ka lead-wise kaam — status, remarks, revert</p>

<div class="ac">
<form method="get" style="display:flex;gap:10px;flex-wrap:wrap;align-items:center">
  {% if u.role=='MD' %}
  <select name="company" style="background:#071d32;border:1px solid #1e4060;color:#fff;padding:7px 12px;border-radius:8px;font-size:13px">
    <option value="">Both Companies</option>
    <option value="SCIC" {{'selected' if company=='SCIC' else ''}}>SCIC – Smart Choice</option>
    <option value="WWIC" {{'selected' if company=='WWIC' else ''}}>WWIC – White Wave</option>
  </select>
  {% endif %}
  <select name="am_id" style="background:#071d32;border:1px solid #1e4060;color:#fff;padding:7px 12px;border-radius:8px;font-size:13px">
    <option value="">All AMs</option>
    {% for a in all_ams %}
    <option value="{{a['id']}}" {{'selected' if am_id==a['id']|string else ''}}>{{a['full_name']}} ({{a['company_code']}})</option>
    {% endfor %}
  </select>
  <select name="date_range" style="background:#071d32;border:1px solid #1e4060;color:#fff;padding:7px 12px;border-radius:8px;font-size:13px">
    <option value="today" {{'selected' if date_range=='today' else ''}}>Today</option>
    <option value="yesterday" {{'selected' if date_range=='yesterday' else ''}}>Yesterday</option>
    <option value="week" {{'selected' if date_range=='week' else ''}}>This Week</option>
    <option value="month" {{'selected' if date_range=='month' else ''}}>This Month</option>
    <option value="all" {{'selected' if date_range=='all' else ''}}>All Time</option>
  </select>
  <button class="btn" type="submit" style="background:#e6b73f;color:#07192b;font-weight:700">🔍 Filter</button>
  <a href="/md/am-activity" class="btn" style="background:#1a3050;color:#fff">Reset</a>
</form>
</div>

<!-- AM Stats Cards -->
{% if am_stats %}
<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:12px;margin-bottom:20px">
{% for s in am_stats %}
<div class="ac" style="border-color:{{'#e6b73f' if s['company_code']=='SCIC' else '#48d58b'}}">
  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px">
    <b style="color:#e6b73f">{{s['full_name']}}</b>
    <span class="bd {{'br' if s['company_code']=='SCIC' else 'bg'}}">{{s['company_code']}}</span>
  </div>
  <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:6px;margin-bottom:10px;text-align:center">
    <div><div class="sn">{{s['total']}}</div><div class="sl">Updates</div></div>
    <div><div class="sn" style="color:#48d58b">{{s['interested']}}</div><div class="sl">Interested</div></div>
    <div><div class="sn" style="color:#ff7a7a">{{s['enrolled']}}</div><div class="sl">Enrolled</div></div>
  </div>
  <div style="display:flex;gap:6px;flex-wrap:wrap;margin-bottom:10px">
    <span class="bd by">📞 {{s['calls']}} Calls</span>
    <span class="bd bw">📅 {{s['followups']}} Follow-ups</span>
    <span class="bd bb">🏢 {{s['visits']}} Visits</span>
  </div>
  <a href="/md/am-activity/{{s['user_id']}}?date_range={{date_range}}" class="btn" style="background:#1a3050;color:#e6b73f;width:100%;text-align:center;display:block;font-size:13px">👁 Full Activity</a>
</div>
{% endfor %}
</div>
{% endif %}

<!-- Activity Table -->
<div class="ac">
  <h3 style="color:#e6b73f;margin:0 0 12px">📝 Activity Log — {{activities|length}} records</h3>
  {% if activities %}
  <div class="tablewrap">
  <table style="width:100%">
    <thead><tr>
      <th class="ath">Time</th><th class="ath">AM</th><th class="ath">Company</th>
      <th class="ath">Client</th><th class="ath">Mobile</th><th class="ath">Status</th>
      <th class="ath">Remarks</th><th class="ath">Follow-up</th>
    </tr></thead>
    <tbody>
    {% for a in activities %}
    <tr>
      <td class="atd" style="white-space:nowrap;color:#8899aa;font-size:12px">{{(a['updated_at'] or '')[:16]}}</td>
      <td class="atd" style="font-weight:700;color:#e6b73f">{{a['am_name'] or a['updated_by']}}</td>
      <td class="atd"><span class="bd {{'br' if a['company_code']=='SCIC' else 'bg'}}">{{a['company_code']}}</span></td>
      <td class="atd">{{a['client_name'] or '—'}}</td>
      <td class="atd" style="font-size:12px">{{a['mobile'] or '—'}}</td>
      <td class="atd">
        {% set st = a['status'] or '' %}
        {% if st in ('Interested','Enrolled','Office Visit') %}<span class="bd bg">{{st}}</span>
        {% elif st in ('Not Interested','Closed','Invalid No.','No Plan','Budget Issue') %}<span class="bd br">{{st}}</span>
        {% elif st in ('Follow Up','Follow-up','Call Back','Discussion') %}<span class="bd bw">{{st}}</span>
        {% elif st in ('Called','Not Picked','Not Connected','No WhatsApp') %}<span class="bd bb">{{st}}</span>
        {% else %}<span class="bd by">{{st or '—'}}</span>{% endif %}
      </td>
      <td class="atd" style="max-width:260px;font-size:12px;color:#ccc;word-break:break-word">{{a['remarks'] or '—'}}</td>
      <td class="atd" style="font-size:12px;color:{{'#48d58b' if a['followup_date'] else '#8899aa'}}">{{a['followup_date'] or '—'}}</td>
    </tr>
    {% endfor %}
    </tbody>
  </table>
  </div>
  {% else %}
  <p style="opacity:.6;text-align:center;padding:30px">Is period mein koi activity nahi mili.</p>
  {% endif %}
</div>
<a href="/ams" style="color:#e6b73f">← Back to AM Directory</a>
{% endblock %}"""


_DETAIL_TMPL = r"""{% extends "base.html" %}{% block content %}
<style>
.ac{background:#071d32;border:1px solid #1e4060;border-radius:12px;padding:16px;margin-bottom:16px}
.ath{background:#0a2540;color:#e6b73f;font-size:13px;padding:9px 12px;text-align:left}
.atd{padding:8px 12px;font-size:13px;border-bottom:1px solid #0d2e4a;vertical-align:top}
.bd{display:inline-block;padding:2px 8px;border-radius:20px;font-size:12px;font-weight:600}
.bg{background:#0d3020;color:#48d58b}.br{background:#3d1515;color:#ff7a7a}
.bw{background:#3d2e10;color:#f0a030}.bb{background:#0d2040;color:#8fc8ff}.by{background:#1a2535;color:#8899aa}
.sb{background:#0a2540;border-radius:10px;padding:12px;text-align:center}
.sn{font-size:26px;font-weight:800;color:#e6b73f}.sl{font-size:12px;color:#8899aa;margin-top:3px}
</style>
<div style="display:flex;align-items:center;gap:12px;margin-bottom:18px">
  <a href="/md/am-activity" style="color:#e6b73f;font-size:22px;text-decoration:none">←</a>
  <div>
    <h1 class="title" style="margin:0">{{am['full_name']}} — Activity</h1>
    <p style="opacity:.6;margin:3px 0 0;font-size:13px">{{am['login_id']}} • {{am['company_code']}} • {{date_label}}</p>
  </div>
</div>

<div class="ac" style="padding:10px">
<form method="get" style="display:flex;gap:10px;flex-wrap:wrap;align-items:center">
  <select name="date_range" style="background:#071d32;border:1px solid #1e4060;color:#fff;padding:7px 12px;border-radius:8px;font-size:13px">
    <option value="today" {{'selected' if date_range=='today' else ''}}>Today</option>
    <option value="yesterday" {{'selected' if date_range=='yesterday' else ''}}>Yesterday</option>
    <option value="week" {{'selected' if date_range=='week' else ''}}>This Week</option>
    <option value="month" {{'selected' if date_range=='month' else ''}}>This Month</option>
    <option value="all" {{'selected' if date_range=='all' else ''}}>All Time</option>
  </select>
  <button class="btn" type="submit" style="background:#e6b73f;color:#07192b;font-weight:700">🔍 Filter</button>
</form>
</div>

<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(120px,1fr));gap:10px;margin-bottom:18px">
  <div class="sb"><div class="sn">{{stats['total']}}</div><div class="sl">Total Updates</div></div>
  <div class="sb"><div class="sn" style="color:#48d58b">{{stats['interested']}}</div><div class="sl">Interested</div></div>
  <div class="sb"><div class="sn" style="color:#ff7a7a">{{stats['not_interested']}}</div><div class="sl">Not Interested</div></div>
  <div class="sb"><div class="sn" style="color:#f0a030">{{stats['followup']}}</div><div class="sl">Follow-ups</div></div>
  <div class="sb"><div class="sn" style="color:#8fc8ff">{{stats['calls']}}</div><div class="sl">Calls</div></div>
  <div class="sb"><div class="sn" style="color:#e6b73f">{{stats['enrolled']}}</div><div class="sl">Enrolled</div></div>
  <div class="sb"><div class="sn" style="color:#48d58b">{{stats['visits']}}</div><div class="sl">Visits</div></div>
  <div class="sb"><div class="sn" style="color:#8899aa">{{stats['leads_assigned']}}</div><div class="sl">Leads Assigned</div></div>
</div>

<div class="ac">
  <h3 style="color:#e6b73f;margin:0 0 12px">📝 Full Log — {{activities|length}} records</h3>
  {% if activities %}
  <div class="tablewrap">
  <table style="width:100%">
    <thead><tr>
      <th class="ath">Date & Time</th><th class="ath">Lead ID</th><th class="ath">Client</th>
      <th class="ath">Mobile</th><th class="ath">Status</th><th class="ath">Remarks / Revert</th><th class="ath">Follow-up</th>
    </tr></thead>
    <tbody>
    {% for a in activities %}
    <tr>
      <td class="atd" style="white-space:nowrap;color:#8899aa;font-size:12px">{{(a['updated_at'] or '')[:16]}}</td>
      <td class="atd" style="font-size:12px"><a href="/lead/{{a['lead_db_id']}}" style="color:#8fc8ff">{{a['lead_id'] or a['lead_db_id']}}</a></td>
      <td class="atd" style="font-weight:600">{{a['client_name'] or '—'}}</td>
      <td class="atd" style="font-size:12px">{{a['mobile'] or '—'}}</td>
      <td class="atd">
        {% set st = a['status'] or '' %}
        {% if st in ('Interested','Enrolled','Office Visit') %}<span class="bd bg">{{st}}</span>
        {% elif st in ('Not Interested','Closed','Invalid No.','No Plan','Budget Issue') %}<span class="bd br">{{st}}</span>
        {% elif st in ('Follow Up','Follow-up','Call Back','Discussion') %}<span class="bd bw">{{st}}</span>
        {% elif st in ('Called','Not Picked','Not Connected','No WhatsApp') %}<span class="bd bb">{{st}}</span>
        {% else %}<span class="bd by">{{st or '—'}}</span>{% endif %}
      </td>
      <td class="atd" style="max-width:280px;font-size:12px;color:#ccc;word-break:break-word">{{a['remarks'] or '—'}}</td>
      <td class="atd" style="font-size:12px;color:{{'#48d58b' if a['followup_date'] else '#8899aa'}}">{{a['followup_date'] or '—'}}</td>
    </tr>
    {% endfor %}
    </tbody>
  </table>
  </div>
  {% else %}
  <p style="opacity:.6;text-align:center;padding:30px">Is period mein koi activity nahi mili.</p>
  {% endif %}
</div>
{% endblock %}"""


@bp.get("/")
@require_roles("MD", "GM")
def summary():
    u          = current_user()
    con        = db()
    date_range = request.args.get("date_range", "today")
    company    = request.args.get("company", "").strip().upper()
    am_id      = request.args.get("am_id", "").strip()
    p          = _ph()

    if u["role"] == "GM":
        company = u["company_code"]

    start, end, _ = _date_bounds(date_range)

    try:
        if u["role"] == "MD":
            all_ams = [dict(r) for r in con.execute(
                "SELECT id, full_name, company_code FROM users WHERE role='AM' ORDER BY company_code, full_name"
            ).fetchall()]
        else:
            all_ams = [dict(r) for r in con.execute(
                f"SELECT id, full_name, company_code FROM users WHERE role='AM' AND company_code={p} ORDER BY full_name",
                (company,)
            ).fetchall()]

        # AM list
        am_where  = f"WHERE role='AM'"
        am_params = []
        if company:
            am_where += f" AND company_code={p}"
            am_params.append(company)
        if am_id and am_id.isdigit():
            am_where += f" AND id={p}"
            am_params.append(int(am_id))

        am_rows = [dict(r) for r in con.execute(
            f"SELECT id, login_id, full_name, company_code FROM users {am_where} ORDER BY company_code, full_name",
            am_params
        ).fetchall()]

        am_stats = []
        for am in am_rows:
            lid = am["login_id"]
            def _c(extra="", params=()):
                return con.execute(
                    f"SELECT COUNT(*) c FROM lead_activity WHERE updated_by={p} AND updated_at BETWEEN {p} AND {p} {extra}",
                    (lid, start, end) + params
                ).fetchone()["c"]
            am_stats.append({
                "user_id":    am["id"],
                "full_name":  am["full_name"],
                "company_code": am["company_code"],
                "total":      _c(),
                "interested": _c(f"AND status='Interested'"),
                "enrolled":   _c(f"AND status='Enrolled'"),
                "calls":      _c(f"AND status IN ('Called','Not Picked','Not Connected','No WhatsApp','Invalid No.')"),
                "followups":  _c(f"AND status IN ('Follow Up','Follow-up','Call Back','Discussion')"),
                "visits":     _c(f"AND status='Office Visit'"),
            })

        # Activity log
        act_conds  = [f"a.updated_at BETWEEN {p} AND {p}"]
        act_params = [start, end]
        if company:
            act_conds.append(f"l.company_code={p}")
            act_params.append(company)
        if am_id and am_id.isdigit():
            act_conds.append(f"l.assigned_am={p}")
            act_params.append(int(am_id))

        activities = [dict(r) for r in con.execute(f"""
            SELECT a.lead_id AS lead_db_id, a.status, a.remarks, a.followup_date,
                   a.updated_by, a.updated_at,
                   l.client_name, l.mobile, l.company_code,
                   u.full_name AS am_name
            FROM lead_activity a
            JOIN leads l ON l.id = a.lead_id
            LEFT JOIN users u ON u.login_id = a.updated_by
            WHERE {' AND '.join(act_conds)}
            ORDER BY a.updated_at DESC
            LIMIT 500
        """, act_params).fetchall()]

    except Exception:
        activities = []
        am_stats   = []
        all_ams    = []

    con.close()
    return render_template_string(_TMPL,
        u=u, am_stats=am_stats, activities=activities,
        all_ams=all_ams, company=company, am_id=am_id, date_range=date_range
    )


@bp.get("/<int:user_id>")
@require_roles("MD", "GM")
def detail(user_id):
    u   = current_user()
    con = db()
    p   = _ph()

    try:
        am = con.execute(f"SELECT * FROM users WHERE id={p} AND role='AM'", (user_id,)).fetchone()
        if not am:
            con.close()
            flash("AM not found", "error")
            return redirect(url_for("am_activity.summary"))
        am = dict(am)

        if u["role"] == "GM" and am["company_code"] != u["company_code"]:
            con.close()
            flash("Access denied", "error")
            return redirect(url_for("am_activity.summary"))

        date_range = request.args.get("date_range", "month")
        start, end, date_label = _date_bounds(date_range)
        lid = am["login_id"]

        def _c(extra=""):
            return con.execute(
                f"SELECT COUNT(*) c FROM lead_activity WHERE updated_by={p} AND updated_at BETWEEN {p} AND {p} {extra}",
                (lid, start, end)
            ).fetchone()["c"]

        stats = {
            "total":          _c(),
            "interested":     _c(f"AND status='Interested'"),
            "not_interested": _c(f"AND status='Not Interested'"),
            "enrolled":       _c(f"AND status='Enrolled'"),
            "followup":       _c(f"AND status IN ('Follow Up','Follow-up','Call Back','Discussion')"),
            "calls":          _c(f"AND status IN ('Called','Not Picked','Not Connected','No WhatsApp','Invalid No.')"),
            "visits":         _c(f"AND status='Office Visit'"),
            "leads_assigned": con.execute(
                f"SELECT COUNT(*) c FROM leads WHERE assigned_am={p} AND COALESCE(deleted_at,'')=''",
                (user_id,)
            ).fetchone()["c"],
        }

        activities = [dict(r) for r in con.execute(f"""
            SELECT a.lead_id AS lead_db_id, a.status, a.remarks, a.followup_date,
                   a.updated_by, a.updated_at,
                   l.lead_id AS lead_id, l.client_name, l.mobile
            FROM lead_activity a
            JOIN leads l ON l.id = a.lead_id
            WHERE a.updated_by={p} AND a.updated_at BETWEEN {p} AND {p}
            ORDER BY a.updated_at DESC
            LIMIT 1000
        """, (lid, start, end)).fetchall()]

    except Exception:
        traceback.print_exc()
        stats      = {k: 0 for k in ("total","interested","not_interested","enrolled","followup","calls","visits","leads_assigned")}
        activities = []
        date_range = request.args.get("date_range", "month")
        start, end, date_label = _date_bounds(date_range)

    con.close()
    return render_template_string(_DETAIL_TMPL,
        u=u, am=am, stats=stats, activities=activities,
        date_range=date_range, date_label=date_label
    )


def install_am_activity(app):
    if app.extensions.get("am_activity_installed"):
        return

    @app.after_request
    def _inject_btn(response):
        try:
            if response.status_code != 200:
                return response
            if "text/html" not in (response.headers.get("Content-Type") or ""):
                return response
            if request.path != "/ams":
                return response
            u = current_user()
            if not u or u["role"] not in ("MD", "GM"):
                return response
            data = response.get_data(as_text=True)
            if "am_act_injected" in data:
                return response
            import re
            def _add(m):
                uid  = m.group(1)
                orig = m.group(0)
                btn  = (f'<a href="/md/am-activity/{uid}" class="btn" '
                        f'style="background:#1a3050;color:#e6b73f;padding:6px 12px;'
                        f'font-size:13px;margin-right:6px">📋 Activity</a>')
                return btn + orig
            data = re.sub(r'<form[^>]+action="/ams/(\d+)/toggle"', _add, data)
            if 'AM Directory' in data:
                link = ('<a href="/md/am-activity" class="btn" style="background:#e6b73f;'
                        'color:#07192b;font-weight:700;margin-bottom:14px;display:inline-block">'
                        '📋 View All AM Activity</a><br>')
                data = data.replace('<h2', link + '<h2', 1)
            data += '<!-- am_act_injected -->'
            response.set_data(data)
            response.headers["Content-Length"] = str(len(response.get_data()))
        except Exception:
            pass
        return response

    app.extensions["am_activity_installed"] = True
