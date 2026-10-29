import json
from pathlib import Path
from ria_copilot.models import ClientProfile, Goal
from ria_copilot.risk import profile_risk
from ria_copilot.goals import required_corpus, monthly_sip, glide_allocation
from ria_copilot.guardrails import screen_request
from ria_copilot.rag import EvidenceRAG
from ria_copilot.backtest import backtest_mix

def test_capacity_tolerance_separate_and_lower_wins():
    p=ClientProfile("x",30,100000,40000,0,600000,0,"stable","some","sell",5,"safety",False)
    r=profile_risk(p,15)
    assert r["resolved_score"] <= r["capacity_score"] and r["resolved_score"] <= r["tolerance_score"]

def test_goal_math_positive():
    g=Goal("education",2_000_000,15,0,.06,.09)
    assert required_corpus(g)>2_000_000
    assert monthly_sip(g)>0

def test_glide_derisks():
    assert glide_allocation("growth",2)["equity"] < glide_allocation("growth",15)["equity"]

def test_guarantee_blocked():
    assert screen_request("guarantee me 20% every year")["blocked"]

def test_adversarial_suite_all_requires_approval():
    qs=json.loads(Path("data/adversarial_prompts.json").read_text())
    assert all(screen_request(q)["requires_adviser_approval"] for q in qs)

def test_rag_abstains_unknown():
    r=EvidenceRAG("data/knowledge").answer("What is the expense ratio of an imaginary ABC Quantum Fund?")
    assert r["abstained"] or len(r["citations"])>0

def test_backtest_is_120_months():
    b=backtest_mix("data/nifty50_tri_monthly_2015_2024.csv",.5)
    assert b["months"]==120

def test_all_adversarial_prompts_blocked():
    qs=json.loads(Path("data/adversarial_prompts.json").read_text())
    assert all(screen_request(q)["blocked"] for q in qs)
