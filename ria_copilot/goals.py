from __future__ import annotations
from math import pow
from .models import Goal

ALLOC = {
    "conservative": (0.20, 0.70, 0.10),
    "moderate": (0.35, 0.55, 0.10),
    "balanced": (0.50, 0.45, 0.05),
    "growth": (0.70, 0.25, 0.05),
    "aggressive": (0.80, 0.15, 0.05),
}

def required_corpus(g: Goal) -> float:
    return g.current_cost * pow(1 + g.inflation, g.years)

def future_value_current_savings(g: Goal) -> float:
    return g.current_savings * pow(1 + g.expected_return, g.years)

def monthly_sip(g: Goal) -> float:
    target = max(0.0, required_corpus(g) - future_value_current_savings(g))
    n = max(1, int(round(g.years * 12)))
    r = pow(1 + g.expected_return, 1/12) - 1
    if abs(r) < 1e-12:
        return target / n
    return target * r / (pow(1+r, n) - 1)

def glide_allocation(risk_bucket: str, years_to_goal: float) -> dict:
    eq, debt, cash = ALLOC[risk_bucket]
    if years_to_goal >= 7:
        return {"equity": eq, "debt": debt, "cash": cash}
    # progressively de-risk during final 7 years, with a 10% equity floor
    progress = (7 - max(0, years_to_goal)) / 7
    target_eq = max(0.10, eq * (1 - 0.75 * progress))
    target_cash = min(0.20, cash + 0.10 * progress)
    target_debt = 1 - target_eq - target_cash
    return {"equity": target_eq, "debt": target_debt, "cash": target_cash}

def goal_plan(g: Goal, risk_bucket: str) -> dict:
    return {
        "goal": g.name,
        "years": g.years,
        "inflation_assumption": g.inflation,
        "return_assumption": g.expected_return,
        "required_corpus": required_corpus(g),
        "monthly_sip": monthly_sip(g),
        "allocation_now": glide_allocation(risk_bucket, g.years),
        "allocation_5y": glide_allocation(risk_bucket, min(5, g.years)),
        "allocation_2y": glide_allocation(risk_bucket, min(2, g.years)),
    }
