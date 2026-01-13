#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Minimal agent demo that can see and call the local tool set.
"""

# ===== Config (edit here) =====
UIUI_BASE_URL = "https://sg.uiuiapi.com/v1"
MODEL_ID = "gpt-5.2"
API_KEY = "sk-c0sBK7t2p6LV84r5s7KUknm4BvzcEdiwjd3jRNE1IdV0Ero5"

# ===== Code (usually no changes needed) =====
from pathlib import Path

from openai import AsyncOpenAI
from agents import (
    Agent,
    Runner,
    set_default_openai_client,
    set_default_openai_api,
    set_tracing_disabled,
)

from agent_tools_min__r20260113_162010 import (
    run_upsert,
    run_get,
    run_search,
    log_tail,
    log_search,
    run_log_tail,
    run_log_search,
    artifact_find,
    artifact_list,
    proc_status,
    proc_kill,
    resource_gpu,
    resource_disk,
    skill_search,
)


REPO_ROOT = Path(__file__).resolve().parents[1]

client = AsyncOpenAI(
    base_url=UIUI_BASE_URL,
    api_key=API_KEY,
)

set_default_openai_api("chat_completions")
set_default_openai_client(client)
set_tracing_disabled(True)


agent = Agent(
    name="ToolCaller",
    instructions=(
        "You are a tool orchestrator. Follow these steps in order:\n"
        "1) Call run_upsert(run_id='demo_tools', run_dir=repo_root, "
        "logs=['docs/draft_tool_of_agent.txt'], status='demo', note='tool smoke test').\n"
        "2) Call run_get(run_id='demo_tools').\n"
        "3) Call log_tail(path='docs/draft_tool_of_agent.txt', n=20).\n"
        "4) Call resource_disk(paths=['.']).\n"
        "5) Call skill_search(query='robotwin', top_k=3).\n"
        "Do not call proc_kill.\n"
        "Then summarize results with short bullets."
    ),
    tools=[
        run_upsert,
        run_get,
        run_search,
        log_tail,
        log_search,
        run_log_tail,
        run_log_search,
        artifact_find,
        artifact_list,
        proc_status,
        proc_kill,
        resource_gpu,
        resource_disk,
        skill_search,
    ],
    model=MODEL_ID,
)


def run_demo() -> str:
    prompt = (
        "Run the tool smoke test. "
        f"The repo root is: {REPO_ROOT}. "
        "Use the exact steps from your instructions."
    )
    result = Runner.run_sync(agent, prompt)
    return result.final_output


if __name__ == "__main__":
    if not API_KEY or API_KEY.startswith("sk-REPLACE_"):
        raise SystemExit("Please set API_KEY at the top of this script.")

    output = run_demo()
    print(output)
