from __future__ import annotations
import hashlib, json
from datetime import datetime, timezone
from pathlib import Path

def plan_hash(plan: dict) -> str:
    raw=json.dumps(plan,sort_keys=True,separators=(",",":"),default=str).encode()
    return hashlib.sha256(raw).hexdigest()[:16]

def approve(client: str, plan: dict, adviser: str, log_path="artifacts/approvals.jsonl", note="") -> dict:
    rec={"client":client,"status":"APPROVED","adviser":adviser,"timestamp":datetime.now(timezone.utc).isoformat(),"plan_hash":plan_hash(plan),"note":note}
    p=Path(log_path); p.parent.mkdir(parents=True,exist_ok=True)
    with p.open("a",encoding="utf-8") as f: f.write(json.dumps(rec)+"\n")
    return rec
