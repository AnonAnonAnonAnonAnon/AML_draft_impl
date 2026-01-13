#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Minimal UIUI + OpenAI Agents SDK tool-calling test.
- Uses chat.completions via UIUI OpenAI-compatible endpoint.
- Calls a single tool once to read a local file.
"""

from pathlib import Path
import os

from openai import AsyncOpenAI
from agents import (
    Agent,
    Runner,
    function_tool,
    set_default_openai_api,
    set_default_openai_client,
    set_tracing_disabled,
)


UIUI_BASE_URL = "https://sg.uiuiapi.com/v1"
MODEL_ID = "gpt-5.2"
API_KEY = "sk-c0sBK7t2p6LV84r5s7KUknm4BvzcEdiwjd3jRNE1IdV0Ero5"

REPO_ROOT = Path(__file__).resolve().parents[1]


@function_tool
def read_text_file(rel_path: str, max_bytes: int = 800) -> str:
    """
    Read a small chunk of a text file under the repo root.
    """
    target = (REPO_ROOT / rel_path).resolve()
    if not str(target).startswith(str(REPO_ROOT)):
        raise ValueError("path outside repo root")
    print(f"[tool:read_text_file] {target} (max_bytes={max_bytes})")
    with open(target, "r", encoding="utf-8", errors="ignore") as f:
        return f.read(max_bytes)


def run_demo() -> None:
    if not API_KEY or API_KEY == "REPLACE_WITH_YOUR_UIUI_KEY":
        raise SystemExit("Please set API_KEY at the top of this file.")

    client = AsyncOpenAI(
        base_url=UIUI_BASE_URL,
        api_key=API_KEY,
    )

    set_default_openai_api("chat_completions")
    set_default_openai_client(client)
    set_tracing_disabled(True)

    agent = Agent(
        name="ToolReader",
        instructions=(
            "Call read_text_file exactly once with rel_path='README.md' and max_bytes=400. "
            "Then reply with a one-sentence summary of the content you read."
        ),
        tools=[read_text_file],
        model=MODEL_ID,
    )

    result = Runner.run_sync(agent, "Read README.md and summarize it in one sentence.")
    print(result.final_output)


if __name__ == "__main__":
    run_demo()
