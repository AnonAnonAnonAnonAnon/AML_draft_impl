#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
UIUI + OpenAI Agents SDK minimal tool-call test.
Creates a txt file under docs/ via a function tool.
"""

# ===== Config =====
UIUI_BASE_URL = "https://sg.uiuiapi.com/v1"
MODEL_ID = "gpt-5.2"
API_KEY = "sk-c0sBK7t2p6LV84r5s7KUknm4BvzcEdiwjd3jRNE1IdV0Ero5"

RUN_ID = "20260114_182616"
PROJECT_ROOT = "/home/sumita-mana/aml/AML_draft_impl"
DOCS_DIR = f"{PROJECT_ROOT}/docs"
DEFAULT_FILENAME = f"uiui_tool_test__r{RUN_ID}.txt"

# ===== Code =====
import os
from datetime import datetime

from openai import AsyncOpenAI
from agents import (
    Agent,
    Runner,
    set_default_openai_client,
    set_default_openai_api,
    set_tracing_disabled,
    function_tool,
)


def _resolve_docs_path(filename: str) -> str:
    if os.path.isabs(filename):
        abs_path = os.path.normpath(filename)
    else:
        abs_path = os.path.normpath(os.path.join(DOCS_DIR, filename))

    docs_prefix = DOCS_DIR + os.sep
    if not abs_path.startswith(docs_prefix):
        raise ValueError("filename must resolve under docs/")

    base, ext = os.path.splitext(abs_path)
    if ext == "":
        abs_path = f"{base}.txt"
    return abs_path


@function_tool
def create_txt_in_docs(filename: str, content: str) -> str:
    """Create a new txt file under docs/ and return its relative path."""
    target = _resolve_docs_path(filename)
    if os.path.exists(target):
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        base, ext = os.path.splitext(target)
        target = f"{base}__{ts}{ext}"

    os.makedirs(os.path.dirname(target), exist_ok=True)
    with open(target, "w", encoding="utf-8") as handle:
        handle.write(content)

    rel_path = os.path.relpath(target, PROJECT_ROOT)
    print(f"[tool:create_txt_in_docs] wrote {len(content)} chars to {target}")
    return rel_path


client = AsyncOpenAI(
    base_url=UIUI_BASE_URL,
    api_key=API_KEY,
)

set_default_openai_api("chat_completions")
set_default_openai_client(client)
set_tracing_disabled(True)

agent = Agent(
    name="ToolTester",
    instructions=(
        "You test tool-calling. Call create_txt_in_docs exactly once. "
        f"Use filename '{DEFAULT_FILENAME}'. "
        "After the tool returns, reply with the path only."
    ),
    tools=[create_txt_in_docs],
    model=MODEL_ID,
)


if __name__ == "__main__":
    prompt = (
        "Create a txt file in docs/ by calling create_txt_in_docs. "
        f"filename: {DEFAULT_FILENAME}. "
        f"content: UIUI tool call ok: {RUN_ID}"
    )
    result = Runner.run_sync(agent, prompt)
    print(result.final_output)
