#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
UIUI + OpenAI Agents SDK minimal tool-call test.
Reads all files in this script's directory via a function tool.
"""

# ===== Config =====
UIUI_BASE_URL = "https://sg.uiuiapi.com/v1"
MODEL_ID = "gpt-5.2"
API_KEY = "sk-c0sBK7t2p6LV84r5s7KUknm4BvzcEdiwjd3jRNE1IdV0Ero5"

RUN_ID = "20260114_183350"

# ===== Code =====
import os

from openai import AsyncOpenAI
from agents import (
    Agent,
    Runner,
    set_default_openai_client,
    set_default_openai_api,
    set_tracing_disabled,
    function_tool,
)


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


@function_tool
def read_script_dir_files(max_bytes_per_file: int = 2000) -> list:
    """
    Read text files in the same directory as this script.
    Returns a list of dicts: {name, bytes, preview}.
    """
    results = []
    for name in sorted(os.listdir(SCRIPT_DIR)):
        path = os.path.join(SCRIPT_DIR, name)
        if not os.path.isfile(path):
            continue
        try:
            size = os.path.getsize(path)
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
    return results


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
        "You test tool-calling. Call read_script_dir_files exactly once. "
        "After the tool returns, reply with a short Chinese summary and list file names."
    ),
    tools=[read_script_dir_files],
    model=MODEL_ID,
)


if __name__ == "__main__":
    prompt = (
        "请调用 read_script_dir_files 读取当前脚本目录下的文件。"
        f"这是一次工具调用测试，RUN_ID={RUN_ID}。"
    )
    result = Runner.run_sync(agent, prompt)
    print(result.final_output)
