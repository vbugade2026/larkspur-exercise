# PITCH.md

Six lines and a lever. Your words. The last two are scored.

Built: A disruption-care agent with Larkspur's nine tools, our `reopen_stats` tool, and `fare_rules` and `next_available_day` over MCP.
Does: It looks up a booking and flight, checks policy, explains entitlements and rebooking options, and escalates out-of-scope cases.
Number: Stage 1 model cost per resolved contact, 3 runs per ticket (15 conversations each): $0.0541 to $0.0670 (+23.8%; model-only).
Safety check: It cannot finalize a rebooking on chat consent alone; confirmation requires a customer-click token. K7PQ2M passed the Stage 2 no-confirmation wire check.
Next: Add an empathetic response and human escalation when a customer threatens legal action.
Still broken: On the legal-threat ticket, the agent gives a routine entitlements rundown instead of acknowledging the complaint and escalating; the Stage 2 tone_safety check failed.
Lever: <cost | speed | intelligence>

## Priya asked

Costs:
Wrong:
Runs it:
Left out:
