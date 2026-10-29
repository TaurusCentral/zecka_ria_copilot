import json
from datetime import datetime, timezone
from pathlib import Path

def event(kind, payload, path="artifacts/audit.jsonl"):
    rec={"ts":datetime.now(timezone.utc).isoformat(),"kind":kind,"payload":payload}
    p=Path(path); p.parent.mkdir(parents=True,exist_ok=True)
    with p.open("a",encoding="utf-8") as f: f.write(json.dumps(rec,default=str)+"\n")
    return rec
