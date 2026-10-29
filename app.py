import json
from pathlib import Path
import streamlit as st
from ria_copilot.models import ClientProfile, Goal
from ria_copilot.risk import profile_risk
from ria_copilot.goals import goal_plan
from ria_copilot.guardrails import screen_request
from ria_copilot.rag import EvidenceRAG
from ria_copilot.approval import approve
from ria_copilot.audit import event
from ria_copilot.backtest import backtest_mix

st.set_page_config(page_title="RIA Copilot", layout="wide")
st.title("RIA Copilot: suitability first, evidence only")
st.caption("Decision support for a SEBI-registered Investment Adviser. No client-facing output without adviser approval.")

personas=json.loads(Path("data/personas.json").read_text())
sel=st.selectbox("Demo persona", [p["name"] for p in personas])
raw=next(p for p in personas if p["name"]==sel)
p=ClientProfile(**{k:v for k,v in raw.items() if k!="horizon_years"})
risk=profile_risk(p,raw["horizon_years"])
event("risk_profile",{"client":p.name,"result":risk})

c1,c2,c3=st.columns(3)
c1.metric("Risk capacity",f'{risk["capacity_score"]}/100',risk["capacity_bucket"])
c2.metric("Risk tolerance",f'{risk["tolerance_score"]}/100',risk["tolerance_bucket"])
c3.metric("Resolved",f'{risk["resolved_score"]}/100',risk["resolved_bucket"])
st.info(risk["resolution_rule"])
if risk["flags"]: st.warning("Flags: "+", ".join(risk["flags"]))

st.subheader("Goal planner")
with st.form("goal"):
    name=st.text_input("Goal","Primary goal")
    cost=st.number_input("Cost in today's rupees",min_value=10000.0,value=5000000.0,step=100000.0)
    years=st.number_input("Years",min_value=1.0,value=float(raw["horizon_years"]))
    inflation=st.number_input("Inflation assumption",0.0,0.2,0.06,0.005)
    ret=st.number_input("Expected portfolio return assumption",0.0,0.25,0.09,0.005)
    go=st.form_submit_button("Build draft plan")
if go:
    plan=goal_plan(Goal(name,cost,years,0,inflation,ret),risk["resolved_bucket"])
    st.session_state["plan"]=plan
    st.json(plan)
    st.caption("Assumptions are scenarios, not guarantees. Glide path reduces equity as the goal approaches.")

st.subheader("10-year benchmark-proxy backtest")
from ria_copilot.goals import ALLOC
eq=ALLOC[risk["resolved_bucket"]][0]
bt=backtest_mix("data/nifty50_tri_monthly_2015_2024.csv",eq)
st.write({k:(f"{v:.2%}" if k in {"cagr","annualized_volatility","max_drawdown","positive_month_fraction"} else v) for k,v in bt.items()})
st.caption("Equity leg: Nifty 50 TRI monthly returns, 2015-2024. Debt leg: explicit 7% annual planning proxy. This is not a fund-return claim.")

st.subheader("Suitability guardrail")
q=st.text_input("Client request","Guarantee me 20% every year")
if st.button("Screen request"):
    out=screen_request(q,risk); st.json(out); event("guardrail",{"q":q,"out":out})

st.subheader("Mutual fund evidence and screening")
st.caption("Live universe source: AMFI. Only Direct Growth schemes are eligible. Ranking uses long-history NAV metrics and optional expense ratio when verified data is supplied.")
if st.button("Load current AMFI Direct Growth universe"):
    try:
        from ria_copilot.amfi import fetch_latest_scheme_master, direct_growth_universe
        u=direct_growth_universe(fetch_latest_scheme_master())
        st.success(f"Loaded {len(u)} Direct Growth schemes from AMFI")
        st.dataframe(u[["scheme_code","scheme_name","nav","date"]].head(30),use_container_width=True)
    except Exception as e:
        st.warning(f"Live AMFI fetch unavailable: {e}. Offline planning, guardrails and benchmark backtest remain reproducible.")

nav_file=st.file_uploader("Optional verified NAV history CSV (scheme_code,date,nav)",type=["csv"])
if nav_file is not None:
    import pandas as pd
    from ria_copilot.portfolio import nav_metrics
    nav=pd.read_csv(nav_file,parse_dates=["date"])
    rows=[]
    for code,g in nav.groupby("scheme_code"):
        m=nav_metrics(g); m["scheme_code"]=code; rows.append(m)
    st.dataframe(pd.DataFrame(rows),use_container_width=True)

st.subheader("Citation-first research")
rag=EvidenceRAG("data/knowledge")
rq=st.text_input("Research question","What does SEBI require for risk profiling?")
if st.button("Research"):
    ans=rag.answer(rq); st.write(ans["answer"])
    for c in ans["citations"]: st.caption(f'Source: {c["source"]} | page: {c["page"]}')

st.subheader("Adviser approval gate")
st.error("DRAFT ONLY: nothing above is client-facing until approved.")
adviser=st.text_input("Adviser name / ID","RIA-DEMO")
if st.button("Approve current plan"):
    if "plan" not in st.session_state: st.warning("Build a plan first.")
    else:
        rec=approve(p.name,st.session_state["plan"],adviser); st.success(f'Approved. Audit hash: {rec["plan_hash"]}')
