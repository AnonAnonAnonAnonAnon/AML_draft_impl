#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""UIUI-driven OpenAI Agents SDK demo that calls a Python tool which invokes Codex."""

import os
from pathlib import Path

from openai import AsyncOpenAI
from agents import (
    Agent,
    ModelSettings,
    Runner,
    function_tool,
    set_default_openai_api,
    set_default_openai_client,
    set_tracing_disabled,
)

from codex_wrapper_with_log__r20260115_183455 import (
    codex_exec_to_log,
    extract_section_from_log,
)


# ===== 配置区（按需修改） =====
UIUI_BASE_URL = "https://sg.uiuiapi.com/v1"
MODEL_ID = "gpt-5.2"
API_KEY = "sk-c0sBK7t2p6LV84r5s7KUknm4BvzcEdiwjd3jRNE1IdV0Ero5"
UIUI_TIMEOUT = float(os.getenv("UIUI_TIMEOUT", "60"))

REPO_ROOT = Path(__file__).resolve().parents[1]
TOOL_CALL_COUNT = 0


def _codex_list_repo_root_impl(limit: int = 5) -> str:
    """Call Codex to list the first N entries in the repo root."""
    global TOOL_CALL_COUNT
    TOOL_CALL_COUNT += 1
    print(f"[tool] codex_list_repo_root: limit={limit}")
    instruction = f"List the first {limit} entries in the repo root directory."
    log_path = codex_exec_to_log(
        instruction,
        repo_root=REPO_ROOT,
        search=False,
        check=True,
    )
    print(f"[tool] codex_list_repo_root: log_path={log_path}")

    log_text = Path(log_path).read_text(encoding="utf-8", errors="ignore")
    stdout = extract_section_from_log(log_text, "---- stdout ----", "---- stderr ----")
    stdout = stdout.strip() or "(no stdout captured)"
    return f"codex stdout:\n{stdout}\nlog_path: {log_path}"


codex_list_repo_root = function_tool(_codex_list_repo_root_impl)


def _build_client() -> AsyncOpenAI:
    if not API_KEY:
        raise ValueError("Missing UIUI API key in script.")
    return AsyncOpenAI(base_url=UIUI_BASE_URL, api_key=API_KEY, timeout=UIUI_TIMEOUT)


def run_demo() -> str:
    client = _build_client()

    set_default_openai_api("chat_completions")
    set_default_openai_client(client)
    set_tracing_disabled(True)

    print(f"[demo] UIUI_BASE_URL={UIUI_BASE_URL}")
    print(f"[demo] MODEL_ID={MODEL_ID}")
    print(f"[demo] UIUI_TIMEOUT={UIUI_TIMEOUT}")

    agent = Agent(
        name="CodexToolAgent",
        instructions=(
            "You must call the codex_list_repo_root tool exactly once and then "
            "summarize its output. The tool already knows the repo root; do not "
            "ask the user for a path."
        ),
        tools=[codex_list_repo_root],
        model_settings=ModelSettings(tool_choice="required"),
        model=MODEL_ID,
    )

    prompt = f"Call codex_list_repo_root now. Repo root is {REPO_ROOT}."
    result = Runner.run_sync(agent, prompt, max_turns=4)

    if TOOL_CALL_COUNT == 0:
        print("[demo] Tool was not invoked by the model. Running fallback tool call.")
        tool_output = _codex_list_repo_root_impl()
        return "[fallback]\n" + tool_output

    return result.final_output


if __name__ == "__main__":
    output = run_demo()
    print(output)
