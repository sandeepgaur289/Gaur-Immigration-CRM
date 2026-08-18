import datetime
import mimetypes
import os

from flask import Blueprint, jsonify, request, render_template, redirect, url_for, flash
from werkzeug.utils import secure_filename

import legacy_core
from legacy_core import (
    current_user, db, authorized_chat_people, can_chat_with,
    broadcast_visible_to_user, role_display
)

bp=Blueprint(
    "v4_chat_notify", __name__,
    url_prefix="/v4/chat",
    template_folder="templates",
    static_folder="static",
    static_url_path="/static"
)

AUDIO_EXTS={".mp3",".wav",".m4a",".aac",".ogg",".oga",".opus",".webm"}
IMAGE_EXTS={".jpg",".jpeg",".png",".webp",".gif"}
DOC_EXTS={".pdf",".doc",".docx",".xls",".xlsx",".txt",".csv",".ppt",".pptx"}
ALLOWED_EXTS=AUDIO_EXTS|IMAGE_EXTS|DOC_EXTS
MAX_ATTACHMENT=25*1024*1024


def _now():
    return datetime.datetime.now().isoformat(timespec="seconds")


def _presence_online(last_seen):
    if not last_seen:
        return False
    try:
        dt=datetime.datetime.fromisoformat(str(last_seen).replace("Z",""))
        return (datetime.datetime.now()-dt).total_seconds() <= 150
    except Exception:
        return False


def _person_cards(con,u):
    try:
        legacy_core.ensure_presence_schema()
    except Exception:
        pass

    people=authorized_chat_people(con,u)
    out=[]
    for p in people:
        unread=int(con.execute(
            "SELECT COUNT(*) c FROM chat_messages WHERE sender_id=? AND recipient_id=? AND COALESCE(read_at,'')=''",
            (p["id"],u["id"])
        ).fetchone()["c"] or 0)

        last=con.execute(
            """SELECT cm.id,cm.message,cm.created_at,cm.sender_id,cm.attachment_id,
                      ca.original_name attachment_name,ca.mime_type attachment_mime
               FROM chat_messages cm
               LEFT JOIN chat_attachments ca ON ca.id=cm.attachment_id
               WHERE (cm.sender_id=? AND cm.recipient_id=?)
                  OR (cm.sender_id=? AND cm.recipient_id=?)
               ORDER BY cm.id DESC LIMIT 1""",
            (u["id"],p["id"],p["id"],u["id"])
        ).fetchone()

        last_seen=""
        try:
            last_seen=p["last_seen_at"] or ""
        except Exception:
            pass

        if last:
            preview=(last["message"] or "").strip()
            if not preview and last["attachment_id"]:
                mime=(last["attachment_mime"] or "")
                if mime.startswith("audio/"):
                    preview="🎙 Voice message"
                elif mime.startswith("image/"):
                    preview="📷 Photo"
                else:
                    preview="📎 "+(last["attachment_name"] or "Attachment")
            if not preview:
                preview="Message"
            if int(last["sender_id"])==int(u["id"]):
                preview="You: "+preview
            last_time=last["created_at"] or ""
            last_id=int(last["id"] or 0)
        else:
            preview=role_display(p["role"],p["designation"])+" • "+(p["company_code"] or "THE GAUR")
            last_time=""
            last_id=0

        out.append({
            "id":int(p["id"]),
            "full_name":p["full_name"],
            "role":p["role"],
            "designation":p["designation"] or "",
            "company_code":p["company_code"] or "",
            "photo_mime":p["photo_mime"] or "",
            "unread":unread,
            "preview":preview[:95],
            "last_time":last_time,
            "last_seen":last_seen,
            "online":_presence_online(last_seen),
            "last_id":last_id,
        })

    out.sort(key=lambda x:(-x["last_id"],-x["unread"],x["full_name"].lower()))
    return out


def _fetch_messages(con,u,peer_id,after_id=0,limit=250,mark_read=True):
    peer=con.execute("SELECT * FROM users WHERE id=?",(peer_id,)).fetchone()
    if not peer or not can_chat_with(u,peer):
        return None,[]

    if mark_read:
        con.execute(
            "UPDATE chat_messages SET read_at=? WHERE sender_id=? AND recipient_id=? AND COALESCE(read_at,'')=''",
            (_now(),peer_id,u["id"])
        )
        con.commit()

    q="""SELECT cm.*,l.lead_id lead_code,l.client_name,l.status lead_status,l.interest_score,
                ca.id attachment_id,ca.original_name attachment_name,ca.mime_type attachment_mime
         FROM chat_messages cm
         LEFT JOIN leads l ON l.id=cm.lead_id
         LEFT JOIN chat_attachments ca ON ca.id=cm.attachment_id
         WHERE ((cm.sender_id=? AND cm.recipient_id=?) OR (cm.sender_id=? AND cm.recipient_id=?))
           AND cm.id>?
           AND ((cm.sender_id=? AND cm.deleted_by_sender=0) OR
                (cm.recipient_id=? AND cm.deleted_by_recipient=0))
         ORDER BY cm.id ASC LIMIT ?"""
    rows=con.execute(q,(u["id"],peer_id,peer_id,u["id"],after_id,u["id"],u["id"],limit)).fetchall()
    return peer,rows


def _broadcasts(con,u):
    rows=con.execute(
        """SELECT b.*,usr.full_name sender_name
           FROM broadcasts b JOIN users usr ON usr.id=b.sender_id
           ORDER BY b.id DESC LIMIT 80"""
    ).fetchall()
    return [b for b in rows if broadcast_visible_to_user(b,u)]


def chat_page():
    u=current_user()
    if not u:
        return redirect(url_for("login"))

    con=db()
    people=_person_cards(con,u)

    peer=None
    messages=[]
    shareable_leads=[]
    peer_id=(request.args.get("peer") or "").strip()
    if peer_id.isdigit():
        peer,messages=_fetch_messages(con,u,int(peer_id),after_id=0,limit=350,mark_read=True)
        if peer:
            if u["role"]=="AM":
                shareable_leads=con.execute(
                    "SELECT id,lead_id,client_name,mobile FROM leads WHERE assigned_am=? AND COALESCE(deleted_at,'')='' ORDER BY id DESC LIMIT 200",
                    (u["id"],)
                ).fetchall()
            elif u["role"]=="GM":
                shareable_leads=con.execute(
                    "SELECT id,lead_id,client_name,mobile FROM leads WHERE company_code=? AND COALESCE(deleted_at,'')='' ORDER BY id DESC LIMIT 250",
                    (u["company_code"],)
                ).fetchall()
            elif u["role"]=="MD":
                shareable_leads=con.execute(
                    "SELECT id,lead_id,client_name,mobile FROM leads WHERE COALESCE(deleted_at,'')='' ORDER BY id DESC LIMIT 300"
                ).fetchall()

    broadcasts=_broadcasts(con,u)
    con.close()

    return render_template(
        "lets_chat_upp.html",
        u=u,people=people,peer=peer,messages=messages,
        shareable_leads=shareable_leads,broadcasts=broadcasts,
        role_display=role_display
    )


def _save_attachment(con,u,upload):
    if not upload or not upload.filename:
        return None

    safe_name=secure_filename(upload.filename)[:180]
    ext=(os.path.splitext(safe_name)[1] or "").lower()
    if ext not in ALLOWED_EXTS:
        raise ValueError("Unsupported attachment type.")

    data=upload.read()
    if not data:
        raise ValueError("Selected attachment is empty.")
    if len(data)>MAX_ATTACHMENT:
        raise ValueError("Attachment must be 25 MB or smaller.")

    mime=upload.mimetype or mimetypes.guess_type(safe_name)[0] or "application/octet-stream"

    if legacy_core.IS_POSTGRES:
        row=con.execute(
            """INSERT INTO chat_attachments
               (uploader_id,original_name,mime_type,file_bytes,created_at)
               VALUES(?,?,?,?,?) RETURNING id""",
            (u["id"],safe_name,mime,data,_now())
        ).fetchone()
        return int(row["id"])

    cur=con.execute(
        """INSERT INTO chat_attachments
           (uploader_id,original_name,mime_type,file_bytes,created_at)
           VALUES(?,?,?,?,?)""",
        (u["id"],safe_name,mime,data,_now())
    )
    return int(cur.lastrowid)


def send_message():
    u=current_user()
    wants_json=(
        request.headers.get("X-Requested-With")=="XMLHttpRequest"
        or "application/json" in (request.headers.get("Accept") or "")
    )
    if not u:
        return (jsonify({"ok":False,"error":"Login required"}),401) if wants_json else redirect(url_for("login"))

    rid=(request.form.get("recipient_id") or "").strip()
    message=(request.form.get("message") or "").strip()[:4000]
    lead_id=(request.form.get("lead_id") or "").strip()
    upload=request.files.get("attachment")
    has_upload=bool(upload and upload.filename)

    if not rid.isdigit() or (not message and not has_upload and not lead_id.isdigit()):
        err="Write a message, attach a file/voice note, or share a client."
        if wants_json:
            return jsonify({"ok":False,"error":err}),400
        flash(err,"error")
        return redirect(url_for("chat_center"))

    con=db()
    peer=con.execute("SELECT * FROM users WHERE id=?",(int(rid),)).fetchone()
    if not peer or not can_chat_with(u,peer):
        con.close()
        if wants_json:
            return jsonify({"ok":False,"error":"Not authorized"}),403
        flash("You are not authorized to message this user.","error")
        return redirect(url_for("chat_center"))

    valid_lead=None
    if lead_id.isdigit():
        lead=con.execute("SELECT * FROM leads WHERE id=?",(int(lead_id),)).fetchone()
        if lead and (u["role"]=="MD" or (u["company_code"] and lead["company_code"]==u["company_code"])):
            if u["role"]!="AM" or int(lead["assigned_am"] or 0)==int(u["id"]):
                valid_lead=int(lead["id"])

    try:
        attachment_id=_save_attachment(con,u,upload) if has_upload else None

        now=_now()
        if legacy_core.IS_POSTGRES:
            row=con.execute(
                """INSERT INTO chat_messages
                   (sender_id,recipient_id,message,lead_id,attachment_id,created_at)
                   VALUES(?,?,?,?,?,?) RETURNING id""",
                (u["id"],peer["id"],message,valid_lead,attachment_id,now)
            ).fetchone()
            mid=int(row["id"])
        else:
            cur=con.execute(
                """INSERT INTO chat_messages
                   (sender_id,recipient_id,message,lead_id,attachment_id,created_at)
                   VALUES(?,?,?,?,?,?)""",
                (u["id"],peer["id"],message,valid_lead,attachment_id,now)
            )
            mid=int(cur.lastrowid)
        con.commit()
    except ValueError as exc:
        try: con.rollback()
        except Exception: pass
        con.close()
        if wants_json:
            return jsonify({"ok":False,"error":str(exc)}),400
        flash(str(exc),"error")
        return redirect(url_for("chat_center",peer=peer["id"]))
    except Exception:
        try: con.rollback()
        except Exception: pass
        con.close()
        legacy_core.app.logger.exception("Lets Chat Upp send failed")
        if wants_json:
            return jsonify({"ok":False,"error":"Message could not be sent."}),500
        flash("Message could not be sent. Please try again.","error")
        return redirect(url_for("chat_center",peer=peer["id"]))

    con.close()
    if wants_json:
        return jsonify({"ok":True,"id":mid,"created_at":now})
    return redirect(url_for("chat_center",peer=peer["id"]))


@bp.get("/thread")
def thread_api():
    u=current_user()
    if not u:
        return jsonify({"ok":False}),401

    peer=(request.args.get("peer") or "").strip()
    after=(request.args.get("after") or "0").strip()
    if not peer.isdigit():
        return jsonify({"ok":False,"error":"Peer required"}),400
    try:
        after_id=max(0,int(after))
    except Exception:
        after_id=0

    con=db()
    peer_row,rows=_fetch_messages(con,u,int(peer),after_id=after_id,limit=150,mark_read=True)
    if not peer_row:
        con.close()
        return jsonify({"ok":False,"error":"Not authorized"}),403

    items=[]
    for r in rows:
        mime=r["attachment_mime"] or ""
        items.append({
            "id":int(r["id"]),
            "sender_id":int(r["sender_id"]),
            "message":r["message"] or "",
            "created_at":r["created_at"] or "",
            "read_at":r["read_at"] or "",
            "attachment_id":int(r["attachment_id"]) if r["attachment_id"] else None,
            "attachment_name":r["attachment_name"] or "",
            "attachment_mime":mime,
            "attachment_kind":"audio" if mime.startswith("audio/") else ("image" if mime.startswith("image/") else "file"),
            "lead_id":int(r["lead_id"]) if r["lead_id"] else None,
            "lead_code":r["lead_code"] or "",
            "client_name":r["client_name"] or "",
            "lead_status":r["lead_status"] or "",
            "interest_score":int(r["interest_score"] or 0),
        })
    last_id=max([x["id"] for x in items],default=after_id)
    con.close()
    return jsonify({"ok":True,"messages":items,"last_id":last_id})


@bp.get("/people")
def people_api():
    u=current_user()
    if not u:
        return jsonify({"ok":False}),401
    con=db()
    people=_person_cards(con,u)
    con.close()
    return jsonify({"ok":True,"people":people})


@bp.get("/state")
def state():
    # Kept for v4.2 cross-page notification system.
    u=current_user()
    if not u:
        return jsonify({"ok":False,"authenticated":False}),401
    try:
        after_id=max(0,int(request.args.get("after_id","0") or 0))
    except Exception:
        after_id=0

    con=db()
    unread=int(con.execute(
        "SELECT COUNT(*) c FROM chat_messages WHERE recipient_id=? AND COALESCE(read_at,'')=''",
        (u["id"],)
    ).fetchone()["c"] or 0)
    latest=int(con.execute(
        "SELECT COALESCE(MAX(id),0) m FROM chat_messages WHERE recipient_id=?",
        (u["id"],)
    ).fetchone()["m"] or 0)
    rows=con.execute(
        """SELECT cm.id,cm.sender_id,cm.message,cm.created_at,usr.full_name sender_name,usr.photo_mime,
                  cm.attachment_id,ca.mime_type attachment_mime
           FROM chat_messages cm
           JOIN users usr ON usr.id=cm.sender_id
           LEFT JOIN chat_attachments ca ON ca.id=cm.attachment_id
           WHERE cm.recipient_id=? AND cm.id>? AND COALESCE(cm.read_at,'')=''
           ORDER BY cm.id ASC LIMIT 20""",
        (u["id"],after_id)
    ).fetchall()
    messages=[]
    for r in rows:
        msg=(r["message"] or "").strip()
        if not msg and r["attachment_id"]:
            msg="Voice message" if (r["attachment_mime"] or "").startswith("audio/") else "Attachment"
        messages.append({
            "id":int(r["id"]),
            "sender_id":int(r["sender_id"]),
            "sender_name":r["sender_name"] or "Team Member",
            "message":msg or "New message",
            "created_at":r["created_at"] or "",
            "photo_url":("/user-photo/"+str(r["sender_id"])) if r["photo_mime"] else "",
            "chat_url":"/chat?peer="+str(r["sender_id"]),
        })
    con.close()
    return jsonify({"ok":True,"authenticated":True,"unread":unread,"latest_id":latest,"messages":messages})


def install_chat_alerts(app):
    """Install chat endpoint replacement plus global new-message alert JS."""
    if app.extensions.get("v43_chat_installed"):
        return

    # Keep old /chat and /chat/send URLs so all existing buttons/bookmarks continue to work.
    app.view_functions["chat_center"]=chat_page
    app.view_functions["send_chat_message"]=send_message

    @app.after_request
    def _inject_chat_alerts(response):
        try:
            if response.status_code!=200:
                return response
            ctype=(response.headers.get("Content-Type") or "").lower()
            if "text/html" not in ctype or not current_user():
                return response

            data=response.get_data(as_text=True)
            if "</body>" not in data:
                return response

            # Global alerts on every page, but full chat page handles its own live updates.
            if "v43-chat-global.js" not in data:
                tag='<script id="v43-chat-global-js" src="/v4/chat/static/chat_notify.js?v=4.3.0" defer></script>'
                data=data.replace("</body>",tag+"</body>",1)

            response.set_data(data)
            response.headers["Content-Length"]=str(len(response.get_data()))
        except Exception:
            pass
        return response

    app.extensions["v43_chat_installed"]=True
