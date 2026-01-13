#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Minimal single-file Agents SDK tool-calling test (UIUI backend).
"""

import importlib
import json
import os
import sys
import time
from pathlib import Path


UIUI_BASE_URL = os.getenv("UIUI_BASE_URL", "https://sg.uiuiapi.com/v1")
MODEL_ID = os.getenv("UIUI_MODEL_ID", "gpt-5.2")
API_KEY = os.getenv("UIUI_API_KEY", "sk-c0sBK7t2p6LV84r5s7KUknm4BvzcEdiwjd3jRNE1IdV0Ero5")


def _import_agents_sdk():
    repo_root = Path(__file__).resolve().parents[1]
    script_dir = Path(__file__).resolve().parent
    for p in (str(script_dir), str(repo_root)):
        while p in sys.path:
            sys.path.remove(p)
    try:
        return importlib.import_module("agents")
    except Exception as exc:
        raise SystemExit(
            "OpenAI Agents SDK not found. Install 'openai-agents' (and 'openai'), "
            "and ensure the local 'agents/' folder is not shadowing the SDK."
        ) from exc


_agents_sdk = _import_agents_sdk()
Agent = _agents_sdk.Agent
Runner = _agents_sdk.Runner
function_tool = _agents_sdk.function_tool
set_default_openai_api = _agents_sdk.set_default_openai_api
set_default_openai_client = _agents_sdk.set_default_openai_client
set_tracing_disabled = _agents_sdk.set_tracing_disabled


@function_tool
def ping(message: str) -> str:
    """
    Echo a message with a timestamp so we can verify tool execution.
    """
    payload = {
        "message": message,
        "ts": time.time(),
    }
    print(f"[tool:ping] {payload}")
    return json.dumps(payload, ensure_ascii=True)


def run_demo() -> None:
    if not API_KEY:
        raise SystemExit("Please set UIUI_API_KEY in the environment.")

    try:
        from openai import AsyncOpenAI
    except Exception as exc:
        raise SystemExit(
            "OpenAI SDK not found. Install 'openai' in your environment."
        ) from exc

    client = AsyncOpenAI(
        base_url=UIUI_BASE_URL,
        api_key=API_KEY,
    )

    set_default_openai_api("chat_completions")
    set_default_openai_client(client)
    set_tracing_disabled(True)

    agent = Agent(
        name="ToolProbe",
        instructions=(
            "Call the ping tool exactly once with message='hello-tools'. "
            "Then answer with the tool result only."
        ),
        tools=[ping],
        model=MODEL_ID,
    )

    result = Runner.run_sync(agent, "Run the tool call now.")
    print(result.final_output)


if __name__ == "__main__":
    run_demo()
