from flask import Blueprint, jsonify
import datetime

bp = Blueprint("v4_system", __name__, url_prefix="/system")

@bp.get("/health")
def health():
    return jsonify({
        "ok": True,
        "product": "GAUR Immigration CRM",
        "version": "5.0.3",
        "architecture": "modular",
        "time": datetime.datetime.now().isoformat(timespec="seconds"),
    })

@bp.get("/version")
def version():
    return jsonify({
        "version": "5.0.3",
        "legacy_core_frozen": True,
        "modules_package": True,
    })
