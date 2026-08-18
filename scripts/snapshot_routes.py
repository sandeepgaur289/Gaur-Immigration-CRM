import json
from app import app

rows=[]
for rule in app.url_map.iter_rules():
    rows.append({
        "rule": str(rule),
        "endpoint": rule.endpoint,
        "methods": sorted(m for m in rule.methods if m not in {"HEAD","OPTIONS"}),
    })
rows.sort(key=lambda x:(x["rule"],x["endpoint"]))
with open("route_snapshot.json","w",encoding="utf-8") as f:
    json.dump(rows,f,indent=2)
print("Saved",len(rows),"routes")
