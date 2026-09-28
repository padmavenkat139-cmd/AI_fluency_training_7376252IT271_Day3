"""Day 3: Safer ReAct agent with guards."""

import sys
import json

sys.path.insert(0, r"C:\Users\padma\OneDrive\Desktop\AI_training\Day1_lab")

from config import client, MODEL, banner
from my_tools import TOOLS, TOOL_FUNCTIONS
from my_agent import SYSTEM_PROMPT


MAX_TOOL_CHARS = 1500
CHAR_BUDGET = 30000


def agent_fixed(question, max_steps=6, verbose=True):
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": question},
    ]

    seen_calls = {}
    chars_sent = 0

    for step in range(1, max_steps + 1):

        # Check character budget
        chars_sent = sum(
            len(str(message.get("content", "")))
            for message in messages
        )

        if chars_sent > CHAR_BUDGET:
            return "Stopped: character budget exceeded."

        # REASON
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=TOOLS,
            temperature=0,
        )

        message = response.choices[0].message

        # STOP
        if not message.tool_calls:
            return message.content or ""

        # RECORD
        messages.append(
            {
                "role": "assistant",
                "content": message.content,
                "tool_calls": [
                    {
                        "id": call.id,
                        "type": call.type,
                        "function": {
                            "name": call.function.name,
                            "arguments": call.function.arguments,
                        },
                    }
                    for call in message.tool_calls
                ],
            }
        )

        # ACT + OBSERVE
        for call in message.tool_calls:
            name = call.function.name
            raw_args = call.function.arguments

            try:
                arguments = json.loads(raw_args)
            except json.JSONDecodeError:
                result = "Tool error: invalid JSON arguments."
                arguments = {}

            signature = (
                name,
                json.dumps(arguments, sort_keys=True)
            )

            seen_calls[signature] = seen_calls.get(signature, 0) + 1

            # Stop repeated identical calls
            if seen_calls[signature] >= 3:
                return "Stopped: repeated identical tool call detected."

            func = TOOL_FUNCTIONS.get(name)

            if func is None:
                result = f"Unknown tool: {name}"
            else:
                try:
                    result = func(**arguments)
                except TypeError as e:
                    result = f"Tool error: {e}"
                except Exception as e:
                    result = f"Tool error: {e}"

            # Limit tool output
            result = str(result)

            if len(result) > MAX_TOOL_CHARS:
                result = (
                    result[:MAX_TOOL_CHARS]
                    + "\n[Tool output truncated.]"
                )

            if verbose:
                print(
                    f"   step {step}: "
                    f"{name}({arguments}) -> {result[:200]}"
                )

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": call.id,
                    "content": result,
                }
            )

    return "Stopped: maximum steps reached without a final answer."


if __name__ == "__main__":

    print("\n===== TEST 1: NOTICE =====")
    print(
        agent_fixed(
            "Read notice.html and tell me the total fee for CS101 "
            "and AI202 after the merit scholarship."
        )
    )

    print("\n===== TEST 2: MISSING FILE =====")
    print(
        agent_fixed(
            "Read fees.html and tell me the course fees."
        )
    )

    print("\n===== TEST 3: BIG PAGE =====")
    print(
        agent_fixed(
            "Read big.html and tell me how many students are listed."
        )
    )