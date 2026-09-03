"""
AM Activity Report — MD Portal
================================
Route:
  GET /md/am-activity/<user_id>   Full activity log of a specific AM (MD/GM only)
  GET /md/am-activity              All AMs activity summary (MD only)
"""

import datetime
import traceback
from flask import Blueprint, render_template_string, request, redirect, url_for, flash
from legacy_core import current_user, require_roles, db, IS_POSTGRES

bp = Blueprint("am_activity", __name__, url_prefix="/md/am-activity")

def _ph():
    return "%s" if IS_POSTGRES else "?"

# ── HTML Templates ────────────────────────────────────────────────────────────

_SUMMARY_TMPL = r"""{% extends "base.html" %}{% block content %}
<style>
.act-card{background:#071d32;border:1px solid #1e4060;border-radius:12px;padding:16px;margin-bottom:16px}
.act-table th{background:#0a2540;color:#e6b73f;font-size:13px;padding:10px 12px;text-align:left}
.act-table td{padding:9px 12px;font-size:13px;border-bottom:1px solid #0d2e4a;vertical-align:top}
.act-table tr:hover td{background:#0a2540}
.badge{display:inline-block;padding:3px 9px;border-radius:20px;font-size:12px;font-weight:600}
.badge-hot{background:#3d1515;color:#ff7a7a}
.badge-warm{background:#3d2e10;color:#f0a030}
.badge-cold{background:#0d2040;color:#8fc8ff}
.badge-green{background:#0d3020;color:#48d58b}
.badge-grey{background:#1a2535;color:#8899aa}
.am-name{font-weight:700;color:#e6b73f}
.stat-num{font-size:22px;font-weight:800;color:#e6b73f}
.stat-label{font-size:12px;color:#8899aa;margin-top:2px}
.filter-bar{display:flex;gap:10px;flex-wrap:wrap;margin-bottom:16px;align-items:center}
.filter-bar select,.filter-bar input{background:#071d32;border:1px solid #1e4060;color:#fff;padding:7px 12px;border-radius:8px;font-size:13px}
</style>

<h1 class="title">📋 AM Activity Report</h1>
<p style="opacity:.7;margin-top:-8px;margin-bottom:16px">Har AM ka lead-wise kaam — status updates, remarks, revert</p>

<!-- Filters -->
<div class="act-card filter-bar">
  <form method="get" style="display:flex;gap:10px;flex-wrap:wrap;align-items:center;width:100%">
    <select name="company">
      <option value="">Both Companies</option>
      <option value="SCIC" {{'selected' if company=='SCIC'}}>SCIC – Smart Choice</option>
      <option value="WWIC" {{'selected' if company=='WWIC'}}>WWIC – White Wave</option>
    </select>
    <select name="am_id">
      <option value="">All AMs</option>
      {% for am in all_ams %}
      <option value="{{am.id}}" {{'selected' if am_id==am.id|string}}>{{am.full_name}} ({{am.company_code}})</option>
      {% endfor %}
    </select>
    <select name="date_range">
      <option value="today" {{'selected' if date_range=='today'}}>Today</option>
      <option value="yesterday" {{'selected' if date_range=='yesterday'}}>Yesterday</option>
      <option value="week" {{'selected' if date_range=='week'}}>This Week</option>
      <option value="month" {{'selected' if date_range=='month'}}>This Month</option>
      <option value="all" {{'selected' if date_range=='all'}}>All Time</option>
    </select>
    <button class="btn" type="submit" style="background:#e6b73f;color:#07192b;font-weight:700">🔍 Filter</button>
    <a href="/md/am-activity" class="btn" style="background:#1a3050;color:#fff">Reset</a>
  </form>
</div>

<!-- AM-wise Stats Cards -->
{% if am_stats %}
<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:14px;margin-bottom:20px">
  {% for s in am_stats %}
  <div class="act-card" style="border-color:{{'#e6b73f' if s.company_code=='SCIC' else '#48d58b'}}">
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px">
      <span class="am-name">{{s.full_name}}</span>
      <span class="badge {{'badge-hot' if s.company_code=='SCIC' else 'badge-green'}}">{{s.company_code}}</span>
    </div>
    <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px;margin-bottom:12px">
      <div style="text-align:center"><div class="stat-num">{{s.total_updates}}</div><div class="stat-label">Updates</div></div>
      <div style="text-align:center"><div class="stat-num" style="color:#48d58b">{{s.interested}}</div><div class="stat-label">Interested</div></div>
      <div style="text-align:center"><div class="stat-num" style="color:#ff7a7a">{{s.enrolled}}</div><div class="stat-label">Enrolled</div></div>
    </div>
    <div style="display:flex;gap:6px;flex-wrap:wrap;margin-bottom:12px">
      <span class="badge badge-grey">📞 {{s.calls}} Calls</span>
      <span class="badge badge-warm">📅 {{s.followups}} Follow-ups</span>
      <span class="badge badge-cold">🏢 {{s.visits}} Visits</span>
    </div>
    <a href="/md/am-activity/{{s.user_id}}?date_range={{date_range}}" class="btn" style="background:#1a3050;color:#e6b73f;width:100%;text-align:center;display:block;font-size:13px">👁 View Full Activity</a>
  </div>
  {% endfor %}
</div>
{% endif %}

<!-- Detailed Activity Table -->
<div class="act-card">
  <h3 style="color:#e6b73f;margin:0 0 12px">📝 Activity Log ({{activities|length}} records)</h3>
  {% if activities %}
  <div class="tablewrap">
  <table class="act-table" style="width:100%">
    <thead><tr>
      <th>Time</th><th>AM Name</th><th>Company</th><th>Client</th><th>Mobile</th><th>Status</th><th>Remarks</th><th>Follow-up</th>
    </tr></thead>
    <tbody>
    {% for a in activities %}
    <tr>
      <td style="white-space:nowrap;color:#8899aa;font-size:12px">{{a.updated_at[:16] if a.updated_at else '—'}}</td>
      <td class="am-name">{{a.am_name or a.updated_by}}</td>
      <td><span class="badge {{'badge-hot' if a.company_code=='SCIC' else 'badge-green'}}">{{a.company_code}}</span></td>
      <td>{{a.client_name or '—'}}</td>
      <td style="font-size:12px">{{a.mobile or '—'}}</td>
      <td>
        {% set s = a.status or '' %}
        {% if s in ('Interested','Enrolled','Office Visit') %}
          <span class="badge badge-green">{{s}}</span>
        {% elif s in ('Not Interested','Closed','Invalid No.') %}
          <span class="badge badge-hot">{{s}}</span>
        {% elif s in ('Follow Up','Follow-up','Call Back','Discussion') %}
          <span class="badge badge-warm">{{s}}</span>
        {% else %}
          <span class="badge badge-grey">{{s}}</span>
        {% endif %}
      </td>
      <td style="max-width:280px;font-size:12px;color:#ccc">{{a.remarks or '—'}}</td>
      <td style="font-size:12px;color:#8899aa">{{a.followup_date or '—'}}</td>
    </tr>
    {% endfor %}
    </tbody>
  </table>
  </div>
  {% else %}
  <p style="opacity:.6;text-align:center;padding:30px">Is period mein koi activity nahi mili.</p>
  {% endif %}
</div>

<div style="margin-top:12px">
  <a href="/ams" style="color:#e6b73f">← Back to AM Directory</a>
</div>
{% endblock %}"""


_DETAIL_TMPL = r"""{% extends "base.html" %}{% block content %}
<style>
.act-card{background:#071d32;border:1px solid #1e4060;border-radius:12px;padding:16px;margin-bottom:16px}
.act-table th{background:#0a2540;color:#e6b73f;font-size:13px;padding:10px 12px;text-align:left}
.act-table td{padding:9px 12px;font-size:13px;border-bottom:1px solid #0d2e4a;vertical-align:top}
.act-table tr:hover td{background:#0a2540}
.badge{display:inline-block;padding:3px 9px;border-radius:20px;font-size:12px;font-weight:600}
.badge-hot{background:#3d1515;color:#ff7a7a}
.badge-warm{background:#3d2e10;color:#f0a030}
.badge-cold{background:#0d2040;color:#8fc8ff}
.badge-green{background:#0d3020;color:#48d58b}
.badge-grey{background:#1a2535;color:#8899aa}
.stat-box{background:#0a2540;border-radius:10px;padding:14px;text-align:center}
.stat-num{font-size:28px;font-weight:800;color:#e6b73f}
.stat-label{font-size:12px;color:#8899aa;margin-top:4px}
</style>

<div style="display:flex;align-items:center;gap:14px;margin-bottom:20px">
  <a href="/md/am-activity" style="color:#e6b73f;font-size:20px">←</a>
  <div>
    <h1 class="title" style="margin:0">{{am.full_name}} — Activity Report</h1>
    <p style="opacity:.6;margin:4px 0 0;font-size:14px">{{am.login_id}} • {{am.company_code}} • {{date_label}}</p>
  </div>
</div>

<!-- Date Filter -->
<div class="act-card" style="padding:12px">
  <form method="get" style="display:flex;gap:10px;flex-wrap:wrap;align-items:center">
    <select name="date_range" style="background:#071d32;border:1px solid #1e4060;color:#fff;padding:7px 12px;border-radius:8px;font-size:13px">
      <option value="today" {{'selected' if date_range=='today'}}>Today</option>
      <option value="yesterday" {{'selected' if date_range=='yesterday'}}>Yesterday</option>
      <option value="week" {{'selected' if date_range=='week'}}>This Week</option>
      <option value="month" {{'selected' if date_range=='month'}}>This Month</option>
      <option value="all" {{'selected' if date_range=='all'}}>All Time</option>
    </select>
    <button class="btn" type="submit" style="background:#e6b73f;color:#07192b;font-weight:700">🔍 Filter</button>
  </form>
</div>

<!-- Stats Row -->
<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(130px,1fr));gap:12px;margin-bottom:20px">
  <div class="stat-box"><div class="stat-num">{{stats.total}}</div><div class="stat-label">Total Updates</div></div>
  <div class="stat-box"><div class="stat-num" style="color:#48d58b">{{stats.interested}}</div><div class="stat-label">Interested</div></div>
  <div class="stat-box"><div class="stat-num" style="color:#ff7a7a">{{stats.not_interested}}</div><div class="stat-label">Not Interested</div></div>
  <div class="stat-box"><div class="stat-num" style="color:#f0a030">{{stats.followup}}</div><div class="stat-label">Follow-ups</div></div>
  <div class="stat-box"><div class="stat-num" style="color:#8fc8ff">{{stats.calls}}</div><div class="stat-label">Calls Done</div></div>
  <div class="stat-box"><div class="stat-num" style="color:#e6b73f">{{stats.enrolled}}</div><div class="stat-label">Enrolled</div></div>
  <div class="stat-box"><div class="stat-num" style="color:#48d58b">{{stats.visits}}</div><div class="stat-label">Office Visits</div></div>
  <div class="stat-box"><div class="stat-num" style="color:#8899aa">{{stats.leads_assigned}}</div><div class="stat-label">Leads Assigned</div></div>
</div>

<!-- Activity Table -->
<div class="act-card">
  <h3 style="color:#e6b73f;margin:0 0 12px">📝 Full Activity Log ({{activities|length}} records)</h3>
  {% if activities %}
  <div class="tablewrap">
  <table class="act-table" style="width:100%">
    <thead><tr>
      <th>Date & Time</th><th>Lead ID</th><th>Client Name</th><th>Mobile</th><th>Status</th><th>Remarks / Revert</th><th>Follow-up Date</th>
    </tr></thead>
    <tbody>
    {% for a in activities %}
    <tr>
      <td style="white-space:nowrap;color:#8899aa;font-size:12px">{{a.updated_at[:16] if a.updated_at else '—'}}</td>
      <td style="font-size:12px"><a href="/lead/{{a.lead_db_id}}" style="color:#8fc8ff">{{a.lead_id or a.lead_db_id}}</a></td>
      <td style="font-weight:600">{{a.client_name or '—'}}</td>
      <td style="font-size:12px">{{a.mobile or '—'}}</td>
      <td>
        {% set s = a.status or '' %}
        {% if s in ('Interested','Enrolled','Office Visit') %}
          <span class="badge badge-green">{{s}}</span>
        {% elif s in ('Not Interested','Closed','Invalid No.','No Plan','Budget Issue') %}
          <span class="badge badge-hot">{{s}}</span>
        {% elif s in ('Follow Up','Follow-up','Call Back','Discussion') %}
          <span class="badge badge-warm">{{s}}</span>
        {% elif s in ('Called','Not Picked','Not Connected','No WhatsApp') %}
          <span class="badge badge-cold">{{s}}</span>
        {% else %}
          <span class="badge badge-grey">{{s}}</span>
        {% endif %}
      </td>
      <td style="max-width:300px;font-size:12px;color:#ccc;word-break:break-word">{{a.remarks or '—'}}</td>
      <td style="font-size:12px;color:{{'#48d58b' if a.followup_date else '#8899aa'}}">{{a.followup_date or '—'}}</td>
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


# ── Helpers ───────────────────────────────────────────────────────────────────

def _date_bounds(date_range):
    today = datetime.date.today()
    if date_range == "today":
        return today.isoformat() + "T00:00:00", today.isoformat() + "T23:59:59", "Today"
    elif date_range == "yesterday":
        yd = (today - datetime.timedelta(days=1)).isoformat()
        return yd + "T00:00:00", yd + "T23:59:59", "Yesterday"
    elif date_range == "week":
        start = (today - datetime.timedelta(days=today.weekday())).isoformat()
        return start + "T00:00:00", today.isoformat() + "T23:59:59", "This Week"
    elif date_range == "month":
        start = today.replace(day=1).isoformat()
        return start + "T00:00:00", today.isoformat() + "T23:59:59", "This Month"
    else:
        return "2000-01-01T00:00:00", "2099-12-31T23:59:59", "All Time"


# ── Routes ────────────────────────────────────────────────────────────────────

@bp.get("/")
@require_roles("MD", "GM")
def summary():
    u = current_user()
    con = db()

    date_range = request.args.get("date_range", "today")
    company    = request.args.get("company", "").strip().upper()
    am_id      = request.args.get("am_id", "").strip()

    # GM sirf apni company dekh sakta hai
    if u["role"] == "GM":
        company = u["company_code"]

    start, end, _ = _date_bounds(date_range)

    # All AMs for filter dropdown
    if u["role"] == "MD":
        all_ams = [dict(r) for r in con.execute(
            "SELECT id, full_name, company_code FROM users WHERE role='AM' ORDER BY company_code, full_name"
        ).fetchall()]
    else:
        all_ams = [dict(r) for r in con.execute(
            f"SELECT id, full_name, company_code FROM users WHERE role='AM' AND company_code={_ph()} ORDER BY full_name",
            (company,)
        ).fetchall()]

    # AM-wise stats
    am_where = "WHERE u.role='AM'"
    am_params = []
    if company:
        am_where += f" AND u.company_code={_ph()}"
        am_params.append(company)
    if am_id and am_id.isdigit():
        am_where += f" AND u.id={_ph()}"
        am_params.append(int(am_id))

    am_rows = [dict(r) for r in con.execute(
        f"SELECT id, login_id, full_name, company_code FROM users {am_where} ORDER BY company_code, full_name",
        am_params
    ).fetchall()]

    am_stats = []
    for am in am_rows:
        lid = am["login_id"]
        p = _ph()
        total = con.execute(
            f"SELECT COUNT(*) c FROM lead_activity WHERE updated_by={p} AND updated_at BETWEEN {p} AND {p}",
            (lid, start, end)
        ).fetchone()["c"]
        interested = con.execute(
            f"SELECT COUNT(*) c FROM lead_activity WHERE updated_by={p} AND status='Interested' AND updated_at BETWEEN {p} AND {p}",
            (lid, start, end)
        ).fetchone()["c"]
        enrolled = con.execute(
            f"SELECT COUNT(*) c FROM lead_activity WHERE updated_by={p} AND status='Enrolled' AND updated_at BETWEEN {p} AND {p}",
            (lid, start, end)
        ).fetchone()["c"]
        calls = con.execute(
            f"SELECT COUNT(*) c FROM lead_activity WHERE updated_by={p} AND status IN ('Called','Not Picked','Not Connected','No WhatsApp','Invalid No.') AND updated_at BETWEEN {p} AND {p}",
            (lid, start, end)
        ).fetchone()["c"]
        followups = con.execute(
            f"SELECT COUNT(*) c FROM lead_activity WHERE updated_by={p} AND status IN ('Follow Up','Follow-up','Call Back','Discussion') AND updated_at BETWEEN {p} AND {p}",
            (lid, start, end)
        ).fetchone()["c"]
        visits = con.execute(
            f"SELECT COUNT(*) c FROM lead_activity WHERE updated_by={p} AND status='Office Visit' AND updated_at BETWEEN {p} AND {p}",
            (lid, start, end)
        ).fetchone()["c"]
        am_stats.append({
            "user_id": am["id"],
            "full_name": am["full_name"],
            "company_code": am["company_code"],
            "total_updates": total,
            "interested": interested,
            "enrolled": enrolled,
            "calls": calls,
            "followups": followups,
            "visits": visits,
        })

    # Detailed activity log
    act_where = [f"a.updated_at BETWEEN {_ph()} AND {_ph()}"]
    act_params = [start, end]

    if company:
        act_where.append(f"l.company_code={_ph()}")
        act_params.append(company)
    if am_id and am_id.isdigit():
        act_where.append(f"l.assigned_am={_ph()}")
        act_params.append(int(am_id))

    w = " AND ".join(act_where)
    try:
        activities = [dict(r) for r in con.execute(f"""
            SELECT a.id, a.lead_id as lead_db_id, a.status, a.remarks, a.followup_date, a.updated_by, a.updated_at,
                   l.lead_id as lead_code, l.client_name, l.mobile, l.company_code,
                   u.full_name as am_name
            FROM lead_activity a
            JOIN leads l ON l.id = a.lead_id
            LEFT JOIN users u ON u.login_id = a.updated_by
            WHERE {w}
            ORDER BY a.updated_at DESC
            LIMIT 500
        """, act_params).fetchall()]
    except Exception:
        activities = []

    for act in activities:
        act["lead_id"] = act.get("lead_code", "")

    con.close()

    return render_template_string(_SUMMARY_TMPL,
        u=u, am_stats=am_stats, activities=activities,
        all_ams=all_ams, company=company, am_id=am_id, date_range=date_range
    )


@bp.get("/<int:user_id>")
@require_roles("MD", "GM")
def detail(user_id):
    u   = current_user()
    con = db()

    am = con.execute(f"SELECT * FROM users WHERE id={_ph()} AND role='AM'", (user_id,)).fetchone()
    if not am:
        con.close()
        flash("AM not found", "error")
        return redirect(url_for("am_activity.summary"))

    am = dict(am)

    # GM access check
    if u["role"] == "GM" and am["company_code"] != u["company_code"]:
        con.close()
        flash("Access denied", "error")
        return redirect(url_for("am_activity.summary"))

    date_range = request.args.get("date_range", "month")
    start, end, date_label = _date_bounds(date_range)
    lid = am["login_id"]

    # Stats
    p = _ph()
    def cnt(extra_where, extra_params=[]):
        return con.execute(
            f"SELECT COUNT(*) c FROM lead_activity WHERE updated_by={p} AND updated_at BETWEEN {p} AND {p} {extra_where}",
            [lid, start, end] + extra_params
        ).fetchone()["c"]

    stats = {
        "total":         cnt(""),
        "interested":    cnt(f"AND status='Interested'"),
        "not_interested":cnt(f"AND status='Not Interested'"),
        "enrolled":      cnt(f"AND status='Enrolled'"),
        "followup":      cnt(f"AND status IN ('Follow Up','Follow-up','Call Back','Discussion')"),
        "calls":         cnt(f"AND status IN ('Called','Not Picked','Not Connected','No WhatsApp','Invalid No.')"),
        "visits":        cnt(f"AND status='Office Visit'"),
        "leads_assigned":con.execute(
            f"SELECT COUNT(*) c FROM leads WHERE assigned_am={p} AND COALESCE(deleted_at,'')=''",
            (user_id,)
        ).fetchone()["c"],
    }

    # Full activity
    try:
        p = _ph()
        activities = [dict(r) for r in con.execute(f"""
            SELECT a.id, a.lead_id as lead_db_id, a.status, a.remarks, a.followup_date, a.updated_by, a.updated_at,
                   l.lead_id as lead_code, l.client_name, l.mobile
            FROM lead_activity a
            JOIN leads l ON l.id = a.lead_id
            WHERE a.updated_by={p} AND a.updated_at BETWEEN {p} AND {p}
            ORDER BY a.updated_at DESC
            LIMIT 1000
        """, (lid, start, end)).fetchall()]
    except Exception:
        activities = []

    for act in activities:
        act["lead_id"] = act.get("lead_code", "")

    con.close()

    return render_template_string(_DETAIL_TMPL,
        u=u, am=am, stats=stats, activities=activities,
        date_range=date_range, date_label=date_label
    )


def install_am_activity(app):
    """Inject 'View Activity' button into /ams page for MD."""
    if app.extensions.get("am_activity_installed"):
        return

    @app.after_request
    def _inject_activity_btn(response):
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
            if "am_activity_injected" in data:
                return response

            # Inject button next to each Deactivate/Reactivate button
            import re
            # Find pattern: /ams/<id>/toggle  → add View Activity button before it
            def add_btn(m):
                user_id = m.group(1)
                orig = m.group(0)
                btn = (
                    f'<a href="/md/am-activity/{user_id}" '
                    f'class="btn" style="background:#1a3050;color:#e6b73f;'
                    f'padding:6px 12px;font-size:13px;margin-right:6px">📋 Activity</a>'
                )
                return btn + orig

            new_data = re.sub(
                r'<form[^>]+action="/ams/(\d+)/toggle"',
                add_btn,
                data
            )

            # Also add summary link at top
            marker = '<h2'
            if marker in new_data and 'AM Directory' in new_data:
                link = (
                    '<a href="/md/am-activity" class="btn" '
                    'style="background:#e6b73f;color:#07192b;font-weight:700;margin-bottom:14px;display:inline-block">'
                    '📋 View All AM Activity</a><br>'
                )
                new_data = new_data.replace(
                    '<h2', link + '<h2', 1
                )

            new_data += '<!-- am_activity_injected -->'
            response.set_data(new_data)
            response.headers["Content-Length"] = str(len(response.get_data()))
        except Exception:
            pass
        return response

    app.extensions["am_activity_installed"] = True
