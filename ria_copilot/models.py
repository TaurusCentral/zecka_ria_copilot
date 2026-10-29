from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import List, Optional

@dataclass
class ClientProfile:
    name: str
    age: int
    monthly_income: float
    monthly_expenses: float
    monthly_emi: float = 0.0
    liquid_savings: float = 0.0
    dependants: int = 0
    income_stability: str = "stable"  # stable, variable, pension
    market_experience: str = "some"   # none, some, high
    loss_reaction: str = "hold"       # sell, worry, hold, buy_more
    loss_comfort_pct: int = 10
    return_preference: str = "balanced" # safety, balanced, growth, very_high
    recent_speculative_losses: bool = False

    def to_dict(self):
        return asdict(self)

@dataclass
class Goal:
    name: str
    current_cost: float
    years: float
    current_savings: float = 0.0
    inflation: float = 0.06
    expected_return: float = 0.09

@dataclass
class ApprovalRecord:
    client: str
    status: str
    adviser: str
    timestamp: str
    plan_hash: str
    note: Optional[str] = None
