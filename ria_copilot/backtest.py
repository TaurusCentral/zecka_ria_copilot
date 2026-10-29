from __future__ import annotations
import pandas as pd
import numpy as np


def max_drawdown(values: pd.Series) -> float:
    peak = values.cummax()
    dd = values / peak - 1
    return float(dd.min())

def backtest_mix(csv_path: str, equity_weight: float, debt_annual: float = 0.07, rebalance_months: int = 12) -> dict:
    df = pd.read_csv(csv_path, parse_dates=["date"])
    er = df["equity_return"].astype(float)
    dr = pd.Series((1 + debt_annual) ** (1/12) - 1, index=df.index)
    w = equity_weight
    port = w * er + (1-w) * dr
    values = (1 + port).cumprod()
    years = len(port) / 12
    cagr = float(values.iloc[-1] ** (1/years) - 1)
    vol = float(port.std(ddof=1) * np.sqrt(12))
    mdd = max_drawdown(values)
    positive_months = float((port > 0).mean())
    return {
        "months": int(len(port)), "years": years, "equity_weight": w,
        "debt_proxy_annual": debt_annual, "cagr": cagr, "annualized_volatility": vol,
        "max_drawdown": mdd, "positive_month_fraction": positive_months,
        "ending_value_on_1": float(values.iloc[-1]),
    }
