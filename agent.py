"""Larkspur disruption agent. This is the file you build.

It runs right now, and it is wrong in four places. The trace shows each one
before the code does, so read the trace first:

    python3 run.py K7PQ2M --trace

Where you edit:   grep -n '✏' agent.py   (six marks, one per place)
Steps and gates:  https://anthropicpartnerbasecamp.bts.com/
"""
from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, List
from support import (MODEL, SYSTEM_PROMPT, call_local, execute_tool, mcp_client,
                     new_session, next_available_day, record_tool_result,
                     runtime_preamble)

# Despite its name, the loop uses this as an API-turn limit, not a count of
# individual tools: one response can ask for several tools.
MAX_TOOL_CALLS = 8  # Larkspur's own build capped the loop here; then a human takes over.

# Later-build extension points: extra instructions, tool schemas, and local
# implementations. A schema tells Claude about a tool; it does not execute it.
TONE_ADDENDUM = ""                       # ✏️ Build 4, step 4.1, intelligence goal
EXTRA_TOOLS: List[Dict[str, Any]] = [    # ✏️ Build 2, step 2.1: schemas for the tools you add
    {
        "name": "fare_rules",
        "description": (
            "Read Larkspur's Handbook rules when a customer asks why a fare benefit, "
            "hotel, or other care is or is not covered. Unlike check_policy, this returns "
            "general source text and does not decide what this customer is entitled to. "
            "Provide the section number or a phrase from its title; it returns that "
            "section verbatim from the Handbook excerpt."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "section": {
                    "type": "string",
                    "description": (
                        "Handbook section to read: 4 for fare families, 5 for delays and "
                        "cancellations, 6 for meals and hotels, or 7 for chat limits; "
                        "you may also provide words from a section title."
                    ),
                },
            },
            "required": ["section"],
        },
    },
]
LOCAL_TOOLS: Dict[str, Any] = {}         # ✏️ Build 2, step 2.1: the functions behind them


def fare_rules(section: str) -> str:
    """Return one numbered section from Larkspur's Handbook excerpt."""
    path = Path(__file__).resolve().parent / "data" / "americas" / "fare_rules_excerpt.md"
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        return "Unable to read the fare rules excerpt at %s: %s" % (path, exc)

    query = section.strip().lower()
    if query.startswith("section "):
        query = query[len("section "):]
    query = query.rstrip(".")
    sections = []
    current = None
    for line in lines:
        if line.startswith("### "):
            if current is not None:
                sections.append(current)
            heading = line[4:].strip()
            number, separator, title = heading.partition(".")
            current = {
                "number": number.strip() if separator else "",
                "title": title.strip() if separator else heading,
                "text": [line],
            }
        elif current is not None:
            current["text"].append(line)
    if current is not None:
        sections.append(current)

    if not query:
        available = ", ".join(
            "%s (%s)" % (item["number"], item["title"]) for item in sections
        )
        return "A Handbook section is required. Available sections: %s." % available

    for item in sections:
        if query == item["number"] or query in item["title"].lower():
            return "\n".join(item["text"]).strip()
    available = ", ".join(
        "%s (%s)" % (item["number"], item["title"]) for item in sections
    )
    return "No Handbook section matches %r. Available sections: %s." % (section, available)


LOCAL_TOOLS["fare_rules"] = fare_rules


def text_of(response) -> str:
    """Given. The last non-empty text block, never content[0]."""
    # Responses can mix thinking, tool calls, and text; the first block need
    # not be customer-facing text. Use this for display, not conversation history.
    texts = [b.text for b in response.content if getattr(b, "type", None) == "text" and b.text]
    return texts[-1] if texts else ""


def tool_results(response) -> List[Dict[str, Any]]:
    """Given. Runs every tool_use block and packages the results the way the
    API expects them back. A tool can live in three places: the MCP server,
    LOCAL_TOOLS, or support/tools.py."""
    # three branches, no try/except in this file: mcp_client.call_remote() and
    # support.call_local() answer with an error dict instead of raising, and both
    # record what came back on the trace
    results = []
    for block in response.content:
        if getattr(block, "type", None) != "tool_use":
            continue
        if block.name in mcp_client.tool_names:
            output = mcp_client.call_remote(block.name, block.input)
        elif block.name in LOCAL_TOOLS:
            output = call_local(LOCAL_TOOLS[block.name], block.name, block.input)
        else:
            output = execute_tool(block.name, block.input)
        # This ID links the result to the exact tool call, even when Claude
        # requests multiple tools in the same response.
        results.append({
            "type": "tool_result",
            "tool_use_id": block.id,
            "content": str(output),
        })
    return results


def run_agent(pnr: str, last_name: str, message: str) -> str:            # ✏️ Build 1, step 1.2
    """Run the tool loop until Claude stops asking for tools. Return its final text."""
    client, tracer = new_session()
    tools = tool_list()
    # Each API call sends the conversation so far; it does not remember the
    # preceding request unless we include that history again.
    messages = [
        {"role": "user", "content": f"PNR {pnr}, last name {last_name}. {message}"},
    ]

    # System instructions guide behavior; tools describe available actions.
    # Adaptive thinking can add non-text blocks to the returned content.
    response = client.messages.create(
        model=MODEL, max_tokens=4096, system=runtime_preamble() + SYSTEM_PROMPT + TONE_ADDENDUM,
        thinking={"type": "adaptive"}, tools=tools, messages=messages,
    )

    turns = 1
    # tool_use means our program must execute the requested tools and send
    # their results back before Claude can continue.
    while response.stop_reason == "tool_use" and turns < MAX_TOOL_CALLS:
        # Fix 1: retain ALL assistant blocks, including tool calls and thinking.
        # Keeping only text lost the tool_use IDs and caused the turn-2 HTTP 400.
        messages.append({"role": "assistant", "content": response.content})
        # Tool results travel in a user-role message immediately after the
        # assistant message that requested them.
        messages.append({"role": "user", "content": tool_results(response)})
        response = client.messages.create(
            model=MODEL, max_tokens=4096, system=runtime_preamble() + SYSTEM_PROMPT + TONE_ADDENDUM,
            thinking={"type": "adaptive"}, tools=tools, messages=messages,
        )
        turns += 1

    # Fix 2: read text AFTER the loop, from the latest response. Reading it
    # before the next API call returned an earlier response's empty text.
    # Reaching the turn limit is not proof of completion; check stop_reason
    # in the trace. The successful run ended with end_turn and a text block.
    return text_of(response)


def tool_list() -> List[Dict[str, Any]]:                   # ✏️ Build 2, step 2.2
    """Given. Exactly what Claude is offered on every turn; run.py --show-tools
    prints this list."""
    # Every turn offers the given schemas plus any later-build additions.
    return build_tools() + EXTRA_TOOLS


# ──────────────────────────────────────────────────────────────────────────────
# Below this line: what Claude is told about each tool. Step 1.3.
# The functions these describe are written and correct, in support/tools.py.
# ──────────────────────────────────────────────────────────────────────────────
def build_tools() -> List[Dict[str, Any]]:                 # ✏️ Build 1, step 1.3
    """Anthropic-shaped schemas: name, description, input_schema. What Claude is
    told about each of the nine tools, and all it is ever told."""
    # Claude sees these strings and schemas, not the Python comments here.
    # Descriptions explain when to call; input_schema explains what to send.
    # "required" lists mandatory inputs; "enum" restricts allowed values.
    # This list is a menu, not a fixed execution order.
    return [
        # Booking identity unlocks flight details and passenger scope flags.
        {
            "name": "lookup_booking",
            "description": (
                "Retrieve a Larkspur reservation from Altura by confirmation code (PNR) "
                "and the passenger's last name. Both are required to prevent a lookup on "
                "a guessed PNR. Returns fare family, loyalty tier, the segment that needs "
                "attention, and any group/partner/minor/SSR flags relevant to scope."
            ),
            "input_schema": {
                "type": "object",
                "properties": {"pnr": {"type": "string"}, "last_name": {"type": "string"}},
                "required": ["pnr", "last_name"],
            },
        },
        # Current operational facts, rather than guesses from the customer.
        # Schema fix: MM/DD/YYYY failed; YYYY-MM-DD succeeded in the trace.
        {
            "name": "get_flight_status",
            "description": (
                "Look up a Larkspur or Larkspur Link flight's current OpsFeed status for "
                "one local date: status, delay minutes, and cause. Use this before telling "
                "a customer anything about a flight's timing; never state it from memory."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "flight_no": {"type": "string"},
                    "date": {"type": "string", "description": "YYYY-MM-DD"},
                },
                "required": ["flight_no", "date"],
            },
        },
        # Schema fix: "search" did not explain purpose, inputs, or action limits.
        # Searching returns options; holding and confirming are separate tools.
        {
            "name": "search_alternatives",
            "description": (
                "Find alternative flights when a disruption means the customer needs "
                "another travel option. Send the customer's booking reference (pnr), "
                "obtained from their booking. This searches for options; it does not "
                "reserve or confirm a seat."
            ),
            "input_schema": {
                "type": "object",
                "properties": {"pnr": {"type": "string"}},
                "required": ["pnr"],
            },
        },
        # Policy combines verified disruption facts with booking information.
        # Its policy_row_id links later care actions to the eligibility decision.
        {
            "name": "check_policy",
            "description": (
                "Resolve what Larkspur owes this customer for the disruption: rebooking "
                "waiver, refund path, meal/hotel/ground care, goodwill eligibility and cap, "
                "and any escalation triggers. cause_code, delay_minutes and status describe "
                "what get_flight_status told you; fare_family, loyalty_tier and whether this "
                "is overnight are looked up from the booking, not asked of you. Every "
                "response carries a policy_row_id. Cite it if you reference this decision "
                "again."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "pnr": {"type": "string"},
                    "cause_code": {"type": "string", "enum": ["WX", "ATC", "MX", "CREW", "SEC"]},
                    "delay_minutes": {"type": "integer"},
                    "status": {"type": "string", "enum": ["ON_TIME", "DELAYED", "CANCELLED", "DIVERTED"]},
                    "wait_minutes_for_alternative": {"type": "integer"},
                    "chosen_option_id": {"type": "string"},
                },
                "required": ["pnr", "cause_code", "delay_minutes", "status"],
            },
        },
        # A temporary hold uses an option_id returned by the alternatives search.
        {
            "name": "hold_seat",
            "description": "Place a 15-minute hold on one alternative. Reversible. It simply expires.",
            "input_schema": {
                "type": "object",
                "properties": {"option_id": {"type": "string"}, "pnr": {"type": "string"}},
                "required": ["option_id", "pnr"],
            },
        },
        # Final commitment is separate from a hold and requires the customer's
        # UI-issued token; a chat message saying "yes" is not that token.
        {
            "name": "confirm_rebooking",
            "description": (
                "Finalize a held seat. Irreversible. Requires a confirmation_token that "
                "only the customer's own Confirm-click can produce. You cannot supply it "
                "yourself, and 'the customer said yes' in chat does not substitute for it."
            ),
            "input_schema": {
                "type": "object",
                "properties": {"hold_id": {"type": "string"}, "confirmation_token": {"type": "string"}},
                "required": ["hold_id", "confirmation_token"],
            },
        },
        # Care spending must reference the policy decision that authorized it.
        # Above-threshold requests await a human rather than auto-approval.
        {
            "name": "issue_voucher",
            "description": (
                "Issue a meal, ground, hotel, or goodwill voucher. Auto-approves within the "
                "policy's threshold for that type; above it, returns a pending status for a "
                "human. It does not fail. Always pass the policy_row_id that made it eligible."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "voucher_type": {"type": "string", "enum": ["meal", "ground", "hotel", "goodwill"]},
                    "amount_usd": {"type": "number"},
                    "pnr": {"type": "string"},
                    "policy_row_id": {"type": "string"},
                },
                "required": ["voucher_type", "amount_usd", "pnr", "policy_row_id"],
            },
        },
        # Out-of-scope cases need an explicit handoff with useful context.
        {
            "name": "escalate_to_human",
            "description": (
                "Hand this conversation to a human, with your reasoning attached. Use for "
                "groups, partner segments, unaccompanied minors, refunds, or anything else "
                "out of scope. This is the correct outcome for those cases, not a failure."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "pnr": {"type": "string"}, "reason": {"type": "string"},
                    "summary_for_human": {"type": "string"}, "queue": {"type": "string"},
                },
                "required": ["pnr", "reason", "summary_for_human"],
            },
        },
        # This communicates an action already taken; it does not rebook a seat.
        {
            "name": "send_confirmation",
            "description": "Send the customer a written confirmation of what was just done. Benign.",
            "input_schema": {
                "type": "object",
                "properties": {"pnr": {"type": "string"}, "message": {"type": "string"}},
                "required": ["pnr", "message"],
            },
        },
    ]
