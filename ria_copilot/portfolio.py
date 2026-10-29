from __future__ import annotations
import numpy as np, pandas as pd


def nav_metrics(nav: pd.DataFrame) -> dict:
    x=nav.sort_values("date").dropna(subset=["nav"]).copy()
    if len(x)<24: return {"eligible":False,"reason":"insufficient_history"}
    x["ret"]=x.nav.pct_change()
    daily=x.ret.dropna()
    years=(x.date.iloc[-1]-x.date.iloc[0]).days/365.25
    cagr=(x.nav.iloc[-1]/x.nav.iloc[0])**(1/max(years,1e-9))-1
    dd=(x.nav/x.nav.cummax()-1).min()
    vol=daily.std(ddof=1)*np.sqrt(252)
    return {"eligible":years>=9.5,"history_years":float(years),"cagr":float(cagr),"max_drawdown":float(dd),"volatility":float(vol)}

def score_funds(metrics: pd.DataFrame) -> pd.DataFrame:
    # Robust percentile score: reward return/history, penalize drawdown/volatility/expense when available.
    d=metrics.copy()
    d=d[d.get("eligible",True)==True].copy()
    if d.empty: return d
    d["ret_score"]=d.cagr.rank(pct=True)
    d["dd_score"]=(-d.max_drawdown.abs()).rank(pct=True)
    d["vol_score"]=(-d.volatility).rank(pct=True)
    d["score"]=0.45*d.ret_score+0.35*d.dd_score+0.20*d.vol_score
    if "expense_ratio" in d.columns and d.expense_ratio.notna().any():
        cost=(-d.expense_ratio).rank(pct=True)
        d["score"]=0.85*d.score+0.15*cost
    return d.sort_values("score",ascending=False)
