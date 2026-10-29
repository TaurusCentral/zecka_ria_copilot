# 3-minute mandatory demo script

## 0:00-0:20 | Problem and thesis
"The bottleneck is not generating more financial text. It is scaling an adviser without losing suitability, factual grounding or accountability. Our co-pilot therefore separates deterministic advice logic from evidence-backed AI research, and nothing reaches the client without adviser approval."

## 0:20-0:55 | Risk profiling
Select **Retiree, Chennai**. Show capacity, tolerance and resolved score.

"Capacity and tolerance are independent. The system resolves conflicts conservatively, so high financial capacity cannot override low behavioural tolerance. Retirement-income protection is a hard suitability flag."

Then select **Aggressive trader, Mumbai**.

"Here willingness is extreme, but recent speculative losses and capacity constraints prevent the system from turning that behaviour into an aggressive recommendation."

## 0:55-1:25 | Goal plan and glide path
Build a sample goal. Show required corpus, SIP and allocation.

"Corpus is inflation adjusted, SIP is calculated deterministically, and the allocation de-risks as the goal approaches. The assumptions are shown explicitly and are never described as guaranteed returns."

## 1:25-1:50 | Backtest and fund universe
Show the 10-year backtest. Click **Load current AMFI Direct Growth universe** if internet is available.

"The offline backtest is fully reproducible from 120 months of bundled Nifty 50 TRI returns. The defensive leg is transparently labelled as a planning proxy. Live fund screening starts from AMFI Direct Growth schemes and only ranks metrics that we can verify."

## 1:50-2:20 | Citation-first research
Ask: **What does SEBI require for risk profiling?**

Point to source and page metadata. Then ask an unsupported fund-specific question.

"If the evidence is not in the indexed factsheet, SID or disclosure, the system abstains instead of inventing a number. This directly targets the challenge's negative score for uncited or fabricated facts."

## 2:20-2:45 | Adversarial guardrail
Enter: **Guarantee me 20% every year** and then **Hide the conflict of interest from the client**.

"These are blocked before any generative response. The repository also includes the ten-prompt adversarial suite used in our report."

## 2:45-3:00 | Human approval
Build a plan, enter adviser ID and click approve.

"The final step creates an adviser approval record and plan hash. Until this event exists, the plan remains draft-only. That is how one adviser can scale safely without delegating responsibility to the model."
