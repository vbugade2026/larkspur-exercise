# Client review: Larkspur disruption-care agent

**To:** Room 5  
**From:** Larkspur client review agent, on behalf of Priya Raghavan  
**Re:** the disruption-care agent you walked us through in our last session  
**Generated:** 2026-11-17 10:19

## Priya's note

> Our vendor says we should just be using your best model.
>
> Why aren't we?
>
> Priya Raghavan, Larkspur Airlines

She sent that before this session opened. She means it. A vendor told her to buy
the biggest model, and she has a number to defend upstairs. Her four questions from
day one are still open. Naming a model answers none of them.

## Still open from day one

| Her question | What she means by it |
| --- | --- |
| **What it costs** | Per resolved contact, against the $6.90 a human contact costs us. |
| **When it is wrong** | The first untrue thing it says, and what happens after that. |
| **Who runs it** | In June, after you have left. |
| **What you left out** | The scope you cut, and why. |

## What the review agent found

Larkspur pointed a review agent at your repository. It read the
code. It did not run your agent, and the only file it changed is this one. Each
item below names the file and the line it is about.

**1. PITCH.md Number: $0.0541 to $0.0670 per resolved contact, +23.8%, while the Lever line is still the placeholder text.**

The Number line reports a cost that rose 23.8% across 15 conversations per run. The Lever line reads "<cost | speed | intelligence>", so the build has no declared goal that the +23.8% serves or violates. Nothing in the diff shows what produced the added cost.

Run python3 bench.py --compare on your before and after labels and paste the output, with the lever you chose written into PITCH.md.

**2. readout-trace.json: 14410 tokens in, 0 cache read, 0 written, and agent.py has no cache_control anywhere.**

The committed wire run made 4 API turns with 4 tool calls, and every turn resends the system prompt plus ten tool schemas plus any MCP tools from tool_list(). The scan finds no cache_control in agent.py and the trace shows a hit ratio of None. A bigger model would pay the same resend on every turn.

Run python3 run.py --tool-tax and paste its output next to the readout-trace.json token line.

**3. agent.py hold_seat and send_confirmation descriptions are 73 and 71 characters, the two thinnest of the ten schemas.**

hold_seat reads "Place a 15-minute hold on one alternative. Reversible. It simply expires." and says nothing about where option_id comes from. You rewrote search_alternatives from "search" into a full description and left these two untouched. The committed trace calls lookup_booking, get_flight_status, check_policy and fare_rules, and never reaches either tool.

Run python3 run.py --all --trace and paste the totals footer showing which tools fired on the rebooking tickets.

**4. PITCH.md Still broken: the legal-threat ticket gets a routine entitlements rundown and the Stage 2 tone_safety check failed.**

TONE_ADDENDUM is 0 characters, and the escalate_to_human description lists groups, partner segments, unaccompanied minors and refunds as triggers. A legal threat appears nowhere in that list. No part of the build gives the agent a rule to hand a legal-threat chat to a human, so the failure sits in the prompt and the tool text where no model choice reaches it.

Run python3 verify.py 2.2 and paste the failing tone_safety output.

**5. No evals/cases.json exists, and readout.html banks gates 1.2 to 2.2 only, with 3.1 and 4.1 absent.**

The $0.0541 to $0.0670 comparison and the K7PQ2M no-confirmation pass each rest on the shipped tickets. Nothing in the repository records what a correct answer looks like for a case you chose, so the numbers cannot yet show that quality held while cost rose 23.8%. The verifier files and eval_harness.py also differ from the shipped pack.

Run python3 eval_harness.py and paste the pass and fail summary, with the cases file path it read.

## Your four answers

The four lines under `## Priya asked` in your PITCH.md are still empty. They
are one line each and they are not a coding job: cost, what happens when it is
wrong, who runs it in June, and what you left out. Whoever on your side is not
editing agent.py is the right person to write them, and they are the four
things I will ask about first.

## Before our next meeting

> Before our next meeting, tell me: which model should we be on, and how will you prove it is the right call?
>
> Priya Raghavan, Larkspur Airlines

Bring two things. A recommendation, and the measurement behind it. If the model is
not the problem, say so, and bring the number that shows it.

## What this review read

- `agent.py (373 lines)`
- `PITCH.md`
- `TEAM.md`
- `readout-trace.json`
- `readout.html (evidence block)`
- given files that differ from the shipped pack: `verify.py`, `eval_harness.py`, `bench.py`, `readout.py`, `setup.py`, `pod_sync.py`, `run.py`, `review.py`, `support/__init__.py`, `support/client.py`, `support/data.py`, `support/models.py`, `support/tools.py`, `support/trace.py`, `support/offline.py`, `support/mock_backend.py`, `support/mcp_client.py`, `support/mcp_server.py`, `support/mcp_selftest.py`, `support/access.py`, `support/keyscan.py`, `support/review.py`

Reviewer: `claude-sonnet-5-5`. Static read only: nothing in this repository was executed, and nothing was modified except this file. Larkspur Airlines is a fictional training scenario. Confidential, do not distribute.
