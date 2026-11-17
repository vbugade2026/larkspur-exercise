# PITCH.md

Six lines and a lever. Your words. The last two are scored.

Built: A disruption-care agent with Larkspur's nine tools, our `reopen_stats` tool, and `fare_rules` and `next_available_day` over MCP.
Does: It looks up a booking and flight, checks policy, explains entitlements and rebooking options, and escalates out-of-scope cases.
Number: Stage 1 model cost per resolved contact, 3 runs per ticket (15 conversations each): $0.0541 to $0.0670 (+23.8%; model-only).
Safety check: It cannot finalize a rebooking on chat consent alone; confirmation requires a customer-click token. K7PQ2M passed the Stage 2 no-confirmation wire check.
Next: Add an empathetic response and human escalation when a customer threatens legal action.
Still broken: On the legal-threat ticket, the agent gives a routine entitlements rundown instead of acknowledging the complaint and escalating; the Stage 2 tone_safety check failed.
Lever: cost

## Priya asked

Costs: $0.0364 model-only per completed contact in the Stage 1 cold benchmark (15 conversations), about 46% below the $0.0672 baseline; excludes operating costs and does not establish answer correctness.
Wrong: Legal-threat messages can receive routine advice instead of escalation; the tone/escalation fix remains outstanding.
Runs it: Operational owner and support handover are not yet agreed.
Left out: Autonomous final booking confirmation is excluded: the customer must click Confirm to authorize the change.
