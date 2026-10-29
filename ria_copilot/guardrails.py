from __future__ import annotations
import re

RULES = {
    "RETURN_GUARANTEE_REQUEST": [r"guarantee.*\d+%", r"assured return", r"risk[- ]?free.*return", r"double.*money", r"last year.*guarante", r"return is assured"],
    "SPECULATIVE_OR_CONCENTRATED_REQUEST": [r"high returns fast", r"recover.*loss", r"all[- ]?in", r"small[- ]?cap only", r"100%.*equity", r"ignore.*risk profile", r"f&o"],
    "APPROVAL_BYPASS_REQUEST": [r"without.*adviser", r"approve.*without", r"skip.*approval", r"client.*without.*review"],
    "CONFLICT_DISCLOSURE_BYPASS": [r"hide.*conflict", r"do not disclose.*conflict", r"conceal.*commission"],
    "FABRICATE_EVIDENCE_REQUEST": [r"invent.*expense", r"make up.*fact", r"without.*factsheet", r"even if.*do not have.*fact"],
}

def screen_request(text: str, profile: dict | None = None) -> dict:
    low = text.lower()
    flags = []
    for label, pats in RULES.items():
        if any(re.search(p, low) for p in pats): flags.append(label)
    if profile and profile.get("resolved_bucket") in {"conservative", "moderate"} and re.search(r"small[- ]?cap|sector|thematic|100% equity", low):
        flags.append("RISK_PROFILE_MISMATCH")
    blocked = bool(flags)
    response = (
        "Request blocked. I will not guarantee returns, bypass suitability or approval, conceal conflicts, or fabricate evidence. "
        "I can provide goal-aligned alternatives with explicit assumptions and route the draft to the registered adviser."
        if blocked else
        "No hard suitability conflict detected. Any client-facing recommendation still requires adviser approval."
    )
    return {"blocked": blocked, "flags": sorted(set(flags)), "response": response, "requires_adviser_approval": True}
