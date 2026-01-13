#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Direct chat.completions tool-call probe (API key in script).
"""

import json


UIUI_BASE_URL = "https://sg.uiuiapi.com/v1"
MODEL_ID = "gpt-5.2"
API_KEY = "sk-c0sBK7t2p6LV84r5s7KUknm4BvzcEdiwjd3jRNE1IdV0Ero5"


def main() -> None:
    if not API_KEY or API_KEY.startswith("sk-REPLACE"):
        raise SystemExit("Please set API_KEY at the top of this script.")

    try:
        from openai import OpenAI
    except Exception as exc:
        raise SystemExit(
            "OpenAI SDK not found. Install 'openai' in your environment."
        ) from exc

    client = OpenAI(
        base_url=UIUI_BASE_URL,
        api_key=API_KEY,
    )

    tools = [
        {
            "type": "function",
            "function": {
                "name": "ping",
                "description": "Echo a message and timestamp.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "message": {"type": "string"},
                    },
                    "required": ["message"],
                },
            },
        }
    ]

    messages = [
        {
            "role": "user",
            "content": "Call the ping tool with message='hello-tools'.",
        }
    ]

    resp = client.chat.completions.create(
        model=MODEL_ID,
        messages=messages,
        tools=tools,
        tool_choice={"type": "function", "function": {"name": "ping"}},
    )

    data = resp.model_dump()
    choice = data.get("choices", [{}])[0]
    message = choice.get("message", {})
    tool_calls = message.get("tool_calls", [])

    print(
        json.dumps(
            {
                "model": data.get("model"),
                "finish_reason": choice.get("finish_reason"),
                "tool_calls": tool_calls,
                "content": message.get("content"),
            },
            ensure_ascii=True,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
