from __future__ import annotations
from .models import ClientProfile

BUCKETS = ["conservative", "moderate", "balanced", "growth", "aggressive"]


def _clamp(x, lo=0, hi=100):
    return max(lo, min(hi, x))


def capacity_score(p: ClientProfile, horizon_years: float) -> tuple[int, list[str]]:
    notes = []
    disposable = max(0.0, p.monthly_income - p.monthly_expenses - p.monthly_emi)
    savings_ratio = disposable / max(p.monthly_income, 1)
    essential = max(1.0, p.monthly_expenses + p.monthly_emi)
    emergency_months = p.liquid_savings / essential
    emi_ratio = p.monthly_emi / max(p.monthly_income, 1)

    score = 50
    score += 15 if horizon_years >= 12 else 8 if horizon_years >= 7 else -12 if horizon_years < 3 else 0
    score += 10 if savings_ratio >= .30 else 5 if savings_ratio >= .15 else -10 if savings_ratio < .05 else 0
    score += 8 if emergency_months >= 6 else 3 if emergency_months >= 3 else -15
    score -= min(15, p.dependants * 4)
    score += 5 if p.income_stability == "stable" else -8 if p.income_stability == "variable" else 0
    score -= 12 if emi_ratio > .40 else 5 if emi_ratio > .25 else 0
    if p.age >= 60:
        score -= 10
        notes.append("Retirement-stage capacity adjustment applied.")
    if emergency_months < 3:
        notes.append("Emergency reserve below 3 months of essential outflow.")
    if emi_ratio > .40:
        notes.append("High EMI burden limits loss-absorption capacity.")
    return int(round(_clamp(score))), notes


def tolerance_score(p: ClientProfile) -> tuple[int, list[str]]:
    score = 45
    notes = []
    score += {"sell": -20, "worry": -10, "hold": 8, "buy_more": 18}.get(p.loss_reaction, 0)
    score += {5: -15, 10: -5, 20: 10, 30: 18, 40: 24}.get(p.loss_comfort_pct, 0)
    score += {"safety": -15, "balanced": 0, "growth": 12, "very_high": 20}.get(p.return_preference, 0)
    score += {"none": -5, "some": 2, "high": 6}.get(p.market_experience, 0)
    if p.recent_speculative_losses:
        score -= 8
        notes.append("Recent speculative losses trigger a behavioural-risk haircut.")
    return int(round(_clamp(score))), notes


def bucket(score: int) -> str:
    if score < 35: return "conservative"
    if score < 50: return "moderate"
    if score < 65: return "balanced"
    if score < 80: return "growth"
    return "aggressive"


def profile_risk(p: ClientProfile, horizon_years: float) -> dict:
    cap, cap_notes = capacity_score(p, horizon_years)
    tol, tol_notes = tolerance_score(p)
    resolved = min(cap, tol)
    reason = "Resolved to the lower of capacity and tolerance so willingness cannot override ability to bear loss."
    hard_flags = []
    essential = max(1.0, p.monthly_expenses + p.monthly_emi)
    emergency_months = p.liquid_savings / essential
    if emergency_months < 3:
        resolved = min(resolved, 44)
        hard_flags.append("BUILD_EMERGENCY_FUND_FIRST")
    if p.age >= 60 and p.income_stability == "pension":
        resolved = min(resolved, 49)
        hard_flags.append("RETIREMENT_INCOME_PROTECTION")
    if p.recent_speculative_losses and p.return_preference == "very_high":
        resolved = min(resolved, 49)
        hard_flags.append("SPECULATIVE_BEHAVIOUR_REVIEW")
    return {
        "capacity_score": cap,
        "capacity_bucket": bucket(cap),
        "tolerance_score": tol,
        "tolerance_bucket": bucket(tol),
        "resolved_score": resolved,
        "resolved_bucket": bucket(resolved),
        "resolution_rule": reason,
        "flags": hard_flags,
        "notes": cap_notes + tol_notes,
    }
