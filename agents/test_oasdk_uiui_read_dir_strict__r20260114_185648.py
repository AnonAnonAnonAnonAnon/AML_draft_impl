#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
UIUI + OpenAI Agents SDK tool-call test (strict).
Reads all files in this script's directory via a function tool.
"""

import importlib
import json
import os
import sys
from pathlib import Path


RUN_ID = "20260114_185648"

UIUI_BASE_URL = os.getenv("UIUI_BASE_URL", "https://sg.uiuiapi.com/v1")
MODEL_ID = os.getenv("UIUI_MODEL_ID", "gpt-5.2")
API_KEY = os.getenv("UIUI_API_KEY", "sk-c0sBK7t2p6LV84r5s7KUknm4BvzcEdiwjd3jRNE1IdV0Ero5")

SCRIPT_DIR = Path(__file__).resolve().parent
TOOL_CALLED = False


def _import_agents_sdk():
    repo_root = SCRIPT_DIR.parent
    for p in (str(SCRIPT_DIR), str(repo_root)):
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
def read_script_dir_files(max_bytes_per_file: int = 2000) -> str:
    """
    Read text files in the same directory as this script.
    Returns a JSON string list of {name, bytes, preview}.
    """
    global TOOL_CALLED
    TOOL_CALLED = True

    results = []
    for name in sorted(os.listdir(SCRIPT_DIR)):
        path = SCRIPT_DIR / name
        if not path.is_file():
            continue
        try:
            size = path.stat().st_size
            with open(path, "r", encoding="utf-8", errors="ignore") as handle:
                preview = handle.read(max_bytes_per_file)
            results.append(
                {
                    "name": name,
                    "bytes": size,
                    "preview": preview,
                }
            )
        except OSError as exc:
            results.append(
                {
                    "name": name,
                    "error": str(exc),
                }
            )
    return json.dumps(results, ensure_ascii=True, indent=2)


def run_demo() -> None:
    if not API_KEY:
        raise SystemExit("Please set UIUI_API_KEY in the environment.")

    try:
        from openai import AsyncOpenAI
    except Exception as exc:
        raise SystemExit("OpenAI SDK not found. Install 'openai' in your environment.") from exc

    client = AsyncOpenAI(
        base_url=UIUI_BASE_URL,
        api_key=API_KEY,
    )

    set_default_openai_api("chat_completions")
    set_default_openai_client(client)
    set_tracing_disabled(True)

    agent = Agent(
        name="DirReader",
        instructions=(
            "Call read_script_dir_files exactly once with max_bytes_per_file=2000. "
            "After the tool returns, reply with a short Chinese summary and list file names. "
            "If you cannot call tools, reply with EXACTLY: TOOL_CALL_UNAVAILABLE"
        ),
        tools=[read_script_dir_files],
        model=MODEL_ID,
    )

    prompt = f"请读取当前脚本目录下的文件（RUN_ID={RUN_ID}）。"
    result = Runner.run_sync(agent, prompt)

    if not TOOL_CALLED:
        print("TOOL_NOT_CALLED: check model/tool support or UIUI tool-call compatibility.")
    print(result.final_output)


if __name__ == "__main__":
    run_demo()
